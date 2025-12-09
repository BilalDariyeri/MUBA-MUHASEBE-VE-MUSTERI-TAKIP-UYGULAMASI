"""
Alım Faturası Model - Veri katmanı
SQLite işlemlerini yönetir
"""
from sql_init import get_db, json_loads, json_dumps
from typing import List, Dict, Optional
import uuid
from datetime import datetime


class PurchaseInvoiceModel:
    """Alım faturası veri modeli - Model katmanı"""
    
    def __init__(self):
        self.db = get_db()
        self.table_name = 'purchase_invoices'
        self.items_table_name = 'purchase_items'
    
    def get_all(self) -> List[Dict]:
        """Tüm alım faturalarını getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    SELECT * FROM {self.table_name} 
                    ORDER BY fatura_tarihi DESC, created_at DESC
                """)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            raise Exception(f"Veri getirme hatası: {str(e)}")
    
    def get_by_id(self, invoice_id: str) -> Optional[Dict]:
        """ID'ye göre alım faturası getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (invoice_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                
                invoice = dict(row)
                # Satırları da getir
                invoice['items'] = self.get_items_by_invoice_id(invoice_id)
                return invoice
        except Exception as e:
            raise Exception(f"Veri getirme hatası: {str(e)}")
    
    def get_items_by_invoice_id(self, invoice_id: str) -> List[Dict]:
        """Faturaya ait satırları getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    SELECT * FROM {self.items_table_name} 
                    WHERE purchase_invoice_id = ?
                    ORDER BY sira_no
                """, (invoice_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            raise Exception(f"Satır getirme hatası: {str(e)}")
    
    def _generate_fatura_no(self) -> str:
        """Otomatik alım faturası numarası oluştur (AL2025000000001 formatında)"""
        try:
            # En son alım fatura numarasını bul
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT fatura_no FROM {self.table_name} ORDER BY created_at DESC LIMIT 100")
                rows = cursor.fetchall()
                
                max_num = 0
                for row in rows:
                    fatura_no = row['fatura_no']
                    # AL2025000000001 formatından sayıyı çıkar
                    if fatura_no and fatura_no.startswith('AL') and len(fatura_no) > 7:
                        try:
                            # AL + yıl + numara formatından numarayı çıkar
                            num_part_str = fatura_no[7:]  # AL2025'ten sonrasını al
                            num_part = int(num_part_str)
                            if num_part > max_num:
                                max_num = num_part
                        except:
                            pass
                
                # Yeni numara oluştur
                year = datetime.now().year
                new_num = max_num + 1
                return f"AL{year}{new_num:07d}"
        except:
            # Hata durumunda basit numara
            year = datetime.now().year
            return f"AL{year}0000001"
    
    def create(self, data: Dict) -> Dict:
        """
        Yeni alım faturası oluştur
        
        Args:
            data: {
                'fatura_no': str (otomatik oluşturulur),
                'fatura_tarihi': str,
                'tedarikci_unvani': str (manuel giriş),
                'items': List[Dict],  # Satırlar
                'aciklama': str (optional)
            }
        
        Returns:
            Oluşturulan fatura dict'i
        """
        try:
            # Fatura numarası otomatik oluştur (eğer verilmemişse)
            if not data.get('fatura_no'):
                data['fatura_no'] = self._generate_fatura_no()
            
            # Validasyon
            if not data.get('fatura_tarihi'):
                raise ValueError("Fatura tarihi zorunludur")
            if not data.get('items') or len(data['items']) == 0:
                raise ValueError("En az bir satır eklenmelidir")
            
            invoice_id = str(uuid.uuid4())
            
            # Toplamları hesapla
            net_tutar = sum(item.get('net_tutar', 0) for item in data['items'])
            toplam_kdv = sum(item.get('tutar', 0) - item.get('net_tutar', 0) for item in data['items'])
            toplam = net_tutar + toplam_kdv
            
            # Fatura başlığını kaydet
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {self.table_name} 
                    (id, fatura_no, fatura_tarihi, tedarikci_id, tedarikci_unvani, 
                     toplam, toplam_kdv, net_tutar, aciklama, vade_tarihi)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    invoice_id,
                    data['fatura_no'],
                    data['fatura_tarihi'],
                    data.get('tedarikci_id'),  # Tedarikçi ID varsa kaydet
                    data.get('tedarikci_unvani', ''),
                    toplam,
                    toplam_kdv,
                    net_tutar,
                    data.get('aciklama', ''),
                    data.get('vade_tarihi', '')
                ))
                
                # Satırları kaydet
                for idx, item in enumerate(data['items']):
                    item_id = str(uuid.uuid4())
                    cursor.execute(f"""
                        INSERT INTO {self.items_table_name}
                        (id, purchase_invoice_id, malzeme_id, malzeme_kodu, malzeme_adi,
                         miktar, birim, birim_fiyat, kdv_orani, tutar, net_tutar, sira_no)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item_id,
                        invoice_id,
                        item['malzeme_id'],
                        item.get('malzeme_kodu', ''),
                        item.get('malzeme_adi', ''),
                        item['miktar'],
                        item.get('birim', ''),
                        item['birim_fiyat'],
                        item.get('kdv_orani', 0),
                        item['tutar'],
                        item['net_tutar'],
                        idx + 1
                    ))
            
            return self.get_by_id(invoice_id)
        except Exception as e:
            raise Exception(f"Oluşturma hatası: {str(e)}")
    
    def delete(self, invoice_id: str) -> bool:
        """Alım faturasını sil (CASCADE ile satırlar da silinir)"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (invoice_id,))
                return cursor.rowcount > 0
        except Exception as e:
            raise Exception(f"Silme hatası: {str(e)}")

