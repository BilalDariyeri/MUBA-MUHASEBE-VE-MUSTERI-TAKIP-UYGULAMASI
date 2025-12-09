"""
Ödeme Model - Veri katmanı
SQLite işlemlerini yönetir
"""
from sql_init import get_db
from typing import List, Dict, Optional
import uuid


class OdemeModel:
    """Ödeme veri modeli - Model katmanı"""
    
    # Kategoriler
    KATEGORI_TEDARIKCI = 'TEDARIKCI'
    KATEGORI_MAAS = 'MAAS'
    KATEGORI_KIRA = 'KIRA'
    KATEGORI_DIGER = 'DIGER'
    
    def __init__(self):
        self.db = get_db()
        self.table_name = 'odemeler'
    
    def get_all(self, kategori: Optional[str] = None) -> List[Dict]:
        """Tüm ödemeleri getir (opsiyonel kategori filtresi)"""
        try:
            with self.db.get_cursor() as cursor:
                if kategori:
                    cursor.execute(f"""
                        SELECT o.*, 
                               COALESCE(o.tedarikci_unvani, c.unvani, '') as tedarikci_unvani,
                               pi.fatura_no as alim_faturasi_no
                        FROM {self.table_name} o
                        LEFT JOIN cari_hesap c ON o.tedarikci_id = c.id
                        LEFT JOIN purchase_invoices pi ON o.alim_faturasi_id = pi.id
                        WHERE o.kategori = ?
                        ORDER BY o.tarih DESC, o.created_at DESC
                    """, (kategori,))
                else:
                    cursor.execute(f"""
                        SELECT o.*, 
                               COALESCE(o.tedarikci_unvani, c.unvani, '') as tedarikci_unvani,
                               pi.fatura_no as alim_faturasi_no
                        FROM {self.table_name} o
                        LEFT JOIN cari_hesap c ON o.tedarikci_id = c.id
                        LEFT JOIN purchase_invoices pi ON o.alim_faturasi_id = pi.id
                        ORDER BY o.tarih DESC, o.created_at DESC
                    """)
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    data = dict(row)
                    # Eğer tedarikci_unvani hala boşsa ve tedarikci_id varsa, cari hesaptan çek
                    if not data.get('tedarikci_unvani') and data.get('tedarikci_id'):
                        try:
                            from models.cari_hesap_model import CariHesapModel
                            cari_model = CariHesapModel()
                            cari = cari_model.get_by_id(data['tedarikci_id'])
                            if cari:
                                data['tedarikci_unvani'] = cari.get('unvani', '')
                        except:
                            pass
                    result.append(data)
                return result
        except Exception as e:
            raise Exception(f"Ödeme getirme hatası: {str(e)}")
    
    def get_by_id(self, odeme_id: str) -> Optional[Dict]:
        """ID'ye göre ödeme getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    SELECT o.*, 
                           COALESCE(o.tedarikci_unvani, c.unvani, '') as tedarikci_unvani,
                           pi.fatura_no as alim_faturasi_no
                    FROM {self.table_name} o
                    LEFT JOIN cari_hesap c ON o.tedarikci_id = c.id
                    LEFT JOIN purchase_invoices pi ON o.alim_faturasi_id = pi.id
                    WHERE o.id = ?
                """, (odeme_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            raise Exception(f"Ödeme getirme hatası: {str(e)}")
    
    def get_by_kategori(self, kategori: str) -> List[Dict]:
        """Kategoriye göre ödemeleri getir"""
        return self.get_all(kategori=kategori)
    
    def get_by_alim_faturasi_id(self, alim_faturasi_id: str) -> List[Dict]:
        """Alım faturası ID'sine göre ödemeleri getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    SELECT o.*, 
                           COALESCE(o.tedarikci_unvani, c.unvani, '') as tedarikci_unvani,
                           pi.fatura_no as alim_faturasi_no
                    FROM {self.table_name} o
                    LEFT JOIN cari_hesap c ON o.tedarikci_id = c.id
                    LEFT JOIN purchase_invoices pi ON o.alim_faturasi_id = pi.id
                    WHERE o.alim_faturasi_id = ?
                    ORDER BY o.tarih DESC
                """, (alim_faturasi_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            raise Exception(f"Ödeme getirme hatası: {str(e)}")
    
    def create(self, data: Dict) -> Dict:
        """Yeni ödeme oluştur"""
        try:
            odeme_id = data.get('id', str(uuid.uuid4()))
            
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {self.table_name} 
                    (id, kategori, tedarikci_id, tedarikci_unvani, alim_faturasi_id,
                     tarih, tutar, odeme_turu, kasa, banka, aciklama, belge_no, vade_tarihi)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    odeme_id,
                    data.get('kategori', self.KATEGORI_DIGER),
                    data.get('tedarikci_id'),
                    data.get('tedarikci_unvani', ''),
                    data.get('alim_faturasi_id'),
                    data.get('tarih'),
                    float(data.get('tutar', 0)),
                    data.get('odeme_turu', 'Nakit'),
                    data.get('kasa', ''),
                    data.get('banka', ''),
                    data.get('aciklama', ''),
                    data.get('belge_no', ''),
                    data.get('vade_tarihi', '')
                ))
            
            return self.get_by_id(odeme_id)
        except Exception as e:
            raise Exception(f"Ödeme oluşturma hatası: {str(e)}")
    
    def update(self, odeme_id: str, data: Dict) -> Dict:
        """Ödemeyi güncelle"""
        try:
            with self.db.get_cursor() as cursor:
                update_fields = []
                update_values = []
                
                if 'kategori' in data:
                    update_fields.append('kategori = ?')
                    update_values.append(data['kategori'])
                if 'tedarikci_id' in data:
                    update_fields.append('tedarikci_id = ?')
                    update_values.append(data['tedarikci_id'])
                if 'tedarikci_unvani' in data:
                    update_fields.append('tedarikci_unvani = ?')
                    update_values.append(data['tedarikci_unvani'])
                if 'alim_faturasi_id' in data:
                    update_fields.append('alim_faturasi_id = ?')
                    update_values.append(data['alim_faturasi_id'])
                if 'tarih' in data:
                    update_fields.append('tarih = ?')
                    update_values.append(data['tarih'])
                if 'tutar' in data:
                    update_fields.append('tutar = ?')
                    update_values.append(float(data['tutar']))
                if 'odeme_turu' in data:
                    update_fields.append('odeme_turu = ?')
                    update_values.append(data['odeme_turu'])
                if 'kasa' in data:
                    update_fields.append('kasa = ?')
                    update_values.append(data['kasa'])
                if 'banka' in data:
                    update_fields.append('banka = ?')
                    update_values.append(data['banka'])
                if 'aciklama' in data:
                    update_fields.append('aciklama = ?')
                    update_values.append(data['aciklama'])
                if 'belge_no' in data:
                    update_fields.append('belge_no = ?')
                    update_values.append(data['belge_no'])
                if 'vade_tarihi' in data:
                    update_fields.append('vade_tarihi = ?')
                    update_values.append(data['vade_tarihi'])
                
                update_fields.append('updated_at = CURRENT_TIMESTAMP')
                update_values.append(odeme_id)
                
                cursor.execute(f"""
                    UPDATE {self.table_name}
                    SET {', '.join(update_fields)}
                    WHERE id = ?
                """, update_values)
            
            return self.get_by_id(odeme_id)
        except Exception as e:
            raise Exception(f"Ödeme güncelleme hatası: {str(e)}")
    
    def delete(self, odeme_id: str) -> bool:
        """Ödeme sil"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (odeme_id,))
                return cursor.rowcount > 0
        except Exception as e:
            raise Exception(f"Ödeme silme hatası: {str(e)}")

