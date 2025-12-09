from flask import Blueprint, jsonify, request, render_template, session
from sql_init import get_db
from models.cari_hesap_model import CariHesapModel
from models.fatura_model import FaturaModel
from models.malzeme_model import MalzemeModel
from services.auth_service import AuthService
from services.logging_service import LoggingService
from utils.validators import Validators
import uuid

# Blueprint'ler
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Servisler
auth_service = AuthService()
logging_service = LoggingService()

@main_bp.route('/')
def index():
    """Ana sayfa - Karşılama ekranı"""
    # Eğer giriş yapılmamışsa login sayfasına yönlendir
    if not auth_service.is_logged_in():
        return render_template('login.html')
    return render_template('dashboard.html')

@main_bp.route('/login')
def login_page():
    """Login sayfası"""
    return render_template('login.html')

@main_bp.route('/register')
def register_page():
    """Kayıt sayfası"""
    return render_template('register.html')

@main_bp.route('/cari-hesap')
def cari_hesap_liste():
    """Cari hesap listesi sayfası"""
    return render_template('cari_hesap_liste.html')

@main_bp.route('/cari-hesap/ekle')
def cari_hesap_ekle():
    """Cari hesap ekleme sayfası"""
    return render_template('cari_hesap_ekle.html')

@main_bp.route('/malzemeler')
def malzeme_liste():
    """Malzeme listesi sayfası"""
    return render_template('malzeme_liste.html')

@main_bp.route('/satis-faturalari')
def satis_faturalari():
    """Satış faturaları sayfası"""
    return render_template('fatura_liste.html')

@main_bp.route('/satis-faturalari/ekle')
def satis_faturalari_ekle():
    """Yeni fatura ekleme sayfası"""
    return render_template('fatura_ekle.html')

@main_bp.route('/satis-faturalari/<fatura_id>')
def satis_faturalari_detay(fatura_id):
    """Fatura detay sayfası"""
    # Faturayı getir ve template'e gönder
    try:
        model = FaturaModel()
        fatura_list = model.get_all()
        fatura = next((f for f in fatura_list if f['id'] == fatura_id), None)
        return render_template('fatura_detay.html', fatura_id=fatura_id, fatura=fatura)
    except:
        return render_template('fatura_detay.html', fatura_id=fatura_id, fatura=None)

@main_bp.route('/health')
def health():
    """Sağlık kontrolü"""
    return jsonify({
        'status': 'healthy',
        'service': 'SQLite Python API'
    })

