"""
Fatura Controller - İş mantığı katmanı
Model ve View arasındaki köprü
"""
from PyQt5.QtCore import QThread, pyqtSignal
from models.fatura_model import FaturaModel
from typing import Dict, List, Optional


class FaturaController(QThread):
    """Fatura controller - Controller katmanı"""
    
    # Signal'ler (View'a veri göndermek için)
    data_loaded = pyqtSignal(list)
    operation_success = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, operation: str, data: Optional[Dict] = None, user_id: str = None, user_name: str = None):
        super().__init__()
        self.operation = operation
        self.data = data
        self.user_id = user_id
        self.user_name = user_name
        self.model = FaturaModel()
    
    def run(self):
        """Thread'de çalışacak işlem"""
        try:
            if self.operation == 'get_all':
                result = self.model.get_all()
                self.data_loaded.emit(result)
            elif self.operation == 'get_by_cari_id':
                result = self.model.get_by_cari_id(self.data['cari_id'])
                self.data_loaded.emit(result)
            elif self.operation == 'get_by_id':
                result = self.model.get_by_id(self.data['id'])
                self.operation_success.emit(result if result else {})
            elif self.operation == 'create':
                result = self.model.create(self.data, self.user_id, self.user_name)
                self.operation_success.emit(result)
            elif self.operation == 'update':
                result = self.model.update(self.data['id'], self.data, self.user_id, self.user_name)
                self.operation_success.emit(result if result else {})
        except Exception as e:
            self.error_occurred.emit(str(e))

