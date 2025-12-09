"""
Malzeme Controller - İş mantığı katmanı
Model ve View arasındaki köprü
"""
from PyQt5.QtCore import QThread, pyqtSignal
from models.malzeme_model import MalzemeModel
from typing import Dict, List, Optional


class MalzemeController(QThread):
    """Malzeme controller - Controller katmanı"""
    
    # Signal'ler (View'a veri göndermek için)
    data_loaded = pyqtSignal(list)
    operation_success = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, operation: str, data: Optional[Dict] = None):
        super().__init__()
        self.operation = operation
        self.data = data
        self.model = MalzemeModel()
    
    def run(self):
        """Thread'de çalışacak işlem"""
        try:
            if self.operation == 'get_all':
                result = self.model.get_all()
                self.data_loaded.emit(result)
            elif self.operation == 'get_by_id':
                result = self.model.get_by_id(self.data['id'])
                self.data_loaded.emit([result] if result else [])
            elif self.operation == 'create':
                # Kod unique kontrolü (kod None veya boş olabilir, otomatik oluşturulacak)
                kod = self.data.get('kod')
                if kod:
                    # Kod varsa ve None değilse kontrol et
                    kod = str(kod).strip().upper()
                    if kod and self.model._kod_exists(kod):
                        raise ValueError(f"Bu malzeme kodu zaten kayıtlı: {kod}")
                # Kod None veya boşsa model otomatik oluşturur
                result = self.model.create(self.data)
                self.operation_success.emit(result)
            elif self.operation == 'update':
                malzeme_id = self.data.pop('id')
                result = self.model.update(malzeme_id, self.data)
                self.operation_success.emit(result)
            elif self.operation == 'delete':
                self.model.delete(self.data['id'])
                self.operation_success.emit({'id': self.data['id']})
            elif self.operation == 'search':
                result = self.model.search(self.data['query'])
                self.data_loaded.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))

