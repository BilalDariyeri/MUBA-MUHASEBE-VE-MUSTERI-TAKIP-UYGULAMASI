"""
Cari Hesap Ekstre Controller - İş mantığı katmanı
Model ve View arasındaki köprü
"""
from PyQt5.QtCore import QThread, pyqtSignal
from models.cari_hesap_model import CariHesapModel
from typing import Dict, List


class CariHesapEkstreController(QThread):
    """Cari hesap ekstre controller - Controller katmanı"""
    
    # Signal'ler (View'a veri göndermek için)
    ekstre_loaded = pyqtSignal(dict)  # Artık dict döndürüyor
    error_occurred = pyqtSignal(str)
    
    def __init__(self, filters: Dict):
        super().__init__()
        self.filters = filters
        self.model = CariHesapModel()
    
    def run(self):
        """Thread'de çalışacak işlem"""
        try:
            result = self.model.get_ekstre(self.filters)
            self.ekstre_loaded.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))


class CariHesapEkstreListController:
    """Cari hesap ekstre listesi controller - MVC Controller"""
    
    def __init__(self, view, main_window):
        self.view = view
        self.main_window = main_window
        self.setup_callbacks()
        self.load_ekstre()
    
    def setup_callbacks(self):
        """View callback'lerini ayarla"""
        self.view.set_callbacks(
            on_tamam=self.on_tamam,
            on_kapat=self.on_kapat
        )
    
    def load_ekstre(self):
        """Ekstre verilerini yükle"""
        filters = self.view.get_filters()
        self.controller = CariHesapEkstreController(filters)
        self.controller.ekstre_loaded.connect(self.on_ekstre_loaded)
        self.controller.error_occurred.connect(self.on_error)
        self.controller.start()
    
    def on_ekstre_loaded(self, result):
        """Ekstre yüklendiğinde"""
        hareketler = result.get('hareketler', [])
        ozet = result.get('ozet', {})
        self.view.display_ekstre(hareketler, ozet)
    
    def on_error(self, error_msg):
        """Hata oluştuğunda"""
        self.view.show_error(f"Ekstre yüklenirken hata oluştu:\n{error_msg}")
    
    def on_tamam(self):
        """Tamam butonuna tıklandığında - Ekstre'yi yeniden yükle"""
        self.load_ekstre()
    
    def on_kapat(self):
        """Kapat butonuna tıklandığında"""
        self.main_window.show_dashboard()

