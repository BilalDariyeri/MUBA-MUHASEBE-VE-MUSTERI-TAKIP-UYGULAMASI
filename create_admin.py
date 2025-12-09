"""
Admin Kullanıcı Oluşturma Scripti
"""
import sys
import os

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.user_model import UserModel

def create_admin_user(force=False):
    """Admin kullanıcı oluştur"""
    try:
        user_model = UserModel()
        
        # Admin kullanıcı bilgileri
        admin_data = {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'admin123',  # Varsayılan şifre - değiştirilebilir
            'name': 'Sistem Yöneticisi',
            'role': 'admin'
        }
        
        # Mevcut admin kontrolü
        if user_model._admin_exists():
            existing_admin = user_model.get_by_username('admin')
            if not existing_admin:
                # Username ile bulunamadıysa role ile ara
                all_users = user_model.get_all()
                existing_admin = next((u for u in all_users if u.get('role') == 'admin' and u.get('is_active')), None)
            
            if existing_admin:
                if not force:
                    print("⚠️  Admin kullanıcısı zaten mevcut!")
                    print(f"\n📋 Mevcut Admin Bilgileri:")
                    print(f"   Kullanıcı Adı: {existing_admin.get('username', 'N/A')}")
                    print(f"   Email: {existing_admin.get('email', 'N/A')}")
                    print(f"   Ad: {existing_admin.get('name', 'N/A')}")
                    print(f"   Role: {existing_admin.get('role', 'N/A')}")
                    print("\n💡 Yeni admin oluşturmak için mevcut admin'i devre dışı bırakılıyor...")
                
                # Mevcut admin'i devre dışı bırak
                user_model.update(existing_admin['id'], {'is_active': 0})
                print(f"✅ Mevcut admin devre dışı bırakıldı: {existing_admin.get('username', 'N/A')}")
        
        # Admin kullanıcı oluştur
        admin_user = user_model.create(admin_data)
        
        print("\n✅ Yeni admin kullanıcısı başarıyla oluşturuldu!")
        print("\n" + "="*50)
        print("📋 YENİ ADMIN GİRİŞ BİLGİLERİ:")
        print("="*50)
        print(f"   Kullanıcı Adı: {admin_data['username']}")
        print(f"   Email: {admin_data['email']}")
        print(f"   Şifre: {admin_data['password']}")
        print(f"   Ad: {admin_data['name']}")
        print("="*50)
        print("\n⚠️  ÖNEMLİ: İlk girişten sonra şifrenizi değiştirmeniz önerilir!")
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return False
    
    return True

if __name__ == '__main__':
    import sys
    force = '--force' in sys.argv or '-f' in sys.argv
    
    print("=" * 50)
    print("Admin Kullanıcı Oluşturma")
    print("=" * 50)
    print()
    create_admin_user(force=force)
    print()
    print("=" * 50)
