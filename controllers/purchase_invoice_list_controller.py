"""
Alış Faturası List Controller - İş mantığı katmanı
"""
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from models.purchase_invoice_model import PurchaseInvoiceModel
from views.purchase_invoice_view import PurchaseInvoiceView
from services.export_service import ExportService


class PurchaseInvoiceListWorker(QThread):
    """Alış faturaları listesini yükleyen worker"""
    data_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        try:
            model = PurchaseInvoiceModel()
            invoices = model.get_all()
            self.data_loaded.emit(invoices)
        except Exception as e:
            self.error_occurred.emit(str(e))


class PurchaseInvoiceListController:
    """Alış faturası listesi controller - MVC Controller"""
    
    def __init__(self, view, main_window):
        self.view = view
        self.main_window = main_window
        self.all_invoice_data = []
        self.setup_callbacks()
        self.load_data()
        self.export_service = ExportService()
    
    def setup_callbacks(self):
        """View callback'lerini ayarla"""
        self.view.set_callbacks(
            on_geri=self.on_geri,
            on_yeni=self.on_yeni,
            on_double_click=self.on_double_click,
            on_search=self.on_search,
            on_export_pdf=self.on_export_pdf,
            on_export_excel=self.on_export_excel,
            on_export_csv=self.on_export_csv
        )
    
    def load_data(self):
        """Veriyi yükle"""
        self.worker = PurchaseInvoiceListWorker()
        self.worker.data_loaded.connect(self.on_data_loaded)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()
    
    def on_data_loaded(self, data):
        """Veri yüklendiğinde"""
        if data is None:
            data = []
        self.all_invoice_data = data
        self.view.display_data(data)
    
    def on_error(self, error_msg):
        """Hata oluştuğunda"""
        self.view.show_error(f"Veri yüklenirken hata oluştu:\n{error_msg}")
    
    def on_geri(self):
        """Geri butonuna tıklandığında"""
        self.main_window.show_dashboard()
    
    def on_yeni(self):
        """Yeni alış faturası ekle"""
        try:
            form_view = PurchaseInvoiceView(self.main_window)
            from controllers.purchase_invoice_controller import PurchaseInvoiceController
            controller = PurchaseInvoiceController(form_view, self.main_window)
            
            # Dialog olarak göster
            result = form_view.exec_()
            if result == QDialog.Accepted:
                # Veriyi yeniden yükle
                self.load_data()
        except Exception as e:
            QMessageBox.critical(self.view, "Hata", f"Fatura ekleme ekranı açılırken hata oluştu:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def on_double_click(self, invoice):
        """Çift tıklama - Fatura düzenle (şimdilik sadece görüntüle)"""
        if invoice:
            QMessageBox.information(
                self.view,
                "Alış Faturası",
                f"Fatura No: {invoice.get('fatura_no', '-')}\n"
                f"Tedarikçi: {invoice.get('tedarikci_unvani', '-')}\n"
                f"Toplam: {invoice.get('toplam', 0):.2f} ₺"
            )
    
    def on_search(self, query):
        """Arama yap"""
        if not query or not query.strip():
            self.view.filter_data(self.all_invoice_data)
        else:
            query_lower = query.lower().strip()
            filtered = []
            for invoice in self.all_invoice_data:
                fatura_no = str(invoice.get('fatura_no', '')).lower()
                tarih = str(invoice.get('fatura_tarihi', '')).lower()
                tedarikci = str(invoice.get('tedarikci_unvani', '')).lower()
                
                if (query_lower in fatura_no or 
                    query_lower in tarih or 
                    query_lower in tedarikci):
                    filtered.append(invoice)
            self.view.filter_data(filtered)
    
    def on_export_pdf(self):
        """PDF olarak export et"""
        try:
            data_to_export = self.view.filtered_list if hasattr(self.view, 'filtered_list') else self.all_invoice_data
            if not data_to_export:
                QMessageBox.warning(self.view, "Uyarı", "Export edilecek veri bulunamadı")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self.view, "PDF Olarak Kaydet", "alis_faturalari.pdf", "PDF Files (*.pdf)"
            )
            if filename:
                export_data = []
                for invoice in data_to_export:
                    export_data.append({
                        'Fatura No': invoice.get('fatura_no', ''),
                        'Tarih': invoice.get('fatura_tarihi', ''),
                        'Tedarikçi': invoice.get('tedarikci_unvani', ''),
                        'Toplam': float(invoice.get('toplam', 0) or 0),
                        'KDV': float(invoice.get('toplam_kdv', 0) or 0),
                        'Net Tutar': float(invoice.get('net_tutar', 0) or 0),
                        'Durum': invoice.get('durum', '')
                    })
                
                columns = ['Fatura No', 'Tarih', 'Tedarikçi', 'Toplam', 'KDV', 'Net Tutar', 'Durum']
                self.export_service.export_to_pdf(export_data, "Alış Faturaları", columns, filename)
                QMessageBox.information(self.view, "Başarılı", f"PDF dosyası oluşturuldu:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self.view, "Hata", f"PDF export hatası:\n{str(e)}")
    
    def on_export_excel(self):
        """Excel olarak export et"""
        try:
            data_to_export = self.view.filtered_list if hasattr(self.view, 'filtered_list') else self.all_invoice_data
            if not data_to_export:
                QMessageBox.warning(self.view, "Uyarı", "Export edilecek veri bulunamadı")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self.view, "Excel Olarak Kaydet", "alis_faturalari.xlsx", "Excel Files (*.xlsx)"
            )
            if filename:
                export_data = []
                for invoice in data_to_export:
                    export_data.append({
                        'Fatura No': invoice.get('fatura_no', ''),
                        'Tarih': invoice.get('fatura_tarihi', ''),
                        'Tedarikçi': invoice.get('tedarikci_unvani', ''),
                        'Toplam': float(invoice.get('toplam', 0) or 0),
                        'KDV': float(invoice.get('toplam_kdv', 0) or 0),
                        'Net Tutar': float(invoice.get('net_tutar', 0) or 0),
                        'Durum': invoice.get('durum', '')
                    })
                
                columns = ['Fatura No', 'Tarih', 'Tedarikçi', 'Toplam', 'KDV', 'Net Tutar', 'Durum']
                self.export_service.export_to_excel(export_data, "Alış Faturaları", columns, filename)
                QMessageBox.information(self.view, "Başarılı", f"Excel dosyası oluşturuldu:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self.view, "Hata", f"Excel export hatası:\n{str(e)}")
    
    def on_export_csv(self):
        """CSV olarak export et"""
        try:
            data_to_export = self.view.filtered_list if hasattr(self.view, 'filtered_list') else self.all_invoice_data
            if not data_to_export:
                QMessageBox.warning(self.view, "Uyarı", "Export edilecek veri bulunamadı")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self.view, "CSV Olarak Kaydet", "alis_faturalari.csv", "CSV Files (*.csv)"
            )
            if filename:
                export_data = []
                for invoice in data_to_export:
                    export_data.append({
                        'Fatura No': invoice.get('fatura_no', ''),
                        'Tarih': invoice.get('fatura_tarihi', ''),
                        'Tedarikçi': invoice.get('tedarikci_unvani', ''),
                        'Toplam': float(invoice.get('toplam', 0) or 0),
                        'KDV': float(invoice.get('toplam_kdv', 0) or 0),
                        'Net Tutar': float(invoice.get('net_tutar', 0) or 0),
                        'Durum': invoice.get('durum', '')
                    })
                
                columns = ['Fatura No', 'Tarih', 'Tedarikçi', 'Toplam', 'KDV', 'Net Tutar', 'Durum']
                self.export_service.export_to_csv(export_data, "Alış Faturaları", columns, filename)
                QMessageBox.information(self.view, "Başarılı", f"CSV dosyası oluşturuldu:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self.view, "Hata", f"CSV export hatası:\n{str(e)}")

