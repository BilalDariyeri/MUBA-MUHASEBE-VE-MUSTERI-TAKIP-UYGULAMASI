"""
Malzeme List Controller - İş mantığı katmanı
"""
from PyQt5.QtWidgets import QDialog, QMenu
from controllers.malzeme_controller import MalzemeController
from views.malzeme_form_view import MalzemeFormView


class MalzemeListController:
    """Malzeme listesi controller - MVC Controller"""
    
    def __init__(self, view, main_window):
        self.view = view
        self.main_window = main_window
        self.setup_callbacks()
        self.load_data()
    
    def setup_callbacks(self):
        """View callback'lerini ayarla"""
        self.view.set_callbacks(
            on_geri=self.on_geri,
            on_yeni=self.on_yeni,
            on_context_menu=self.on_context_menu,
            on_double_click=self.on_double_click,
            on_search=self.on_search
        )
        self.all_malzeme_data = []
    
    def load_data(self):
        """Veriyi yükle"""
        self.controller = MalzemeController('get_all')
        self.controller.data_loaded.connect(self.on_data_loaded)
        self.controller.error_occurred.connect(self.on_error)
        self.controller.start()
    
    def on_data_loaded(self, data):
        """Veri yüklendiğinde"""
        self.all_malzeme_data = data
        self.view.display_data(data)
    
    def on_error(self, error_msg):
        """Hata oluştuğunda"""
        self.view.show_error(f"Veri yüklenirken hata oluştu:\n{error_msg}")
    
    def on_geri(self):
        """Geri butonuna tıklandığında"""
        self.main_window.show_dashboard()
    
    def on_yeni(self):
        """Yeni malzeme ekle"""
        form_view = MalzemeFormView(self.view)
        if form_view.exec_() == QDialog.Accepted:
            if form_view.validate():
                data = form_view.get_data()
                self.save_malzeme(data)
    
    def save_malzeme(self, data):
        """Malzemeyi kaydet"""
        self.controller = MalzemeController('create', data)
        self.controller.operation_success.connect(self.on_save_success)
        self.controller.error_occurred.connect(self.on_error)
        self.controller.start()
    
    def on_save_success(self, data):
        """Kayıt başarılı"""
        self.view.show_success("Malzeme başarıyla eklendi!")
        self.load_data()
    
    def on_context_menu(self, position):
        """Sağ tık menüsü"""
        item = self.view.table.itemAt(position)
        if item:
            row = item.row()
            malzeme = self.view.filtered_list[row] if row < len(self.view.filtered_list) else None
            
            if malzeme:
                menu = QMenu(self.view)
                edit_action = menu.addAction("Düzenle")
                delete_action = menu.addAction("Sil")
                
                action = menu.exec_(self.view.table.viewport().mapToGlobal(position))
                
                if action == edit_action:
                    self.edit_malzeme(malzeme)
                elif action == delete_action:
                    self.delete_malzeme(malzeme['id'])
    
    def edit_malzeme(self, malzeme):
        """Malzemeyi düzenle"""
        form_view = MalzemeFormView(self.view, malzeme)
        if form_view.exec_() == QDialog.Accepted:
            if form_view.validate():
                data = form_view.get_data()
                data['id'] = malzeme['id']
                self.update_malzeme(data)
    
    def update_malzeme(self, data):
        """Malzemeyi güncelle"""
        self.controller = MalzemeController('update', data)
        self.controller.operation_success.connect(self.on_update_success)
        self.controller.error_occurred.connect(self.on_error)
        self.controller.start()
    
    def on_update_success(self, data):
        """Güncelleme başarılı"""
        self.view.show_success("Malzeme başarıyla güncellendi!")
        self.load_data()
    
    def delete_malzeme(self, malzeme_id):
        """Malzemeyi sil"""
        if self.view.show_delete_confirmation():
            self.controller = MalzemeController('delete', {'id': malzeme_id})
            self.controller.operation_success.connect(self.on_delete_success)
            self.controller.error_occurred.connect(self.on_error)
            self.controller.start()
    
    def on_delete_success(self, data):
        """Silme başarılı"""
        self.view.show_success("Malzeme başarıyla silindi!")
        self.load_data()
    
    def on_double_click(self, malzeme):
        """Çift tıklama - Malzeme düzenle"""
        if malzeme:
            self.edit_malzeme(malzeme)
    
    def on_search(self, query):
        """Arama yap"""
        if not query or not query.strip():
            self.view.filter_data(self.all_malzeme_data)
        else:
            self.controller = MalzemeController('search', {'query': query})
            self.controller.data_loaded.connect(self.on_search_result)
            self.controller.error_occurred.connect(self.on_error)
            self.controller.start()
    
    def on_search_result(self, results):
        """Arama sonuçlarını göster"""
        self.view.filter_data(results)

