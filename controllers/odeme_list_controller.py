"""
Ödeme List Controller - Controller katmanı
Ödemeler listesi görünümü ve model arasındaki bağlantıyı yönetir
"""
from models.odeme_model import OdemeModel
from views.odeme_form_view import OdemeFormView
from services.export_service import ExportService
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMenu, QFileDialog, QMessageBox


class OdemeListWorker(QThread):
    """Ödeme listesi yükleme worker thread"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, kategori=None):
        super().__init__()
        self.kategori = kategori
        self.odeme_model = OdemeModel()
    
    def run(self):
        """Thread'i çalıştır"""
        try:
            if self.kategori:
                odemeler = self.odeme_model.get_by_kategori(self.kategori)
            else:
                odemeler = self.odeme_model.get_all()
            self.finished.emit(odemeler)
        except Exception as e:
            self.error.emit(str(e))


class OdemeDeleteWorker(QThread):
    """Ödeme silme worker thread"""
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)
    
    def __init__(self, odeme_id):
        super().__init__()
        self.odeme_id = odeme_id
        self.odeme_model = OdemeModel()
    
    def run(self):
        """Thread'i çalıştır"""
        try:
            self.odeme_model.delete(self.odeme_id)
            self.finished.emit(True)
        except Exception as e:
            self.error.emit(str(e))


