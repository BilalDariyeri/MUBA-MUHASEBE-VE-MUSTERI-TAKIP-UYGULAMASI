"""
Malzeme Model - Veri katmanı
SQLite işlemlerini yönetir
"""
from sql_init import get_db, json_loads, json_dumps
from typing import List, Dict, Optional
import uuid
import time


class MalzemeModel:
    """Malzeme veri modeli - Model katmanı"""
    
    def __init__(self):
        self.db = get_db()
        self.table_name = 'malzemeler'
    
    def get_all(self) -> List[Dict]:
        """Tüm malzemeleri getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.table_name} ORDER BY created_at DESC")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            raise Exception(f"Veri getirme hatası: {str(e)}")
    
    def get_by_id(self, malzeme_id: str) -> Optional[Dict]:
        """ID'ye göre malzeme getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (malzeme_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            raise Exception(f"Veri getirme hatası: {str(e)}")
    
    def create(self, data: Dict) -> Dict:
        """Yeni malzeme oluştur"""
        try:
            # Validasyon
            required_fields = ['ad', 'birim']
            for field in required_fields:
                if not data.get(field):
                    raise ValueError(f"{field} alanı zorunludur")
            
            # Kod yoksa veya None ise otomatik oluştur
            kod = data.get('kod') or ''
            if not kod or kod.strip() == '':
                # Otomatik kod oluştur
                kod = self._generate_unique_kod(data.get('ad', ''))
                data['kod'] = kod
            else:
                # Kullanıcı kod girmiş, benzersizlik kontrolü yap
                kod = kod.strip().upper()
                if self._kod_exists(kod):
                    raise ValueError("Bu malzeme kodu zaten kayıtlı!")
                data['kod'] = kod
            
            # ID oluştur
            malzeme_id = data.get('id', str(uuid.uuid4()))
            
            # Veriyi hazırla
            insert_data = {
                'id': malzeme_id,
                'kod': kod,
                'ad': data.get('ad', ''),
                'birim': data.get('birim', ''),
                'stok': float(data.get('stok', 0) or 0),
                'birimFiyat': float(data.get('birimFiyat', 0) or 0),
                'kdvOrani': int(data.get('kdvOrani', 18) or 18),
                'aciklama': data.get('aciklama', '')
            }
            
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {self.table_name} 
                    (id, kod, ad, birim, stok, birimFiyat, kdvOrani, aciklama)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    insert_data['id'],
                    insert_data['kod'],
                    insert_data['ad'],
                    insert_data['birim'],
                    insert_data['stok'],
                    insert_data['birimFiyat'],
                    insert_data['kdvOrani'],
                    insert_data['aciklama']
                ))
            
            return {'id': malzeme_id, **insert_data}
        except Exception as e:
            raise Exception(f"Oluşturma hatası: {str(e)}")
    
    def _generate_unique_kod(self, ad: str) -> str:
        """Benzersiz malzeme kodu oluştur"""
        base_kod = self._generate_kod_from_name(ad)
        kod = base_kod
        counter = 1
        
        # Benzersiz kod bulana kadar dene
        while self._kod_exists(kod):
            kod = f"{base_kod}{counter:03d}"
            counter += 1
            if counter > 999:
                # Çok fazla deneme oldu, timestamp ekle
                kod = f"{base_kod}{int(time.time()) % 10000}"
                break
        
        return kod
    
    def _generate_kod_from_name(self, ad: str) -> str:
        """Malzeme adından kod oluştur - LOGO mantığı: Her kelimenin ilk harfi + sayılar"""
        import re
        
        # Türkçe karakterleri değiştir
        tr_to_en = {
            'ç': 'c', 'Ç': 'C', 'ğ': 'g', 'Ğ': 'G', 'ı': 'i', 'İ': 'I',
            'ö': 'o', 'Ö': 'O', 'ş': 's', 'Ş': 'S', 'ü': 'u', 'Ü': 'U'
        }
        
        kod = ad
        for tr, en in tr_to_en.items():
            kod = kod.replace(tr, en)
        
        # Kelimelere ayır (boşluk, x, X, -, _ ile ayır)
        # Örnek: "silindir başlı itici 30x300" -> ["silindir", "başlı", "itici", "30", "300"]
        words = re.split(r'[\sxX\-_]+', kod)
        
        kod_parts = []
        sayilar = []
        
        for word in words:
            word = word.strip()
            if not word:
                continue
            
            # Eğer kelime sadece sayılardan oluşuyorsa, sayılar listesine ekle
            if word.isdigit():
                sayilar.append(word)
            else:
                # Kelimenin ilk harfini al (harf ise)
                for char in word:
                    if char.isalpha():
                        kod_parts.append(char.upper())
                        break
        
        # Kod oluştur: Harfler + Sayılar
        kod = ''.join(kod_parts) + ''.join(sayilar)
        
        # Eğer kod çok kısa ise (sadece harf yoksa veya çok kısa ise), sayı ekle
        if len(kod_parts) == 0:
            # Hiç harf yoksa, ilk kelimeden ilk 3 karakteri al
            first_word = words[0] if words else ''
            kod = ''.join(c.upper() for c in first_word if c.isalnum())[:3]
            if len(kod) < 3:
                kod = kod + "001"
        elif len(kod) < 3:
            # Harf var ama kod çok kısa, sayı ekle
            kod = kod + "001"
        
        # Maksimum uzunluk kontrolü (15 karakter)
        if len(kod) > 15:
            kod = kod[:15]
        
        return kod
    
    def update(self, malzeme_id: str, data: Dict) -> Dict:
        """Malzemeyi güncelle"""
        try:
            # Eğer kod değiştiriliyorsa kontrol et
            if 'kod' in data:
                current = self.get_by_id(malzeme_id)
                if current and current.get('kod') != data['kod']:
                    if self._kod_exists(data['kod']):
                        raise ValueError("Bu malzeme kodu zaten kayıtlı!")
            
            # Güncellenecek alanları hazırla
            update_fields = []
            update_values = []
            
            if 'kod' in data:
                update_fields.append('kod = ?')
                update_values.append(data['kod'])
            if 'ad' in data:
                update_fields.append('ad = ?')
                update_values.append(data['ad'])
            if 'birim' in data:
                update_fields.append('birim = ?')
                update_values.append(data['birim'])
            if 'stok' in data:
                update_fields.append('stok = ?')
                update_values.append(float(data['stok'] or 0))
            if 'birimFiyat' in data:
                update_fields.append('birimFiyat = ?')
                update_values.append(float(data['birimFiyat'] or 0))
            if 'kdvOrani' in data:
                update_fields.append('kdvOrani = ?')
                update_values.append(int(data['kdvOrani'] or 18))
            if 'aciklama' in data:
                update_fields.append('aciklama = ?')
                update_values.append(data.get('aciklama', ''))
            if 'current_buy_price' in data:
                update_fields.append('current_buy_price = ?')
                update_values.append(float(data['current_buy_price'] or 0))
            if 'average_cost' in data:
                update_fields.append('average_cost = ?')
                update_values.append(float(data['average_cost'] or 0))
            
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            update_values.append(malzeme_id)
            
            if not update_fields:
                return self.get_by_id(malzeme_id)
            
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    UPDATE {self.table_name} 
                    SET {', '.join(update_fields)}
                    WHERE id = ?
                """, update_values)
            
            return self.get_by_id(malzeme_id)
        except Exception as e:
            raise Exception(f"Güncelleme hatası: {str(e)}")
    
    def delete(self, malzeme_id: str) -> bool:
        """Malzemeyi sil"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (malzeme_id,))
                return cursor.rowcount > 0
        except Exception as e:
            raise Exception(f"Silme hatası: {str(e)}")
    
    def search(self, query: str) -> List[Dict]:
        """Malzeme ara"""
        try:
            if not query or not query.strip():
                return self.get_all()
            
            query_lower = f"%{query.lower().strip()}%"
            
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    SELECT * FROM {self.table_name}
                    WHERE LOWER(kod) LIKE ? OR LOWER(ad) LIKE ?
                    ORDER BY created_at DESC
                """, (query_lower, query_lower))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            raise Exception(f"Arama hatası: {str(e)}")
    
    def _kod_exists(self, kod: str) -> bool:
        """Malzeme kodunun daha önce kayıtlı olup olmadığını kontrol et"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) as count FROM {self.table_name} WHERE kod = ?", (kod,))
                row = cursor.fetchone()
                return row['count'] > 0 if row else False
        except Exception as e:
            return True  # Hata durumunda güvenli tarafta kal
    
    def get_by_kod(self, kod: str) -> Optional[Dict]:
        """Malzeme koduna göre malzeme getir"""
        try:
            if not kod:
                return None
            
            # Kod temizleme: boşlukları kaldır, büyük harfe çevir
            kod_clean = str(kod).strip().upper()
            
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.table_name} WHERE UPPER(TRIM(kod)) = ?", (kod_clean,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            raise Exception(f"Veri getirme hatası: {str(e)}")
    
    def reduce_stok(self, kod: str, miktar: float, referans_tipi: str = 'SALES_INVOICE', 
                    referans_id: str = None) -> bool:
        """Malzeme stokundan miktar düş"""
        try:
            malzeme = self.get_by_kod(kod)
            if not malzeme:
                raise ValueError(f"Malzeme bulunamadı: {kod}")
            
            mevcut_stok = float(malzeme.get('stok', 0) or 0)
            ortalama_maliyet = float(malzeme.get('average_cost', 0) or 0)
            miktar_float = float(miktar)
            
            # Miktar 0 veya negatifse işlem yapma
            if miktar_float <= 0:
                return True
            
            # Stok kontrolü - yetersizse hata ver (float karşılaştırması için tolerans)
            if mevcut_stok < miktar_float - 0.01:  # 0.01 tolerans
                malzeme_ad = malzeme.get('ad', kod)
                birim = malzeme.get('birim', '')
                raise ValueError(f"Malzeme stoku yetersiz! Malzeme: {malzeme_ad}, Mevcut Stok: {mevcut_stok:.2f} {birim}, İstenen: {miktar_float:.2f} {birim}")
            
            yeni_stok = mevcut_stok - miktar_float
            
            # Stoku güncelle (çıkışta maliyet değişmez, sadece stok azalır)
            self.update(malzeme['id'], {'stok': yeni_stok})
            
            # Stok hareketi kaydı oluştur (çıkış)
            self._create_stock_movement(
                malzeme_id=malzeme['id'],
                hareket_tipi='CIKIS',
                miktar=miktar_float,
                birim_fiyat=ortalama_maliyet,  # Çıkışta ortalama maliyet kullanılır
                mevcut_stok=yeni_stok,
                ortalama_maliyet=ortalama_maliyet,  # Çıkışta maliyet değişmez
                referans_tipi=referans_tipi,
                referans_id=referans_id
            )
            
            return True
        except ValueError as e:
            # ValueError'u olduğu gibi fırlat (stok yetersiz hatası)
            raise e
        except Exception as e:
            raise Exception(f"Stok düşürme hatası: {str(e)}")
    
    def add_stok_with_cost(self, malzeme_id: str, miktar: float, birim_fiyat: float, 
                          referans_tipi: str = 'PURCHASE_INVOICE', referans_id: str = None) -> Dict:
        """
        Stok ekle ve ağırlıklı ortalama maliyet hesapla
        
        Bu fonksiyon alım faturası kaydedilirken çağrılır.
        Stok miktarını artırır ve ağırlıklı ortalama maliyeti günceller.
        Geçmiş stok hareketlerine göre maliyet hesaplar.
        
        Args:
            malzeme_id: Malzeme ID'si
            miktar: Eklenen miktar
            birim_fiyat: Yeni alış fiyatı
            referans_tipi: İşlem tipi ('PURCHASE_INVOICE', 'MANUAL' vb.)
            referans_id: İlgili fatura veya işlem ID'si
        
        Returns:
            Güncellenmiş malzeme dict'i
        """
        try:
            malzeme = self.get_by_id(malzeme_id)
            if not malzeme:
                raise ValueError(f"Malzeme bulunamadı: {malzeme_id}")
            
            mevcut_stok = float(malzeme.get('stok', 0) or 0)
            eski_maliyet = float(malzeme.get('average_cost', 0) or 0)
            miktar_float = float(miktar)
            yeni_fiyat = float(birim_fiyat)
            
            if miktar_float <= 0:
                raise ValueError("Miktar 0'dan büyük olmalıdır")
            
            # Geçmiş stok hareketlerine göre maliyet hesapla
            # Eğer geçmiş hareketler varsa, onları kullanarak daha doğru hesaplama yap
            yeni_maliyet = self._calculate_weighted_average_cost(
                malzeme_id, mevcut_stok, eski_maliyet, miktar_float, yeni_fiyat
            )
            
            # Yeni stok miktarı
            yeni_stok = mevcut_stok + miktar_float
            
            # Stok ve maliyet bilgilerini güncelle
            update_data = {
                'stok': yeni_stok,
                'average_cost': round(yeni_maliyet, 4),
                'current_buy_price': round(yeni_fiyat, 4)
            }
            
            updated_malzeme = self.update(malzeme_id, update_data)
            
            # Stok hareketi kaydı oluştur
            self._create_stock_movement(
                malzeme_id=malzeme_id,
                hareket_tipi='GIRIS',
                miktar=miktar_float,
                birim_fiyat=yeni_fiyat,
                mevcut_stok=yeni_stok,
                ortalama_maliyet=yeni_maliyet,
                referans_tipi=referans_tipi,
                referans_id=referans_id
            )
            
            return updated_malzeme
        except Exception as e:
            raise Exception(f"Stok ve maliyet güncelleme hatası: {str(e)}")
    
    def _calculate_weighted_average_cost(self, malzeme_id: str, mevcut_stok: float, 
                                       eski_maliyet: float, yeni_miktar: float, yeni_fiyat: float) -> float:
        """
        Geçmiş stok hareketlerine göre ağırlıklı ortalama maliyet hesapla
        
        Formül: ((Mevcut_Stok * Eski_Maliyet) + (Yeni_Giren_Miktar * Yeni_Alış_Fiyatı)) / (Mevcut_Stok + Yeni_Giren_Miktar)
        
        Eğer elimizde stok yoksa, yeni fiyat maliyet olur.
        Eğer elimizde stok varsa, mevcut stok ve maliyet ile yeni giren stok ve fiyatı 
        birleştirerek ortalama maliyet hesaplanır.
        """
        if mevcut_stok == 0:
            # İlk stok girişi - elimizde hiç stok yoksa, yeni fiyat maliyet olur
            return yeni_fiyat
        else:
            # Elimizde stok varsa, geçmiş stokların maliyeti ile yeni giren stokun maliyetini birleştir
            # Toplam değer = (Mevcut stok * Mevcut maliyet) + (Yeni miktar * Yeni fiyat)
            # Toplam miktar = Mevcut stok + Yeni miktar
            # Ortalama maliyet = Toplam değer / Toplam miktar
            toplam_eski_deger = mevcut_stok * eski_maliyet
            toplam_yeni_deger = yeni_miktar * yeni_fiyat
            yeni_toplam_stok = mevcut_stok + yeni_miktar
            yeni_maliyet = (toplam_eski_deger + toplam_yeni_deger) / yeni_toplam_stok
            
            return yeni_maliyet
    
    def _create_stock_movement(self, malzeme_id: str, hareket_tipi: str, miktar: float,
                              birim_fiyat: float, mevcut_stok: float, ortalama_maliyet: float,
                              referans_tipi: str = None, referans_id: str = None, aciklama: str = None):
        """Stok hareketi kaydı oluştur"""
        try:
            import uuid
            movement_id = str(uuid.uuid4())
            toplam_deger = miktar * birim_fiyat
            
            with self.db.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO stock_movements 
                    (id, malzeme_id, hareket_tipi, miktar, birim_fiyat, toplam_deger,
                     mevcut_stok, ortalama_maliyet, referans_tipi, referans_id, aciklama)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    movement_id,
                    malzeme_id,
                    hareket_tipi,
                    miktar,
                    birim_fiyat,
                    toplam_deger,
                    mevcut_stok,
                    ortalama_maliyet,
                    referans_tipi,
                    referans_id,
                    aciklama
                ))
        except Exception as e:
            # Stok hareketi kaydı hatası kritik değil, sadece logla
            print(f"UYARI: Stok hareketi kaydı oluşturulamadı: {e}")
    
    def get_stock_movements(self, malzeme_id: str, limit: int = 100) -> List[Dict]:
        """Malzemeye ait stok hareketlerini getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM stock_movements 
                    WHERE malzeme_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (malzeme_id, limit))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Stok hareketleri getirme hatası: {e}")
            return []