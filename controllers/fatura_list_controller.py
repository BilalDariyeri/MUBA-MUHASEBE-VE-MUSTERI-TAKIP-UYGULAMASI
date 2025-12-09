"""
Fatura List Controller - İş mantığı katmanı
"""
from PyQt5.QtWidgets import (
    QDialog, QFileDialog, QMessageBox, QCheckBox, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QScrollArea, QWidget, QComboBox, QRadioButton, 
    QButtonGroup, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from controllers.fatura_controller import FaturaController
from views.fatura_form_view import FaturaFormView
from views.gmail_settings_dialog import GmailSettingsDialog
from services.export_service import ExportService
from services.fatura_pdf_service import FaturaPDFService
from services.email_service import EmailService


class FaturaListController:
    """Fatura listesi controller - MVC Controller"""
    
    def __init__(self, view, main_window):
        try:
            self.view = view
            self.main_window = main_window
            self.all_fatura_data = []
            self.setup_callbacks()
            self.load_data()
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise
    
    def setup_callbacks(self):
        """View callback'lerini ayarla"""
        self.view.set_callbacks(
            on_geri=self.on_geri,
            on_yeni=self.on_yeni,
            on_double_click=self.on_double_click,
            on_search=self.on_search,
            on_export_pdf=self.on_export_pdf,
            on_export_excel=self.on_export_excel,
            on_export_csv=self.on_export_csv,
            on_gonder=self.on_gonder
        )
        self.all_fatura_data = []
        self.export_service = ExportService()
        self.fatura_pdf_service = FaturaPDFService()
    
    def load_data(self):
        """Veriyi yükle"""
        self.controller = FaturaController('get_all')
        self.controller.data_loaded.connect(self.on_data_loaded)
        self.controller.error_occurred.connect(self.on_error)
        self.controller.start()
    
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
    
    def on_yeni(self):
        """Yeni fatura ekle"""
        form_view = FaturaFormView(self.view)
        if form_view.exec_() == QDialog.Accepted:
            if form_view.validate():
                data = form_view.get_data()
                self.save_fatura(data)
    
    def save_fatura(self, data):
        """Faturayı kaydet"""
        # Kullanıcı bilgisini al
        user_id = None
        user_name = None
        if hasattr(self.main_window, 'current_user') and self.main_window.current_user:
            user_id = self.main_window.current_user.get('id', '')
            user_name = self.main_window.current_user.get('name', '')
        
        self.controller = FaturaController('create', data, user_id, user_name)
        self.controller.operation_success.connect(self.on_save_success)
        self.controller.error_occurred.connect(self.on_save_error)
        self.controller.start()
    
    def update_fatura(self, fatura_id, data):
        """Faturayı güncelle"""
        # Kullanıcı bilgisini al (en son giriş yapan kullanıcı)
        user_id = None
        user_name = None
        if hasattr(self.main_window, 'current_user') and self.main_window.current_user:
            user_id = self.main_window.current_user.get('id', '')
            user_name = self.main_window.current_user.get('name', '')
        
        self.controller = FaturaController('update', {'id': fatura_id, **data}, user_id, user_name)
        self.controller.operation_success.connect(self.on_update_success)
        self.controller.error_occurred.connect(self.on_update_error)
        self.controller.start()
    
    def on_save_success(self, data):
        """Kayıt başarılı"""
        self.view.show_success("Fatura başarıyla oluşturuldu!")
        self.load_data()
    
    def on_save_error(self, error_msg):
        """Fatura kaydetme hatası - uygulamadan çıkmasın"""
        # Stok hatası veya diğer hatalar için mesaj göster
        self.view.show_error(f"Fatura kaydedilemedi:\n{error_msg}")
    
    def on_update_success(self, data):
        """Güncelleme başarılı"""
        user_name = "Bilinmeyen"
        if hasattr(self.main_window, 'current_user') and self.main_window.current_user:
            user_name = self.main_window.current_user.get('name', 'Bilinmeyen')
        self.view.show_success(f"Fatura başarıyla güncellendi!\n\nSon düzenleyen: {user_name}")
        self.load_data()
    
    def on_update_error(self, error_msg):
        """Fatura güncelleme hatası"""
        self.view.show_error(f"Fatura güncellenemedi:\n{error_msg}")
    
    def on_double_click(self, fatura):
        """Çift tıklama - Fatura düzenle"""
        if fatura:
            form_view = FaturaFormView(self.view, fatura)
            if form_view.exec_() == QDialog.Accepted:
                if form_view.validate():
                    data = form_view.get_data()
                    self.update_fatura(fatura.get('id'), data)
    
    def on_search(self, query):
        """Arama yap"""
        if not query or not query.strip():
            self.view.filter_data(self.all_fatura_data)
        else:
            query_lower = query.lower().strip()
            filtered = []
            for fatura in self.all_fatura_data:
                fatura_no = str(fatura.get('faturaNo', '')).lower()
                tarih = str(fatura.get('tarih', '')).lower()
                cari_hesap = fatura.get('cariHesap', {})
                unvan = cari_hesap.get('unvani', '').lower()
                
                if (query_lower in fatura_no or 
                    query_lower in tarih or 
                    query_lower in unvan):
                    filtered.append(fatura)
            self.view.filter_data(filtered)
    
    def on_export_pdf(self):
        """PDF olarak export et"""
        try:
            data_to_export = self.view.filtered_list if hasattr(self.view, 'filtered_list') else self.all_fatura_data
            if not data_to_export:
                QMessageBox.warning(self.view, "Uyarı", "Export edilecek veri bulunamadı")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self.view, "PDF Olarak Kaydet", "faturalar.pdf", "PDF Files (*.pdf)"
            )
            if filename:
                # Veriyi export formatına çevir
                export_data = []
                for fatura in data_to_export:
                    cari_hesap = fatura.get('cariHesap', {})
                    export_data.append({
                        'Fatura No': fatura.get('faturaNo', ''),
                        'Tarih': fatura.get('tarih', ''),
                        'Cari Hesap': cari_hesap.get('kodu', ''),
                        'Unvan': cari_hesap.get('unvani', ''),
                        'Toplam': float(fatura.get('toplam', 0) or 0),
                        'KDV': float(fatura.get('toplamKDV', 0) or 0),
                        'Net Tutar': float(fatura.get('netTutar', 0) or 0),
                        'Durum': fatura.get('durum', '')
                    })
                
                columns = ['Fatura No', 'Tarih', 'Cari Hesap', 'Unvan', 'Toplam', 'KDV', 'Net Tutar', 'Durum']
                self.export_service.export_to_pdf(export_data, "Satış Faturaları", columns, filename)
                QMessageBox.information(self.view, "Başarılı", f"PDF dosyası oluşturuldu:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self.view, "Hata", f"PDF export hatası:\n{str(e)}")
    
    def on_export_excel(self):
        """Excel olarak export et"""
        try:
            data_to_export = self.view.filtered_list if hasattr(self.view, 'filtered_list') else self.all_fatura_data
            if not data_to_export:
                QMessageBox.warning(self.view, "Uyarı", "Export edilecek veri bulunamadı")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self.view, "Excel Olarak Kaydet", "faturalar.xlsx", "Excel Files (*.xlsx)"
            )
            if filename:
                export_data = []
                for fatura in data_to_export:
                    cari_hesap = fatura.get('cariHesap', {})
                    export_data.append({
                        'Fatura No': fatura.get('faturaNo', ''),
                        'Tarih': fatura.get('tarih', ''),
                        'Cari Hesap': cari_hesap.get('kodu', ''),
                        'Unvan': cari_hesap.get('unvani', ''),
                        'Toplam': float(fatura.get('toplam', 0) or 0),
                        'KDV': float(fatura.get('toplamKDV', 0) or 0),
                        'Net Tutar': float(fatura.get('netTutar', 0) or 0),
                        'Durum': fatura.get('durum', '')
                    })
                
                columns = ['Fatura No', 'Tarih', 'Cari Hesap', 'Unvan', 'Toplam', 'KDV', 'Net Tutar', 'Durum']
                self.export_service.export_to_excel(export_data, "Satış Faturaları", columns, filename)
                QMessageBox.information(self.view, "Başarılı", f"Excel dosyası oluşturuldu:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self.view, "Hata", f"Excel export hatası:\n{str(e)}")
    
    def on_export_csv(self):
        """CSV olarak export et"""
        try:
            data_to_export = self.view.filtered_list if hasattr(self.view, 'filtered_list') else self.all_fatura_data
            if not data_to_export:
                QMessageBox.warning(self.view, "Uyarı", "Export edilecek veri bulunamadı")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self.view, "CSV Olarak Kaydet", "faturalar.csv", "CSV Files (*.csv)"
            )
            if filename:
                export_data = []
                for fatura in data_to_export:
                    cari_hesap = fatura.get('cariHesap', {})
                    export_data.append({
                        'Fatura No': fatura.get('faturaNo', ''),
                        'Tarih': fatura.get('tarih', ''),
                        'Cari Hesap': cari_hesap.get('kodu', ''),
                        'Unvan': cari_hesap.get('unvani', ''),
                        'Toplam': float(fatura.get('toplam', 0) or 0),
                        'KDV': float(fatura.get('toplamKDV', 0) or 0),
                        'Net Tutar': float(fatura.get('netTutar', 0) or 0),
                        'Durum': fatura.get('durum', '')
                    })
                
                columns = ['Fatura No', 'Tarih', 'Cari Hesap', 'Unvan', 'Toplam', 'KDV', 'Net Tutar', 'Durum']
                self.export_service.export_to_csv(export_data, "Satış Faturaları", columns, filename)
                QMessageBox.information(self.view, "Başarılı", f"CSV dosyası oluşturuldu:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self.view, "Hata", f"CSV export hatası:\n{str(e)}")
    
    def on_gonder(self):
        """Fatura gönder - E-Fatura formatında PDF oluştur veya Email gönder"""
        try:
            # Gmail ayarlarını kontrol et (config'den veya env'den)
            from config import Config
            import os
            gmail_email = os.environ.get('GMAIL_EMAIL') or getattr(Config, 'GMAIL_EMAIL', '')
            gmail_password = os.environ.get('GMAIL_PASSWORD') or getattr(Config, 'GMAIL_PASSWORD', '')
            
            # Gmail ayarları yoksa sessizce devam et (soru sorma)
            # Kullanıcı isterse Ayarlar > Gmail Ayarları'ndan yapılandırabilir
            
            # Gönderilecek faturaları seçmek için dialog aç
            data_to_send = self.view.filtered_list if hasattr(self.view, 'filtered_list') else self.all_fatura_data
            
            if not data_to_send:
                QMessageBox.warning(self.view, "Uyarı", "Gönderilecek fatura bulunamadı")
                return
            
            # Fatura seçim dialog'u
            dialog = FaturaGonderDialog(data_to_send, self.view, gmail_email and gmail_password)
            if dialog.exec_() == QDialog.Accepted:
                selected_faturalar = dialog.get_selected_faturalar()
                send_method = dialog.get_send_method()  # 'pdf' veya 'email'
                
                if not selected_faturalar:
                    QMessageBox.warning(self.view, "Uyarı", "Lütfen en az bir fatura seçin")
                    return
                
                if send_method == 'email':
                    # Email gönder
                    self.send_fatura_by_email(selected_faturalar)
                else:
                    # PDF olarak kaydet
                    self.save_fatura_as_pdf(selected_faturalar)
        except Exception as e:
            QMessageBox.critical(self.view, "Hata", f"Fatura gönderme hatası:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def save_fatura_as_pdf(self, selected_faturalar):
        """Faturaları PDF olarak kaydet"""
        folder = QFileDialog.getExistingDirectory(
            self.view, "Faturaları Kaydet", ""
        )
        
        if folder:
            success_count = 0
            error_count = 0
            
            for fatura in selected_faturalar:
                try:
                    fatura_no = fatura.get('faturaNo', 'FATURA')
                    filename = os.path.join(folder, f"Fatura_{fatura_no}.pdf")
                    
                    # E-Fatura formatında PDF oluştur
                    self.fatura_pdf_service.generate_efatura_pdf(fatura, filename)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Fatura gönderme hatası ({fatura.get('faturaNo', 'Bilinmeyen')}): {e}")
            
            if success_count > 0:
                QMessageBox.information(
                    self.view, 
                    "Başarılı", 
                    f"{success_count} fatura başarıyla oluşturuldu!\n"
                    f"{'(' + str(error_count) + ' hata oluştu)' if error_count > 0 else ''}\n"
                    f"Konum: {folder}"
                )
            else:
                QMessageBox.critical(self.view, "Hata", "Hiçbir fatura oluşturulamadı")
    
    def send_fatura_by_email(self, selected_faturalar):
        """Faturaları email ile gönder"""
        try:
            import os
            import tempfile
            
            email_service = EmailService()
            
            success_count = 0
            error_count = 0
            
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
                    
                    # Alıcı email
                    to_email = cari_hesap.get('email', '')
                    if not to_email:
                        QMessageBox.warning(
                            self.view,
                            "Uyarı",
                            f"Fatura {fatura.get('faturaNo', '-')} için e-posta adresi bulunamadı.\n"
                            f"Cari hesap: {cari_hesap.get('unvani', '-')}"
                        )
                        error_count += 1
                        continue
                    
                    # Geçici PDF oluştur
                    temp_dir = tempfile.gettempdir()
                    fatura_no = fatura.get('faturaNo', 'FATURA')
                    pdf_path = os.path.join(temp_dir, f"Fatura_{fatura_no}.pdf")
                    
                    # PDF oluştur
                    self.fatura_pdf_service.generate_efatura_pdf(fatura, pdf_path)
                    
                    # Email gönder
                    email_service.send_fatura_email(to_email, fatura, pdf_path)
                    
                    # Geçici dosyayı sil
                    try:
                        os.remove(pdf_path)
                    except:
                        pass
                    
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Email gönderme hatası ({fatura.get('faturaNo', 'Bilinmeyen')}): {e}")
            
            if success_count > 0:
                QMessageBox.information(
                    self.view,
                    "Başarılı",
                    f"{success_count} fatura başarıyla e-posta ile gönderildi!\n"
                    f"{'(' + str(error_count) + ' hata oluştu)' if error_count > 0 else ''}"
                )
            else:
                QMessageBox.critical(self.view, "Hata", "Hiçbir fatura gönderilemedi")
        except Exception as e:
            QMessageBox.critical(self.view, "Hata", f"E-posta gönderme hatası:\n{str(e)}")
            import traceback
            traceback.print_exc()


class FaturaGonderDialog(QDialog):
    """Fatura gönderme dialog'u - Gönderilecek faturaları seç"""
    
    def __init__(self, faturalar, parent=None, email_enabled=False):
        super().__init__(parent)
        self.faturalar = faturalar
        self.filtered_faturalar = faturalar
        self.checkboxes = []
        self.email_enabled = email_enabled
        self.send_method = 'pdf'  # 'pdf' veya 'email'
        self.setWindowTitle("Fatura Gönder - Fatura Seçimi")
        self.setMinimumSize(900, 700)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title = QLabel("📧 Fatura Gönder - Fatura Seçimi")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #667eea; padding: 10px; background-color: white; border-radius: 5px;")
        layout.addWidget(title)
        
        # Arama ve filtreleme
        filter_group = QGroupBox("🔍 Arama ve Filtreleme")
        filter_layout = QVBoxLayout()
        
        search_layout = QHBoxLayout()
        search_label = QLabel("Ara:")
        search_label.setStyleSheet("font-weight: bold;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Fatura no, cari hesap, tarih veya tutar ile ara...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        filter_layout.addLayout(search_layout)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # İstatistikler
        stats_layout = QHBoxLayout()
        self.label_toplam = QLabel("Toplam: 0")
        self.label_toplam.setStyleSheet("font-weight: bold; color: #667eea; padding: 5px 15px; background-color: white; border-radius: 5px;")
        stats_layout.addWidget(self.label_toplam)
        
        self.label_secili = QLabel("Seçili: 0")
        self.label_secili.setStyleSheet("font-weight: bold; color: #28a745; padding: 5px 15px; background-color: white; border-radius: 5px;")
        stats_layout.addWidget(self.label_secili)
        
        self.label_tutar = QLabel("Toplam Tutar: 0.00 ₺")
        self.label_tutar.setStyleSheet("font-weight: bold; color: #dc3545; padding: 5px 15px; background-color: white; border-radius: 5px;")
        stats_layout.addWidget(self.label_tutar)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Tablo
        table_group = QGroupBox("📋 Faturalar")
        table_layout = QVBoxLayout()
        
        # Tümünü seç/seçme
        select_all_layout = QHBoxLayout()
        self.select_all_checkbox = QCheckBox("✅ Tümünü Seç")
        self.select_all_checkbox.setStyleSheet("font-weight: bold; font-size: 12px; padding: 5px;")
        self.select_all_checkbox.stateChanged.connect(self.on_select_all_changed)
        select_all_layout.addWidget(self.select_all_checkbox)
        select_all_layout.addStretch()
        table_layout.addLayout(select_all_layout)
        
        # Modern tablo
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["", "Fatura No", "Cari Hesap", "Tarih", "E-Posta", "Tutar"])
        
        # Tablo ayarları
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Checkbox
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Fatura No
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Cari Hesap
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Tarih
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # E-Posta
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Tutar
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
        """)
        
        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Gönderme yöntemi seçimi
        if self.email_enabled:
            method_group = QGroupBox("📤 Gönderme Yöntemi")
            method_layout = QHBoxLayout()
            
            self.method_group = QButtonGroup()
            
            self.method_pdf = QRadioButton("📄 PDF olarak kaydet")
            self.method_pdf.setChecked(True)
            self.method_pdf.setStyleSheet("font-size: 12px; padding: 5px;")
            self.method_group.addButton(self.method_pdf, 0)
            method_layout.addWidget(self.method_pdf)
            
            self.method_email = QRadioButton("📧 E-posta ile gönder")
            self.method_email.setStyleSheet("font-size: 12px; padding: 5px;")
            self.method_group.addButton(self.method_email, 1)
            method_layout.addWidget(self.method_email)
            
            method_layout.addStretch()
            
            # Radio button değişikliklerini dinle
            self.method_pdf.toggled.connect(lambda checked: setattr(self, 'send_method', 'pdf') if checked else None)
            self.method_email.toggled.connect(lambda checked: setattr(self, 'send_method', 'email') if checked else None)
            
            method_group.setLayout(method_layout)
            layout.addWidget(method_group)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_iptal = QPushButton("❌ İptal")
        btn_iptal.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 10px 25px;
                font-weight: bold;
                font-size: 13px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        btn_iptal.clicked.connect(self.reject)
        button_layout.addWidget(btn_iptal)
        
        btn_gonder = QPushButton("✅ Gönder")
        btn_gonder.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 10px 30px;
                font-weight: bold;
                font-size: 13px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        btn_gonder.clicked.connect(self.accept)
        button_layout.addWidget(btn_gonder)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Veriyi yükle
        self.load_data()
    
    def load_data(self):
        """Veriyi tabloya yükle"""
        self.update_table()
    
    def update_table(self):
        """Tabloyu güncelle"""
        self.table.setRowCount(0)
        self.checkboxes = []
        
        was_sorting_enabled = self.table.isSortingEnabled()
        self.table.setSortingEnabled(False)
        
        for fatura in self.filtered_faturalar:
            cari_hesap = fatura.get('cariHesap', {})
            if isinstance(cari_hesap, str):
                import json
                try:
                    cari_hesap = json.loads(cari_hesap)
                except:
                    cari_hesap = {}
            
            fatura_no = fatura.get('faturaNo', '-')
            unvan = cari_hesap.get('unvani', '-')
            tarih = fatura.get('tarih', '-')
            toplam = float(fatura.get('toplam', 0) or 0)
            email = cari_hesap.get('email', '-')
            
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.update_statistics)
            self.table.setCellWidget(row, 0, checkbox)
            self.checkboxes.append((checkbox, fatura))
            
            # Fatura No
            self.table.setItem(row, 1, QTableWidgetItem(str(fatura_no)))
            
            # Cari Hesap
            self.table.setItem(row, 2, QTableWidgetItem(str(unvan)))
            
            # Tarih
            self.table.setItem(row, 3, QTableWidgetItem(str(tarih)))
            
            # E-Posta
            email_item = QTableWidgetItem(str(email))
            if email == '-' or not email or '@' not in str(email):
                email_item.setForeground(QColor(220, 53, 69))
            else:
                email_item.setForeground(QColor(40, 167, 69))
            self.table.setItem(row, 4, email_item)
            
            # Tutar
            tutar_item = QTableWidgetItem(f"{toplam:.2f} ₺")
            tutar_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 5, tutar_item)
        
        if was_sorting_enabled:
            self.table.setSortingEnabled(True)
        
        self.update_statistics()
    
    def on_search_changed(self, text):
        """Arama metni değiştiğinde"""
        query = text.lower().strip()
        if not query:
            self.filtered_faturalar = self.faturalar
        else:
            self.filtered_faturalar = []
            for fatura in self.faturalar:
                cari_hesap = fatura.get('cariHesap', {})
                if isinstance(cari_hesap, str):
                    import json
                    try:
                        cari_hesap = json.loads(cari_hesap)
                    except:
                        cari_hesap = {}
                
                fatura_no = str(fatura.get('faturaNo', '')).lower()
                unvan = str(cari_hesap.get('unvani', '')).lower()
                tarih = str(fatura.get('tarih', '')).lower()
                toplam = str(fatura.get('toplam', '')).lower()
                email = str(cari_hesap.get('email', '')).lower()
                
                if (query in fatura_no or query in unvan or 
                    query in tarih or query in toplam or query in email):
                    self.filtered_faturalar.append(fatura)
        
        self.update_table()
    
    def update_statistics(self):
        """İstatistikleri güncelle"""
        total = len(self.filtered_faturalar)
        selected = len(self.get_selected_faturalar())
        
        selected_faturalar = self.get_selected_faturalar()
        toplam_tutar = sum(float(f.get('toplam', 0) or 0) for f in selected_faturalar)
        
        self.label_toplam.setText(f"Toplam: {total}")
        self.label_secili.setText(f"Seçili: {selected}")
        self.label_tutar.setText(f"Toplam Tutar: {toplam_tutar:.2f} ₺")
    
    def on_select_all_changed(self, state):
        """Tümünü seç/seçme"""
        checked = state == 2
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(checked)
        self.update_statistics()
    
    def on_select_all_changed(self, state):
        """Tümünü seç/seçme"""
        checked = state == 2  # Qt.Checked = 2
        for checkbox, _ in self.checkboxes:
            checkbox.setChecked(checked)
    
    def get_selected_faturalar(self):
        """Seçili faturaları döndür"""
        selected = []
        for checkbox, fatura in self.checkboxes:
            if checkbox.isChecked():
                selected.append(fatura)
        return selected
        """Seçili faturaları döndür"""
        selected = []
        for checkbox, fatura in self.checkboxes:
            if checkbox.isChecked():
                selected.append(fatura)
        return selected
    
    def get_send_method(self):
        """Gönderme yöntemini döndür"""
        if self.email_enabled:
            if self.method_email.isChecked():
                return 'email'
        return 'pdf'

