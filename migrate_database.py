"""
Database Migration Script
Mevcut veritabanını yeni şemaya günceller
"""
import sqlite3
import os
from sql_init import get_db


def migrate_database():
    """Veritabanı migration işlemi"""
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Users tablosunu kontrol et ve gerekirse güncelle
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Eksik kolonları ekle
        if 'username' not in columns:
            print("username kolonu ekleniyor...")
            cursor.execute("ALTER TABLE users ADD COLUMN username TEXT UNIQUE")
        
        if 'password_hash' not in columns:
            print("password_hash kolonu ekleniyor...")
            cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
            cursor.execute("UPDATE users SET password_hash = '' WHERE password_hash IS NULL")
        
        if 'is_active' not in columns:
            print("is_active kolonu ekleniyor...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
            cursor.execute("UPDATE users SET is_active = 1 WHERE is_active IS NULL")
        
        if 'last_login' not in columns:
            print("last_login kolonu ekleniyor...")
            cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
        
        conn.commit()
        print("Migration tamamlandı!")
        
    except Exception as e:
        print(f"Migration hatası: {e}")
        conn.rollback()


if __name__ == "__main__":
    migrate_database()

