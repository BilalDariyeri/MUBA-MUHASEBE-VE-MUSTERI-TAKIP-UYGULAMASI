"""
SQLite Veritabanı Bağlantı ve Şema Yönetimi
"""
import sqlite3
import os
from typing import Optional
from contextlib import contextmanager
from config import Config


def migrate_users_table(cursor):
    """Users tablosunu migrate et - eksik kolonları ekle"""
    try:
        # Mevcut kolonları kontrol et
        cursor.execute("PRAGMA table_info(users)")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        # Eksik kolonları ekle
        if 'username' not in columns:
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN username TEXT")
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise
        
        if 'password_hash' not in columns:
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
                # Mevcut kullanıcılar için boş password_hash
                cursor.execute("UPDATE users SET password_hash = '' WHERE password_hash IS NULL")
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise
        
        if 'is_active' not in columns:
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
                cursor.execute("UPDATE users SET is_active = 1 WHERE is_active IS NULL")
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise
        
        if 'last_login' not in columns:
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise
        
        if 'updated_at' not in columns:
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise
        
        # UNIQUE constraint'leri ekle (eğer yoksa)
        try:
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique ON users(email)")
        except:
            pass
        
        try:
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_unique ON users(username) WHERE username IS NOT NULL")
        except:
            pass
            
    except Exception as e:
        print(f"Migration uyarısı (devam ediliyor): {e}")


