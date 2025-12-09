"""
Cari Hesap Controller - İş mantığı katmanı
Model ve View arasındaki köprü
"""
from PyQt5.QtCore import QThread, pyqtSignal
from models.cari_hesap_model import CariHesapModel
from typing import Dict, List, Optional


class CariHesapController(QThread):
    """Cari hesap controller - Controller katmanı"""
    
    # Signal'ler (View'a veri göndermek için)
    data_loaded = pyqtSignal(list)
    operation_success = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, operation: str, data: Optional[Dict] = None):
        super().__init__()
        self.operation = operation
        self.data = data
        self.model = CariHesapModel()
    
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
                result = self.model.create(self.data)
                self.operation_success.emit(result)
            elif self.operation == 'update':
                cari_id = self.data.pop('id')
                result = self.model.update(cari_id, self.data)
                self.operation_success.emit(result)
            elif self.operation == 'delete':
                self.model.delete(self.data['id'])
                self.operation_success.emit({'id': self.data['id']})
            elif self.operation == 'search':
                result = self.model.search(self.data['query'])
                self.data_loaded.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))

