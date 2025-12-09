from flask import Flask, session
from flask_cors import CORS
from config import Config
from sql_init import get_db

def create_app():
    """Flask uygulamasını oluşturur ve yapılandırır"""
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)
    
    # Session ayarları
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 saat
    
    # CORS ayarları
    CORS(app, supports_credentials=True)
    
    # SQLite veritabanını başlat
    try:
        db = get_db()
        print("SQLite veritabanı başarıyla başlatıldı")
    except Exception as e:
        print(f"SQLite başlatma hatası: {e}")
    
    # Blueprint'leri kaydet
    from app.routes import main_bp, api_bp, auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    
    return app