class Database:
    """SQLite veritabanı yönetimi"""
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._connection is None:
            self.db_path = getattr(Config, 'SQLITE_DB_PATH', 'database.db')
            self._connection = None
            self.init_database()
    
    def get_connection(self):
        """Veritabanı bağlantısı al"""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row  # Dict-like row access
        return self._connection
    
    @contextmanager
    def get_cursor(self):
        """Cursor context manager"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def init_database(self):
        """Veritabanı şemasını oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Önce mevcut users tablosunu migrate et (eğer varsa)
            try:
                cursor.execute("SELECT COUNT(*) FROM users")
                # Tablo varsa migration yap
                migrate_users_table(cursor)
                conn.commit()
            except sqlite3.OperationalError:
                # Tablo yoksa normal devam et
                pass
            
            # Cari Hesap Tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cari_hesap (
                    id TEXT PRIMARY KEY,
                    unvani TEXT NOT NULL,
                    vergiNo TEXT NOT NULL,
                    vergiNoHash TEXT,
                    telefon TEXT,
                    email TEXT,
                    adres TEXT,
                    sehir TEXT,
                    ad TEXT,
                    borc REAL DEFAULT 0,
                    alacak REAL DEFAULT 0,
                    statusu TEXT DEFAULT 'Kullanımda',
                    odemePlani TEXT DEFAULT '30 Gün',  -- Ödeme planı: Peşin, 30 Gün, 60 Gün, 120 Gün
                    iletisim TEXT,  -- JSON string
                    notlar TEXT,    -- JSON string
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Mevcut tabloya odemePlani kolonu ekle (eğer yoksa)
            try:
                cursor.execute("PRAGMA table_info(cari_hesap)")
                columns = [row[1] for row in cursor.fetchall()]
                if 'odemePlani' not in columns:
                    cursor.execute("ALTER TABLE cari_hesap ADD COLUMN odemePlani TEXT DEFAULT '30 Gün'")
            except:
                pass
            
            # Malzeme Tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS malzemeler (
                    id TEXT PRIMARY KEY,
                    kod TEXT UNIQUE NOT NULL,
                    ad TEXT NOT NULL,
                    birim TEXT NOT NULL,
                    stok REAL DEFAULT 0,
                    birimFiyat REAL DEFAULT 0,
                    kdvOrani INTEGER DEFAULT 18,
                    current_buy_price REAL DEFAULT 0,
                    average_cost REAL DEFAULT 0,
                    aciklama TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Malzemeler tablosuna yeni sütunları ekle (eğer yoksa)
            try:
                cursor.execute("PRAGMA table_info(malzemeler)")
                columns = [row[1] for row in cursor.fetchall()]
                if 'current_buy_price' not in columns:
                    cursor.execute("ALTER TABLE malzemeler ADD COLUMN current_buy_price REAL DEFAULT 0")
                if 'average_cost' not in columns:
                    cursor.execute("ALTER TABLE malzemeler ADD COLUMN average_cost REAL DEFAULT 0")
            except:
                pass
            
            # Fatura Tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS faturalar (
                    id TEXT PRIMARY KEY,
                    faturaNo TEXT UNIQUE NOT NULL,
                    tarih TEXT NOT NULL,
                    faturaTipi TEXT,
                    cariId TEXT,
                    toplam REAL DEFAULT 0,
                    toplamKDV REAL DEFAULT 0,
                    netTutar REAL DEFAULT 0,
                    durum TEXT DEFAULT 'Açık',
                    cariHesap TEXT,  -- JSON string
                    satirlar TEXT,   -- JSON string
                    created_by TEXT,
                    created_by_name TEXT,
                    last_modified_by TEXT,
                    last_modified_by_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cariId) REFERENCES cari_hesap(id)
                )
            """)
            
            # Faturalar tablosuna düzenleyen sütunları ekle (eğer yoksa)
            try:
                cursor.execute("PRAGMA table_info(faturalar)")
                columns = [row[1] for row in cursor.fetchall()]
                if 'created_by' not in columns:
                    cursor.execute("ALTER TABLE faturalar ADD COLUMN created_by TEXT")
                if 'created_by_name' not in columns:
                    cursor.execute("ALTER TABLE faturalar ADD COLUMN created_by_name TEXT")
                if 'last_modified_by' not in columns:
                    cursor.execute("ALTER TABLE faturalar ADD COLUMN last_modified_by TEXT")
                if 'last_modified_by_name' not in columns:
                    cursor.execute("ALTER TABLE faturalar ADD COLUMN last_modified_by_name TEXT")
            except:
                pass
            
            # Users Tablosu (Authentication için genişletilmiş)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    role TEXT DEFAULT 'user' CHECK(role IN ('admin', 'staff', 'user')),
                    is_active INTEGER DEFAULT 1,
                    last_login TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Activity Log Tablosu (Logging için)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    action TEXT NOT NULL,
                    entity_type TEXT,
                    entity_id TEXT,
                    details TEXT,
                    ip_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Fatura satırları için ayrı tablo (N-N ilişki için)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fatura_satirlar (
                    id TEXT PRIMARY KEY,
                    fatura_id TEXT NOT NULL,
                    malzeme_id TEXT,
                    malzeme_kodu TEXT,
                    malzeme_ismi TEXT,
                    miktar REAL DEFAULT 0,
                    birim TEXT,
                    birim_fiyat REAL DEFAULT 0,
                    kdv_orani REAL DEFAULT 0,
                    tutar REAL DEFAULT 0,
                    net_tutar REAL DEFAULT 0,
                    sira_no INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (fatura_id) REFERENCES faturalar(id) ON DELETE CASCADE,
                    FOREIGN KEY (malzeme_id) REFERENCES malzemeler(id)
                )
            """)
            
            # Index'ler
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cari_vergi_no ON cari_hesap(vergiNo)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cari_vergi_no_hash ON cari_hesap(vergiNoHash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_malzeme_kod ON malzemeler(kod)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fatura_no ON faturalar(faturaNo)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fatura_cari_id ON faturalar(cariId)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_log_user ON activity_logs(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_log_created ON activity_logs(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fatura_satirlar_fatura ON fatura_satirlar(fatura_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fatura_satirlar_malzeme ON fatura_satirlar(malzeme_id)")
            
            # Alım Faturaları Tablosu (Purchase Invoices)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchase_invoices (
                    id TEXT PRIMARY KEY,
                    fatura_no TEXT UNIQUE NOT NULL,
                    fatura_tarihi TEXT NOT NULL,
                    tedarikci_id TEXT,
                    tedarikci_unvani TEXT,
                    toplam REAL DEFAULT 0,
                    toplam_kdv REAL DEFAULT 0,
                    net_tutar REAL DEFAULT 0,
                    durum TEXT DEFAULT 'Açık',
                    aciklama TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tedarikci_id) REFERENCES cari_hesap(id)
                )
            """)
            
            # Alım Faturası Satırları Tablosu (Purchase Items)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchase_items (
                    id TEXT PRIMARY KEY,
                    purchase_invoice_id TEXT NOT NULL,
                    malzeme_id TEXT NOT NULL,
                    malzeme_kodu TEXT,
                    malzeme_adi TEXT,
                    miktar REAL DEFAULT 0,
                    birim TEXT,
                    birim_fiyat REAL DEFAULT 0,
                    kdv_orani REAL DEFAULT 0,
                    tutar REAL DEFAULT 0,
                    net_tutar REAL DEFAULT 0,
                    sira_no INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (purchase_invoice_id) REFERENCES purchase_invoices(id) ON DELETE CASCADE,
                    FOREIGN KEY (malzeme_id) REFERENCES malzemeler(id)
                )
            """)
            
            # Index'ler
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchase_invoice_no ON purchase_invoices(fatura_no)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchase_invoice_tedarikci ON purchase_invoices(tedarikci_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchase_items_invoice ON purchase_items(purchase_invoice_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchase_items_malzeme ON purchase_items(malzeme_id)")
            
            # Stok Hareketleri Tablosu (Stock Movements)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_movements (
                    id TEXT PRIMARY KEY,
                    malzeme_id TEXT NOT NULL,
                    hareket_tipi TEXT NOT NULL,  -- 'GIRIS' veya 'CIKIS'
                    miktar REAL NOT NULL,
                    birim_fiyat REAL NOT NULL,
                    toplam_deger REAL NOT NULL,
                    mevcut_stok REAL NOT NULL,  -- Hareket sonrası stok
                    ortalama_maliyet REAL NOT NULL,  -- Hareket sonrası ortalama maliyet
                    referans_tipi TEXT,  -- 'PURCHASE_INVOICE', 'SALES_INVOICE', 'MANUAL' vb.
                    referans_id TEXT,  -- İlgili fatura veya işlem ID'si
                    aciklama TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (malzeme_id) REFERENCES malzemeler(id)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_movements_malzeme ON stock_movements(malzeme_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_movements_tarih ON stock_movements(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_movements_referans ON stock_movements(referans_tipi, referans_id)")
            
            # Tahsilat Tablosu (Payment Records)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tahsilat (
                    id TEXT PRIMARY KEY,
                    cari_id TEXT NOT NULL,
                    cari_unvani TEXT,
                    tarih TEXT NOT NULL,
                    tutar REAL NOT NULL,
                    odeme_turu TEXT NOT NULL,
                    kasa TEXT,
                    aciklama TEXT,
                    vade_tarihi TEXT,
                    belge_no TEXT,
                    banka TEXT,
                    kesideci_borclu TEXT,
                    eski_borc REAL DEFAULT 0,
                    yeni_borc REAL DEFAULT 0,
                    created_by TEXT,
                    created_by_name TEXT,
                    last_modified_by TEXT,
                    last_modified_by_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cari_id) REFERENCES cari_hesap(id)
                )
            """)
            
            # Tahsilat tablosuna düzenleyen sütunları ekle (eğer yoksa)
            try:
                cursor.execute("PRAGMA table_info(tahsilat)")
                columns = [row[1] for row in cursor.fetchall()]
                if 'created_by' not in columns:
                    cursor.execute("ALTER TABLE tahsilat ADD COLUMN created_by TEXT")
                if 'created_by_name' not in columns:
                    cursor.execute("ALTER TABLE tahsilat ADD COLUMN created_by_name TEXT")
                if 'last_modified_by' not in columns:
                    cursor.execute("ALTER TABLE tahsilat ADD COLUMN last_modified_by TEXT")
                if 'last_modified_by_name' not in columns:
                    cursor.execute("ALTER TABLE tahsilat ADD COLUMN last_modified_by_name TEXT")
            except:
                pass
            
            # Ödemeler Tablosu (Expenses/Payments)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS odemeler (
                    id TEXT PRIMARY KEY,
                    kategori TEXT NOT NULL,  -- 'TEDARIKCI', 'MAAS', 'KIRA', 'DIGER'
                    tedarikci_id TEXT,
                    tedarikci_unvani TEXT,
                    alim_faturasi_id TEXT,  -- Eğer alım faturasından geliyorsa
                    tarih TEXT NOT NULL,
                    tutar REAL NOT NULL,
                    odeme_turu TEXT NOT NULL,  -- 'Nakit', 'Havale/EFT', 'Çek', 'Kredi Kartı'
                    kasa TEXT,
                    banka TEXT,
                    aciklama TEXT,
                    belge_no TEXT,
                    vade_tarihi TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tedarikci_id) REFERENCES cari_hesap(id),
                    FOREIGN KEY (alim_faturasi_id) REFERENCES purchase_invoices(id)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_odemeler_kategori ON odemeler(kategori)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_odemeler_tarih ON odemeler(tarih)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_odemeler_tedarikci ON odemeler(tedarikci_id)")
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tahsilat_cari_id ON tahsilat(cari_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tahsilat_tarih ON tahsilat(tarih)")
            
            conn.commit()
            try:
                print("SQLite veritabani semasi basariyla olusturuldu")
            except UnicodeEncodeError:
                print("SQLite database schema created successfully")
        except Exception as e:
            conn.rollback()
            try:
                print(f"Veritabani semasi olusturulurken hata: {e}")
            except UnicodeEncodeError:
                print(f"Database schema creation error: {e}")
            raise
        finally:
            cursor.close()
    
    def close(self):
        """Bağlantıyı kapat"""
        if self._connection:
            self._connection.close()
            self._connection = None


def get_db():
    """Veritabanı instance'ı döndür"""
    return Database()


def get_connection():
    """Veritabanı bağlantısı döndür"""
    db = get_db()
    return db.get_connection()


def dict_factory(cursor, row):
    """Row'u dict'e çevir"""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


# JSON helper functions
import json

def json_loads(data):
    """JSON string'i dict'e çevir"""
    if data is None or data == '':
        return {}
    try:
        return json.loads(data)
    except:
        return {}

def json_dumps(data):
    """Dict'i JSON string'e çevir"""
    if data is None:
        return '{}'
    try:
        return json.dumps(data, ensure_ascii=False)
    except:
        return '{}'

