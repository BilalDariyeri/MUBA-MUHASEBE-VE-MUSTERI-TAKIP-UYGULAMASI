"""
Fatura Gönder Controller - Fatura gönderme iş mantığı
"""
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from controllers.fatura_controller import FaturaController
from services.fatura_pdf_service import FaturaPDFService
from services.email_service import EmailService
import os
import tempfile


class FaturaGonderController:
    """Fatura gönderme controller - MVC Controller"""
    
    def __init__(self, view, main_window):
        self.view = view
        self.main_window = main_window
        self.all_fatura_data = []
        self.setup_callbacks()
        self.load_data()
    
    def setup_callbacks(self):
        """View callback'lerini ayarla"""
        self.view.set_callbacks(
            on_geri=self.on_geri,
            on_yenile=self.on_yenile,
            on_gonder=self.on_gonder,
            on_search=self.on_search,
            on_filter=self.apply_filters
        )
        self.fatura_pdf_service = FaturaPDFService()
        self.email_service = EmailService()
    
    def load_data(self):
        """Veriyi yükle"""
        from models.fatura_model import FaturaModel
        try:
            model = FaturaModel()
            data = model.get_all()
            self.on_data_loaded(data if data else [])
        except Exception as e:
            self.on_error(str(e))
    
    def on_data_loaded(self, data):
        """Veri yüklendiğinde"""
        if data is None:
            data = []
        self.all_fatura_data = data
        self.view.display_data(data)
    
    def on_error(self, error_msg):
        """Hata oluştuğunda"""
        self.view.show_error(f"Veri yüklenirken hata oluştu:\n{error_msg}")
    
    def on_geri(self):
        """Geri butonuna tıklandığında"""
        self.main_window.show_dashboard()
    
    def on_yenile(self):
        """Yenile butonuna tıklandığında"""
        self.load_data()
    
    def on_search(self, query):
        """Arama yap"""
        self.apply_filters()
    
    def apply_filters(self):
        """Tüm filtreleri uygula"""
        filters = self.view.get_filters()
        filtered = []
        
        for fatura in self.all_fatura_data:
            # Tarih filtresi
            fatura_tarih = fatura.get('tarih', '')
            if filters.get('baslangic_tarih'):
                if fatura_tarih < filters['baslangic_tarih']:
                    continue
            if filters.get('bitis_tarih'):
                if fatura_tarih > filters['bitis_tarih']:
                    continue
            
            # Cari hesap filtresi
            if filters.get('cari_id'):
                if fatura.get('cariId') != filters['cari_id']:
                    continue
            
            # Durum filtresi
            if filters.get('durum'):
                if fatura.get('durum') != filters['durum']:
                    continue
            
            # Arama filtresi
            search_query = filters.get('search', '').lower().strip()
            if search_query:
                fatura_no = str(fatura.get('faturaNo', '')).lower()
                tarih = str(fatura.get('tarih', '')).lower()
                cari_hesap = fatura.get('cariHesap', {})
                if isinstance(cari_hesap, str):
                    import json
                    try:
                        cari_hesap = json.loads(cari_hesap)
                    except:
                        cari_hesap = {}
                unvan = cari_hesap.get('unvani', '').lower()
                email = cari_hesap.get('email', '').lower()
                
                if not (search_query in fatura_no or 
                       search_query in tarih or 
                       search_query in unvan or
                       search_query in email):
                    continue
            
            filtered.append(fatura)
        
        self.view.filter_data(filtered)
    
    def on_gonder(self):
        """Fatura gönder"""
        try:
            selected_faturalar = self.view.get_selected_faturalar()
            
            if not selected_faturalar:
                QMessageBox.warning(self.view, "Uyarı", "Lütfen en az bir fatura seçin")
                return
            
            send_method = self.view.get_send_method()
            
            if send_method == 'email':
                self.send_by_email(selected_faturalar)
            else:
                self.save_as_pdf(selected_faturalar)
        except Exception as e:
            error_msg = f"Fatura gönderme hatası:\n{str(e)}"
            import traceback
            error_details = traceback.format_exc()
            print(f"Fatura gönderme hatası detayları:\n{error_details}")
            QMessageBox.critical(self.view, "Hata", error_msg)
    
    def send_by_email(self, selected_faturalar):
        """Faturaları e-posta ile gönder"""
        try:
            success_count = 0
            error_count = 0
            no_email_count = 0
            error_details = []
            
            for fatura in selected_faturalar:
                try:
                    # Cari hesap bilgilerini al
                    cari_hesap = fatura.get('cariHesap', {})
                    if isinstance(cari_hesap, str):
                        import json
                        try:
                            cari_hesap = json.loads(cari_hesap)
                        except:
                            cari_hesap = {}
                    
                    # E-posta adresini bul - önce cariHesap içinde
                    to_email = cari_hesap.get('email', '')
                    
                    # Eğer cariHesap içinde yoksa, veritabanından cari hesabı çek
                    if not to_email or '@' not in str(to_email):
                        cari_id = fatura.get('cariId', '')
                        if cari_id:
                            try:
                                from models.cari_hesap_model import CariHesapModel
                                cari_model = CariHesapModel()
                                cari_data = cari_model.get_by_id(cari_id)
                                if cari_data:
                                    to_email = cari_data.get('email', '')
                                    # Eğer hala yoksa iletisim içinde ara
                                    if not to_email:
                                        iletisim = cari_data.get('iletisim', {})
                                        if isinstance(iletisim, str):
                                            import json
                                            try:
                                                iletisim = json.loads(iletisim)
                                            except:
                                                iletisim = {}
                                        to_email = iletisim.get('email', '') if isinstance(iletisim, dict) else ''
                            except Exception as e:
                                print(f"Cari hesap çekme hatası ({cari_id}): {e}")
                    
                    if not to_email or '@' not in str(to_email):
                        no_email_count += 1
                        # Cari hesap bilgilerini daha detaylı göster
                        cari_unvan = cari_hesap.get('unvani', 'Bilinmeyen')
                        cari_kodu = cari_hesap.get('kodu', 'Bilinmeyen')
                        # Eğer cari_id varsa veritabanından tekrar çek
                        cari_id_check = fatura.get('cariId', '')
                        if cari_id_check:
                            try:
                                from models.cari_hesap_model import CariHesapModel
                                cari_model = CariHesapModel()
                                cari_data = cari_model.get_by_id(cari_id_check)
                                if cari_data:
                                    cari_unvan = cari_data.get('unvani', cari_unvan)
                                    # Cari kodunu al, yoksa unvanı kullan
                                    cari_kodu = cari_data.get('kodu', '') if cari_data.get('kodu') else cari_unvan
                                    # Eğer kod hala yoksa unvanı kullan
                                    if not cari_kodu:
                                        cari_kodu = cari_unvan
                            except Exception as e:
                                print(f"Cari hesap bilgisi çekme hatası: {e}")
                        # Hata mesajını oluştur
                        error_msg = f"Fatura {fatura.get('faturaNo', 'Bilinmeyen')} için e-posta adresi bulunamadı.\nCari hesap: {cari_kodu}"
                        error_details.append(error_msg)
                        continue
                    
                    # Geçici PDF oluştur
                    temp_dir = tempfile.gettempdir()
                    fatura_no = str(fatura.get('faturaNo', 'FATURA')).replace('/', '_').replace('\\', '_')
                    pdf_path = os.path.join(temp_dir, f"Fatura_{fatura_no}.pdf")
                    
                    # PDF oluştur
                    print(f"PDF oluşturuluyor: {pdf_path}")
                    self.fatura_pdf_service.generate_efatura_pdf(fatura, pdf_path)
                    
                    if not os.path.exists(pdf_path):
                        raise Exception(f"PDF dosyası oluşturulamadı: {pdf_path}")
                    
                    # Email gönder (dariyeribilal3@gmail.com adresinden)
                    print(f"E-posta gönderiliyor: {to_email}")
                    self.email_service.send_fatura_email(to_email, fatura, pdf_path)
                    
                    # Geçici dosyayı sil
                    try:
                        os.remove(pdf_path)
                    except:
                        pass
                    
                    success_count += 1
                    print(f"✅ Fatura {fatura.get('faturaNo')} başarıyla gönderildi: {to_email}")
                except Exception as e:
                    error_count += 1
                    error_msg = f"{fatura.get('faturaNo', 'Bilinmeyen')}: {str(e)}"
                    error_details.append(error_msg)
                    print(f"❌ Email gönderme hatası ({fatura.get('faturaNo', 'Bilinmeyen')}): {e}")
                    import traceback
                    traceback.print_exc()
            
            # Sonuç mesajı
            message_parts = []
            if success_count > 0:
                message_parts.append(f"✅ {success_count} fatura başarıyla e-posta ile gönderildi!")
            if no_email_count > 0:
                message_parts.append(f"⚠️ {no_email_count} fatura için e-posta adresi bulunamadı")
                # E-posta bulunamayan faturaların detaylarını göster
                no_email_details = [d for d in error_details if "e-posta adresi bulunamadı" in d]
                if no_email_details:
                    message_parts.append("\n\nE-posta bulunamayan faturalar:")
                    for detail in no_email_details[:10]:  # İlk 10 hatayı göster
                        message_parts.append(f"\n{detail}")
            if error_count > 0:
                message_parts.append(f"❌ {error_count} fatura gönderilemedi")
                # Diğer hataları göster (e-posta dışındaki hatalar)
                other_errors = [d for d in error_details if "e-posta adresi bulunamadı" not in d]
                if other_errors:
                    message_parts.append("\n\nDiğer hatalar:")
                    for detail in other_errors[:5]:  # İlk 5 hatayı göster
                        message_parts.append(f"\n{detail}")
            
            if success_count > 0:
                QMessageBox.information(
                    self.view,
                    "Gönderim Sonucu",
                    "\n".join(message_parts) + "\n\n" +
                    f"Gönderen: dariyeribilal3@gmail.com"
                )
            else:
                QMessageBox.warning(
                    self.view,
                    "Uyarı",
                    "\n".join(message_parts) if message_parts else "Hiçbir fatura gönderilemedi"
                )
        except Exception as e:
            QMessageBox.critical(self.view, "Hata", f"E-posta gönderme hatası:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def save_as_pdf(self, selected_faturalar):
        """Faturaları PDF olarak kaydet"""
        folder = QFileDialog.getExistingDirectory(
            self.view, "Faturaları Kaydet", ""
        )
        
        if folder:
            success_count = 0
            error_count = 0
            error_details = []
            
            for fatura in selected_faturalar:
                try:
                    fatura_no = str(fatura.get('faturaNo', 'FATURA')).replace('/', '_').replace('\\', '_')
                    filename = os.path.join(folder, f"Fatura_{fatura_no}.pdf")
                    
                    # E-Fatura formatında PDF oluştur
                    print(f"PDF oluşturuluyor: {filename}")
                    self.fatura_pdf_service.generate_efatura_pdf(fatura, filename)
                    
                    if not os.path.exists(filename):
                        raise Exception(f"PDF dosyası oluşturulamadı: {filename}")
                    
                    success_count += 1
                    print(f"✅ PDF oluşturuldu: {filename}")
                except Exception as e:
                    error_count += 1
                    error_msg = f"{fatura.get('faturaNo', 'Bilinmeyen')}: {str(e)}"
                    error_details.append(error_msg)
                    print(f"❌ PDF oluşturma hatası ({fatura.get('faturaNo', 'Bilinmeyen')}): {e}")
                    import traceback
                    traceback.print_exc()
            
            if success_count > 0:
                message = f"{success_count} fatura başarıyla PDF olarak kaydedildi!\n"
                if error_count > 0:
                    message += f"\n⚠️ {error_count} fatura oluşturulamadı"
                    if error_details:
                        message += "\n\nHata detayları:\n"
                        message += "\n".join(error_details[:5])
                message += f"\n\nKonum: {folder}"
                QMessageBox.information(self.view, "Başarılı", message)
            else:
                message = "Hiçbir fatura oluşturulamadı"
                if error_details:
                    message += "\n\nHata detayları:\n"
                    message += "\n".join(error_details)
                QMessageBox.critical(self.view, "Hata", message)

