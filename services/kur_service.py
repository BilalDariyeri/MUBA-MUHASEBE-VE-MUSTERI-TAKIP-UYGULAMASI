"""
Kur Servisi - Döviz kurlarını çeker
"""
import requests
import json
from typing import Dict, Optional


class KurService:
    """Döviz kuru servisi"""
    
    def __init__(self):
        # USD ve EUR bazlı API kullan (daha kolay)
        self.usd_url = "https://api.exchangerate-api.com/v4/latest/USD"
        self.eur_url = "https://api.exchangerate-api.com/v4/latest/EUR"
        self.cache = {}
        self.cache_time = None
        import time
        self.cache_duration = 3600  # 1 saat cache
    
    def get_kurlar(self) -> Dict[str, float]:
        """Güncel döviz kurlarını getir (TRY bazlı)"""
        import time
        
        # Cache kontrolü
        if self.cache_time and (time.time() - self.cache_time) < self.cache_duration:
            return self.cache
        
        try:
            # ExchangeRate API kullan (ücretsiz)
            # USD bazlı API'den TRY kurunu al
            usd_response = requests.get(self.usd_url, timeout=5)
            if usd_response.status_code == 200:
                usd_data = usd_response.json()
                usd_rates = usd_data.get('rates', {})
                usd_to_try = usd_rates.get('TRY', 30.0)  # 1 USD = ? TRY
            else:
                usd_to_try = 30.0
            
            # EUR bazlı API'den TRY kurunu al
            eur_response = requests.get(self.eur_url, timeout=5)
            if eur_response.status_code == 200:
                eur_data = eur_response.json()
                eur_rates = eur_data.get('rates', {})
                eur_to_try = eur_rates.get('TRY', 32.0)  # 1 EUR = ? TRY
            else:
                eur_to_try = 32.0
            
            self.cache = {
                'USD': usd_to_try,
                'EUR': eur_to_try
            }
            self.cache_time = time.time()
            return self.cache
        except Exception as e:
            print(f"Kur servisi hatası: {e}")
            # Hata durumunda varsayılan kurlar
            return self._get_default_kurlar()
    
    def _get_default_kurlar(self) -> Dict[str, float]:
        """Varsayılan kurlar (API çalışmazsa)"""
        return {
            'USD': 30.0,  # 1 USD = 30 TL
            'EUR': 32.0   # 1 EUR = 32 TL
        }
    
    def try_to_usd(self, try_amount: float) -> float:
        """TL'yi USD'ye çevir"""
        kurlar = self.get_kurlar()
        return try_amount / kurlar['USD']
    
    def try_to_eur(self, try_amount: float) -> float:
        """TL'yi EUR'ye çevir"""
        kurlar = self.get_kurlar()
        return try_amount / kurlar['EUR']

