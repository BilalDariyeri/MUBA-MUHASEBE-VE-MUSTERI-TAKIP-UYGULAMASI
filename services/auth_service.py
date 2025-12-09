"""
Authentication Service - Kimlik doğrulama servisi
"""
from flask import session
from models.user_model import UserModel
from typing import Optional, Dict
from functools import wraps
from flask import abort, jsonify


class AuthService:
    """Kimlik doğrulama servisi"""
    
    def __init__(self):
        self.user_model = UserModel()
    
    def login(self, email: str, password: str) -> Optional[Dict]:
        """Kullanıcı girişi"""
        try:
            user = self.user_model.authenticate(email, password)
            if user:
                # Session'a kullanıcı bilgilerini kaydet
                session['user_id'] = user['id']
                session['user_email'] = user['email']
                session['user_name'] = user['name']
                session['user_role'] = user['role']
                session['logged_in'] = True
                return user
            return None
        except Exception as e:
            raise Exception(f"Giriş hatası: {str(e)}")
    
    def logout(self):
        """Kullanıcı çıkışı"""
        session.clear()
    
    def register(self, data: Dict) -> Dict:
        """Kullanıcı kaydı"""
        try:
            # Validasyon
            if not data.get('password') or len(data.get('password', '')) < 6:
                raise ValueError("Şifre en az 6 karakter olmalıdır")
            
            user = self.user_model.create(data)
            return user
        except Exception as e:
            raise Exception(f"Kayıt hatası: {str(e)}")
    
    def get_current_user(self) -> Optional[Dict]:
        """Mevcut kullanıcıyı getir"""
        if not session.get('logged_in'):
            return None
        
        user_id = session.get('user_id')
        if user_id:
            return self.user_model.get_by_id(user_id)
        return None
    
    def is_logged_in(self) -> bool:
        """Kullanıcı giriş yapmış mı?"""
        return session.get('logged_in', False)
    
    def is_admin(self) -> bool:
        """Kullanıcı admin mi?"""
        if not self.is_logged_in():
            return False
        
        user = self.get_current_user()
        if not user:
            return False
        
        # Username "admin" ise veya role "admin" ise
        return (user.get('username', '').lower() == 'admin' or 
                user.get('role', '').lower() == 'admin')
    
    def can_view_logs(self) -> bool:
        """Kullanıcı log kayıtlarını görebilir mi?"""
        # Tüm giriş yapmış kullanıcılar log kayıtlarını görebilir
        return self.is_logged_in()
    
    def require_admin(self, f):
        """Admin kontrolü decorator"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.is_admin():
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
        return session.get('logged_in', False)
    
    def has_role(self, *roles) -> bool:
        """Kullanıcının belirtilen rollerden biri var mı?"""
        user_role = session.get('user_role')
        return user_role in roles
    
    def require_login(self, f):
        """Login gerektiren decorator"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.is_logged_in():
                return jsonify({
                    'success': False,
                    'error': 'Giriş yapmanız gerekiyor'
                }), 401
            return f(*args, **kwargs)
        return decorated_function
    
    def require_role(self, *roles):
        """Rol gerektiren decorator"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not self.is_logged_in():
                    return jsonify({
                        'success': False,
                        'error': 'Giriş yapmanız gerekiyor'
                    }), 401
                if not self.has_role(*roles):
                    return jsonify({
                        'success': False,
                        'error': 'Bu işlem için yetkiniz yok'
                    }), 403
                return f(*args, **kwargs)
            return decorated_function
        return decorator

