"""
User Model - Kullanıcı veri katmanı
"""
from sql_init import get_db
from typing import Dict, Optional, List
import uuid
import hashlib
from datetime import datetime


class UserModel:
    """Kullanıcı veri modeli - Model katmanı"""
    
    def __init__(self):
        self.db = get_db()
        self.table_name = 'users'
    
    def create(self, data: Dict) -> Dict:
        """Yeni kullanıcı oluştur"""
        try:
            # Validasyon
            required_fields = ['email', 'password', 'name']
            for field in required_fields:
                if not data.get(field):
                    raise ValueError(f"{field} alanı zorunludur")
            
            # Email format kontrolü
            email = data.get('email', '').strip().lower()
            if '@' not in email or '.' not in email.split('@')[1]:
                raise ValueError("Geçerli bir e-posta adresi giriniz")
            
            # Email benzersizlik kontrolü
            if self._email_exists(email):
                raise ValueError("Bu e-posta adresi zaten kayıtlı")
            
            # Username benzersizlik kontrolü
            username = data.get('username', '').strip()
            if username:
                if self._username_exists(username):
                    raise ValueError("Bu kullanıcı adı zaten kayıtlı")
                
                # Admin kullanıcı adı kontrolü - sadece 1 admin olabilir
                if username.lower() == 'admin':
                    if self._admin_exists():
                        raise ValueError("Admin kullanıcı adı zaten kayıtlı. Sadece bir admin kullanıcısı olabilir.")
                    role = 'admin'
                else:
                    role = data.get('role', 'user')
                    if role not in ['admin', 'staff', 'user']:
                        role = 'user'
            else:
                # Username yoksa normal kullanıcı
                role = data.get('role', 'user')
                if role not in ['admin', 'staff', 'user']:
                    role = 'user'
            
            # Şifre hash'le
            password_hash = self._hash_password(data.get('password', ''))
            
            # ID oluştur
            user_id = data.get('id', str(uuid.uuid4()))
            
            # Veriyi hazırla
            insert_data = {
                'id': user_id,
                'email': email,
                'username': username or None,
                'password_hash': password_hash,
                'name': data.get('name', '').strip(),
                'role': role,
                'is_active': 1
            }
            
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {self.table_name} 
                    (id, email, username, password_hash, name, role, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    insert_data['id'],
                    insert_data['email'],
                    insert_data['username'],
                    insert_data['password_hash'],
                    insert_data['name'],
                    insert_data['role'],
                    insert_data['is_active']
                ))
            
            # Şifreyi döndürme
            result = insert_data.copy()
            result.pop('password_hash', None)
            return result
        except Exception as e:
            raise Exception(f"Kullanıcı oluşturma hatası: {str(e)}")
    
    def authenticate(self, email: str, password: str) -> Optional[Dict]:
        """Kullanıcı doğrulama"""
        try:
            email = email.strip().lower()
            password_hash = self._hash_password(password)
            
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    SELECT * FROM {self.table_name} 
                    WHERE email = ? AND password_hash = ? AND is_active = 1
                """, (email, password_hash))
                row = cursor.fetchone()
                
                if row:
                    user = dict(row)
                    # Son giriş zamanını güncelle
                    self.update_last_login(user['id'])
                    # Şifreyi döndürme
                    user.pop('password_hash', None)
                    return user
            return None
        except Exception as e:
            raise Exception(f"Kimlik doğrulama hatası: {str(e)}")
    
    def get_by_id(self, user_id: str) -> Optional[Dict]:
        """ID'ye göre kullanıcı getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (user_id,))
                row = cursor.fetchone()
                if row:
                    user = dict(row)
                    user.pop('password_hash', None)
                    return user
            return None
        except Exception as e:
            raise Exception(f"Kullanıcı getirme hatası: {str(e)}")
    
    def get_by_email(self, email: str) -> Optional[Dict]:
        """Email'e göre kullanıcı getir"""
        try:
            email = email.strip().lower()
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.table_name} WHERE email = ?", (email,))
                row = cursor.fetchone()
                if row:
                    user = dict(row)
                    user.pop('password_hash', None)
                    return user
            return None
        except Exception as e:
            raise Exception(f"Kullanıcı getirme hatası: {str(e)}")
    
    def get_all(self) -> List[Dict]:
        """Tüm kullanıcıları getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.table_name} ORDER BY created_at DESC")
                rows = cursor.fetchall()
                users = []
                for row in rows:
                    user = dict(row)
                    user.pop('password_hash', None)
                    users.append(user)
                return users
        except Exception as e:
            raise Exception(f"Kullanıcı listesi getirme hatası: {str(e)}")
    
    def update(self, user_id: str, data: Dict) -> Dict:
        """Kullanıcı bilgilerini güncelle"""
        try:
            update_fields = []
            update_values = []
            
            if 'email' in data:
                email = data['email'].strip().lower()
                if self._email_exists(email, exclude_id=user_id):
                    raise ValueError("Bu e-posta adresi zaten kayıtlı")
                update_fields.append('email = ?')
                update_values.append(email)
            
            if 'username' in data:
                username = data['username'].strip()
                if username and self._username_exists(username, exclude_id=user_id):
                    raise ValueError("Bu kullanıcı adı zaten kayıtlı")
                update_fields.append('username = ?')
                update_values.append(username or None)
            
            if 'password' in data:
                password_hash = self._hash_password(data['password'])
                update_fields.append('password_hash = ?')
                update_values.append(password_hash)
            
            if 'name' in data:
                update_fields.append('name = ?')
                update_values.append(data['name'].strip())
            
            if 'role' in data:
                role = data['role']
                if role in ['admin', 'staff', 'user']:
                    update_fields.append('role = ?')
                    update_values.append(role)
            
            if 'is_active' in data:
                update_fields.append('is_active = ?')
                update_values.append(1 if data['is_active'] else 0)
            
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            update_values.append(user_id)
            
            if len(update_fields) <= 1:  # Sadece updated_at varsa
                return self.get_by_id(user_id)
            
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    UPDATE {self.table_name} 
                    SET {', '.join(update_fields)}
                    WHERE id = ?
                """, update_values)
            
            return self.get_by_id(user_id)
        except Exception as e:
            raise Exception(f"Kullanıcı güncelleme hatası: {str(e)}")
    
    def update_last_login(self, user_id: str):
        """Son giriş zamanını güncelle"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    UPDATE {self.table_name} 
                    SET last_login = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (user_id,))
        except:
            pass  # Hata durumunda sessizce geç
    
    def delete(self, user_id: str) -> bool:
        """Kullanıcıyı sil (soft delete)"""
        try:
            return self.update(user_id, {'is_active': 0})
        except Exception as e:
            raise Exception(f"Kullanıcı silme hatası: {str(e)}")
    
    def _hash_password(self, password: str) -> str:
        """Şifreyi hash'le"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _email_exists(self, email: str, exclude_id: Optional[str] = None) -> bool:
        """Email'in kayıtlı olup olmadığını kontrol et"""
        try:
            with self.db.get_cursor() as cursor:
                if exclude_id:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {self.table_name} WHERE email = ? AND id != ?", (email, exclude_id))
                else:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {self.table_name} WHERE email = ?", (email,))
                row = cursor.fetchone()
                return row['count'] > 0 if row else False
        except:
            return True  # Hata durumunda güvenli tarafta kal
    
    def _username_exists(self, username: str, exclude_id: Optional[str] = None) -> bool:
        """Username'in kayıtlı olup olmadığını kontrol et"""
        try:
            with self.db.get_cursor() as cursor:
                if exclude_id:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {self.table_name} WHERE username = ? AND id != ?", (username, exclude_id))
                else:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {self.table_name} WHERE username = ?", (username,))
                row = cursor.fetchone()
                return row['count'] > 0 if row else False
        except:
            return True  # Hata durumunda güvenli tarafta kal
    
    def _admin_exists(self) -> bool:
        """Admin kullanıcısı var mı kontrol et"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    SELECT COUNT(*) as count FROM {self.table_name} 
                    WHERE (username = 'admin' OR role = 'admin') AND is_active = 1
                """)
                row = cursor.fetchone()
                return row['count'] > 0 if row else False
        except:
            return False
    
    def get_by_username(self, username: str) -> Optional[Dict]:
        """Username'e göre kullanıcı getir"""
        try:
            username = username.strip()
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.table_name} WHERE username = ? AND is_active = 1", (username,))
                row = cursor.fetchone()
                if row:
                    user = dict(row)
                    user.pop('password_hash', None)
                    return user
            return None
        except Exception as e:
            raise Exception(f"Kullanıcı getirme hatası: {str(e)}")

