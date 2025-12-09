"""
Tahsilat List Controller - Controller katmanı
Ödemeler listesi görünümü ve model arasındaki bağlantıyı yönetir
"""
from models.tahsilat_model import TahsilatModel
from models.cari_hesap_model import CariHesapModel
from views.tahsilat_list_view import TahsilatListView
from services.export_service import ExportService
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMenu, QFileDialog, QMessageBox


class TahsilatListWorker(QThread):
    """Tahsilat listesi yükleme worker thread"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.tahsilat_model = TahsilatModel()
    
    def run(self):
        """Thread'i çalıştır"""
        try:
            tahsilatlar = self.tahsilat_model.get_all()
            self.finished.emit(tahsilatlar)
        except Exception as e:
            self.error.emit(str(e))


class TahsilatDeleteWorker(QThread):
    """Tahsilat silme worker thread"""
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)
    
    def __init__(self, tahsilat_id, tahsilat_data):
        super().__init__()
        self.tahsilat_id = tahsilat_id
        self.tahsilat_data = tahsilat_data
        self.tahsilat_model = TahsilatModel()
        self.cari_model = CariHesapModel()
    
    def run(self):
        """Thread'i çalıştır"""
        try:
            # Tahsilatı sil
            self.tahsilat_model.delete(self.tahsilat_id)
            
            # Cari hesap borcunu geri ekle
            cari_id = self.tahsilat_data.get('cari_id')
            tutar = float(self.tahsilat_data.get('tutar', 0) or 0)
            
            if cari_id and tutar > 0:
                try:
                    self.cari_model.add_borc(cari_id, tutar)
                except Exception as e:
                    print(f"Cari hesap borcu güncellenirken hata: {e}")
            
            self.finished.emit(True)
        except Exception as e:
            self.error.emit(str(e))


