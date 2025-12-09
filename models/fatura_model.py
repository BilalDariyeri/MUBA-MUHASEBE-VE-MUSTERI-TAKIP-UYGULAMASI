"""
Fatura Model - Veri katmanı
SQLite işlemlerini yönetir
"""
from sql_init import get_db, json_loads, json_dumps
from typing import List, Dict, Optional
import uuid
from datetime import datetime


class FaturaModel:
    """Fatura veri modeli - Model katmanı"""
    
    def __init__(self):
        self.db = get_db()
        self.table_name = 'faturalar'
    
    def get_all(self) -> List[Dict]:
        """Tüm faturaları getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.table_name} ORDER BY created_at DESC")
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    data = dict(row)
                    # JSON alanlarını parse et
                    if data.get('cariHesap'):
                        data['cariHesap'] = json_loads(data['cariHesap'])
                    if data.get('satirlar'):
                        data['satirlar'] = json_loads(data['satirlar'])
                    result.append(data)
                return result
        except Exception as e:
            raise Exception(f"Fatura getirme hatası: {str(e)}")
    
    def get_by_cari_id(self, cari_id: str) -> List[Dict]:
        """Cari hesap ID'sine göre faturaları getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.table_name} WHERE cariId = ? ORDER BY created_at DESC", (cari_id,))
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    data = dict(row)
                    # JSON alanlarını parse et
                    if data.get('cariHesap'):
                        data['cariHesap'] = json_loads(data['cariHesap'])
                    if data.get('satirlar'):
                        data['satirlar'] = json_loads(data['satirlar'])
                    result.append(data)
                return result
        except Exception as e:
            raise Exception(f"Fatura getirme hatası: {str(e)}")
    
    def create(self, data: Dict, user_id: str = None, user_name: str = None) -> Dict:
        """Yeni fatura oluştur"""
        try:
            # Fatura numarası otomatik oluştur
            if not data.get('faturaNo'):
                data['faturaNo'] = self._generate_fatura_no()
            
            # ID oluştur
            fatura_id = data.get('id', str(uuid.uuid4()))
            
            # JSON alanlarını string'e çevir
            cari_hesap = json_dumps(data.get('cariHesap', {}))
            satirlar = json_dumps(data.get('satirlar', []))
            
            # Kullanıcı bilgisi
            created_by = user_id or data.get('created_by', '')
            created_by_name = user_name or data.get('created_by_name', '')
            
            # Veriyi hazırla
            insert_data = {
                'id': fatura_id,
                'faturaNo': data.get('faturaNo', ''),
                'tarih': data.get('tarih', ''),
                'faturaTipi': data.get('faturaTipi', ''),
                'cariId': data.get('cariId', ''),
                'toplam': float(data.get('toplam', 0) or 0),
                'toplamKDV': float(data.get('toplamKDV', 0) or 0),
                'netTutar': float(data.get('netTutar', 0) or 0),
                'durum': data.get('durum', 'Açık'),
                'cariHesap': cari_hesap,
                'satirlar': satirlar,
                'created_by': created_by,
                'created_by_name': created_by_name,
                'last_modified_by': created_by,
                'last_modified_by_name': created_by_name
            }
            
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {self.table_name} 
                    (id, faturaNo, tarih, faturaTipi, cariId, toplam, toplamKDV, netTutar, durum, cariHesap, satirlar,
                     created_by, created_by_name, last_modified_by, last_modified_by_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    insert_data['id'],
                    insert_data['faturaNo'],
                    insert_data['tarih'],
                    insert_data['faturaTipi'],
                    insert_data['cariId'],
                    insert_data['toplam'],
                    insert_data['toplamKDV'],
                    insert_data['netTutar'],
                    insert_data['durum'],
                    insert_data['cariHesap'],
                    insert_data['satirlar'],
                    insert_data['created_by'],
                    insert_data['created_by_name'],
                    insert_data['last_modified_by'],
                    insert_data['last_modified_by_name']
                ))
            
            # Fatura kesildiğinde cari hesabın borcunu güncelle
            cari_id = data.get('cariId')
            net_tutar = data.get('netTutar', 0)
            
            if cari_id and net_tutar:
                try:
                    from models.cari_hesap_model import CariHesapModel
                    cari_model = CariHesapModel()
                    cari_model.add_borc(cari_id, float(net_tutar))
                except Exception as e:
                    pass
            
            # Fatura kesildiğinde stoktan düş - ÖNCE STOK KONTROLÜ YAP
            satirlar = data.get('satirlar', [])
            if satirlar:
                try:
                    from models.malzeme_model import MalzemeModel
                    malzeme_model = MalzemeModel()
                    
                    # Önce tüm stokları kontrol et
                    stok_hatalari = []
                    for satir in satirlar:
                        # Boş satırları atla
                        if not satir or not isinstance(satir, dict):
                            continue
                        
                        # Hem eski hem yeni formatı destekle
                        stok_kodu = satir.get('malzemeKodu', '') or satir.get('stokKodu', '')
                        miktar = float(satir.get('miktar', 0) or 0)
                        
                        # Miktar 0 veya negatifse kontrol etme
                        if not stok_kodu or miktar <= 0:
                            continue
                        
                        try:
                            # Kod boşlukları temizle ve büyük harfe çevir
                            stok_kodu_clean = str(stok_kodu).strip().upper()
                            
                            malzeme = malzeme_model.get_by_kod(stok_kodu_clean)
                            if not malzeme:
                                # Kod bulunamadı, alternatif aramalar dene
                                # Önce tam kod ile ara
                                malzeme = malzeme_model.get_by_kod(stok_kodu_clean)
                                
                                # Hala bulunamadıysa, kodun başlangıcı ile ara (benzersizlik kontrolü sırasında eklenen sayılar olabilir)
                                if not malzeme and len(stok_kodu_clean) > 3:
                                    # Kodun ilk kısmını al (sayıları çıkar)
                                    import re
                                    base_kod = re.sub(r'\d+$', '', stok_kodu_clean)  # Sondaki sayıları çıkar
                                    if base_kod:
                                        # Base kod ile başlayan malzemeleri ara
                                        all_malzemeler = malzeme_model.get_all()
                                        for m in all_malzemeler:
                                            m_kod = str(m.get('kod', '')).strip().upper()
                                            if m_kod.startswith(base_kod):
                                                malzeme = m
                                                break
                                
                                if not malzeme:
                                    stok_hatalari.append(f"Malzeme bulunamadı: {stok_kodu_clean}")
                                    continue
                            
                            mevcut_stok = float(malzeme.get('stok', 0) or 0)
                            birim = malzeme.get('birim', '')
                            
                            # Float karşılaştırması için küçük tolerans ekle (ondalık hatalar için)
                            # Eğer stok negatifse (borç stok) izin ver
                            if mevcut_stok >= 0 and mevcut_stok < miktar - 0.01:
                                malzeme_ad = malzeme.get('ad', stok_kodu_clean)
                                stok_hatalari.append(f"{malzeme_ad}: Mevcut stok ({mevcut_stok:.2f} {birim}) yetersiz, istenen: {miktar:.2f} {birim}")
                        except Exception as e:
                            import traceback
                            traceback.print_exc()
                            stok_hatalari.append(f"{stok_kodu}: {str(e)}")
                    
                    # Eğer stok hatası varsa fatura oluşturma
                    if stok_hatalari:
                        hata_mesaji = "Stok yetersiz!\n\n" + "\n".join(stok_hatalari)
                        raise ValueError(hata_mesaji)
                    
                    # Stoklar yeterliyse düş
                    for satir in satirlar:
                        # Hem eski hem yeni formatı destekle
                        stok_kodu = satir.get('malzemeKodu', '') or satir.get('stokKodu', '')
                        miktar = float(satir.get('miktar', 0) or 0)
                        
                        if stok_kodu and miktar > 0:
                            try:
                                # Stok çıkışı yap ve stok hareketi kaydı oluştur
                                malzeme_model.reduce_stok(
                                    stok_kodu, 
                                    miktar,
                                    referans_tipi='SALES_INVOICE',
                                    referans_id=insert_data['id']
                                )
                            except Exception as e:
                                raise Exception(f"Stok düşürme hatası ({stok_kodu}): {str(e)}")
                except ValueError as e:
                    # Stok hatası - fatura oluşturulmasın
                    raise e
                except Exception as e:
                    # Diğer hatalar
                    raise Exception(f"Stok işlemi hatası: {str(e)}")
            
            # JSON alanlarını geri parse et
            result = insert_data.copy()
            result['cariHesap'] = json_loads(cari_hesap)
            result['satirlar'] = json_loads(satirlar)
            return result
        except Exception as e:
            raise Exception(f"Fatura oluşturma hatası: {str(e)}")
    
    def update(self, fatura_id: str, data: Dict, user_id: str = None, user_name: str = None) -> Dict:
        """Faturayı güncelle"""
        try:
            # Kullanıcı bilgisi
            last_modified_by = user_id or data.get('last_modified_by', '')
            last_modified_by_name = user_name or data.get('last_modified_by_name', '')
            
            # JSON alanlarını string'e çevir
            cari_hesap = json_dumps(data.get('cariHesap', {})) if 'cariHesap' in data else None
            satirlar = json_dumps(data.get('satirlar', [])) if 'satirlar' in data else None
            
            with self.db.get_cursor() as cursor:
                # Dinamik güncelleme sorgusu oluştur
                update_fields = ['last_modified_by = ?', 'last_modified_by_name = ?', 'updated_at = CURRENT_TIMESTAMP']
                update_values = [last_modified_by, last_modified_by_name]
                
                if 'tarih' in data:
                    update_fields.append('tarih = ?')
                    update_values.append(data['tarih'])
                if 'faturaTipi' in data:
                    update_fields.append('faturaTipi = ?')
                    update_values.append(data['faturaTipi'])
                if 'toplam' in data:
                    update_fields.append('toplam = ?')
                    update_values.append(float(data.get('toplam', 0) or 0))
                if 'toplamKDV' in data:
                    update_fields.append('toplamKDV = ?')
                    update_values.append(float(data.get('toplamKDV', 0) or 0))
                if 'netTutar' in data:
                    update_fields.append('netTutar = ?')
                    update_values.append(float(data.get('netTutar', 0) or 0))
                if 'durum' in data:
                    update_fields.append('durum = ?')
                    update_values.append(data['durum'])
                if cari_hesap:
                    update_fields.append('cariHesap = ?')
                    update_values.append(cari_hesap)
                if satirlar:
                    update_fields.append('satirlar = ?')
                    update_values.append(satirlar)
                
                update_values.append(fatura_id)
                
                cursor.execute(f"""
                    UPDATE {self.table_name}
                    SET {', '.join(update_fields)}
                    WHERE id = ?
                """, update_values)
            
            # Güncellenmiş faturayı döndür
            return self.get_by_id(fatura_id)
        except Exception as e:
            raise Exception(f"Fatura güncelleme hatası: {str(e)}")
    
    def get_by_id(self, fatura_id: str) -> Optional[Dict]:
        """ID'ye göre fatura getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (fatura_id,))
                row = cursor.fetchone()
                if row:
                    data = dict(row)
                    if data.get('cariHesap'):
                        data['cariHesap'] = json_loads(data['cariHesap'])
                    if data.get('satirlar'):
                        data['satirlar'] = json_loads(data['satirlar'])
                    return data
                return None
        except Exception as e:
            raise Exception(f"Fatura getirme hatası: {str(e)}")
    
    def _generate_fatura_no(self) -> str:
        """Otomatik fatura numarası oluştur"""
        try:
            # En son fatura numarasını bul
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT faturaNo FROM {self.table_name} ORDER BY created_at DESC LIMIT 100")
                rows = cursor.fetchall()
                
                max_num = 0
                for row in rows:
                    fatura_no = row['faturaNo']
                    # AAA2025000000003 formatından sayıyı çıkar
                    if fatura_no and len(fatura_no) > 7:
                        try:
                            num_part = int(fatura_no[-7:])  # Son 7 haneyi al
                            if num_part > max_num:
                                max_num = num_part
                        except:
                            pass
                
                # Yeni numara oluştur
                year = datetime.now().year
                new_num = max_num + 1
                return f"AAA{year}{new_num:07d}"
        except:
            # Hata durumunda basit numara
            year = datetime.now().year
            return f"AAA{year}0000001"
