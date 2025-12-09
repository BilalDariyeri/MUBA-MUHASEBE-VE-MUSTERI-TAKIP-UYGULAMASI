"""
Müşteri Ödeme Davranışı Analiz Modeli
Makine Öğrenmesi ile müşteri ödeme tahmini ve güven skoru hesaplama

Yazar: ML Engineer
Tarih: 2024
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class PaymentPredictor:
    """
    Müşteri Ödeme Davranışı Tahmin Modeli
    
    Bu sınıf, müşterilerin geçmiş ödeme verilerine bakarak:
    - Gelecekteki ödeme gecikmelerini tahmin eder
    - Her müşteriye bir güven skoru (0-100) verir
    - Risk gruplarını belirler (Düşük/Orta/Yüksek)
    """
    
    def __init__(self, model_path: str = 'model.pkl'):
        """
        PaymentPredictor sınıfını başlat
        
        Args:
            model_path: Eğitilmiş modelin kaydedileceği/yükleneceği dosya yolu
        """
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Model parametreleri
        self.feature_columns = [
            'Ortalama_Gecikme',
            'Odeme_Sayisi',
            'Gecikme_Standart_Sapma',
            'Tutar_Ortalama',
            'Tutar_Standart_Sapma'
        ]
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ham veriden özellik çıkarımı (Feature Engineering)
        
        Bu fonksiyon ham veriyi alır ve ML modeli için gerekli
        türetilmiş özellikleri hesaplar.
        
        Args:
            df: Ham veri DataFrame'i
                Sütunlar: [MusteriID, VadeTarihi, OdemeTarihi, Tutar]
        
        Returns:
            Özelliklerle zenginleştirilmiş DataFrame
        """
        # DataFrame'in bir kopyasını al (orijinal veriyi koru)
        df_features = df.copy()
        
        # Tarih sütunlarını datetime'a çevir
        df_features['VadeTarihi'] = pd.to_datetime(df_features['VadeTarihi'])
        df_features['OdemeTarihi'] = pd.to_datetime(df_features['OdemeTarihi'])
        
        # ============================================================
        # 1. TEMEL ÖZELLİK: Gecikme_Gun
        # ============================================================
        # Ödeme tarihi ile vade tarihi arasındaki fark (gün cinsinden)
        # Negatif değer = erken ödeme, Pozitif değer = geç ödeme
        df_features['Gecikme_Gun'] = (
            df_features['OdemeTarihi'] - df_features['VadeTarihi']
        ).dt.days
        
        # ============================================================
        # 2. MÜŞTERİ BAZLI ÖZELLİKLER
        # ============================================================
        # Her müşteri için istatistiksel özellikler hesapla
        musteri_stats = df_features.groupby('MusteriID').agg({
            'Gecikme_Gun': [
                'mean',      # Ortalama gecikme
                'std',       # Standart sapma (tutarlılık)
                'count'      # Toplam ödeme sayısı
            ],
            'Tutar': [
                'mean',      # Ortalama tutar
                'std'        # Tutar standart sapması
            ]
        }).reset_index()
        
        # Sütun isimlerini düzelt (MultiIndex'ten normal isimlere)
        musteri_stats.columns = [
            'MusteriID',
            'Ortalama_Gecikme',
            'Gecikme_Standart_Sapma',
            'Odeme_Sayisi',
            'Tutar_Ortalama',
            'Tutar_Standart_Sapma'
        ]
        
        # NaN değerleri doldur (sadece 1 ödeme varsa std NaN olabilir)
        musteri_stats['Gecikme_Standart_Sapma'] = musteri_stats['Gecikme_Standart_Sapma'].fillna(0)
        musteri_stats['Tutar_Standart_Sapma'] = musteri_stats['Tutar_Standart_Sapma'].fillna(0)
        
        # ============================================================
        # 3. ÖZELLİKLERİ ANA VERİSETİNE BİRLEŞTİR
        # ============================================================
        # Her satıra müşteri istatistiklerini ekle
        df_features = df_features.merge(musteri_stats, on='MusteriID', how='left')
        
        return df_features
    
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Eğitim verisi hazırlama
        
        Bu fonksiyon, geçmiş verilerden gelecekteki gecikmeyi tahmin etmek
        için eğitim verisi oluşturur.
        
        Strateji: Her müşterinin son ödemesi hariç tüm ödemelerini kullanarak,
        son ödemenin gecikmesini tahmin etmeye çalışırız.
        
        Args:
            df: Özelliklerle zenginleştirilmiş DataFrame
        
        Returns:
            X: Özellik matrisi (features)
            y: Hedef değişken (target) - Gelecek tahmini gecikme
        """
        # Her müşteri için son ödemeyi bul
        df_sorted = df.sort_values(['MusteriID', 'OdemeTarihi'])
        
        # Son ödeme indekslerini bul
        last_payment_idx = df_sorted.groupby('MusteriID')['OdemeTarihi'].idxmax()
        
        # Eğitim verisi: Son ödeme hariç tüm ödemeler
        train_df = df_sorted.drop(index=last_payment_idx)
        
        # Her müşteri için, o ana kadar olan istatistikleri hesapla
        # (Son ödeme bilgisi olmadan)
        training_data = []
        
        for musteri_id in train_df['MusteriID'].unique():
            # Bu müşterinin tüm ödemelerini al
            musteri_payments = train_df[train_df['MusteriID'] == musteri_id].copy()
            
            if len(musteri_payments) < 2:
                # En az 2 ödeme gerekli (1'i tahmin için, diğeri hedef)
                continue
            
            # Son ödemeyi hedef olarak al
            last_payment = musteri_payments.iloc[-1]
            
            # Önceki ödemelerden özellikleri hesapla
            previous_payments = musteri_payments.iloc[:-1]
            
            features = {
                'Ortalama_Gecikme': previous_payments['Gecikme_Gun'].mean(),
                'Odeme_Sayisi': len(previous_payments),
                'Gecikme_Standart_Sapma': previous_payments['Gecikme_Gun'].std() if len(previous_payments) > 1 else 0,
                'Tutar_Ortalama': previous_payments['Tutar'].mean(),
                'Tutar_Standart_Sapma': previous_payments['Tutar'].std() if len(previous_payments) > 1 else 0
            }
            
            # Hedef: Son ödemenin gecikmesi
            target = last_payment['Gecikme_Gun']
            
            training_data.append({**features, 'target': target})
        
        # DataFrame'e çevir
        train_data_df = pd.DataFrame(training_data)
        
        # Özellikler ve hedef değişkeni ayır
        X = train_data_df[self.feature_columns]
        y = train_data_df['target']
        
        return X, y
    
    def train(self, df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
        """
        Modeli eğit
        
        Args:
            df: Ham veri DataFrame'i [MusteriID, VadeTarihi, OdemeTarihi, Tutar]
            test_size: Test seti oranı (0-1 arası)
            random_state: Rastgelelik seed'i (tekrarlanabilirlik için)
        """
        print("🔄 Özellik çıkarımı yapılıyor...")
        df_features = self.prepare_features(df)
        
        print("🔄 Eğitim verisi hazırlanıyor...")
        X, y = self.prepare_training_data(df_features)
        
        if len(X) == 0:
            raise ValueError("Eğitim verisi yetersiz! En az 2 ödeme gereklidir.")
        
        print(f"✅ {len(X)} örnek ile eğitim başlıyor...")
        
        # Veriyi train/test olarak ayır
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Özellikleri ölçeklendir (StandardScaler)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Random Forest Regressor modelini oluştur ve eğit
        print("🌲 Random Forest modeli eğitiliyor...")
        self.model = RandomForestRegressor(
            n_estimators=100,      # Ağaç sayısı
            max_depth=10,          # Maksimum derinlik (overfitting'i önlemek için)
            min_samples_split=5,   # Bölme için minimum örnek sayısı
            min_samples_leaf=2,    # Yaprak için minimum örnek sayısı
            random_state=random_state,
            n_jobs=-1              # Tüm CPU çekirdeklerini kullan
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Model performansını değerlendir
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        print(f"📊 Eğitim Skoru (R²): {train_score:.4f}")
        print(f"📊 Test Skoru (R²): {test_score:.4f}")
        
        # Modeli kaydet
        self.save_model()
        
        self.is_trained = True
        print("✅ Model eğitimi tamamlandı ve kaydedildi!")
    
    def save_model(self):
        """Eğitilmiş modeli diske kaydet"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }
        joblib.dump(model_data, self.model_path)
        print(f"💾 Model kaydedildi: {self.model_path}")
    
    def load_model(self):
        """Kaydedilmiş modeli diskten yükle"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model dosyası bulunamadı: {self.model_path}")
        
        model_data = joblib.load(self.model_path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.is_trained = True
        print(f"✅ Model yüklendi: {self.model_path}")
    
    def calculate_credit_score(self, predicted_delay: float) -> Tuple[int, str]:
        """
        Güven skoru hesapla
        
        Gecikme süresine göre 0-100 arası bir skor verir.
        - Erken ödeme (negatif gecikme) = Yüksek skor
        - Geç ödeme (pozitif gecikme) = Düşük skor
        
        Args:
            predicted_delay: Tahmin edilen gecikme (gün)
        
        Returns:
            (skor, risk_grubu) tuple'ı
        """
        # Skor hesaplama formülü
        # Erken ödeme: +30 gün = 100 puan
        # Zamanında ödeme: 0 gün = 80 puan
        # Geç ödeme: Her gün için -2 puan
        
        if predicted_delay <= -30:
            # Çok erken ödeme
            score = 100
        elif predicted_delay < 0:
            # Erken ödeme (0 ile -30 arası)
            score = 80 + (predicted_delay / 30) * 20
        elif predicted_delay == 0:
            # Tam zamanında
            score = 80
        elif predicted_delay <= 10:
            # 1-10 gün gecikme
            score = 80 - (predicted_delay * 3)
        elif predicted_delay <= 30:
            # 11-30 gün gecikme
            score = 50 - ((predicted_delay - 10) * 1.5)
        else:
            # 30+ gün gecikme
            score = max(0, 20 - ((predicted_delay - 30) * 0.5))
        
        # Skoru 0-100 aralığına sınırla
        score = max(0, min(100, int(score)))
        
        # Risk grubunu belirle
        if score >= 70:
            risk_group = "Düşük Risk"
        elif score >= 40:
            risk_group = "Orta Risk"
        else:
            risk_group = "Yüksek Risk"
        
        return score, risk_group
    
    def predict(self, musteri_id: str, df: pd.DataFrame) -> Dict:
        """
        Bir müşteri için ödeme davranışı tahmini yap
        
        Args:
            musteri_id: Tahmin yapılacak müşteri ID'si
            df: Tüm ödeme verisi DataFrame'i
        
        Returns:
            Tahmin sonuçları dictionary'si:
            {
                'musteri_id': str,
                'tahmini_gecikme': float,
                'guven_skoru': int,
                'risk_grubu': str,
                'ozellikler': dict
            }
        """
        if not self.is_trained:
            # Model yüklü değilse yükle
            try:
                self.load_model()
            except FileNotFoundError:
                raise ValueError("Model eğitilmemiş! Önce train() metodunu çağırın.")
        
        # Müşterinin geçmiş ödemelerini al
        musteri_payments = df[df['MusteriID'] == musteri_id].copy()
        
        if len(musteri_payments) == 0:
            raise ValueError(f"Müşteri bulunamadı: {musteri_id}")
        
        # Özellikleri hazırla
        df_features = self.prepare_features(df)
        musteri_features = df_features[df_features['MusteriID'] == musteri_id]
        
        if len(musteri_features) == 0:
            raise ValueError(f"Müşteri için özellik hesaplanamadı: {musteri_id}")
        
        # Son ödeme hariç özellikleri hesapla (tahmin için)
        if len(musteri_features) > 1:
            # Son ödemeyi hariç tut
            previous_features = musteri_features.iloc[:-1]
        else:
            # Sadece 1 ödeme varsa onu kullan
            previous_features = musteri_features
        
        # Özellik vektörünü oluştur
        feature_vector = pd.DataFrame([{
            'Ortalama_Gecikme': previous_features['Gecikme_Gun'].mean(),
            'Odeme_Sayisi': len(previous_features),
            'Gecikme_Standart_Sapma': previous_features['Gecikme_Gun'].std() if len(previous_features) > 1 else 0,
            'Tutar_Ortalama': previous_features['Tutar'].mean(),
            'Tutar_Standart_Sapma': previous_features['Tutar'].std() if len(previous_features) > 1 else 0
        }])
        
        # Eksik sütunları kontrol et ve doldur
        for col in self.feature_columns:
            if col not in feature_vector.columns:
                feature_vector[col] = 0
        
        # Özellikleri sırala (model beklentisine göre)
        feature_vector = feature_vector[self.feature_columns]
        
        # Ölçeklendir
        feature_vector_scaled = self.scaler.transform(feature_vector)
        
        # Tahmin yap
        predicted_delay = self.model.predict(feature_vector_scaled)[0]
        
        # Güven skoru hesapla
        credit_score, risk_group = self.calculate_credit_score(predicted_delay)
        
        # Sonuçları döndür
        return {
            'musteri_id': musteri_id,
            'tahmini_gecikme': round(predicted_delay, 2),
            'guven_skoru': credit_score,
            'risk_grubu': risk_group,
            'ozellikler': {
                'ortalama_gecikme': round(previous_features['Gecikme_Gun'].mean(), 2),
                'odeme_sayisi': len(previous_features),
                'gecikme_std': round(previous_features['Gecikme_Gun'].std(), 2) if len(previous_features) > 1 else 0,
                'tutar_ortalama': round(previous_features['Tutar'].mean(), 2)
            }
        }


def generate_synthetic_data(n_samples: int = 100, random_state: int = 42) -> pd.DataFrame:
    """
    Sentetik ödeme verisi oluştur (Test için)
    
    Bu fonksiyon, gerçekçi müşteri ödeme davranışlarını simüle eder:
    - Bazı müşteriler erken öder
    - Bazı müşteriler geç öder
    - Bazı müşteriler tutarlı, bazıları tutarsız
    
    Args:
        n_samples: Oluşturulacak örnek sayısı
        random_state: Rastgelelik seed'i
    
    Returns:
        DataFrame: [MusteriID, VadeTarihi, OdemeTarihi, Tutar]
    """
    np.random.seed(random_state)
    
    # Müşteri sayısı (her müşteri için birkaç ödeme olacak)
    n_musteriler = max(10, n_samples // 5)
    musteri_ids = [f"MUSTERI_{i+1:03d}" for i in range(n_musteriler)]
    
    data = []
    base_date = datetime.now() - timedelta(days=365)  # 1 yıl öncesinden başla
    
    for musteri_id in musteri_ids:
        # Her müşteri için 2-8 arası ödeme oluştur
        n_odemeler = np.random.randint(2, 9)
        
        # Müşteri davranış profili belirle
        # 0: Erken ödeyen, 1: Zamanında ödeyen, 2: Geç ödeyen, 3: Tutarsız
        behavior_type = np.random.choice([0, 1, 2, 3], p=[0.3, 0.3, 0.25, 0.15])
        
        for i in range(n_odemeler):
            # Vade tarihi (rastgele, son 1 yıl içinde)
            days_offset = np.random.randint(0, 365)
            vade_tarihi = base_date + timedelta(days=days_offset)
            
            # Ödeme davranışına göre ödeme tarihi belirle
            if behavior_type == 0:
                # Erken ödeyen: -10 ile 0 gün arası
                gecikme = np.random.randint(-10, 1)
            elif behavior_type == 1:
                # Zamanında ödeyen: -2 ile 2 gün arası
                gecikme = np.random.randint(-2, 3)
            elif behavior_type == 2:
                # Geç ödeyen: 5 ile 30 gün arası
                gecikme = np.random.randint(5, 31)
            else:
                # Tutarsız: -15 ile 45 gün arası (geniş aralık)
                gecikme = np.random.randint(-15, 46)
            
            odeme_tarihi = vade_tarihi + timedelta(days=gecikme)
            
            # Tutar (1000 ile 50000 TL arası)
            tutar = np.random.uniform(1000, 50000)
            
            data.append({
                'MusteriID': musteri_id,
                'VadeTarihi': vade_tarihi.strftime('%Y-%m-%d'),
                'OdemeTarihi': odeme_tarihi.strftime('%Y-%m-%d'),
                'Tutar': round(tutar, 2)
            })
    
    df = pd.DataFrame(data)
    
    # Veriyi tarihe göre sırala
    df = df.sort_values('OdemeTarihi').reset_index(drop=True)
    
    return df


if __name__ == "__main__":
    """
    Ana test bloğu - Sentetik veri ile model eğitimi ve tahmin örneği
    """
    print("=" * 60)
    print("MÜŞTERİ ÖDEME DAVRANIŞI ANALİZ MODELİ - TEST")
    print("=" * 60)
    print()
    
    # 1. Sentetik veri oluştur
    print("📊 Sentetik veri oluşturuluyor...")
    df = generate_synthetic_data(n_samples=100, random_state=42)
    print(f"✅ {len(df)} ödeme kaydı oluşturuldu")
    print(f"   Müşteri sayısı: {df['MusteriID'].nunique()}")
    print()
    
    # 2. Modeli oluştur ve eğit
    print("🤖 Model eğitimi başlıyor...")
    predictor = PaymentPredictor(model_path='model.pkl')
    
    try:
        predictor.train(df, test_size=0.2, random_state=42)
        print()
    except Exception as e:
        print(f"❌ Eğitim hatası: {e}")
        exit(1)
    
    # 3. Birkaç müşteri için tahmin yap
    print("🔮 Tahmin örnekleri:")
    print("-" * 60)
    
    sample_musteriler = df['MusteriID'].unique()[:5]
    
    for musteri_id in sample_musteriler:
        try:
            result = predictor.predict(musteri_id, df)
            
            print(f"\n📋 Müşteri: {result['musteri_id']}")
            print(f"   Tahmini Gecikme: {result['tahmini_gecikme']} gün")
            print(f"   Güven Skoru: {result['guven_skoru']}/100")
            print(f"   Risk Grubu: {result['risk_grubu']}")
            print(f"   Özellikler:")
            print(f"     - Ortalama Gecikme: {result['ozellikler']['ortalama_gecikme']} gün")
            print(f"     - Ödeme Sayısı: {result['ozellikler']['odeme_sayisi']}")
            print(f"     - Gecikme Std Sapma: {result['ozellikler']['gecikme_std']}")
            
        except Exception as e:
            print(f"❌ Tahmin hatası ({musteri_id}): {e}")
    
    print()
    print("=" * 60)
    print("✅ Test tamamlandı!")
    print("=" * 60)