@api_bp.route('/users', methods=['GET'])
def get_users():
    """Tüm kullanıcıları getir"""
    try:
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            users = [dict(row) for row in rows]
        
        return jsonify({
            'success': True,
            'users': users
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/users', methods=['POST'])
def create_user():
    """Yeni kullanıcı oluştur"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Veri bulunamadı'
            }), 400
        
        user_id = str(uuid.uuid4())
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (id, email, name, role)
                VALUES (?, ?, ?, ?)
            """, (
                user_id,
                data.get('email', ''),
                data.get('name', ''),
                data.get('role', 'user')
            ))
        
        return jsonify({
            'success': True,
            'id': user_id,
            'message': 'Kullanıcı başarıyla oluşturuldu'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Belirli bir kullanıcıyı getir"""
    try:
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
            if not row:
                return jsonify({
                    'success': False,
                    'error': 'Kullanıcı bulunamadı'
                }), 404
            
            return jsonify({
                'success': True,
                'user': dict(row)
            }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Kullanıcı bilgilerini güncelle"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Veri bulunamadı'
            }), 400
        
        db = get_db()
        update_fields = []
        update_values = []
        
        if 'email' in data:
            update_fields.append('email = ?')
            update_values.append(data['email'])
        if 'name' in data:
            update_fields.append('name = ?')
            update_values.append(data['name'])
        if 'role' in data:
            update_fields.append('role = ?')
            update_values.append(data['role'])
        
        if not update_fields:
            return jsonify({
                'success': False,
                'error': 'Güncellenecek alan bulunamadı'
            }), 400
        
        update_values.append(user_id)
        
        with db.get_cursor() as cursor:
            cursor.execute(f"""
                UPDATE users 
                SET {', '.join(update_fields)}
                WHERE id = ?
            """, update_values)
        
        return jsonify({
            'success': True,
            'message': 'Kullanıcı başarıyla güncellendi'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Kullanıcıyı sil"""
    try:
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        return jsonify({
            'success': True,
            'message': 'Kullanıcı başarıyla silindi'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/cari-hesap', methods=['POST'])
def create_cari_hesap():
    """Yeni cari hesap oluştur"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Veri bulunamadı'
            }), 400
        
        # Validation
        valid, error = Validators.validate_required(data.get('unvani'), 'Unvan')
        if not valid:
            return jsonify({'success': False, 'error': error}), 400
        
        valid, error = Validators.validate_tax_number(data.get('vergiNo', ''))
        if not valid:
            return jsonify({'success': False, 'error': error}), 400
        
        if data.get('email'):
            valid, error = Validators.validate_email(data.get('email'))
            if not valid:
                return jsonify({'success': False, 'error': error}), 400
        
        if data.get('telefon'):
            valid, error = Validators.validate_phone(data.get('telefon'))
            if not valid:
                return jsonify({'success': False, 'error': error}), 400
        
        # Model kullanarak oluştur
        model = CariHesapModel()
        result = model.create(data)
        
        # Log kaydı
        user_id = session.get('user_id')
        logging_service.log(user_id, 'CREATE', 'cari_hesap', result['id'],
                          {'action': 'Cari hesap oluşturuldu', 'unvan': result.get('unvani')},
                          request.remote_addr)
        
        return jsonify({
            'success': True,
            'id': result['id'],
            'message': 'Cari hesap başarıyla oluşturuldu'
        }), 201
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/cari-hesap', methods=['GET'])
def get_cari_hesap_list():
    """Tüm cari hesapları getir"""
    try:
        model = CariHesapModel()
        cari_list = model.get_all()
        
        return jsonify({
            'success': True,
            'cari_hesap': cari_list
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/cari-hesap/<cari_id>', methods=['PUT'])
@auth_service.require_admin
def update_cari_hesap(cari_id):
    """Cari hesabı güncelle - Sadece admin"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Veri bulunamadı'
            }), 400
        
        model = CariHesapModel()
        result = model.update(cari_id, data)
        
        # Log kaydı
        user_id = session.get('user_id')
        logging_service.log(user_id, 'UPDATE', 'cari_hesap', cari_id,
                          {'action': 'Cari hesap güncellendi'}, request.remote_addr)
        
        return jsonify({
            'success': True,
            'message': 'Cari hesap başarıyla güncellendi'
        }), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/cari-hesap/<cari_id>', methods=['DELETE'])
def delete_cari_hesap(cari_id):
    """Cari hesabı sil - Sadece admin"""
    try:
        # Admin kontrolü
        if not auth_service.is_admin():
            return jsonify({
                'success': False,
                'error': 'Bu işlem için admin yetkisi gereklidir'
            }), 403
        
        model = CariHesapModel()
        model.delete(cari_id)
        
        # Log kaydı
        user_id = session.get('user_id')
        logging_service.log(user_id, 'DELETE', 'cari_hesap', cari_id,
                          {'action': 'Cari hesap silindi'}, request.remote_addr)
        
        return jsonify({
            'success': True,
            'message': 'Cari hesap başarıyla silindi'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/fatura', methods=['GET'])
def get_fatura_list():
    """Tüm faturaları getir"""
    try:
        model = FaturaModel()
        fatura_list = model.get_all()
        
        return jsonify({
            'success': True,
            'faturalar': fatura_list
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/fatura', methods=['POST'])
def create_fatura():
    """Yeni fatura oluştur"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Veri bulunamadı'
            }), 400
        
        # Kullanıcı bilgisini session'dan al
        user_id = session.get('user_id')
        user_name = session.get('user_name', '')
        
        # Model kullanarak oluştur
        model = FaturaModel()
        result = model.create(data, user_id, user_name)
        
        return jsonify({
            'success': True,
            'id': result['id'],
            'message': 'Fatura başarıyla oluşturuldu'
        }), 201
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/fatura/<fatura_id>', methods=['GET'])
def get_fatura(fatura_id):
    """Belirli bir faturayı getir"""
    try:
        model = FaturaModel()
        fatura_list = model.get_all()
        fatura = next((f for f in fatura_list if f['id'] == fatura_id), None)
        
        if not fatura:
            return jsonify({
                'success': False,
                'error': 'Fatura bulunamadı'
            }), 404
        
        return jsonify({
            'success': True,
            'fatura': fatura
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/fatura/<fatura_id>', methods=['PUT'])
def update_fatura(fatura_id):
    """Faturayı güncelle"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Veri bulunamadı'
            }), 400
        
        # Kullanıcı bilgisini session'dan al
        user_id = session.get('user_id')
        user_name = session.get('user_name', '')
        
        # Model kullanarak güncelle
        model = FaturaModel()
        result = model.update(fatura_id, data, user_id, user_name)
        
        # Log kaydı
        logging_service.log(user_id, 'UPDATE', 'fatura', fatura_id,
                          {'action': 'Fatura güncellendi'}, request.remote_addr)
        
        return jsonify({
            'success': True,
            'fatura': result,
            'message': 'Fatura başarıyla güncellendi'
        }), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/fatura/<fatura_id>', methods=['DELETE'])
def delete_fatura(fatura_id):
    """Faturayı sil - Sadece admin"""
    try:
        # Admin kontrolü
        if not auth_service.is_admin():
            return jsonify({
                'success': False,
                'error': 'Bu işlem için admin yetkisi gereklidir'
            }), 403
        
        db = get_db()
        with db.get_cursor() as cursor:
            cursor.execute("DELETE FROM faturalar WHERE id = ?", (fatura_id,))
        
        # Log kaydı
        user_id = session.get('user_id')
        logging_service.log(user_id, 'DELETE', 'fatura', fatura_id, 
                          {'action': 'Fatura silindi'}, request.remote_addr)
        
        return jsonify({
            'success': True,
            'message': 'Fatura başarıyla silindi'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/fatura/<fatura_id>/pdf', methods=['GET'])
def get_fatura_pdf(fatura_id):
    """Fatura PDF'i oluştur ve indir"""
    try:
        from services.fatura_pdf_service import FaturaPDFService
        import tempfile
        import os
        
        # Faturayı getir
        model = FaturaModel()
        fatura_list = model.get_all()
        fatura = next((f for f in fatura_list if f['id'] == fatura_id), None)
        
        if not fatura:
            return jsonify({
                'success': False,
                'error': 'Fatura bulunamadı'
            }), 404
        
        # PDF oluştur
        pdf_service = FaturaPDFService()
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, f"Fatura_{fatura['faturaNo']}.pdf")
        
        pdf_service.generate_efatura_pdf(fatura, pdf_path)
        
        # PDF'i oku ve gönder
        from flask import send_file
        return send_file(pdf_path, as_attachment=True, download_name=f"Fatura_{fatura['faturaNo']}.pdf")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/fatura/<fatura_id>/send-email', methods=['POST'])
def send_fatura_email(fatura_id):
    """Faturayı e-posta ile gönder"""
    try:
        from services.fatura_pdf_service import FaturaPDFService
        from services.email_service import EmailService
        import tempfile
        import os
        
        # Faturayı getir
        model = FaturaModel()
        fatura_list = model.get_all()
        fatura = next((f for f in fatura_list if f['id'] == fatura_id), None)
        
        if not fatura:
            return jsonify({
                'success': False,
                'error': 'Fatura bulunamadı'
            }), 404
        
        # Cari hesap bilgilerini al
        cari_hesap = fatura.get('cariHesap', {})
        if isinstance(cari_hesap, str):
            import json
            try:
                cari_hesap = json.loads(cari_hesap)
            except:
                cari_hesap = {}
        
        to_email = cari_hesap.get('email', '')
        if not to_email:
            return jsonify({
                'success': False,
                'error': 'Cari hesap için e-posta adresi bulunamadı'
            }), 400
        
        # PDF oluştur
        pdf_service = FaturaPDFService()
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, f"Fatura_{fatura['faturaNo']}.pdf")
        
        pdf_service.generate_efatura_pdf(fatura, pdf_path)
        
        # E-posta gönder
        email_service = EmailService()
        email_service.send_fatura_email(to_email, fatura, pdf_path)
        
        # Geçici dosyayı sil
        try:
            os.remove(pdf_path)
        except:
            pass
        
        # Log kaydı
        user_id = session.get('user_id')
        logging_service.log(user_id, 'SEND_EMAIL', 'fatura', fatura_id,
                          {'action': 'Fatura e-posta ile gönderildi', 'to': to_email}, request.remote_addr)
        
        return jsonify({
            'success': True,
            'message': 'Fatura başarıyla e-posta ile gönderildi'
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Authentication Routes
@auth_bp.route('/login', methods=['POST'])
def login():
    """Kullanıcı girişi"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'E-posta ve şifre gereklidir'
            }), 400
        
        user = auth_service.login(email, password)
        if user:
            # Log kaydı
            logging_service.log(user['id'], 'LOGIN', 'user', user['id'],
                              {'action': 'Kullanıcı giriş yaptı'}, request.remote_addr)
            
            return jsonify({
                'success': True,
                'user': user,
                'message': 'Giriş başarılı'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'E-posta veya şifre hatalı'
            }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Kullanıcı çıkışı"""
    try:
        user_id = session.get('user_id')
        auth_service.logout()
        
        # Log kaydı
        if user_id:
            logging_service.log(user_id, 'LOGOUT', 'user', user_id,
                              {'action': 'Kullanıcı çıkış yaptı'}, request.remote_addr)
        
        return jsonify({
            'success': True,
            'message': 'Çıkış başarılı'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Kullanıcı kaydı"""
    try:
        data = request.get_json()
        
        # Validasyon
        if not data.get('email') or not data.get('password') or not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'E-posta, şifre ve isim gereklidir'
            }), 400
        
        if len(data.get('password', '')) < 6:
            return jsonify({
                'success': False,
                'error': 'Şifre en az 6 karakter olmalıdır'
            }), 400
        
        # Admin kullanıcı adı kontrolü
        username = data.get('username', '').strip() if data.get('username') else ''
        if username.lower() == 'admin':
            from models.user_model import UserModel
            user_model = UserModel()
            if user_model._admin_exists():
                return jsonify({
                    'success': False,
                    'error': 'Admin kullanıcı adı zaten kayıtlı. Sadece bir admin kullanıcısı olabilir.'
                }), 400
        
        user = auth_service.register(data)
        
        # Log kaydı
        logging_service.log(user['id'], 'REGISTER', 'user', user['id'],
                          {'action': 'Yeni kullanıcı kaydı', 'username': user.get('username', '')}, request.remote_addr)
        
        return jsonify({
            'success': True,
            'user': user,
            'message': 'Kayıt başarılı'
        }), 201
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Mevcut kullanıcı bilgilerini getir"""
    try:
        user = auth_service.get_current_user()
        if user:
            # Admin kontrolü ekle
            is_admin = auth_service.is_admin()
            can_view_logs = auth_service.can_view_logs()
            user['is_admin'] = is_admin
            user['can_view_logs'] = can_view_logs
            return jsonify({
                'success': True,
                'user': user
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Giriş yapılmamış'
            }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/auth/me', methods=['GET'])
def get_current_user_api():
    """Mevcut kullanıcı bilgilerini getir (API endpoint)"""
    try:
        user = auth_service.get_current_user()
        if user:
            # Admin kontrolü ekle
            try:
                is_admin = auth_service.is_admin()
                can_view_logs = auth_service.can_view_logs()
            except:
                is_admin = False
                can_view_logs = False
            
            user['is_admin'] = is_admin
            user['can_view_logs'] = can_view_logs
            return jsonify({
                'success': True,
                'user': user
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Giriş yapılmamış'
            }), 401
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Admin Log Routes
@main_bp.route('/admin/logs')
def admin_logs_page():
    """Admin log sayfası"""
    # Log görüntüleme kontrolü
    if not auth_service.can_view_logs():
        from flask import redirect, url_for
        return redirect(url_for('main.index'))
    return render_template('admin_logs.html')

@api_bp.route('/admin/logs', methods=['GET'])
def get_admin_logs():
    """Admin loglarını getir"""
    try:
        # Log görüntüleme kontrolü
        if not auth_service.can_view_logs():
            return jsonify({
                'success': False,
                'error': 'Yetkisiz erişim'
            }), 403
        
        # Parametreler
        limit = request.args.get('limit', 100, type=int)
        entity_type = request.args.get('entity_type', None)
        user_id = request.args.get('user_id', None)
        action = request.args.get('action', None)
        
        logs = logging_service.get_logs(
            user_id=user_id,
            entity_type=entity_type,
            action=action,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'logs': logs,
            'count': len(logs)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Malzeme API Routes
@api_bp.route('/malzeme', methods=['GET'])
def get_malzeme_list():
    """Tüm malzemeleri getir"""
    try:
        model = MalzemeModel()
        malzeme_list = model.get_all()
        
        return jsonify({
            'success': True,
            'malzemeler': malzeme_list
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/malzeme', methods=['POST'])
def create_malzeme():
    """Yeni malzeme oluştur"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Veri bulunamadı'
            }), 400
        
        # Validation
        if not data.get('ad'):
            return jsonify({'success': False, 'error': 'Malzeme adı zorunludur'}), 400
        
        if not data.get('birim'):
            return jsonify({'success': False, 'error': 'Birim zorunludur'}), 400
        
        # Model kullanarak oluştur
        model = MalzemeModel()
        result = model.create(data)
        
        # Log kaydı
        user_id = session.get('user_id')
        logging_service.log(user_id, 'CREATE', 'malzeme', result['id'],
                          {'action': 'Malzeme oluşturuldu', 'ad': result.get('ad')},
                          request.remote_addr)
        
        return jsonify({
            'success': True,
            'id': result['id'],
            'message': 'Malzeme başarıyla oluşturuldu'
        }), 201
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/malzeme/<malzeme_id>', methods=['PUT'])
def update_malzeme(malzeme_id):
    """Malzemeyi güncelle"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Veri bulunamadı'
            }), 400
        
        model = MalzemeModel()
        updated_malzeme = model.update(malzeme_id, data)
        
        if updated_malzeme:
            # Log kaydı
            user_id = session.get('user_id')
            logging_service.log(user_id, 'UPDATE', 'malzeme', malzeme_id,
                              {'action': 'Malzeme güncellendi', 'ad': updated_malzeme.get('ad')},
                              request.remote_addr)
            
            return jsonify({
                'success': True,
                'malzeme': updated_malzeme,
                'message': 'Malzeme başarıyla güncellendi'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Malzeme bulunamadı'
            }), 404
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/malzeme/<malzeme_id>', methods=['DELETE'])
def delete_malzeme(malzeme_id):
    """Malzemeyi sil"""
    try:
        model = MalzemeModel()
        model.delete(malzeme_id)
        
        # Log kaydı
        user_id = session.get('user_id')
        logging_service.log(user_id, 'DELETE', 'malzeme', malzeme_id,
                          {'action': 'Malzeme silindi'}, request.remote_addr)
        
        return jsonify({
            'success': True,
            'message': 'Malzeme başarıyla silindi'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
