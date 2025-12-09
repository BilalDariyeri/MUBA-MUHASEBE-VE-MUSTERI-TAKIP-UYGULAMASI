"""
Cari Hesap Model - Veri katmanı
SQLite işlemlerini yönetir
"""
from sql_init import get_db, json_loads, json_dumps
from typing import List, Dict, Optional
import hashlib
import uuid


class CariHesapModel:
    """Cari hesap veri modeli - Model katmanı"""
    
    def __init__(self):
        self.db = get_db()
        self.table_name = 'cari_hesap'
    
    def get_all(self) -> List[Dict]:
        """Tüm cari hesapları getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.table_name} ORDER BY created_at DESC")
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    data = dict(row)
                    # JSON alanlarını parse et
                    if data.get('iletisim'):
                        data['iletisim'] = json_loads(data['iletisim'])
                    if data.get('notlar'):
                        data['notlar'] = json_loads(data['notlar'])
                    result.append(data)
                return result
        except Exception as e:
            raise Exception(f"Veri getirme hatası: {str(e)}")
    
    def get_by_id(self, cari_id: str) -> Optional[Dict]:
        """ID'ye göre cari hesap getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (cari_id,))
                row = cursor.fetchone()
                if row:
                    data = dict(row)
                    # JSON alanlarını parse et
                    if data.get('iletisim'):
                        data['iletisim'] = json_loads(data['iletisim'])
                    if data.get('notlar'):
                        data['notlar'] = json_loads(data['notlar'])
                    return data
                return None
        except Exception as e:
            raise Exception(f"Veri getirme hatası: {str(e)}")
    
    def create(self, data: Dict) -> Dict:
        """Yeni cari hesap oluştur"""
        try:
            # Validasyon
            required_fields = ['unvani', 'vergiNo', 'telefon', 'email', 'adres']
            for field in required_fields:
                if not data.get(field):
                    raise ValueError(f"{field} alanı zorunludur")
            
            # Vergi numarası benzersizlik kontrolü
            vergi_no = data.get('vergiNo', '')
            if self._vergi_no_exists(vergi_no):
                raise ValueError("Bu vergi numarası zaten kayıtlı!")
            
            # Vergi numarasını hash'le
            vergi_no_hash = hashlib.sha256(vergi_no.encode()).hexdigest()
            
            # ID oluştur
            cari_id = data.get('id', str(uuid.uuid4()))
            
            # JSON alanlarını string'e çevir
            iletisim = json_dumps(data.get('iletisim', {}))
            notlar = json_dumps(data.get('notlar', {}))
            
            # Veriyi hazırla
            insert_data = {
                'id': cari_id,
                'unvani': data.get('unvani', ''),
                'vergiNo': vergi_no,
                'vergiNoHash': vergi_no_hash,
                'telefon': data.get('telefon', ''),
                'email': data.get('email', ''),
                'adres': data.get('adres', ''),
                'sehir': data.get('sehir', ''),
                'ad': data.get('ad', ''),
                'borc': float(data.get('borc', 0) or 0),
                'alacak': float(data.get('alacak', 0) or 0),
                'statusu': data.get('statusu', 'Kullanımda'),
                'iletisim': iletisim,
                'notlar': notlar
            }
            
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {self.table_name} 
                    (id, unvani, vergiNo, vergiNoHash, telefon, email, adres, sehir, ad, 
                     borc, alacak, statusu, iletisim, notlar)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    insert_data['id'],
                    insert_data['unvani'],
                    insert_data['vergiNo'],
                    insert_data['vergiNoHash'],
                    insert_data['telefon'],
                    insert_data['email'],
                    insert_data['adres'],
                    insert_data['sehir'],
                    insert_data['ad'],
                    insert_data['borc'],
                    insert_data['alacak'],
                    insert_data['statusu'],
                    insert_data['iletisim'],
                    insert_data['notlar']
                ))
            
            # JSON alanlarını geri parse et
            result = insert_data.copy()
            result['iletisim'] = json_loads(iletisim)
            result['notlar'] = json_loads(notlar)
            return result
        except Exception as e:
            raise Exception(f"Oluşturma hatası: {str(e)}")
    
    def _vergi_no_exists(self, vergi_no: str) -> bool:
        """Vergi numarasının daha önce kayıtlı olup olmadığını kontrol et"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) as count FROM {self.table_name} WHERE vergiNo = ?", (vergi_no,))
                row = cursor.fetchone()
                return row['count'] > 0 if row else False
        except Exception as e:
            # Hata durumunda güvenli tarafta kal (kayıt yapılmasın)
            return True
    
    def update(self, cari_id: str, data: Dict) -> Dict:
        """Cari hesabı güncelle"""
        try:
            # Eğer vergi numarası değiştiriliyorsa kontrol et
            if 'vergiNo' in data:
                vergi_no = data.get('vergiNo', '')
                # Mevcut kaydı al
                current = self.get_by_id(cari_id)
                if current and current.get('vergiNo') != vergi_no:
                    # Vergi numarası değişmiş, benzersizlik kontrolü yap
                    if self._vergi_no_exists(vergi_no):
                        raise ValueError("Bu vergi numarası zaten kayıtlı!")
                    # Yeni vergi numarasını hash'le
                    vergi_no_hash = hashlib.sha256(vergi_no.encode()).hexdigest()
                    data['vergiNoHash'] = vergi_no_hash
            
            # Güncellenecek alanları hazırla
            update_fields = []
            update_values = []
            
            if 'unvani' in data:
                update_fields.append('unvani = ?')
                update_values.append(data['unvani'])
            if 'vergiNo' in data:
                update_fields.append('vergiNo = ?')
                update_values.append(data['vergiNo'])
            if 'vergiNoHash' in data:
                update_fields.append('vergiNoHash = ?')
                update_values.append(data['vergiNoHash'])
            if 'telefon' in data:
                update_fields.append('telefon = ?')
                update_values.append(data['telefon'])
            if 'email' in data:
                update_fields.append('email = ?')
                update_values.append(data['email'])
            if 'adres' in data:
                update_fields.append('adres = ?')
                update_values.append(data['adres'])
            if 'sehir' in data:
                update_fields.append('sehir = ?')
                update_values.append(data['sehir'])
            if 'ad' in data:
                update_fields.append('ad = ?')
                update_values.append(data['ad'])
            if 'borc' in data:
                update_fields.append('borc = ?')
                update_values.append(float(data['borc'] or 0))
            if 'alacak' in data:
                update_fields.append('alacak = ?')
                update_values.append(float(data['alacak'] or 0))
            if 'statusu' in data:
                update_fields.append('statusu = ?')
                update_values.append(data['statusu'])
            if 'iletisim' in data:
                update_fields.append('iletisim = ?')
                update_values.append(json_dumps(data['iletisim']))
            if 'notlar' in data:
                update_fields.append('notlar = ?')
                update_values.append(json_dumps(data['notlar']))
            
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            update_values.append(cari_id)
            
            if not update_fields:
                return self.get_by_id(cari_id)
            
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    UPDATE {self.table_name} 
                    SET {', '.join(update_fields)}
                    WHERE id = ?
                """, update_values)
            
            return self.get_by_id(cari_id)
        except Exception as e:
            raise Exception(f"Güncelleme hatası: {str(e)}")
    
    def delete(self, cari_id: str) -> bool:
        """Cari hesabı sil"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (cari_id,))
                return cursor.rowcount > 0
        except Exception as e:
            raise Exception(f"Silme hatası: {str(e)}")
    
    def search(self, query: str) -> List[Dict]:
        """Cari hesap ara - Şirket adı, vergi numarası ve ad'a göre"""
        try:
            if not query or not query.strip():
                return self.get_all()
            
            query_lower = f"%{query.lower().strip()}%"
            
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    SELECT * FROM {self.table_name}
                    WHERE LOWER(unvani) LIKE ? 
                       OR LOWER(vergiNo) LIKE ? 
                       OR LOWER(vergiNoHash) LIKE ?
                       OR LOWER(ad) LIKE ?
                    ORDER BY created_at DESC
                """, (query_lower, query_lower, query_lower, query_lower))
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    data = dict(row)
                    # JSON alanlarını parse et
                    if data.get('iletisim'):
                        data['iletisim'] = json_loads(data['iletisim'])
                    if data.get('notlar'):
                        data['notlar'] = json_loads(data['notlar'])
                    result.append(data)
                return result
        except Exception as e:
            raise Exception(f"Arama hatası: {str(e)}")
    
    def add_borc(self, cari_id: str, tutar: float) -> Dict:
        """Cari hesabın borcuna tutar ekle"""
        try:
            # Mevcut cari hesabı al
            cari = self.get_by_id(cari_id)
            if not cari:
                raise ValueError(f"Cari hesap bulunamadı: {cari_id}")
            
            # Mevcut borç değerini al
            mevcut_borc = float(cari.get('borc', 0) or 0)
            
            # Yeni borç = mevcut borç + eklenen tutar
            yeni_borc = mevcut_borc + float(tutar)
            
            # SQLite'da sadece borç alanını güncelle
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    UPDATE {self.table_name} 
                    SET borc = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (yeni_borc, cari_id))
            
            # Güncellenmiş veriyi döndür
            return self.get_by_id(cari_id)
        except Exception as e:
            raise Exception(f"Borç ekleme hatası: {str(e)}")
    
    def get_ekstre(self, filters: Dict) -> List[Dict]:
        """Cari hesap ekstresi getir - Filtrelere göre"""
        try:
            # Lazy import to avoid circular dependency
            from models.fatura_model import FaturaModel
            
            cari_ids = filters.get('cari_ids', [])
            baslangic_tarih = filters.get('baslangic_tarih', '')
            bitis_tarih = filters.get('bitis_tarih', '')
            hareket_turleri = filters.get('hareket_turleri', [])
            fatura_detay = filters.get('fatura_detay', True)
            bordro_detay = filters.get('bordro_detay', True)
            siparis_detay = filters.get('siparis_detay', True)
            
            fatura_model = FaturaModel()
            ekstre_hareketleri = []
            
            # Cari hesap ID'leri için döngü
            if not cari_ids:
                # Tüm cari hesaplar
                all_cari = self.get_all()
                cari_ids = [c['id'] for c in all_cari]
            
            for cari_id in cari_ids:
                # Cari hesap bilgilerini al
                cari = self.get_by_id(cari_id)
                if not cari:
                    continue
                
                # Faturaları getir
                faturalar = fatura_model.get_by_cari_id(cari_id)
                
                for fatura in faturalar:
                    fatura_tarih = fatura.get('tarih', '')
                    
                    # Tarih filtresi
                    if baslangic_tarih and fatura_tarih and fatura_tarih < baslangic_tarih:
                        continue
                    if bitis_tarih and fatura_tarih and fatura_tarih > bitis_tarih:
                        continue
                    
                    # Hareket türü filtresi (fatura tipine göre)
                    # Eğer hareket_turleri boş değilse ve fatura tipi listede yoksa atla
                    if hareket_turleri:
                        # Hareket türleri string listesi olabilir, kontrol et
                        fatura_tipi = str(fatura.get('faturaTipi', ''))
                        if fatura_tipi and fatura_tipi not in [str(ht) for ht in hareket_turleri]:
                            continue
                    
                    # Ekstre hareketi oluştur
                    hareket = {
                        'cari_id': cari_id,
                        'cari_unvani': cari.get('unvani', ''),
                        'tarih': fatura_tarih,
                        'belge_no': fatura.get('faturaNo', ''),
                        'belge_tipi': 'Fatura',
                        'hareket_turu': fatura.get('faturaTipi', ''),
                        'aciklama': f"Fatura: {fatura.get('faturaNo', '')}",
                        'borc': float(fatura.get('netTutar', 0) or 0),
                        'alacak': 0.0,
                        'bakiye': 0.0,  # Hesaplanacak
                        'detay': fatura if fatura_detay else None
                    }
                    ekstre_hareketleri.append(hareket)
                
                # Tahsilatları getir ve ekstreye ekle (ALACAK olarak)
                try:
                    from models.tahsilat_model import TahsilatModel
                    tahsilat_model = TahsilatModel()
                    tahsilatlar = tahsilat_model.get_by_cari_id(cari_id)
                    
                    for tahsilat in tahsilatlar:
                        tahsilat_tarih = tahsilat.get('tarih', '')
                        
                        # Tarih filtresi
                        if baslangic_tarih and tahsilat_tarih and tahsilat_tarih < baslangic_tarih:
                            continue
                        if bitis_tarih and tahsilat_tarih and tahsilat_tarih > bitis_tarih:
                            continue
                        
                        # Ekstre hareketi oluştur (ALACAK)
                        odeme_turu = tahsilat.get('odeme_turu', 'Nakit')
                        belge_no = tahsilat.get('belge_no', '') or f"Tahsilat-{tahsilat.get('id', '')[:8]}"
                        
                        hareket = {
                            'cari_id': cari_id,
                            'cari_unvani': cari.get('unvani', ''),
                            'tarih': tahsilat_tarih,
                            'belge_no': belge_no,
                            'belge_tipi': 'Tahsilat',
                            'hareket_turu': odeme_turu,
                            'aciklama': f"Tahsilat ({odeme_turu})",
                            'borc': 0.0,
                            'alacak': float(tahsilat.get('tutar', 0) or 0),  # ALACAK
                            'bakiye': 0.0,  # Hesaplanacak
                            'detay': tahsilat if fatura_detay else None,
                            'vade_tarihi': tahsilat.get('vade_tarihi', '') if odeme_turu in ['Çek', 'Senet'] else ''
                        }
                        ekstre_hareketleri.append(hareket)
                except Exception as e:
                    print(f"Tahsilat ekstreye eklenirken hata: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Bakiyeyi hesapla (kronolojik sıraya göre)
            # Tarih yoksa en sona koy
            ekstre_hareketleri.sort(key=lambda x: x['tarih'] if x['tarih'] else '9999-99-99')
            
            # Özet bilgileri hesapla
            toplam_borc = sum(h.get('borc', 0) for h in ekstre_hareketleri)
            toplam_alacak = sum(h.get('alacak', 0) for h in ekstre_hareketleri)
            
            bakiye = 0.0
            for hareket in ekstre_hareketleri:
                bakiye = bakiye + hareket['borc'] - hareket['alacak']
                hareket['bakiye'] = bakiye
                
                # Vade tarihi ekle - Ödeme planına göre
                if not hareket.get('vade_tarihi'):
                    try:
                        if hareket.get('tarih'):
                            from datetime import datetime, timedelta
                            fatura_tarih = datetime.strptime(hareket['tarih'], '%Y-%m-%d')
                            
                            # Önce fatura detayından ödeme planını al
                            detay = hareket.get('detay')
                            odeme_plani = None
                            
                            if detay and isinstance(detay, dict):
                                # Fatura verisinden ödeme planını al
                                odeme_plani = detay.get('odemePlani')
                                
                                # Eğer yoksa cariHesap JSON'undan al
                                if not odeme_plani:
                                    cari_hesap = detay.get('cariHesap', {})
                                    if isinstance(cari_hesap, dict):
                                        odeme_plani = cari_hesap.get('odemePlani')
                            
                            # Eğer hala yoksa cari hesaptan al
                            if not odeme_plani:
                                cari_id = hareket.get('cari_id')
                                if cari_id:
                                    cari = self.get_by_id(cari_id)
                                    if cari:
                                        odeme_plani = cari.get('odemePlani', '')
                            
                            # Ödeme planına göre gün sayısını belirle
                            odeme_gun_sayisi = 30  # Varsayılan 30 gün
                            
                            if odeme_plani:
                                if odeme_plani == 'Peşin':
                                    odeme_gun_sayisi = 0  # Peşin = aynı gün
                                elif '30' in str(odeme_plani) or odeme_plani == '30 Gün':
                                    odeme_gun_sayisi = 30
                                elif '60' in str(odeme_plani) or odeme_plani == '60 Gün':
                                    odeme_gun_sayisi = 60
                                elif '120' in str(odeme_plani) or odeme_plani == '120 Gün':
                                    odeme_gun_sayisi = 120
                            
                            # Vade tarihini hesapla
                            vade_tarih = fatura_tarih + timedelta(days=odeme_gun_sayisi)
                            hareket['vade_tarihi'] = vade_tarih.strftime('%Y-%m-%d')
                        else:
                            hareket['vade_tarihi'] = ''
                    except Exception as e:
                        print(f"Vade tarihi hesaplama hatası: {e}")
                        import traceback
                        traceback.print_exc()
                        hareket['vade_tarihi'] = ''
            
            son_bakiye = bakiye
            
            # Özet bilgileri döndür
            return {
                'hareketler': ekstre_hareketleri,
                'ozet': {
                    'toplam_borc': toplam_borc,
                    'toplam_alacak': toplam_alacak,
                    'son_bakiye': son_bakiye
                }
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(f"Ekstre getirme hatası: {str(e)}")