class OdemeListController:
    """Ödeme listesi controller - Controller katmanı"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.view = None  # Lazy load
        self.model = OdemeModel()
        self.export_service = ExportService()
        self.all_odeme_data = []
        self.filtered_lists = {
            'TEDARIKCI': [],
            'MAAS': [],
            'KIRA': [],
            'DIGER': []
        }
    
    def set_view(self, view):
        """View'i ayarla"""
        self.view = view
        self.setup_callbacks()
        self.load_data()
    
    def setup_callbacks(self):
        """Callback'leri ayarla"""
        if not self.view:
            return
        
        self.view.set_callbacks(
            on_geri=self.on_geri,
            on_yeni=self.on_yeni,
            on_search=self.on_search,
            on_filter=self.on_filter,
            on_context_menu=self.on_context_menu,
            on_export_pdf=self.on_export_pdf,
            on_export_excel=self.on_export_excel,
            on_refresh=self.on_refresh,
            on_sync=self.on_sync_purchase_invoices
        )
    
    def load_data(self, kategori=None):
        """Veriyi yükle"""
        self.worker = OdemeListWorker(kategori)
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def on_data_loaded(self, odeme_list):
        """Veri yüklendiğinde"""
        self.all_odeme_data = odeme_list
        
        # Kategorilere göre ayır
        for kategori in ['TEDARIKCI', 'MAAS', 'KIRA', 'DIGER']:
            self.filtered_lists[kategori] = [
                o for o in odeme_list if o.get('kategori') == kategori
            ]
        
        if self.view:
            self.view.display_data(odeme_list)
    
    def on_error(self, error_msg):
        """Hata oluştuğunda"""
        if self.view:
            self.view.show_error(f"Veri yüklenirken hata: {error_msg}")
    
    def on_refresh(self, kategori):
        """Sekme değiştiğinde yenile"""
        self.load_data(kategori)
    
    def on_search(self, text, kategori):
        """Arama ve filtreleme"""
        if not text:
            # Boşsa tümünü göster
            filtered = self.filtered_lists.get(kategori, [])
        else:
            text_lower = text.lower()
            filtered = [
                o for o in self.filtered_lists.get(kategori, [])
                if text_lower in str(o.get('tedarikci_unvani', '')).lower() or
                   text_lower in str(o.get('tarih', '')).lower() or
                   text_lower in str(o.get('odeme_turu', '')).lower() or
                   text_lower in str(o.get('belge_no', '')).lower() or
                   text_lower in str(o.get('tutar', '')).lower() or
                   text_lower in str(o.get('aciklama', '')).lower()
            ]
        
        if self.view:
            self.view._update_table(filtered, kategori)
    
    def on_filter(self, filter_type, kategori):
        """Ödeme türü filtresi"""
        if filter_type == "Tümü":
            filtered = self.filtered_lists.get(kategori, [])
        else:
            filtered = [
                o for o in self.filtered_lists.get(kategori, [])
                if filter_type.lower() in str(o.get('odeme_turu', '')).lower()
            ]
        
        if self.view:
            self.view._update_table(filtered, kategori)
    
    def on_context_menu(self, position, kategori):
        """Sağ tık menüsü"""
        if not self.view:
            return
        
        table = self.view.tables.get(kategori)
        if not table:
            return
        
        item = table.itemAt(position)
        if item:
            row = item.row()
            filtered_list = self.filtered_lists.get(kategori, [])
            if row >= 0 and row < len(filtered_list):
                odeme = filtered_list[row]
                
                menu = QMenu(self.view)
                
                # Detay görüntüle
                detail_action = menu.addAction("📋 Detay Görüntüle")
                
                menu.addSeparator()
                
                # Düzenle
                edit_action = menu.addAction("✏️ Düzenle")
                
                menu.addSeparator()
                
                # Sil
                delete_action = menu.addAction("🗑️ Sil")
                
                action = menu.exec_(table.viewport().mapToGlobal(position))
                
                if action == detail_action:
                    self.show_detail(odeme)
                elif action == edit_action:
                    self.edit_odeme(odeme)
                elif action == delete_action:
                    self.delete_odeme(odeme)
    
    def show_detail(self, odeme):
        """Ödeme detayını göster"""
        tutar = float(odeme.get('tutar', 0) or 0)
        
        kategori_text = {
            'TEDARIKCI': 'Tedarikçi Ödemesi',
            'MAAS': 'Maaş Ödemesi',
            'KIRA': 'Kira Ödemesi',
            'DIGER': 'Diğer Ödeme'
        }.get(odeme.get('kategori', 'DIGER'), 'Ödeme')
        
        detail_text = f"""
        <h2>💰 {kategori_text} Detayı</h2>
        <hr>
        <table style="width: 100%; font-size: 14px;">
            <tr><td><b>Kategori:</b></td><td>{kategori_text}</td></tr>
            <tr><td><b>Tarih:</b></td><td>{odeme.get('tarih', '-')}</td></tr>
            <tr><td><b>Tutar:</b></td><td style="color: red; font-weight: bold;">{tutar:,.2f} ₺</td></tr>
            <tr><td><b>Ödeme Türü:</b></td><td>{odeme.get('odeme_turu', '-')}</td></tr>
            <tr><td><b>Tedarikçi/Alıcı:</b></td><td>{odeme.get('tedarikci_unvani', odeme.get('aciklama', '-'))}</td></tr>
            <tr><td><b>Kasa:</b></td><td>{odeme.get('kasa', '-')}</td></tr>
            <tr><td><b>Banka:</b></td><td>{odeme.get('banka', '-')}</td></tr>
            <tr><td><b>Belge No:</b></td><td>{odeme.get('belge_no', '-')}</td></tr>
            <tr><td><b>Vade Tarihi:</b></td><td>{odeme.get('vade_tarihi', '-')}</td></tr>
            <tr><td><b>Alım Faturası:</b></td><td>{odeme.get('alim_faturasi_no', '-')}</td></tr>
            <tr><td><b>Açıklama:</b></td><td>{odeme.get('aciklama', '-')}</td></tr>
        </table>
        """
        
        msg = QMessageBox(self.view)
        msg.setWindowTitle("Ödeme Detayı")
        msg.setTextFormat(1)  # Rich text
        msg.setText(detail_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
    
    def edit_odeme(self, odeme):
        """Ödemeyi düzenle"""
        from PyQt5.QtWidgets import QDialog
        form_view = OdemeFormView(self.view, odeme)
        if form_view.exec_() == QDialog.Accepted:
            if form_view.validate():
                data = form_view.get_data()
                self.update_odeme(odeme.get('id'), data)
    
    def update_odeme(self, odeme_id, data):
        """Ödemeyi güncelle"""
        try:
            updated = self.model.update(odeme_id, data)
            if self.view:
                self.view.show_success("Ödeme başarıyla güncellendi!")
            self.load_data()
        except Exception as e:
            if self.view:
                self.view.show_error(f"Güncelleme hatası: {str(e)}")
    
    def delete_odeme(self, odeme):
        """Ödemeyi sil"""
        if not self.view or not self.view.show_delete_confirmation():
            return
        
        odeme_id = odeme.get('id')
        if not odeme_id:
            if self.view:
                self.view.show_error("Ödeme ID bulunamadı!")
            return
        
        self.delete_worker = OdemeDeleteWorker(odeme_id)
        self.delete_worker.finished.connect(self.on_delete_success)
        self.delete_worker.error.connect(self.on_delete_error)
        self.delete_worker.start()
    
    def on_delete_success(self, success):
        """Silme başarılı"""
        if self.view:
            self.view.show_success("Ödeme başarıyla silindi!")
        self.load_data()
    
    def on_delete_error(self, error_msg):
        """Silme hatası"""
        if self.view:
            self.view.show_error(f"Silme hatası: {error_msg}")
    
    def on_yeni(self):
        """Yeni ödeme ekle"""
        from PyQt5.QtWidgets import QDialog
        form_view = OdemeFormView(self.view)
        if form_view.exec_() == QDialog.Accepted:
            if form_view.validate():
                data = form_view.get_data()
                self.save_odeme(data)
    
    def save_odeme(self, data):
        """Ödemeyi kaydet"""
        try:
            odeme = self.model.create(data)
            if self.view:
                self.view.show_success("Ödeme başarıyla eklendi!")
            self.load_data()
        except Exception as e:
            if self.view:
                self.view.show_error(f"Kayıt hatası: {str(e)}")
    
    def on_export_pdf(self):
        """PDF export"""
        try:
            kategori = self.view.get_current_kategori() if self.view else None
            data_to_export = self.filtered_lists.get(kategori, []) if kategori else self.all_odeme_data
            
            if not data_to_export:
                QMessageBox.warning(self.view, "Uyarı", "Export edilecek veri bulunamadı")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self.view, "PDF Olarak Kaydet", "odemeler.pdf", "PDF Files (*.pdf)"
            )
            if filename:
                export_data = []
                for o in data_to_export:
                    export_data.append({
                        'Tarih': o.get('tarih', ''),
                        'Kategori': o.get('kategori', ''),
                        'Tedarikçi/Alıcı': o.get('tedarikci_unvani', o.get('aciklama', '')),
                        'Tutar': f"{float(o.get('tutar', 0) or 0):,.2f} ₺",
                        'Ödeme Türü': o.get('odeme_turu', ''),
                        'Belge No': o.get('belge_no', ''),
                        'Açıklama': o.get('aciklama', '')
                    })
                
                columns = ['Tarih', 'Kategori', 'Tedarikçi/Alıcı', 'Tutar', 'Ödeme Türü', 'Belge No', 'Açıklama']
                self.export_service.export_to_pdf(export_data, "Ödemeler", columns, filename)
                QMessageBox.information(self.view, "Başarılı", f"PDF dosyası oluşturuldu:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self.view, "Hata", f"PDF export hatası:\n{str(e)}")
    
    def on_export_excel(self):
        """Excel export"""
        try:
            kategori = self.view.get_current_kategori() if self.view else None
            data_to_export = self.filtered_lists.get(kategori, []) if kategori else self.all_odeme_data
            
            if not data_to_export:
                QMessageBox.warning(self.view, "Uyarı", "Export edilecek veri bulunamadı")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self.view, "Excel Olarak Kaydet", "odemeler.xlsx", "Excel Files (*.xlsx)"
            )
            if filename:
                export_data = []
                for o in data_to_export:
                    export_data.append({
                        'Tarih': o.get('tarih', ''),
                        'Kategori': o.get('kategori', ''),
                        'Tedarikçi/Alıcı': o.get('tedarikci_unvani', o.get('aciklama', '')),
                        'Tutar': float(o.get('tutar', 0) or 0),
                        'Ödeme Türü': o.get('odeme_turu', ''),
                        'Kasa': o.get('kasa', ''),
                        'Banka': o.get('banka', ''),
                        'Belge No': o.get('belge_no', ''),
                        'Açıklama': o.get('aciklama', '')
                    })
                
                columns = ['Tarih', 'Kategori', 'Tedarikçi/Alıcı', 'Tutar', 'Ödeme Türü', 'Kasa', 'Banka', 'Belge No', 'Açıklama']
                self.export_service.export_to_excel(export_data, "Ödemeler", columns, filename)
                QMessageBox.information(self.view, "Başarılı", f"Excel dosyası oluşturuldu:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self.view, "Hata", f"Excel export hatası:\n{str(e)}")
    
    def on_sync_purchase_invoices(self):
        """Alım faturalarını ödemelere senkronize et"""
        try:
            from models.purchase_invoice_model import PurchaseInvoiceModel
            from PyQt5.QtWidgets import QMessageBox
            
            # Onay al
            reply = QMessageBox.question(
                self.view, 
                "Senkronizasyon", 
                "Tüm alım faturaları ödemeler modülüne aktarılacak.\n"
                "Zaten eklenmiş olanlar tekrar eklenmeyecek.\n\n"
                "Devam etmek istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # Alım faturalarını al
            invoice_model = PurchaseInvoiceModel()
            invoices = invoice_model.get_all()
            
            if not invoices:
                QMessageBox.information(self.view, "Bilgi", "Aktarılacak alım faturası bulunamadı.")
                return
            
            # Her fatura için ödeme kaydı oluştur
            added_count = 0
            skipped_count = 0
            
            for invoice in invoices:
                try:
                    # Bu fatura için zaten ödeme kaydı var mı kontrol et
                    existing_odemeler = self.model.get_by_alim_faturasi_id(invoice.get('id'))
                    
                    if not existing_odemeler:
                        # Yeni ödeme kaydı oluştur
                        odeme_data = {
                            'kategori': OdemeModel.KATEGORI_TEDARIKCI,
                            'tedarikci_id': invoice.get('tedarikci_id'),
                            'tedarikci_unvani': invoice.get('tedarikci_unvani', ''),
                            'alim_faturasi_id': invoice.get('id'),
                            'tarih': invoice.get('fatura_tarihi', ''),
                            'tutar': float(invoice.get('toplam', 0)),
                            'odeme_turu': 'Beklemede',
                            'aciklama': f"Alim Faturasi: {invoice.get('fatura_no', '')}",
                            'belge_no': invoice.get('fatura_no', ''),
                            'vade_tarihi': invoice.get('vade_tarihi', '')
                        }
                        
                        self.model.create(odeme_data)
                        added_count += 1
                    else:
                        skipped_count += 1
                except Exception as e:
                    print(f"Fatura senkronizasyon hatasi ({invoice.get('fatura_no', '')}): {e}")
                    continue
            
            # Sonuç mesajı
            QMessageBox.information(
                self.view,
                "Senkronizasyon Tamamlandı",
                f"Toplam {len(invoices)} alım faturası kontrol edildi.\n\n"
                f"✅ {added_count} yeni ödeme kaydı eklendi.\n"
                f"⏭️ {skipped_count} fatura zaten mevcut (atlandı)."
            )
            
            # Listeyi yenile
            self.load_data()
            
        except Exception as e:
            QMessageBox.critical(self.view, "Hata", f"Senkronizasyon hatası:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def on_geri(self):
        """Geri dön"""
        if self.parent:
            self.parent.show_dashboard()

