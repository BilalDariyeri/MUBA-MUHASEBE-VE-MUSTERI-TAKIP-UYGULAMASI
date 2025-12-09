import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QGroupBox, QGridLayout,
    QHBoxLayout, QFrame, QMenu, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QFontDatabase, QPixmap, QIcon, QColor

class DashboardView(QWidget):
    """
    Modernize edilmiş, veri odaklı ve profesyonel Dashboard görünümü.
    View katmanı olarak sadece UI işlemlerini ve güncellemelerini içerir.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._load_brand_fonts()

        # --- YENİ VE CANLI RENK PALETİ ---
        self.color_background = "#e7e3ff"       # Lavanta arka plan
        self.color_sidebar_bg = "#0f112b"       # Koyu lacivert
        self.color_header_bg = "#233568"        # Ana marka laciverti
        self.color_accent = "#f48c06"           # Portakal turuncusu
        self.color_text_light = "#f0f1f9"       # Açık metin (sidebar için)
        self.color_text_dark = "#1e2a4c"        # Koyu metin (ana içerik için)
        self.color_text_muted = "#6b7280"       # Soluk metin
        self.color_card_bg = "#ffffff"          # Kart arka planı
        self.color_border = "#e2e8f0"          # İnce border rengi
        self.color_success = "#10b981"         # Yeşil (Başarı, Gelir)
        self.color_danger = "#ef4444"          # Kırmızı (Tehlike, Gider)

        self.buttons = {}  # Tüm butonları tek bir yerde toplamak için
        self.quick_buttons = {}
        self.nav_buttons = {}
        self.init_ui()

    def _load_brand_fonts(self):
        """Marka fontlarını yükle (yoksa sessiz devam et)"""
        # Bu fonksiyonun içeriği aynı kalabilir, iyi çalışıyor.
        fonts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo", "fonts")
        if not os.path.isdir(fonts_dir):
            return
        for file in os.listdir(fonts_dir):
            if file.lower().endswith((".otf", ".ttf")):
                try:
                    QFontDatabase.addApplicationFont(os.path.join(fonts_dir, file))
                except Exception:
                    pass

    def _brand_font(self, size=16, weight=QFont.Normal, bold=False):
        """SF Pro Display yüklü ise onu, değilse varsayılan fontu kullan"""
        font = QFont("SF Pro Display", pointSize=size, weight=weight)
        font.setBold(bold)
        return font

    # ============================================================
    # UI OLUŞTURMA
    # ============================================================
    def init_ui(self):
        """Ana UI yapısını oluşturur."""
        self.setObjectName("root")
        self.setStyleSheet(f"QWidget#root {{ background: {self.color_background}; }}")

        root_layout = QHBoxLayout(self)
        root_layout.setSpacing(0)
        root_layout.setContentsMargins(0, 0, 0, 0)

        sidebar = self._create_sidebar()
        main_content = self._create_main_content()

        root_layout.addWidget(sidebar)
        root_layout.addLayout(main_content)
        self.setLayout(root_layout)
        self._bind_default_callbacks()
        # İlk metrikleri yükle (parent hazırsa)
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(200, self._load_initial_metrics)

    def _bind_default_callbacks(self):
        """Parent içindeki metodlar varsa hızlı işlemler ve nav'ı onlara bağlar."""
        if not self.parent_window:
            return
        parent = self.parent_window
        # Hızlı işlemler
        default_actions = {
            "yeni_fatura": getattr(parent, "show_fatura_list", None),
            "yeni_tahsilat": getattr(parent, "show_tahsilat_giris", None),
            "hizli_rapor": getattr(parent, "show_finansal_analiz", None),
            "yeni_cari": getattr(parent, "show_cari_list", None),
        }
        for key, fn in default_actions.items():
            if fn and key in self.buttons:
                self.buttons[key].clicked.connect(fn)
        # Yan menü: parent'ta varsa uygun methodlara bağla
        nav_map = {
            "nav_dashboard": getattr(parent, "show_dashboard", None),
            "nav_cari": getattr(parent, "show_cari_list", None),
            "nav_cari_ekstre": getattr(parent, "show_cari_ekstre", None),
            "nav_fatura": getattr(parent, "show_fatura_list", None),
            "nav_alim_fatura": getattr(parent, "show_purchase_invoice", None),
            "nav_fatura_gonder": getattr(parent, "show_fatura_gonder", None),
            "nav_tahsilat": getattr(parent, "show_tahsilat_list", None),
            "nav_odemeler": getattr(parent, "show_odemeler", None),
            "nav_rapor": getattr(parent, "show_finansal_analiz", None),
            "nav_ai_odeme": getattr(parent, "show_ai_payment_predictor", None),
            "nav_malzeme": getattr(parent, "show_malzeme_list", None),
            "nav_ayar": getattr(parent, "show_hesap_makinesi", None),
        }
        for key, fn in nav_map.items():
            if fn and key in self.buttons:
                self.buttons[key].clicked.connect(fn)

    def _load_initial_metrics(self):
        """Varsa parent'tan metrik/aktivite çekip kart ve tabloyu doldur."""
        if not self.parent_window:
            return
        
        # Widget'ların hazır olduğundan emin ol
        if not hasattr(self, 'kpi_ciro') or not hasattr(self.kpi_ciro, 'value_label'):
            # Widget'lar henüz hazır değil, biraz bekle
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(100, self._load_initial_metrics)
            return
        
        parent = self.parent_window
        if hasattr(parent, "get_dashboard_metrics"):
            try:
                metrics = parent.get_dashboard_metrics()
                if metrics:
                    self.update_kpi_data(
                        metrics.get("ciro", 0),
                        metrics.get("alacak", 0),
                        metrics.get("gider", 0),
                        metrics.get("musteri_sayisi", 0),
                    )
            except Exception as e:
                print(f"Dashboard metrikleri yüklenirken hata: {e}")
                import traceback
                traceback.print_exc()
        if hasattr(parent, "get_recent_activity"):
            try:
                activities = parent.get_recent_activity()
                if isinstance(activities, list) and len(activities) > 0:
                    self.update_recent_activity(activities)
                elif isinstance(activities, list):
                    # Boş liste döndü ama hata yok, normal
                    self.update_recent_activity([])
            except Exception as e:
                print(f"Son hareketler yüklenirken hata: {e}")
                import traceback
                traceback.print_exc()
                # Hata durumunda tekrar dene
                QTimer.singleShot(500, self._load_initial_metrics)

    def _create_sidebar(self):
        """Sol navigasyon menüsünü oluşturur."""
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet(f"""
            QFrame#sidebar {{
                background: {self.color_sidebar_bg};
                padding: 10px 0;
            }}
            QPushButton[nav="true"] {{
                color: {self.color_text_light};
                background: transparent;
                border: none;
                padding: 12px 20px;
                font-size: 13px;
                font-weight: 600;
                text-align: left;
                border-radius: 0;
            }}
            QPushButton[nav="true"]:hover {{
                background: rgba(255, 255, 255, 0.05);
            }}
            QPushButton[nav="true"][active="true"] {{
                background: {self.color_header_bg};
                border-left: 3px solid {self.color_accent};
            }}
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(5)

        # Logo (metin yerine ikon)
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo", "muba-1.png")
        if not os.path.exists(logo_path):
            alt = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo", "muba-2.png")
            logo_path = alt if os.path.exists(alt) else logo_path
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(120, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        logo_label.setStyleSheet("padding: 15px 20px;")
        sidebar_layout.addWidget(logo_label)
        sidebar_layout.addSpacing(20)

        # Navigasyon Butonları
        nav_items = {
            "dashboard": "Dashboard",
            "cari": "Cari Hesaplar",
            "cari_ekstre": "Cari Ekstre",
            "fatura": "Satış Faturaları",
            "alim_fatura": "Alım Faturaları",
            "fatura_gonder": "Fatura Gönder",
            "tahsilat": "Tahsilatlar",
            "odemeler": "Ödemeler",
            "rapor": "Finansal Analiz",
            "ai_odeme": "AI Ödeme Tahmini",
            "malzeme": "Malzemeler",
            "ayar": "Hesap Makinesi"
        }
        for key, text in nav_items.items():
            btn = QPushButton(text) # İkonlar eklenebilir: QIcon("path/to/icon.png"), text
            btn.setProperty("nav", True)
            btn.setCursor(Qt.PointingHandCursor)
            if key == "dashboard":
                btn.setProperty("active", True) # Aktif sayfa
            self.buttons[f"nav_{key}"] = btn
            self.nav_buttons[key] = btn
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        return sidebar

    def _create_main_content(self):
        """Sağ taraftaki ana içerik alanını oluşturur."""
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(20)

        # 1. Başlık ve Kullanıcı
        header_layout = self._create_header("Dashboard", "İşletmenizin genel durumuna hoş geldiniz.")
        content_layout.addLayout(header_layout)

        # 2. KPI Kartları
        kpi_layout = self._create_kpi_cards()
        content_layout.addLayout(kpi_layout)

        # 3. Hızlı İşlemler (eski butonlar yerine gerçek aksiyonlar)
        quick_group = self._create_actions_group()
        content_layout.addWidget(quick_group)

        # 4. Son Hareketler tablosu
        activity_group = self._create_recent_activity_group()
        content_layout.addWidget(activity_group)

        content_layout.addStretch()
        return content_layout

    def _create_header(self, title, subtitle):
        """Sayfa başlığını ve alt başlığını oluşturan layout."""
        header_layout = QHBoxLayout()
        title_layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(self._brand_font(size=26, bold=True))
        title_label.setStyleSheet(f"color: {self.color_text_dark};")
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(self._brand_font(size=12))
        subtitle_label.setStyleSheet(f"color: {self.color_text_muted};")

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.setSpacing(2)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        # Buraya kullanıcı profili, bildirimler gibi widget'lar eklenebilir.
        return header_layout

    def _create_kpi_cards(self):
        """Dort anahtar performans gostergesi kartini olusturur."""
        kpi_layout = QGridLayout()
        kpi_layout.setSpacing(18)

        self.kpi_ciro = self._create_kpi_card("Toplam Ciro", "0,00 TL", self.color_success)
        self.kpi_alacak = self._create_kpi_card("Odenmemis Alacak", "0,00 TL", self.color_accent)
        self.kpi_gider = self._create_kpi_card("Bu Ayki Giderler", "0,00 TL", self.color_danger)
        self.kpi_musteri = self._create_kpi_card("Aktif Musteriler", "0", self.color_header_bg)

        kpi_layout.addWidget(self.kpi_ciro, 0, 0)
        kpi_layout.addWidget(self.kpi_alacak, 0, 1)
        kpi_layout.addWidget(self.kpi_gider, 0, 2)
        kpi_layout.addWidget(self.kpi_musteri, 0, 3)
        return kpi_layout

    def _create_kpi_card(self, title, value, color):
        """Tek bir KPI kartı widget'ı oluşturur."""
        card = QFrame()
        card.setObjectName("kpi_card")
        card.setStyleSheet(f"""
            QFrame#kpi_card {{
                background-color: {self.color_card_bg};
                border-radius: 4px;
                border: 1px solid {self.color_border};
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setFont(self._brand_font(size=11, bold=True))
        title_label.setStyleSheet(f"color: {self.color_text_muted};")

        value_label = QLabel(value)
        value_label.setFont(self._brand_font(size=22, bold=True))
        value_label.setStyleSheet(f"color: {color};")
        
        card.value_label = value_label # Değeri güncellemek için referans

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()
        return card

    def _create_actions_group(self):
        """Hızlı işlemler grubunu oluşturur."""
        group = QGroupBox("Hızlı İşlemler")
        group.setFont(self._brand_font(size=14, bold=True))
        group.setStyleSheet(self._get_groupbox_style())
        
        layout = QGridLayout(group)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 20, 15, 15)

        actions = {
            "yeni_fatura": ("Yeni Fatura", self.color_header_bg, self.color_text_light),
            "yeni_tahsilat": ("Tahsilat Ekle", self.color_success, self.color_text_light),
            "hizli_rapor": ("Hızlı Rapor", self.color_accent, self.color_text_light),
            "yeni_cari": ("Cari Hesap Ekle", self.color_sidebar_bg, self.color_text_light),
        }

        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for (key, (text, bg, color)), (r, c) in zip(actions.items(), positions):
            btn = self._create_action_button(text, bg, color)
            self.buttons[key] = btn
            self.quick_buttons[key] = btn
            layout.addWidget(btn, r, c)

        return group

    def _create_recent_activity_group(self):
        """Son Hareketler tablosunu içeren grubu oluşturur."""
        group = QGroupBox("Son Hareketler")
        group.setFont(self._brand_font(size=14, bold=True))
        group.setStyleSheet(self._get_groupbox_style())

        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 25, 15, 15)

        self.activity_table = QTableWidget(0, 5)
        self.activity_table.setHorizontalHeaderLabels(["Tarih", "Müşteri", "Açıklama", "Tutar", "İşlem"])
        self.activity_table.verticalHeader().setVisible(False)
        self.activity_table.setShowGrid(False)
        self.activity_table.setAlternatingRowColors(True)
        self.activity_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.activity_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.activity_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.activity_table.setEditTriggers(QTableWidget.NoEditTriggers)
        # Sağ tık menüsü için
        self.activity_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.activity_table.customContextMenuRequested.connect(self._on_activity_context_menu)
        self.activity_table.setStyleSheet(f"""
            QTableWidget {{ 
                border: none; 
                background-color: transparent;
                alternate-background-color: #f8f9fa;
            }}
            QHeaderView::section {{ 
                background-color: transparent; 
                border: none;
                padding: 4px;
                font-weight: 600;
                color: {self.color_text_muted};
                border-bottom: 1px solid {self.color_border};
            }}
        """)
        layout.addWidget(self.activity_table)
        return group

    # ============================================================
    # YARDIMCI WIDGET OLUŞTURUCULAR VE STİLLER
    # ============================================================
    def _create_action_button(self, text, bg_color, text_color):
        """Stil sahibi bir eylem butonu oluşturur."""
        btn = QPushButton(text)
        btn.setFont(self._brand_font(size=12, bold=True))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(48)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                padding: 10px;
                border-radius: 4px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {self._adjust_color(bg_color, 1.1)};
            }}
            QPushButton:pressed {{
                background-color: {self._adjust_color(bg_color, 0.9)};
            }}
        """)
        return btn

    def _get_groupbox_style(self):
        """QGroupBox için standart stil döndürür."""
        return f"""
            QGroupBox {{
                background-color: {self.color_card_bg};
                border: 1px solid {self.color_border};
                border-radius: 4px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                padding: 0 5px;
                color: {self.color_text_dark};
            }}
        """

    @staticmethod
    def _adjust_color(hex_color, factor):
        """Rengi aydınlatmak/koyulaştırmak için yardımcı fonksiyon."""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    # ============================================================
    # DIŞARIDAN VERİ GÜNCELLEME METODLARI
    # ============================================================
    def update_kpi_data(self, ciro, alacak, gider, musteri_sayisi):
        """Controller'dan gelen verilerle KPI kartlarını günceller."""
        try:
            # Widget'ların hala var olup olmadığını kontrol et
            if not hasattr(self, 'kpi_ciro') or self.kpi_ciro is None:
                return
            
            # Widget'ın silinip silinmediğini kontrol et
            try:
                if hasattr(self.kpi_ciro, 'value_label') and self.kpi_ciro.value_label is not None:
                    self.kpi_ciro.value_label.setText(f"{ciro:,.2f} TL")
            except RuntimeError:
                # Widget silinmiş, işlemi durdur
                return
            
            try:
                if hasattr(self, 'kpi_alacak') and hasattr(self.kpi_alacak, 'value_label') and self.kpi_alacak.value_label is not None:
                    self.kpi_alacak.value_label.setText(f"{alacak:,.2f} TL")
            except RuntimeError:
                return
            
            try:
                if hasattr(self, 'kpi_gider') and hasattr(self.kpi_gider, 'value_label') and self.kpi_gider.value_label is not None:
                    self.kpi_gider.value_label.setText(f"{gider:,.2f} TL")
            except RuntimeError:
                return
            
            try:
                if hasattr(self, 'kpi_musteri') and hasattr(self.kpi_musteri, 'value_label') and self.kpi_musteri.value_label is not None:
                    self.kpi_musteri.value_label.setText(str(musteri_sayisi))
            except RuntimeError:
                return
        except RuntimeError:
            # Widget silinmiş, sessizce çık
            return
        except Exception as e:
            print(f"KPI güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()

    def update_recent_activity(self, activities: list):
        """Controller'dan gelen liste ile son hareketler tablosunu doldurur."""
        try:
            # Widget'ın hala var olup olmadığını kontrol et
            if not hasattr(self, 'activity_table') or self.activity_table is None:
                return
            
            # Widget'ın silinip silinmediğini kontrol et
            try:
                self.activity_table.setRowCount(0) # Tabloyu temizle
            except RuntimeError:
                # Widget silinmiş, işlemi durdur
                return
            
            self._activity_data = activities  # Silme için sakla
            
            for row_idx, row_data in enumerate(activities):
                try:
                    row_position = self.activity_table.rowCount()
                    self.activity_table.insertRow(row_position)
                except RuntimeError:
                    # Widget silinmiş, döngüyü durdur
                    return
            
                # Tutar için özel renklendirme
                tutar_item = QTableWidgetItem(f"{row_data['tutar']:,.2f} TL")
                tutar_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if row_data.get('tip') == 'gelir':
                    tutar_item.setForeground(QColor(self.color_success))
                else:
                    tutar_item.setForeground(QColor(self.color_danger))

                try:
                    self.activity_table.setItem(row_position, 0, QTableWidgetItem(row_data['tarih']))
                    self.activity_table.setItem(row_position, 1, QTableWidgetItem(row_data['musteri']))
                    self.activity_table.setItem(row_position, 2, QTableWidgetItem(row_data['aciklama']))
                    self.activity_table.setItem(row_position, 3, tutar_item)
                    
                    # Sil butonu
                    btn_sil = QPushButton("Sil")
                    btn_sil.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {self.color_danger};
                            color: white;
                            border: none;
                            padding: 4px 8px;
                            border-radius: 3px;
                            font-size: 11px;
                        }}
                        QPushButton:hover {{
                            background-color: #dc2626;
                        }}
                    """)
                    btn_sil.clicked.connect(lambda checked, idx=row_idx: self._delete_activity(idx))
                    self.activity_table.setCellWidget(row_position, 4, btn_sil)
                except RuntimeError:
                    # Widget silinmiş, döngüyü durdur
                    return
        except RuntimeError:
            # Widget silinmiş, sessizce çık
            return
        except Exception as e:
            print(f"Son hareketler güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_activity_context_menu(self, position):
        """Son hareketler için sağ tık menüsü"""
        item = self.activity_table.itemAt(position)
        if item:
            row = item.row()
            if hasattr(self, '_activity_data') and row < len(self._activity_data):
                menu = QMenu(self)
                delete_action = menu.addAction("Sil")
                action = menu.exec_(self.activity_table.viewport().mapToGlobal(position))
                if action == delete_action:
                    self._delete_activity(row)
    
    def _delete_activity(self, row_idx):
        """Son hareketi sil"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            if not hasattr(self, '_activity_data') or row_idx >= len(self._activity_data):
                return
            
            activity = self._activity_data[row_idx]
            
            # Onay al
            reply = QMessageBox.question(
                self,
                "Sil",
                f"Bu hareketi silmek istediğinize emin misiniz?\n\n"
                f"Tarih: {activity.get('tarih', '')}\n"
                f"Müşteri: {activity.get('musteri', '')}\n"
                f"Tutar: {activity.get('tutar', 0):,.2f} TL",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # Entity type'a göre sil
            entity_type = activity.get('entity_type', '')
            entity_id = activity.get('id', '')
            
            if entity_type == 'fatura' and entity_id:
                # Fatura sil
                from models.fatura_model import FaturaModel
                fatura_model = FaturaModel()
                fatura_model.delete(entity_id)
                QMessageBox.information(self, "Başarılı", "Fatura silindi!")
            elif entity_type == 'tahsilat' and entity_id:
                # Tahsilat sil
                from models.tahsilat_model import TahsilatModel
                tahsilat_model = TahsilatModel()
                tahsilat_model.delete(entity_id)
                QMessageBox.information(self, "Başarılı", "Tahsilat silindi!")
            else:
                # Fallback: Açıklamaya göre bul ve sil
                aciklama = activity.get('aciklama', '')
                tip = activity.get('tip', '')
                
                if tip == 'gelir' or 'Fatura' in aciklama or not tip:
                    # Fatura sil
                    from models.fatura_model import FaturaModel
                    fatura_model = FaturaModel()
                    faturalar = fatura_model.get_all()
                    for fatura in faturalar:
                        if fatura.get('faturaNo', '') == aciklama:
                            fatura_model.delete(fatura.get('id'))
                            QMessageBox.information(self, "Başarılı", "Fatura silindi!")
                            break
                elif tip == 'gider' or 'Tahsilat' in aciklama:
                    # Tahsilat sil
                    from models.tahsilat_model import TahsilatModel
                    tahsilat_model = TahsilatModel()
                    tahsilatlar = tahsilat_model.get_all()
                    for tahsilat in tahsilatlar:
                        belge_no = tahsilat.get('belge_no', '')
                        if belge_no == aciklama or str(tahsilat.get('id', ''))[:8] in aciklama:
                            tahsilat_model.delete(tahsilat.get('id'))
                            QMessageBox.information(self, "Başarılı", "Tahsilat silindi!")
                            break
            
            # Listeyi yenile
            if self.parent_window and hasattr(self.parent_window, 'get_recent_activity'):
                activities = self.parent_window.get_recent_activity()
                self.update_recent_activity(activities)
                
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Hata", f"Silme hatası:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    # ============================================================
    # CALLBACK (SİNYAL) BAĞLANTILARI
    # ============================================================
    def _connect_nav(self, key, callback):
        btn = self.nav_buttons.get(key)
        if btn and callback:
            # Önceki bağlantıları temizle (çift bağlantıyı önlemek için)
            try:
                btn.clicked.disconnect()
            except:
                pass
            btn.clicked.connect(callback)

    # Uyum için eski callback imzaları
    def set_cari_button_callback(self, callback):
        self._connect_nav("cari", callback)

    def set_malzeme_button_callback(self, callback):
        self._connect_nav("malzeme", callback)

    def set_satis_button_callback(self, callback):
        self._connect_nav("fatura", callback)

    def set_ekstre_button_callback(self, callback):
        self._connect_nav("cari_ekstre", callback)

    def set_tahsilat_button_callback(self, callback):
        self._connect_nav("tahsilat", callback)

    def set_hesap_makinesi_button_callback(self, callback):
        # Hesap makinesi için sol menüdeki "Hesap Makinesi" satırını kullan
        self._connect_nav("ayar", callback)

    def set_fatura_gonder_button_callback(self, callback):
        self._connect_nav("fatura", callback)

    def set_finansal_button_callback(self, callback):
        self._connect_nav("rapor", callback)

    def set_alim_faturasi_button_callback(self, callback):
        self._connect_nav("alim_fatura", callback)

    def set_tahsilat_list_button_callback(self, callback):
        self._connect_nav("tahsilat", callback)

    def set_ai_model_button_callback(self, callback):
        self._connect_nav("ai_odeme", callback)
    
    def set_odemeler_button_callback(self, callback):
        self._connect_nav("odemeler", callback)

    def connect_signals(self, controller_slots):
        """
        Tüm buton sinyallerini ilgili controller metodlarına bağlar.
        controller_slots: {'buton_adi': metod, ...} şeklinde bir sözlük olmalı.
        Örnek: {'yeni_fatura': self.controller.handle_new_invoice}
        """
        for key, slot in controller_slots.items():
            if key in self.buttons:
                self.buttons[key].clicked.connect(slot)

# Örnek Kullanım (Test için)
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow

    class MockController:
        def __init__(self, view):
            self.view = view
            self.connect_view_signals()
            self.load_initial_data()

        def connect_view_signals(self):
            slots = {
                "yeni_fatura": self.handle_yeni_fatura,
                "nav_cari": self.handle_nav_cari,
                # ... diğer butonlar
            }
            self.view.connect_signals(slots)
        
        def load_initial_data(self):
            # Gerçek uygulamada bu veriler modelden gelir
            self.view.update_kpi_data(
                ciro=125430.50,
                alacak=18200.00,
                gider=45100.75,
                musteri_sayisi=84
            )
            activities = [
                {'tarih': '20.05.2024', 'musteri': 'Tekno A.Ş.', 'aciklama': 'Fatura #2024-15', 'tutar': 5250.00, 'tip': 'gelir'},
                {'tarih': '18.05.2024', 'musteri': 'Ofis Gideri', 'aciklama': 'Kira Ödemesi', 'tutar': 15000.00, 'tip': 'gider'},
                {'tarih': '17.05.2024', 'musteri': 'Global Ltd.', 'aciklama': 'Tahsilat', 'tutar': 1800.00, 'tip': 'gelir'},
            ]
            self.view.update_recent_activity(activities)

        def handle_yeni_fatura(self):
            print("Controller: 'Yeni Fatura Oluştur' butonuna basıldı.")
        
        def handle_nav_cari(self):
            print("Controller: 'Cari Hesaplar' navigasyon menüsüne tıklandı.")


    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Profesyonel Dashboard")
    window.setGeometry(100, 100, 1400, 800)

    dashboard_view = DashboardView()
    controller = MockController(dashboard_view) # Controller View'ı yönetir

    window.setCentralWidget(dashboard_view)
    window.show()
    sys.exit(app.exec_())
