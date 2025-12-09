import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Uygulama yapılandırma ayarları"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SQLite yapılandırması
    SQLITE_DB_PATH = os.environ.get('SQLITE_DB_PATH') or 'database.db'
    
    # Flask ayarları
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('HOST', '127.0.0.1')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Gmail ayarları (varsayılan)
    GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL', 'dariyeribilal3@gmail.com')
    GMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD', 'gmrsuveztjglzmgh')
    
    # Şirket Bilgileri - MUBA
    COMPANY_NAME = "KARABERRY YAZILIM VE TEKNOLOJİ TİC. LTD. ŞTİ."
    COMPANY_ADDRESS = "Yazır Mah. Doç. Dr. Halil Ürün Cd. Teknokent Binası No:15"
    COMPANY_CITY = "42250 SELÇUKLU / KONYA"
    COMPANY_PHONE = "0332 123 45 67"
    COMPANY_FAX = "0332 987 65 43"
    COMPANY_WEBSITE = "www.karaberry.com"
    COMPANY_EMAIL = "info@karaberry.com"
    COMPANY_TAX_OFFICE = "SELÇUK VERGİ DAİRESİ"
    COMPANY_TAX_NUMBER = "1234567890"
    COMPANY_MERSIS = "0123456789000019"
    COMPANY_TRADE_REGISTRY = "54321"
    
    # Banka Bilgileri
    BANK_NAME = "Ziraat Bankası"
    BANK_ACCOUNT_NAME = "Karaberry Yazılım Hesabı"
    BANK_IBAN = "TR12 0001 0002 0003 0004 0005 06"