class TahsilatListController:
    """Tahsilat/Ödemeler listesi controller - Controller katmanı"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.view = TahsilatListView(parent)
        self.model = TahsilatModel()
        self.export_service = ExportService()
        self.all_tahsilat_data = []
        
        self.setup_callbacks()
        self.load_data()
    
    def setup_callbacks(self):
        """Callback'leri ayarla"""
        self.view.set_callbacks({
            'on_geri': self.on_geri,
            'on_search': self.on_search,
            'on_export_pdf': self.on_export_pdf,
            'on_export_excel': self.on_export_excel,
            'on_yeni': self.on_yeni,
            'on_context_menu': self.on_context_menu
        })
    
    def load_data(self):
        """Veriyi yükle"""
        self.worker = TahsilatListWorker()
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def on_data_loaded(self, tahsilat_list):
        """Veri yüklendiğinde"""
        self.all_tahsilat_data = tahsilat_list
        self.view.display_data(tahsilat_list)
    
    def on_error(self, error_msg):
        """Hata oluştuğunda"""
        self.view.show_error(f"Veri yüklenirken hata: {error_msg}")
    
    def on_search(self, text, filter_type="Tümü"):
        """Arama ve filtreleme"""
        if not text and filter_type == "Tümü":
            self.view.filter_data(self.all_tahsilat_data)
            return
        
        filtered = self.all_tahsilat_data.copy()
        
        # Ödeme türü filtresi
        if filter_type and filter_type != "Tümü":
            filtered = [
                t for t in filtered
                if filter_type.lower() in str(t.get('odeme_turu', '')).lower()
            ]
        
        # Metin araması
        if text:
            text_lower = text.lower()
            filtered = [
                t for t in filtered
                if text_lower in str(t.get('cari_unvani', '')).lower() or
                   text_lower in str(t.get('tarih', '')).lower() or
                   text_lower in str(t.get('odeme_turu', '')).lower() or
                   text_lower in str(t.get('belge_no', '')).lower() or
                   text_lower in str(t.get('tutar', '')).lower() or
                   text_lower in str(t.get('aciklama', '')).lower()
            ]
        
        self.view.filter_data(filtered)
    
    def on_context_menu(self, position):
        """Sağ tık menüsü"""
        item = self.view.table.itemAt(position)
        if item:
            row = item.row()
            if row >= 0 and row < len(self.view.filtered_list):
                tahsilat = self.view.filtered_list[row]
                
                menu = QMenu(self.view)
                
                # Detay görüntüle
                detail_action = menu.addAction("📋 Detay Görüntüle")
                
                menu.addSeparator()
                
                # Sil
                delete_action = menu.addAction("🗑️ Sil")
                
                action = menu.exec_(self.view.table.viewport().mapToGlobal(position))
                
                if action == detail_action:
                    self.show_detail(tahsilat)
                elif action == delete_action:
                    self.delete_tahsilat(tahsilat)
    
    def show_detail(self, tahsilat):
        """Tahsilat detayını göster"""
        tutar = float(tahsilat.get('tutar', 0) or 0)
        eski_borc = float(tahsilat.get('eski_borc', 0) or 0)
        yeni_borc = float(tahsilat.get('yeni_borc', 0) or 0)
        
        detail_text = f"""
        <h2>💰 Ödeme Detayı</h2>
        <hr>
        <table style="width: 100%; font-size: 14px;">
            <tr><td><b>Tarih:</b></td><td>{tahsilat.get('tarih', '-')}</td></tr>
            <tr><td><b>Cari Hesap:</b></td><td>{tahsilat.get('cari_unvani', '-')}</td></tr>
            <tr><td><b>Tutar:</b></td><td style="color: green; font-weight: bold;">{tutar:,.2f} ₺</td></tr>
            <tr><td><b>Ödeme Türü:</b></td><td>{tahsilat.get('odeme_turu', '-')}</td></tr>
            <tr><td><b>Kasa/Banka:</b></td><td>{tahsilat.get('kasa', '-') or tahsilat.get('banka', '-')}</td></tr>
            <tr><td><b>Belge No:</b></td><td>{tahsilat.get('belge_no', '-')}</td></tr>
            <tr><td><b>Açıklama:</b></td><td>{tahsilat.get('aciklama', '-')}</td></tr>
            <tr><td><b>Vade Tarihi:</b></td><td>{tahsilat.get('vade_tarihi', '-')}</td></tr>
            <tr><td colspan="2"><hr></td></tr>
            <tr><td><b>Eski Borç:</b></td><td style="color: red;">{eski_borc:,.2f} ₺</td></tr>
            <tr><td><b>Yeni Borç:</b></td><td style="color: {'green' if yeni_borc < eski_borc else 'orange'};">{yeni_borc:,.2f} ₺</td></tr>
        </table>
        """
        
        msg = QMessageBox(self.view)
        msg.setWindowTitle("Ödeme Detayı")
        msg.setTextFormat(1)  # Rich text
        msg.setText(detail_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
    
    def delete_tahsilat(self, tahsilat):
        """Tahsilatı sil"""
        if not self.view.show_delete_confirmation():
            return
        
        tahsilat_id = tahsilat.get('id')
        if not tahsilat_id:
            self.view.show_error("Tahsilat ID bulunamadı!")
            return
        
        self.delete_worker = TahsilatDeleteWorker(tahsilat_id, tahsilat)
        self.delete_worker.finished.connect(self.on_delete_success)
        self.delete_worker.error.connect(self.on_delete_error)
        self.delete_worker.start()
    
    def on_delete_success(self, success):
        """Silme başarılı"""
        self.view.show_success("Ödeme kaydı başarıyla silindi!\nCari hesap borcu geri eklendi.")
        self.load_data()
    
    def on_delete_error(self, error_msg):
        """Silme hatası"""
        self.view.show_error(f"Silme hatası: {error_msg}")
    
    def on_export_pdf(self):
        """PDF export"""
        try:
            data_to_export = self.view.filtered_list if hasattr(self.view, 'filtered_list') else self.all_tahsilat_data
            if not data_to_export:
                QMessageBox.warning(self.view, "Uyarı", "Export edilecek veri bulunamadı")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self.view, "PDF Olarak Kaydet", "odemeler.pdf", "PDF Files (*.pdf)"
            )
            if filename:
                # Veriyi export formatına çevir
                export_data = []
                for t in data_to_export:
                    tutar = float(t.get('tutar', 0) or 0)
                    eski_borc = float(t.get('eski_borc', 0) or 0)
                    yeni_borc = float(t.get('yeni_borc', 0) or 0)
                    
                    export_data.append({
                        'Tarih': t.get('tarih', ''),
                        'Cari Hesap': t.get('cari_unvani', ''),
                        'Tutar': f"{tutar:,.2f} ₺",
                        'Ödeme Türü': t.get('odeme_turu', ''),
                        'Belge No': t.get('belge_no', ''),
                        'Açıklama': t.get('aciklama', ''),
                        'Eski Borç': f"{eski_borc:,.2f} ₺",
                        'Yeni Borç': f"{yeni_borc:,.2f} ₺"
                    })
                
                columns = ['Tarih', 'Cari Hesap', 'Tutar', 'Ödeme Türü', 'Belge No', 'Açıklama', 'Eski Borç', 'Yeni Borç']
                self.export_service.export_to_pdf(export_data, "Ödemeler / Tahsilatlar", columns, filename)
                QMessageBox.information(self.view, "Başarılı", f"PDF dosyası oluşturuldu:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self.view, "Hata", f"PDF export hatası:\n{str(e)}")
    
    def on_export_excel(self):
        """Excel export"""
        try:
            data_to_export = self.view.filtered_list if hasattr(self.view, 'filtered_list') else self.all_tahsilat_data
            if not data_to_export:
                QMessageBox.warning(self.view, "Uyarı", "Export edilecek veri bulunamadı")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self.view, "Excel Olarak Kaydet", "odemeler.xlsx", "Excel Files (*.xlsx)"
            )
            if filename:
                export_data = []
                for t in data_to_export:
                    export_data.append({
                        'Tarih': t.get('tarih', ''),
                        'Cari Hesap': t.get('cari_unvani', ''),
                        'Tutar': float(t.get('tutar', 0) or 0),
                        'Ödeme Türü': t.get('odeme_turu', ''),
                        'Kasa/Banka': t.get('kasa', '') or t.get('banka', ''),
                        'Belge No': t.get('belge_no', ''),
                        'Açıklama': t.get('aciklama', ''),
                        'Eski Borç': float(t.get('eski_borc', 0) or 0),
                        'Yeni Borç': float(t.get('yeni_borc', 0) or 0)
                    })
                
                columns = ['Tarih', 'Cari Hesap', 'Tutar', 'Ödeme Türü', 'Kasa/Banka', 'Belge No', 'Açıklama', 'Eski Borç', 'Yeni Borç']
                self.export_service.export_to_excel(export_data, "Ödemeler", columns, filename)
                QMessageBox.information(self.view, "Başarılı", f"Excel dosyası oluşturuldu:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self.view, "Hata", f"Excel export hatası:\n{str(e)}")
    
    def on_yeni(self):
        """Yeni tahsilat ekle"""
        try:
            # Lazy import - tkcalendar bağımlılığı nedeniyle
            from views.tahsilat_giris_view import TahsilatGirisView
            tahsilat_view = TahsilatGirisView(parent=self.parent)
            tahsilat_view.run()
            # Tahsilat kaydedildikten sonra listeyi yenile
            self.load_data()
        except ImportError as e:
            self.view.show_error(f"Modül eksik: {str(e)}\n\nÇözüm: pip install tkcalendar")
        except Exception as e:
            self.view.show_error(f"Tahsilat ekranı açılırken hata: {str(e)}")
    
    def on_geri(self):
        """Geri dön"""
        if self.parent:
            self.parent.show_dashboard()
