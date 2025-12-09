"""
Alım Faturası Controller - İş Mantığı Katmanı
Model ve View arası köprü
"""
from models.purchase_invoice_model import PurchaseInvoiceModel
from models.malzeme_model import MalzemeModel
from models.cari_hesap_model import CariHesapModel
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal


class PurchaseInvoiceWorker(QThread):
    """Alım faturası kaydetme işlemini ayrı thread'de yapan worker"""
    success = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, invoice_data):
        super().__init__()
        self.invoice_data = invoice_data
    
    def run(self):
        try:
            invoice_model = PurchaseInvoiceModel()
            malzeme_model = MalzemeModel()
            
            # Faturayı kaydet
            invoice = invoice_model.create(self.invoice_data)
            
            # Her satır için stok ve maliyet güncellemesi yap
            for item in self.invoice_data['items']:
                malzeme_id = item['malzeme_id']
                miktar = item['miktar']
                birim_fiyat = item['birim_fiyat']
                
                # Stok ekle ve ağırlıklı ortalama maliyet hesapla
                # Geçmiş stok hareketlerine göre maliyet hesaplanır
                malzeme_model.add_stok_with_cost(
                    malzeme_id, 
                    miktar, 
                    birim_fiyat,
                    referans_tipi='PURCHASE_INVOICE',
                    referans_id=invoice.get('id') if invoice else None
                )
            
            # Ödemeler modülüne otomatik ekle
            try:
                from models.odeme_model import OdemeModel
                odeme_model = OdemeModel()
                
                # Bu fatura için zaten ödeme kaydı var mı kontrol et
                existing_odemeler = odeme_model.get_by_alim_faturasi_id(invoice.get('id'))
                
                if not existing_odemeler:
                    # Yeni ödeme kaydı oluştur
                    odeme_data = {
                        'kategori': OdemeModel.KATEGORI_TEDARIKCI,
                        'tedarikci_id': self.invoice_data.get('tedarikci_id'),
                        'tedarikci_unvani': self.invoice_data.get('tedarikci_unvani', ''),
                        'alim_faturasi_id': invoice.get('id'),
                        'tarih': self.invoice_data.get('fatura_tarihi', ''),
                        'tutar': float(invoice.get('toplam', 0)),
                        'odeme_turu': 'Beklemede',  # Henüz ödenmedi
                        'aciklama': f"Alim Faturasi: {invoice.get('fatura_no', '')}",
                        'belge_no': invoice.get('fatura_no', ''),
                        'vade_tarihi': self.invoice_data.get('vade_tarihi', '')
                    }
                    
                    odeme_model.create(odeme_data)
                    print(f"Odeme kaydi otomatik olusturuldu: {invoice.get('fatura_no', '')}")
            except Exception as e:
                # Ödeme kaydı oluşturma hatası kritik değil, sadece logla
                print(f"Odeme kaydi olusturma hatasi (gormezden gelinebilir): {e}")
                import traceback
                traceback.print_exc()
            
            self.success.emit(invoice)
        except Exception as e:
            self.error.emit(str(e))


class PurchaseInvoiceController:
    """Alım Faturası Controller"""
    
    def __init__(self, view, parent_window=None):
        self.view = view
        self.parent_window = parent_window
        self.invoice_model = PurchaseInvoiceModel()
        self.malzeme_model = MalzemeModel()
        self.cari_model = CariHesapModel()
        
        # View callback'lerini ayarla
        self.view.set_callbacks(on_save=self.on_save)
        
        # Verileri yükle
        self.load_data()
    
    def load_data(self):
        """Verileri yükle (artık gerekli değil, view kendi yüklüyor)"""
        pass
    
    def on_save(self):
        """Faturayı kaydet"""
        try:
            # Form verilerini al
            invoice_data = self.view.get_data()
            
            # Validasyon
            if not invoice_data.get('fatura_no'):
                # Fatura numarası yoksa oluştur
                invoice_data['fatura_no'] = self.invoice_model._generate_fatura_no()
            
            if not invoice_data.get('tedarikci_unvani'):
                QMessageBox.warning(self.view, "Uyarı", "Lütfen tedarikçi adı girin")
                return
            
            if len(invoice_data['items']) == 0:
                QMessageBox.warning(self.view, "Uyarı", "En az bir satır eklenmelidir")
                return
            
            # Her satır için ürün validasyonu (ekstra güvenlik)
            for item in invoice_data['items']:
                malzeme = self.malzeme_model.get_by_id(item['malzeme_id'])
                if not malzeme:
                    QMessageBox.critical(
                        self.view,
                        "Hata",
                        f"Ürün bulunamadı: {item.get('malzeme_adi', '')}\n"
                        "Lütfen önce Stok Kartı açın."
                    )
                    return
            
            # Onay al
            reply = QMessageBox.question(
                self.view,
                "Onay",
                f"Fatura kaydedilecek ve stoklar güncellenecek.\n"
                f"Toplam: {sum(item['tutar'] for item in invoice_data['items']):.2f} ₺\n\n"
                f"Devam etmek istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # Worker thread'de kaydet
            self.worker = PurchaseInvoiceWorker(invoice_data)
            self.worker.success.connect(self.on_save_success)
            self.worker.error.connect(self.on_save_error)
            self.worker.start()
            
            # Loading mesajı göster
            QMessageBox.information(
                self.view,
                "Bilgi",
                "Fatura kaydediliyor, lütfen bekleyin..."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Hata",
                f"Kaydetme hatası:\n{str(e)}"
            )
    
    def on_save_success(self, invoice):
        """Kaydetme başarılı"""
        QMessageBox.information(
            self.view,
            "Başarılı",
            f"Fatura başarıyla kaydedildi!\n\n"
            f"Fatura No: {invoice.get('fatura_no', '')}\n"
            f"Toplam: {invoice.get('toplam', 0):.2f} ₺"
        )
        
        # Dialog'u kapat ve kabul et
        self.view.accept()
    
    def on_save_error(self, error_msg):
        """Kaydetme hatası"""
        QMessageBox.critical(
            self.view,
            "Hata",
            f"Fatura kaydedilirken hata oluştu:\n{error_msg}"
        )

