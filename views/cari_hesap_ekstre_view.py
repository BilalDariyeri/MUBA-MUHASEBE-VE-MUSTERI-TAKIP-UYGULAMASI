"""
Cari Hesap Ekstre View - MUBA teması
"""
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QDateEdit, QComboBox, QLineEdit, QMessageBox, QDialog,
    QTextEdit, QDialogButtonBox, QFrame
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QFontDatabase, QColor


class CariHesapEkstreView(QWidget):
    """Cari hesap ekstre görünümü - MUBA teması"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_hareketler = []
        self.current_ozet = {}
        self._load_brand_fonts()
        self._init_colors()
        self.init_ui()
        
    def _init_colors(self):
        self.color_bg = "#e7e3ff"
        self.color_card = "#ffffff"
        self.color_border = "#d0d4f2"
        self.color_primary = "#233568"
        self.color_primary_dark = "#0f112b"
        self.color_accent = "#f48c06"
        self.color_text = "#1e2a4c"
        self.color_muted = "#666a87"
        self.color_success = "#10b981"
        self.color_danger = "#ef4444"
    
    def _load_brand_fonts(self):
        fonts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo", "fonts")
        if not os.path.isdir(fonts_dir):
            return
        for file in os.listdir(fonts_dir):
            if file.lower().endswith((".otf", ".ttf")):
                try:
                    QFontDatabase.addApplicationFont(os.path.join(fonts_dir, file))
                except Exception:
                    pass
    
    def _brand_font(self, size=13, weight=QFont.Normal, bold=False):
        font = QFont("SF Pro Display", pointSize=size, weight=weight)
        font.setBold(bold)
        return font

    @staticmethod
    def _adjust_color(hex_color, factor=1.08):
        """Hover/pressed durumları için tonu ayarla"""
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    def init_ui(self):
        """UI'yi başlat"""
        self.setStyleSheet(f"background: {self.color_bg};")
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)
        
        # Başlık ve geri
        header_layout = QHBoxLayout()
        self.btn_geri = QPushButton("Geri")
        self._style_primary(self.btn_geri, self.color_primary_dark)
        header_layout.addWidget(self.btn_geri)
        
        title = QLabel("Cari Hesap Ekstresi")
        title.setFont(self._brand_font(size=18, bold=True))
        title.setStyleSheet(f"color: {self.color_text};")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Filtre kartı
        filter_card = QFrame()
        filter_card.setStyleSheet(f"""
            QFrame {{
                background: {self.color_card};
                border: 1px solid {self.color_border};
                border-radius: 8px;
            }}
        """)
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(12, 10, 12, 10)
        filter_layout.setSpacing(10)
        
        filter_layout.addWidget(self._make_label("Cari Hesap:"))
        self.combo_cari = QComboBox()
        self.combo_cari.setMinimumWidth(220)
        self.combo_cari.addItem("Tümü", None)
        self.combo_cari.setStyleSheet(self._combo_style())
        filter_layout.addWidget(self.combo_cari)
        
        filter_layout.addWidget(self._make_label("Başlangıç:"))
        self.date_baslangic = QDateEdit()
        self.date_baslangic.setDate(QDate.currentDate().addDays(-30))
        self.date_baslangic.setCalendarPopup(True)
        self.date_baslangic.setDisplayFormat("dd.MM.yyyy")
        self.date_baslangic.setStyleSheet(self._date_style())
        filter_layout.addWidget(self.date_baslangic)
        
        filter_layout.addWidget(self._make_label("Bitiş:"))
        self.date_bitis = QDateEdit()
        self.date_bitis.setDate(QDate.currentDate())
        self.date_bitis.setCalendarPopup(True)
        self.date_bitis.setDisplayFormat("dd.MM.yyyy")
        self.date_bitis.setStyleSheet(self._date_style())
        filter_layout.addWidget(self.date_bitis)
        
        self.btn_yenile = QPushButton("Yenile")
        self._style_primary(self.btn_yenile, self.color_accent, dark_text=True)
        filter_layout.addWidget(self.btn_yenile)
        
        layout.addWidget(filter_card)
        
        # Özet bilgiler
        summary_group = QGroupBox("Özet Bilgiler")
        summary_group.setStyleSheet(self._group_style())
        summary_layout = QHBoxLayout(summary_group)
        summary_layout.setContentsMargins(12, 14, 12, 14)
        summary_layout.setSpacing(12)
        
        self.label_toplam_borc = self._create_summary_chip("Toplam Borç", "0.00 ₺", self.color_danger)
        self.label_toplam_alacak = self._create_summary_chip("Toplam Alacak", "0.00 ₺", self.color_success)
        self.label_son_bakiye = self._create_summary_chip("Son Bakiye", "0.00 ₺", self.color_primary)
        
        summary_layout.addWidget(self.label_toplam_borc)
        summary_layout.addWidget(self.label_toplam_alacak)
        summary_layout.addWidget(self.label_son_bakiye)
        summary_layout.addStretch()
        
        layout.addWidget(summary_group)
        
        # Ekstre tablosu kartı
        table_card = QFrame()
        table_card.setStyleSheet(f"""
            QFrame {{
                background: {self.color_card};
                border: 1px solid {self.color_border};
                border-radius: 8px;
            }}
        """)
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(12, 12, 12, 12)
        
        table_label = QLabel("Ekstre Hareketleri")
        table_label.setFont(self._brand_font(size=12, bold=True))
        table_label.setStyleSheet(f"color: {self.color_text};")
        table_layout.addWidget(table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Tarih", "Belge No", "Açıklama", "Alacak (Gelir)", 
            "Borç (Gider)", "Bakiye", "Vade Tarihi", "Detay"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.on_double_click)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: #ffffff;
                alternate-background-color: #f5f6fb;
                border: none;
            }}
            QHeaderView::section {{
                background: #f5f6fb;
                padding: 6px;
                border: none;
                border-bottom: 1px solid {self.color_border};
                color: {self.color_muted};
                font-weight: 600;
                font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
            QTableWidget::item:selected {{
                background: #dfe1ff;
                color: {self.color_primary_dark};
            }}
        """)
        table_layout.addWidget(self.table)
        
        layout.addWidget(table_card)
        
        # Alt butonlar
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.btn_yazdir = QPushButton("Yazdır")
        self._style_secondary(self.btn_yazdir, "#6b7280")
        self.btn_excel = QPushButton("Excel'e Aktar")
        self._style_secondary(self.btn_excel, "#059669")
        self.btn_mail = QPushButton("E-Posta Gönder")
        self._style_secondary(self.btn_mail, "#0ea5e9")
        
        button_layout.addWidget(self.btn_yazdir)
        button_layout.addWidget(self.btn_excel)
        button_layout.addWidget(self.btn_mail)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Callback placeholder
        self._tamam_callback = None
        self._kapat_callback = None
        
        # Cari hesapları yükle
        self.load_cari_hesaplar()
    
    def _style_primary(self, btn, bg, dark_text=False):
        text_color = "#0f112b" if dark_text else "#ffffff"
        btn.setMinimumHeight(36)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text_color};
                font-weight: 700;
                border: none;
                border-radius: 6px;
                padding: 8px 14px;
            }}
            QPushButton:hover {{ background-color: {self._adjust_color(bg, 1.08)}; }}
            QPushButton:pressed {{ background-color: {self._adjust_color(bg, 0.9)}; }}
        """)
    
    def _style_secondary(self, btn, bg):
        btn.setMinimumHeight(34)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: #ffffff;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
            }}
            QPushButton:hover {{ background-color: {self._adjust_color(bg, 1.08)}; }}
            QPushButton:pressed {{ background-color: {self._adjust_color(bg, 0.9)}; }}
        """)
    
    def _group_style(self):
        return f"""
            QGroupBox {{
                background-color: {self.color_card};
                border: 1px solid {self.color_border};
                border-radius: 8px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 6px;
                color: {self.color_text};
                font-weight: 600;
            }}
        """
    
    def _make_label(self, text):
        lbl = QLabel(text)
        lbl.setFont(self._brand_font(size=12, bold=True))
        lbl.setStyleSheet(f"color: {self.color_text};")
        return lbl
    
    def _combo_style(self):
        return f"""
            QComboBox {{
                padding: 8px;
                border: 1px solid {self.color_border};
                border-radius: 6px;
                font-size: 13px;
                min-width: 160px;
            }}
            QComboBox:focus {{
                border: 1px solid {self.color_primary};
            }}
        """
    
    def _date_style(self):
        return f"""
            QDateEdit {{
                padding: 8px;
                border: 1px solid {self.color_border};
                border-radius: 6px;
                font-size: 13px;
                min-width: 120px;
            }}
            QDateEdit:focus {{
                border: 1px solid {self.color_primary};
            }}
        """
    
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
    
    def display_ekstre(self, hareketler, ozet):
        """Ekstre hareketlerini göster"""
        self.current_hareketler = hareketler or []
        self.current_ozet = ozet or {}
        
        self.table.setRowCount(len(self.current_hareketler))
        
        for row, hareket in enumerate(self.current_hareketler):
            self.table.setItem(row, 0, QTableWidgetItem(hareket.get('tarih', '')))
            self.table.setItem(row, 1, QTableWidgetItem(hareket.get('belge_no', '')))
            
            aciklama = hareket.get('aciklama', '')
            if hareket.get('hareket_turu'):
                aciklama += f" ({hareket.get('hareket_turu')})"
            self.table.setItem(row, 2, QTableWidgetItem(aciklama))
            
            borc = hareket.get('borc', 0)
            alacak = hareket.get('alacak', 0)
            bakiye = hareket.get('bakiye', 0)
            
            # Yer değiştir: Alacak 3. sütuna, Borç 4. sütuna
            alacak_item = QTableWidgetItem(f"{alacak:.2f} ₺")
            alacak_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if alacak > 0:
                alacak_item.setForeground(QColor(40, 167, 69))
            self.table.setItem(row, 3, alacak_item)
            
            borc_item = QTableWidgetItem(f"{borc:.2f} ₺")
            borc_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if borc > 0:
                borc_item.setForeground(QColor(220, 53, 69))
            self.table.setItem(row, 4, borc_item)
            
            bakiye_item = QTableWidgetItem(f"{bakiye:.2f} ₺")
            bakiye_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if bakiye > 0:
                bakiye_item.setForeground(QColor(220, 53, 69))
            elif bakiye < 0:
                bakiye_item.setForeground(QColor(40, 167, 69))
            self.table.setItem(row, 5, bakiye_item)
            
            vade_tarih = hareket.get('vade_tarihi', '') or '-'
            self.table.setItem(row, 6, QTableWidgetItem(vade_tarih))
            
            detay_btn = QPushButton("Detay")
            self._style_secondary(detay_btn, self.color_primary)
            detay_btn.clicked.connect(lambda checked, r=row: self.show_detay(r))
            self.table.setCellWidget(row, 7, detay_btn)
        
        # Özet bilgileri güncelle
        self.label_toplam_borc.findChild(QLabel, "value_Toplam_Borç").setText(f"{ozet.get('toplam_borc', 0):.2f} ₺")
        self.label_toplam_alacak.findChild(QLabel, "value_Toplam_Alacak").setText(f"{ozet.get('toplam_alacak', 0):.2f} ₺")
        son_bakiye = ozet.get('son_bakiye', 0)
        self.label_son_bakiye.findChild(QLabel, "value_Son_Bakiye").setText(f"{son_bakiye:.2f} ₺")
        if son_bakiye > 0:
            self.label_son_bakiye.setStyleSheet(self.label_son_bakiye.styleSheet().replace(self.color_primary, "#ef4444"))
        elif son_bakiye < 0:
            self.label_son_bakiye.setStyleSheet(self.label_son_bakiye.styleSheet().replace(self.color_primary, "#10b981"))
    
    def _create_summary_chip(self, title, value, color):
        chip = QFrame()
        chip.setStyleSheet(f"""
            QFrame {{
                background: {self.color_card};
                border: 1px solid {self.color_border};
                border-radius: 8px;
                padding: 8px 10px;
            }}
        """)
        layout = QVBoxLayout(chip)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)
        
        title_label = QLabel(title)
        title_label.setFont(self._brand_font(size=11, bold=True))
        title_label.setStyleSheet(f"color: {self.color_muted};")
        value_label = QLabel(value)
        value_label.setFont(self._brand_font(size=15, bold=True))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setObjectName(f"value_{title.replace(' ', '_')}")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return chip
    
    def get_filters(self):
        """Seçili filtreleri döndür"""
        cari_id = self.combo_cari.currentData()
        baslangic = self.date_baslangic.date().toString("yyyy-MM-dd")
        bitis = self.date_bitis.date().toString("yyyy-MM-dd")
        return {
            'cari_ids': [cari_id] if cari_id else [],
            'baslangic_tarih': baslangic,
            'bitis_tarih': bitis
        }
    
    def set_callbacks(self, on_tamam=None, on_kapat=None, on_yazdir=None, on_excel=None, on_mail=None):
        """Callback'leri ayarla"""
        if on_tamam:
            self._tamam_callback = on_tamam
        if on_kapat:
            self._kapat_callback = on_kapat
        self.btn_yenile.clicked.connect(on_tamam or (lambda: None))
        self.btn_geri.clicked.connect(on_kapat or (lambda: None))
        self.btn_yazdir.clicked.connect(on_yazdir or (lambda: QMessageBox.information(self, "Bilgi", "Yazdırma yakında eklenecek")))
        self.btn_excel.clicked.connect(on_excel or (lambda: QMessageBox.information(self, "Bilgi", "Excel export yakında eklenecek")))
        self.btn_mail.clicked.connect(on_mail or self.on_mail_gonder)
    
    def on_double_click(self, item):
        """Çift tıklamada detay göster"""
        row = item.row()
        self.show_detay(row)
    
    def show_detay(self, row):
        """Fatura detaylarını göster"""
        if row >= len(self.current_hareketler):
            return
        
        hareket = self.current_hareketler[row]
        detay = hareket.get('detay')
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Fatura Detayı - {hareket.get('belge_no', '')}")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(500)
        
        layout = QVBoxLayout(dialog)
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        
        html = f"""
        <h3>Fatura Bilgileri</h3>
        <p><b>Fatura No:</b> {hareket.get('belge_no', '')}</p>
        <p><b>Tarih:</b> {hareket.get('tarih', '')}</p>
        <p><b>Cari Hesap:</b> {hareket.get('cari_unvani', '')}</p>
        <p><b>Tutar:</b> {hareket.get('borc', 0):.2f} ₺</p>
        <hr>
        <h3>Fatura Detayları</h3>
        """
        
        if detay and isinstance(detay, dict):
            satirlar = detay.get('satirlar', [])
            if isinstance(satirlar, str):
                try:
                    from sql_init import json_loads
                    satirlar = json_loads(satirlar)
                except:
                    satirlar = []
            if satirlar and isinstance(satirlar, list):
                html += "<table border='1' cellpadding='5' style='border-collapse: collapse; width: 100%;'>"
                html += "<tr><th>Malzeme Kodu</th><th>Malzeme Adı</th><th>Miktar</th><th>Birim</th><th>Birim Fiyat</th><th>KDV %</th><th>Tutar</th></tr>"
                for satir in satirlar:
                    if isinstance(satir, dict):
                        malzeme_kodu = satir.get('stokKodu') or satir.get('malzemeKodu') or satir.get('kod', '')
                        malzeme_adi = satir.get('malzemeIsmi') or satir.get('aciklama') or satir.get('ad') or satir.get('malzemeAdi', '')
                        miktar = satir.get('miktar', 0)
                        birim = satir.get('birim', '')
                        birim_fiyat = float(satir.get('birimFiyat', 0) or 0)
                        kdv = float(satir.get('kdvOrani', 0) or 0)
                        tutar = float(satir.get('tutar', 0) or 0)
                        miktar_text = str(int(miktar)) if birim.upper() in ['ADET', 'ADT'] else f"{miktar:.2f}"
                        html += f"""
                        <tr>
                            <td>{malzeme_kodu}</td>
                            <td>{malzeme_adi}</td>
                            <td>{miktar_text}</td>
                            <td>{birim}</td>
                            <td>{birim_fiyat:.2f} ₺</td>
                            <td>%{kdv:.0f}</td>
                            <td>{tutar:.2f} ₺</td>
                        </tr>
                        """
                html += "</table>"
            else:
                html += "<p>Fatura detayı bulunamadı.</p>"
        else:
            html += "<p>Fatura detayı mevcut değil.</p>"
        
        info_text.setHtml(html)
        layout.addWidget(info_text)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.close)
        layout.addWidget(buttons)
        
        dialog.exec_()
    
    def on_mail_gonder(self):
        """E-posta gönder butonu"""
        if not self.current_hareketler:
            QMessageBox.warning(self, "Uyarı", "Gönderilecek ekstre verisi yok. Lütfen önce ekstreyi yükleyin.")
            return
        cari_id = self.combo_cari.currentData()
        if not cari_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir cari hesap seçin.")
            return
        try:
            from models.cari_hesap_model import CariHesapModel
            cari_model = CariHesapModel()
            cari = cari_model.get_by_id(cari_id)
            if not cari or not cari.get('email'):
                QMessageBox.warning(self, "Uyarı", "Cari hesabın e-posta adresi yok.")
                return
            reply = QMessageBox.question(
                self, "E-Posta Gönder",
                f"Ekstre {cari.get('email')} adresine gönderilecek. Devam edilsin mi?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.send_ekstre_email(cari, cari.get('email'))
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"E-posta gönderilirken hata oluştu:\n{str(e)}")
    
    def send_ekstre_email(self, cari, email):
        """Ekstre'yi e-posta ile gönder"""
        try:
            html_content = self.generate_ekstre_html(cari)
            from services.email_service import EmailService
            email_service = EmailService()
            baslangic = self.date_baslangic.date().toString("dd.MM.yyyy")
            bitis = self.date_bitis.date().toString("dd.MM.yyyy")
            subject = f"Cari Hesap Ekstresi - {baslangic} / {bitis}"
            success = email_service.send_email(
                to_email=email,
                subject=subject,
                body=html_content,
                attachments=None,
                is_html=True
            )
            if success:
                QMessageBox.information(self, "Başarılı", f"Ekstre {email} adresine gönderildi.")
            else:
                QMessageBox.warning(self, "Uyarı", "E-posta gönderilemedi. Ayarları kontrol edin.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"E-posta gönderilirken hata oluştu:\n{str(e)}")
    
    def generate_ekstre_html(self, cari):
        """Ekstre'yi HTML formatında oluştur"""
        baslangic = self.date_baslangic.date().toString("dd.MM.yyyy")
        bitis = self.date_bitis.date().toString("dd.MM.yyyy")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Cari Hesap Ekstresi</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #233568; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #233568; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .summary {{ margin-top: 20px; padding: 15px; background-color: #f8f9fa; }}
                .borc {{ color: #ef4444; font-weight: bold; }}
                .alacak {{ color: #10b981; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>Cari Hesap Ekstresi</h1>
            <p><b>Cari Hesap:</b> {cari.get('unvani', '')}</p>
            <p><b>Tarih Aralığı:</b> {baslangic} - {bitis}</p>
            
            <table>
                <tr>
                    <th>Tarih</th>
                    <th>Belge No</th>
                    <th>Açıklama</th>
                    <th>Alacak</th>
                    <th>Borç</th>
                    <th>Bakiye</th>
                    <th>Vade Tarihi</th>
                </tr>
        """
        
        for hareket in self.current_hareketler:
            tarih_str = hareket.get('tarih', '')
            try:
                if tarih_str:
                    tarih_obj = datetime.strptime(tarih_str, '%Y-%m-%d')
                    tarih = tarih_obj.strftime('%d.%m.%Y')
                else:
                    tarih = ''
            except:
                tarih = tarih_str
            
            belge_no = hareket.get('belge_no', '')
            aciklama = hareket.get('aciklama', '')
            borc = hareket.get('borc', 0)
            alacak = hareket.get('alacak', 0)
            bakiye = hareket.get('bakiye', 0)
            
            vade_str = hareket.get('vade_tarihi', '')
            try:
                if vade_str and vade_str != '-':
                    vade_obj = datetime.strptime(vade_str, '%Y-%m-%d')
                    vade = vade_obj.strftime('%d.%m.%Y')
                else:
                    vade = '-'
            except:
                vade = vade_str or '-'
            
            html += f"""
                <tr>
                    <td>{tarih}</td>
                    <td>{belge_no}</td>
                    <td>{aciklama}</td>
                    <td class="alacak">{alacak:.2f} ₺</td>
                    <td class="borc">{borc:.2f} ₺</td>
                    <td>{bakiye:.2f} ₺</td>
                    <td>{vade}</td>
                </tr>
            """
        
        html += f"""
            </table>
            
            <div class="summary">
                <h3>Özet</h3>
                <p><b>Toplam Borç:</b> <span class="borc">{self.current_ozet.get('toplam_borc', 0):.2f} ₺</span></p>
                <p><b>Toplam Alacak:</b> <span class="alacak">{self.current_ozet.get('toplam_alacak', 0):.2f} ₺</span></p>
                <p><b>Son Bakiye:</b> {self.current_ozet.get('son_bakiye', 0):.2f} ₺</p>
            </div>
        </body>
        </html>
        """
        return html
    
    def show_error(self, message):
        """Hata mesajı göster"""
        QMessageBox.critical(self, "Hata", message)
    
    def show_success(self, message):
        """Başarı mesajı göster"""
        QMessageBox.information(self, "Başarılı", message)
