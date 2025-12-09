"""
Fatura Gönder View - Fatura gönderme ekranı
E-posta ile fatura gönderme işlemleri (MUBA teması)
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLineEdit, QCheckBox, QGroupBox, QRadioButton, QButtonGroup,
    QDateEdit, QComboBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
from datetime import datetime


class FaturaGonderView(QWidget):
    """Fatura gönderme görünümü - View katmanı"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.fatura_list = []
        self.filtered_list = []
        self._init_colors()
        self.init_ui()

    def _init_colors(self):
        self.color_bg = "#f5f6fb"
        self.color_card = "#ffffff"
        self.color_border = "#d0d4f2"
        self.color_primary = "#233568"
        self.color_primary_dark = "#0f112b"
        self.color_accent = "#f48c06"
        self.color_success = "#16a34a"
        self.color_text = "#1e2a4c"
        self.color_muted = "#666a87"

    def _tint(self, hex_color, factor):
        """Hex rengi parlaklaştır/koyulaştır"""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def init_ui(self):
        """UI'yi başlat"""
        self.setStyleSheet(f"""
            QWidget {{
                background: {self.color_bg};
            }}
            QGroupBox {{
                background: {self.color_card};
                border: 1px solid {self.color_border};
                border-radius: 4px;
                margin-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 6px;
                color: {self.color_text};
                font-weight: 700;
            }}
            QLineEdit, QComboBox, QDateEdit {{
                border: 1px solid {self.color_border};
                border-radius: 4px;
                padding: 8px 10px;
                font-size: 13px;
                background: #ffffff;
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
                border: 1px solid {self.color_primary};
            }}
            QTableWidget {{
                background: #ffffff;
                alternate-background-color: #f5f6fb;
                border: none;
            }}
            QHeaderView::section {{
                background: #f3f4ff;
                padding: 6px;
                border: none;
                border-bottom: 1px solid {self.color_border};
                color: {self.color_text};
                font-weight: 600;
                font-size: 12px;
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        def style_btn(btn, bg, fg="#ffffff"):
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {bg};
                    color: {fg};
                    border: none;
                    padding: 9px 14px;
                    font-weight: 700;
                    border-radius: 4px;
                }}
                QPushButton:hover {{ background: {self._tint(bg, 1.07)}; }}
                QPushButton:pressed {{ background: {self._tint(bg, 0.9)}; }}
            """)

        # Başlık
        title = QLabel("Fatura Gönder - E-Posta ile Gönderim")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {self.color_primary_dark}; margin-bottom: 8px;")
        layout.addWidget(title)

        # Bilgi kutusu - Daha kompakt
        info_group = QGroupBox("Bilgi")
        info_layout = QHBoxLayout()
        info_text = QLabel(
            "📧 Faturalar <b>dariyeribilal3@gmail.com</b> adresinden gönderilecektir | "
            "Gönderilecek faturaları seçin | Cari hesabın e-posta adresi kayıtlı olmalıdır"
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet(f"color: {self.color_muted}; padding: 5px; font-size: 11px;")
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Üst toolbar
        toolbar = QHBoxLayout()

        # Geri butonu
        self.btn_geri = QPushButton("← Geri")
        style_btn(self.btn_geri, self.color_primary)
        toolbar.addWidget(self.btn_geri)

        toolbar.addStretch()

        # Yenile butonu
        self.btn_yenile = QPushButton("Yenile")
        style_btn(self.btn_yenile, self.color_accent, "#0f112b")
        toolbar.addWidget(self.btn_yenile)

        layout.addLayout(toolbar)

        # Filtreler ve Arama
        filter_group = QGroupBox("Filtreler ve Arama")
        filter_layout = QVBoxLayout()

        # Üst satır: Hızlı filtreler ve arama
        top_row = QHBoxLayout()

        # Hızlı filtreler
        quick_filter_label = QLabel("Hızlı Filtreler:")
        quick_filter_label.setStyleSheet(f"font-weight: 700; color: {self.color_text};")
        top_row.addWidget(quick_filter_label)

        quick_btn_style = f"padding: 5px 10px; font-size: 11px; border: 1px solid {self.color_border}; border-radius: 4px;"

        self.btn_bugun = QPushButton("Bugün")
        self.btn_bugun.setCheckable(True)
        self.btn_bugun.setStyleSheet(quick_btn_style)
        top_row.addWidget(self.btn_bugun)

        self.btn_bu_hafta = QPushButton("Bu Hafta")
        self.btn_bu_hafta.setCheckable(True)
        self.btn_bu_hafta.setStyleSheet(quick_btn_style)
        top_row.addWidget(self.btn_bu_hafta)

        self.btn_bu_ay = QPushButton("Bu Ay")
        self.btn_bu_ay.setCheckable(True)
        self.btn_bu_ay.setStyleSheet(quick_btn_style)
        top_row.addWidget(self.btn_bu_ay)

        self.btn_son_30_gun = QPushButton("Son 30 Gün")
        self.btn_son_30_gun.setCheckable(True)
        self.btn_son_30_gun.setStyleSheet(quick_btn_style)
        top_row.addWidget(self.btn_son_30_gun)

        top_row.addStretch()

        # Arama
        search_label = QLabel("Ara:")
        search_label.setStyleSheet(f"font-weight: 700; color: {self.color_text};")
        top_row.addWidget(search_label)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Fatura no, cari hesap, tarih...")
        self.search_input.setMinimumWidth(250)
        top_row.addWidget(self.search_input)

        filter_layout.addLayout(top_row)

        # Alt satır: Tarih aralığı ve cari hesap filtresi
        bottom_row = QHBoxLayout()

        bottom_row.addWidget(QLabel("Tarih Aralığı:"))
        self.date_baslangic = QDateEdit()
        self.date_baslangic.setDate(QDate.currentDate().addDays(-30))
        self.date_baslangic.setCalendarPopup(True)
        self.date_baslangic.setDisplayFormat("dd.MM.yyyy")
        bottom_row.addWidget(self.date_baslangic)

        bottom_row.addWidget(QLabel("-"))
        self.date_bitis = QDateEdit()
        self.date_bitis.setDate(QDate.currentDate())
        self.date_bitis.setCalendarPopup(True)
        self.date_bitis.setDisplayFormat("dd.MM.yyyy")
        bottom_row.addWidget(self.date_bitis)

        bottom_row.addWidget(QLabel("Cari Hesap:"))
        self.combo_cari = QComboBox()
        self.combo_cari.setMinimumWidth(200)
        self.combo_cari.addItem("Tümü", None)
        bottom_row.addWidget(self.combo_cari)

        bottom_row.addWidget(QLabel("Durum:"))
        self.combo_durum = QComboBox()
        self.combo_durum.addItems(["Tümü", "Açık", "Kapalı", "İptal"])
        bottom_row.addWidget(self.combo_durum)

        self.btn_filtrele = QPushButton("Filtrele")
        style_btn(self.btn_filtrele, self.color_primary)
        bottom_row.addWidget(self.btn_filtrele)

        self.btn_temizle = QPushButton("Temizle")
        style_btn(self.btn_temizle, self.color_muted)
        bottom_row.addWidget(self.btn_temizle)

        bottom_row.addStretch()

        filter_layout.addLayout(bottom_row)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Hızlı filtre butonlarına callback ekle
        self.btn_bugun.clicked.connect(lambda: self.on_quick_filter('bugun'))
        self.btn_bu_hafta.clicked.connect(lambda: self.on_quick_filter('bu_hafta'))
        self.btn_bu_ay.clicked.connect(lambda: self.on_quick_filter('bu_ay'))
        self.btn_son_30_gun.clicked.connect(lambda: self.on_quick_filter('son_30_gun'))

        # Gönderme yöntemi ve istatistikler - Yan yana
        method_stats_layout = QHBoxLayout()

        # Gönderme yöntemi seçimi
        method_group = QGroupBox("Gönderme Yöntemi")
        method_layout = QHBoxLayout()

        self.method_group = QButtonGroup()

        self.method_email = QRadioButton("📧 E-posta ile gönder")
        self.method_email.setChecked(True)
        self.method_group.addButton(self.method_email, 0)
        method_layout.addWidget(self.method_email)

        self.method_pdf = QRadioButton("📄 PDF olarak kaydet")
        self.method_group.addButton(self.method_pdf, 1)
        method_layout.addWidget(self.method_pdf)

        method_layout.addStretch()
        method_group.setLayout(method_layout)
        method_stats_layout.addWidget(method_group)

        # İstatistikler paneli
        stats_group = QGroupBox("İstatistikler")
        stats_layout = QHBoxLayout()

        self.label_toplam = QLabel("Toplam: 0")
        self.label_toplam.setStyleSheet(f"font-weight: bold; color: {self.color_primary};")
        stats_layout.addWidget(self.label_toplam)

        self.label_secili = QLabel("Seçili: 0")
        self.label_secili.setStyleSheet(f"font-weight: bold; color: {self.color_success};")
        stats_layout.addWidget(self.label_secili)

        self.label_tutar = QLabel("Toplam Tutar: 0.00 TL")
        self.label_tutar.setStyleSheet(f"font-weight: bold; color: {self.color_accent}; font-size: 12px;")
        stats_layout.addWidget(self.label_tutar)

        stats_layout.addStretch()
        stats_group.setLayout(stats_layout)
        method_stats_layout.addWidget(stats_group)

        layout.addLayout(method_stats_layout)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "", "Fatura No", "Tarih", "Cari Hesap", "Unvan",
            "E-Posta", "Durum", "Toplam", "KDV", "Net Tutar"
        ])

        # Tablo ayarları
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Checkbox
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Fatura No
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Tarih
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Cari Hesap
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Unvan
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # E-Posta
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Durum
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Toplam
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # KDV
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Net Tutar

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)  # Sıralama aktif

        layout.addWidget(self.table)

        # Alt toolbar
        bottom_toolbar = QHBoxLayout()

        # Tümünü seç/seçme
        self.select_all_checkbox = QCheckBox("Tümünü Seç")
        self.select_all_checkbox.stateChanged.connect(self.on_select_all_changed)
        bottom_toolbar.addWidget(self.select_all_checkbox)

        # E-posta olanları seç
        btn_email_olanlar = QPushButton("E-Posta Olanları Seç")
        style_btn(btn_email_olanlar, self.color_primary)
        btn_email_olanlar.clicked.connect(self.on_select_with_email)
        bottom_toolbar.addWidget(btn_email_olanlar)

        # E-posta olmayanları seç
        btn_email_olmayanlar = QPushButton("E-Posta Olmayanları Seç")
        style_btn(btn_email_olmayanlar, self.color_accent, "#0f112b")
        btn_email_olmayanlar.clicked.connect(self.on_select_without_email)
        bottom_toolbar.addWidget(btn_email_olmayanlar)

        bottom_toolbar.addStretch()

        # Gönder butonu
        self.btn_gonder = QPushButton("E-Posta Gönder")
        style_btn(self.btn_gonder, self.color_success)
        bottom_toolbar.addWidget(self.btn_gonder)

        layout.addLayout(bottom_toolbar)

        # Cari hesapları yükle
        self.load_cari_hesaplar()

        self.setLayout(layout)

    def display_data(self, fatura_list):
        """Veriyi tabloda göster"""
        if fatura_list is None:
            fatura_list = []
        self.fatura_list = fatura_list
        self.filtered_list = fatura_list
        self._update_table()

    def _update_table(self):
        """Tabloyu güncelle"""
        if not hasattr(self, 'filtered_list') or self.filtered_list is None:
            self.filtered_list = []

        was_sorting_enabled = self.table.isSortingEnabled()
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.filtered_list))

        for row, fatura in enumerate(self.filtered_list):
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(lambda state, r=row: self.update_statistics())
            self.table.setCellWidget(row, 0, checkbox)

            self.table.setItem(row, 1, QTableWidgetItem(str(fatura.get('faturaNo', '-'))))
            self.table.setItem(row, 2, QTableWidgetItem(str(fatura.get('tarih', '-'))))

            cari_hesap = fatura.get('cariHesap', {})
            if not isinstance(cari_hesap, dict):
                import json
                try:
                    cari_hesap = json.loads(cari_hesap) if isinstance(cari_hesap, str) else {}
                except Exception:
                    cari_hesap = {}

            self.table.setItem(row, 3, QTableWidgetItem(str(cari_hesap.get('kodu', '-'))))
            self.table.setItem(row, 4, QTableWidgetItem(str(cari_hesap.get('unvani', '-'))))

            email = cari_hesap.get('email', '')
            if not email or email == '-' or '@' not in str(email):
                cari_id = fatura.get('cariId', '')
                if cari_id:
                    try:
                        from models.cari_hesap_model import CariHesapModel
                        cari_model = CariHesapModel()
                        cari_data = cari_model.get_by_id(cari_id)
                        if cari_data:
                            email = cari_data.get('email', '')
                            if not email:
                                iletisim = cari_data.get('iletisim', {})
                                if isinstance(iletisim, str):
                                    import json
                                    try:
                                        iletisim = json.loads(iletisim)
                                    except Exception:
                                        iletisim = {}
                                email = iletisim.get('email', '') if isinstance(iletisim, dict) else ''
                    except Exception as e:
                        print(f"Cari hesap email çekme hatası: {e}")
                        email = ''

            if not email:
                email = '-'

            email_item = QTableWidgetItem(str(email))
            if email == '-' or not email or '@' not in str(email):
                email_item.setForeground(QColor(220, 53, 69))
            else:
                email_item.setForeground(QColor(40, 167, 69))
            self.table.setItem(row, 5, email_item)

            durum = fatura.get('durum', 'Açık')
            durum_item = QTableWidgetItem(durum)
            if durum == 'Açık':
                durum_item.setForeground(QColor(40, 167, 69))
            elif durum == 'Kapalı':
                durum_item.setForeground(QColor(108, 117, 125))
            elif durum == 'İptal':
                durum_item.setForeground(QColor(220, 53, 69))
            self.table.setItem(row, 6, durum_item)

            toplam = float(fatura.get('toplam', 0) or 0)
            toplam_kdv = float(fatura.get('toplamKDV', 0) or 0)
            net_tutar = float(fatura.get('netTutar', 0) or 0)

            toplam_item = QTableWidgetItem(f"{toplam:.2f} TL")
            toplam_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 7, toplam_item)

            kdv_item = QTableWidgetItem(f"{toplam_kdv:.2f} TL")
            kdv_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 8, kdv_item)

            net_item = QTableWidgetItem(f"{net_tutar:.2f} TL")
            net_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            net_item.setFont(QFont("", -1, QFont.Bold))
            self.table.setItem(row, 9, net_item)

        if was_sorting_enabled:
            self.table.setSortingEnabled(True)

        self.update_statistics()

    def on_search_changed(self, text):
        """Arama metni değiştiğinde"""
        if hasattr(self, '_search_callback'):
            self._search_callback(text)

    def load_cari_hesaplar(self):
        """Cari hesapları combo box'a yükle"""
        try:
            from models.cari_hesap_model import CariHesapModel
            model = CariHesapModel()
            cari_list = model.get_all()

            self.combo_cari.clear()
            self.combo_cari.addItem("Tümü", None)

            for cari in cari_list:
                display_text = f"{cari.get('unvani', '')} ({cari.get('vergiNo', '')[:6]}...)"
                self.combo_cari.addItem(display_text, cari.get('id'))
        except Exception as e:
            print(f"Cari hesaplar yüklenirken hata: {e}")

    def on_quick_filter(self, filter_type):
        """Hızlı filtre uygula"""
        today = QDate.currentDate()

        self.btn_bugun.setChecked(False)
        self.btn_bu_hafta.setChecked(False)
        self.btn_bu_ay.setChecked(False)
        self.btn_son_30_gun.setChecked(False)

        if filter_type == 'bugun':
            self.btn_bugun.setChecked(True)
            self.date_baslangic.setDate(today)
            self.date_bitis.setDate(today)
        elif filter_type == 'bu_hafta':
            self.btn_bu_hafta.setChecked(True)
            days_since_monday = today.dayOfWeek() - 1
            if days_since_monday == -1:
                days_since_monday = 6
            self.date_baslangic.setDate(today.addDays(-days_since_monday))
            self.date_bitis.setDate(today)
        elif filter_type == 'bu_ay':
            self.btn_bu_ay.setChecked(True)
            self.date_baslangic.setDate(QDate(today.year(), today.month(), 1))
            self.date_bitis.setDate(today)
        elif filter_type == 'son_30_gun':
            self.btn_son_30_gun.setChecked(True)
            self.date_baslangic.setDate(today.addDays(-30))
            self.date_bitis.setDate(today)

        if hasattr(self, '_filter_callback') and self._filter_callback:
            self._filter_callback()

    def on_filtrele(self):
        """Filtrele butonuna tıklandığında"""
        if hasattr(self, '_filter_callback'):
            self._filter_callback()

    def on_temizle(self):
        """Temizle butonuna tıklandığında"""
        self.date_baslangic.setDate(QDate.currentDate().addDays(-30))
        self.date_bitis.setDate(QDate.currentDate())
        self.combo_cari.setCurrentIndex(0)
        self.combo_durum.setCurrentIndex(0)
        self.search_input.clear()

        self.btn_bugun.setChecked(False)
        self.btn_bu_hafta.setChecked(False)
        self.btn_bu_ay.setChecked(False)
        self.btn_son_30_gun.setChecked(False)

        if hasattr(self, '_filter_callback'):
            self._filter_callback()

    def get_filters(self):
        """Seçili filtreleri döndür"""
        cari_id = self.combo_cari.currentData()
        baslangic = self.date_baslangic.date().toString("yyyy-MM-dd")
        bitis = self.date_bitis.date().toString("yyyy-MM-dd")
        durum = self.combo_durum.currentText()
        if durum == "Tümü":
            durum = None

        return {
            'cari_id': cari_id,
            'baslangic_tarih': baslangic,
            'bitis_tarih': bitis,
            'durum': durum,
            'search': self.search_input.text().strip()
        }

    def on_select_all_changed(self, state):
        """Tümünü seç/seçme"""
        checked = state == 2  # Qt.Checked = 2
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(checked)
        self.update_statistics()

    def on_select_with_email(self):
        """E-posta adresi olan faturaları seç"""
        for row in range(self.table.rowCount()):
            email_item = self.table.item(row, 5)
            checkbox = self.table.cellWidget(row, 0)
            if email_item and checkbox:
                email = email_item.text()
                if email and email != '-' and '@' in email:
                    checkbox.setChecked(True)
                else:
                    checkbox.setChecked(False)
        self.update_statistics()

    def on_select_without_email(self):
        """E-posta adresi olmayan faturaları seç"""
        for row in range(self.table.rowCount()):
            email_item = self.table.item(row, 5)
            checkbox = self.table.cellWidget(row, 0)
            if email_item and checkbox:
                email = email_item.text()
                if not email or email == '-' or '@' not in email:
                    checkbox.setChecked(True)
                else:
                    checkbox.setChecked(False)
        self.update_statistics()

    def update_statistics(self):
        """İstatistikleri güncelle"""
        total = len(self.filtered_list)
        selected = len(self.get_selected_faturalar())
        selected_faturalar = self.get_selected_faturalar()
        toplam_tutar = sum(float(f.get('netTutar', 0) or 0) for f in selected_faturalar)

        self.label_toplam.setText(f"Toplam: {total}")
        self.label_secili.setText(f"Seçili: {selected}")
        self.label_tutar.setText(f"Toplam Tutar: {toplam_tutar:.2f} TL")

    def get_selected_faturalar(self):
        """Seçili faturaları döndür"""
        selected = []
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                if row < len(self.filtered_list):
                    selected.append(self.filtered_list[row])
        return selected

    def get_send_method(self):
        """Gönderme yöntemini döndür"""
        if self.method_email.isChecked():
            return 'email'
        return 'pdf'

    def filter_data(self, filtered_list):
        """Filtrelenmiş veriyi göster"""
        self.filtered_list = filtered_list
        self._update_table()

    def show_error(self, message):
        """Hata mesajı göster"""
        QMessageBox.critical(self, "Hata", message)

    def show_success(self, message):
        """Başarı mesajı göster"""
        QMessageBox.information(self, "Başarılı", message)

    def set_callbacks(self, on_geri, on_yenile, on_gonder, on_search=None, on_filter=None):
        """Callback'leri ayarla"""
        self.btn_geri.clicked.connect(on_geri)
        self.btn_yenile.clicked.connect(on_yenile)
        self.btn_gonder.clicked.connect(on_gonder)
        if on_search:
            self.search_input.textChanged.connect(on_search)
            self._search_callback = on_search
        if on_filter:
            self._filter_callback = on_filter
            if hasattr(self, 'btn_filtrele'):
                self.btn_filtrele.clicked.connect(self.on_filtrele)
            if hasattr(self, 'btn_temizle'):
                self.btn_temizle.clicked.connect(self.on_temizle)
