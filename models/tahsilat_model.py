"""
Tahsilat Model - Veri katmanı
SQLite işlemlerini yönetir
"""
from sql_init import get_db
from typing import List, Dict, Optional
import uuid


class TahsilatModel:
    """Tahsilat veri modeli - Model katmanı"""
    
    def __init__(self):
        self.db = get_db()
        self.table_name = 'tahsilat'
    
    def get_all(self) -> List[Dict]:
        """Tüm tahsilatları getir"""
        try:
            with self.db.get_cursor() as cursor:
                # Cari hesap bilgisini JOIN ile çek
                cursor.execute(f"""
                    SELECT t.*, 
                           COALESCE(t.cari_unvani, c.unvani, '') as cari_unvani
                    FROM {self.table_name} t
                    LEFT JOIN cari_hesap c ON t.cari_id = c.id
                    ORDER BY t.tarih DESC, t.created_at DESC
                """)
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    data = dict(row)
                    # Eğer cari_unvani hala boşsa ve cari_id varsa, cari hesaptan çek
                    if not data.get('cari_unvani') and data.get('cari_id'):
                        try:
                            from models.cari_hesap_model import CariHesapModel
                            cari_model = CariHesapModel()
                            cari = cari_model.get_by_id(data['cari_id'])
                            if cari:
                                data['cari_unvani'] = cari.get('unvani', '')
                        except:
                            pass
                    result.append(data)
                return result
        except Exception as e:
            raise Exception(f"Tahsilat getirme hatası: {str(e)}")
    
    def get_by_id(self, tahsilat_id: str) -> Optional[Dict]:
        """ID'ye göre tahsilat getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (tahsilat_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            raise Exception(f"Tahsilat getirme hatası: {str(e)}")
    
    def get_by_cari_id(self, cari_id: str) -> List[Dict]:
        """Cari hesap ID'sine göre tahsilatları getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.table_name} WHERE cari_id = ? ORDER BY tarih DESC", (cari_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            raise Exception(f"Tahsilat getirme hatası: {str(e)}")
    
    def create(self, data: Dict, user_id: str = None, user_name: str = None) -> Dict:
        """Yeni tahsilat oluştur"""
        try:
            tahsilat_id = data.get('id', str(uuid.uuid4()))
            
            # Kullanıcı bilgisi
            created_by = user_id or data.get('created_by', '')
            created_by_name = user_name or data.get('created_by_name', '')
            
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {self.table_name} 
                    (id, cari_id, cari_unvani, tarih, tutar, odeme_turu, kasa, aciklama, 
                     vade_tarihi, belge_no, banka, kesideci_borclu, eski_borc, yeni_borc,
                     created_by, created_by_name, last_modified_by, last_modified_by_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tahsilat_id,
                    data.get('cari_id'),
                    data.get('cari_unvani', ''),
                    data.get('tarih'),
                    float(data.get('tutar', 0)),
                    data.get('odeme_turu', 'Nakit'),
                    data.get('kasa', ''),
                    data.get('aciklama', ''),
                    data.get('vade_tarihi', ''),
                    data.get('belge_no', ''),
                    data.get('banka', ''),
                    data.get('kesideci_borclu', ''),
                    float(data.get('eski_borc', 0)),
                    float(data.get('yeni_borc', 0)),
                    created_by,
                    created_by_name,
                    created_by,
                    created_by_name
                ))
            
            return self.get_by_id(tahsilat_id)
        except Exception as e:
            raise Exception(f"Tahsilat oluşturma hatası: {str(e)}")
    
    def delete(self, tahsilat_id: str) -> bool:
        """Tahsilat sil"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (tahsilat_id,))
                return True
        except Exception as e:
            raise Exception(f"Tahsilat silme hatası: {str(e)}")

