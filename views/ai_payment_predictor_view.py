"""
AI Odeme Tahmini View - Yapay zeka ile musteri odeme davranisi tahmini
Musteri dostu, aciklayici ve MUBA temasiyla uyumlu arayuz
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QComboBox, QGroupBox, QFormLayout, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class AIPaymentPredictorView(QWidget):
    """AI Odeme Tahmini gorunumu"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._init_colors()
        self.init_ui()

    def _init_colors(self):
        self.color_bg = "#e7e3ff"            # lavanta arka plan
        self.color_card = "#ffffff"
        self.color_border = "#d0d4f2"
        self.color_primary = "#233568"       # koyu mavi
        self.color_primary_dark = "#0f112b"  # sidebar koyu
        self.color_accent = "#f48c06"        # portakal turuncusu
        self.color_text = "#1f2a44"
        self.color_muted = "#6b7280"
        self.color_success = "#16a34a"
        self.color_warning = "#f97316"
        self.color_danger = "#ef4444"

    def init_ui(self):
        """UI'yi başlat"""
        self.setStyleSheet(f"background: {self.color_bg};")
        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(18, 18, 18, 18)

        # Başlık ve geri butonu
        header_layout = QHBoxLayout()

        btn_geri = QPushButton("← Geri")
        btn_geri.setCursor(Qt.PointingHandCursor)
        btn_geri.setStyleSheet(f"""
            QPushButton {{
                background: {self.color_primary};
                color: #fff;
                border: none;
                padding: 10px 16px;
                font-weight: 700;
                border-radius: 4px;
            }}
            QPushButton:hover {{ background: {self._tint(self.color_primary, 1.08)}; }}
            QPushButton:pressed {{ background: {self._tint(self.color_primary, 0.9)}; }}
        """)
        btn_geri.clicked.connect(self.on_geri)
        header_layout.addWidget(btn_geri)

        title = QLabel("AI Ödeme Davranış Analizi")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {self.color_primary_dark};")
        header_layout.addWidget(title)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Detaylı Bilgi Grubu
        info_group = QGroupBox("Sistem Hakkında")
        info_group.setStyleSheet(self._group_style())
        info_layout = QVBoxLayout()

        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(150)
        info_text.setHtml(f"""
        <div style="font-size: 12px; line-height: 1.6; color: {self.color_text};">
        <p><b>Bu Sistem Ne Yapar?</b></p>
        <p>Yapay zeka ile geçmiş ödeme davranışlarını analiz eder, gelecekteki tahsilat riskini tahmin eder.</p>
        <p><b>Nasıl Çalışır?</b></p>
        <ul>
        <li>Ortalama gecikme gününü hesaplar.</li>
        <li>Ödeme tutarlılığını ve güven skorunu çıkarır.</li>
        <li>Risk grubunu sınıflandırır (düşük/orta/yüksek).</li>
        </ul>
        </div>
        """)
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Müşteri seçimi
        select_group = QGroupBox("Müşteri Seçimi ve Analiz")
        select_group.setStyleSheet(self._group_style())
        select_layout = QVBoxLayout()

        info_label = QLabel("Analiz yapmak istediğiniz müşteriyi seçin:")
        info_label.setStyleSheet(f"color: {self.color_muted}; font-size: 11px; margin-bottom: 6px;")
        select_layout.addWidget(info_label)

        select_form = QFormLayout()
        select_form.setSpacing(10)

        self.cari_combo = QComboBox()
        self.cari_combo.setMinimumHeight(40)
        self.cari_combo.setStyleSheet(f"""
            QComboBox {{
                font-size: 13px;
                padding: 6px 10px;
                border: 1px solid {self.color_border};
                border-radius: 4px;
                background: #fff;
            }}
            QComboBox:focus {{
                border: 1px solid {self.color_primary};
            }}
        """)
        select_form.addRow("Müşteri:", self.cari_combo)

        btn_tahmin = QPushButton("AI Analiz Başlat")
        btn_tahmin.setCursor(Qt.PointingHandCursor)
        btn_tahmin.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color_accent};
                color: #fff;
                padding: 12px 18px;
                font-weight: 700;
                font-size: 14px;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {self._tint(self.color_accent, 1.07)};
            }}
            QPushButton:pressed {{
                background-color: {self._tint(self.color_accent, 0.9)};
            }}
        """)
        btn_tahmin.clicked.connect(self.on_tahmin)
        select_form.addRow("", btn_tahmin)

        select_layout.addLayout(select_form)
        select_group.setLayout(select_layout)
        layout.addWidget(select_group)

        # Detaylı Sonuçlar Bölümü
        results_group = QGroupBox("Analiz Sonuçları")
        results_group.setStyleSheet(self._group_style())
        results_layout = QVBoxLayout()

        # Sonuçlar tablosu
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "Müşteri", "Tahmini Gecikme (Gün)", "Güven Skoru", "Risk Grubu", "Ödeme Sayısı"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setMinimumHeight(180)
        self.results_table.setStyleSheet(f"""
            QTableWidget {{
                font-size: 12px;
                gridline-color: {self.color_border};
                background: transparent;
                alternate-background-color: #f8f9ff;
                border: none;
            }}
            QHeaderView::section {{
                background-color: #f3f4ff;
                padding: 8px;
                border: 1px solid {self.color_border};
                font-weight: bold;
                color: {self.color_text};
            }}
        """)
        results_layout.addWidget(self.results_table)

        # Detaylı Açıklama Alanı
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(200)
        self.detail_text.setPlaceholderText("Analiz sonuçları burada detaylı olarak gösterilecektir...")
        self.detail_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: #f9f9ff;
                border: 1px solid {self.color_border};
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
                color: {self.color_text};
            }}
        """)
        results_layout.addWidget(QLabel("Detaylı Açıklama:"))
        results_layout.addWidget(self.detail_text)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        self.setLayout(layout)

    def on_geri(self):
        """Geri butonu"""
        if hasattr(self, '_geri_callback'):
            self._geri_callback()
        elif self.parent_window:
            self.parent_window.show_dashboard()

    def on_tahmin(self):
        """Tahmin yap butonu"""
        if hasattr(self, '_tahmin_callback'):
            self._tahmin_callback()

    def set_callbacks(self, on_geri=None, on_tahmin=None):
        """Callback'leri ayarla"""
        if on_tahmin:
            self._tahmin_callback = on_tahmin
        if on_geri:
            self._geri_callback = on_geri

    def load_cari_hesaplar(self, cari_list):
        """Cari hesapları yükle"""
        self.cari_combo.clear()
        self.cari_combo.addItem("Müşteri Seçiniz...", None)
        for cari in cari_list:
            display_text = f"{cari.get('unvani', '')} - {cari.get('vergiNo', '')}"
            self.cari_combo.addItem(display_text, cari.get('id'))

    def get_selected_cari_id(self):
        """Seçili cari hesap ID'sini al"""
        return self.cari_combo.currentData()

    def display_results(self, results):
        """Tahmin sonuçlarını göster - Detaylı ve açıklayıcı"""
        self.results_table.setRowCount(len(results))

        for row, result in enumerate(results):
            # Müşteri
            musteri_adi = result.get('musteri_adi', result.get('musteri_id', '-'))
            musteri_item = QTableWidgetItem(musteri_adi)
            musteri_item.setFont(QFont("", 11, QFont.Bold))
            self.results_table.setItem(row, 0, musteri_item)

            # Tahmini gecikme
            gecikme = result.get('tahmini_gecikme', 0)
            gecikme_item = QTableWidgetItem(f"{gecikme:.1f} gün")
            if gecikme > 0:
                gecikme_item.setForeground(QColor(self.color_danger))
            elif gecikme < 0:
                gecikme_item.setForeground(QColor(self.color_success))
            self.results_table.setItem(row, 1, gecikme_item)

            # Güven skoru (guven_skoru veya skor)
            skor = result.get('guven_skoru', result.get('skor', 0))
            skor_item = QTableWidgetItem(f"{skor:.0f}/100")
            skor_item.setForeground(self._get_color_for_score(skor))
            self.results_table.setItem(row, 2, skor_item)

            # Risk grubu (risk_grubu veya risk)
            risk = result.get('risk_grubu', result.get('risk', "Bilinmiyor"))
            risk_item = QTableWidgetItem(risk)
            risk_item.setForeground(self._get_color_for_risk(risk))
            self.results_table.setItem(row, 3, risk_item)

            # Ödeme sayısı
            odeme_sayisi = result.get('odeme_sayisi', result.get('ozellikler', {}).get('odeme_sayisi', 0))
            self.results_table.setItem(row, 4, QTableWidgetItem(str(odeme_sayisi)))
        
        # İlk sonucun detaylarını göster
        if results:
            self.show_prediction_detail(results[0])

    def show_prediction_detail(self, sonuc):
        """Detaylı açıklama alanını doldur"""
        skor = sonuc.get('guven_skoru', sonuc.get('skor', 0))
        risk = sonuc.get('risk_grubu', sonuc.get('risk', "Bilinmiyor"))
        gecikme = sonuc.get('tahmini_gecikme', 0)
        ozellikler = sonuc.get('ozellikler', {})
        musteri_adi = sonuc.get('musteri_adi', sonuc.get('musteri_id', 'Müşteri'))
        
        # Detaylı tavsiye oluştur
        tavsiye = self._generate_detailed_advice(skor, risk, gecikme, ozellikler)
        
        # Yorum oluştur
        yorum = self._generate_comment(skor, risk, gecikme, ozellikler)

        html = f"""
        <div style='font-size:12px; line-height:1.8; color:{self.color_text};'>
        <h3 style='color:{self.color_primary}; margin-top:0;'>📊 {musteri_adi} - Analiz Sonuçları</h3>
        
        <p><b>🎯 Özet:</b></p>
        <ul>
            <li><b>Güven Skoru:</b> <span style='color:{self._get_score_color(skor)};'>{skor:.0f}/100</span></li>
            <li><b>Risk Grubu:</b> <span style='color:{self._get_risk_color(risk)};'>{risk}</span></li>
            <li><b>Tahmini Gecikme:</b> {gecikme:.1f} gün</li>
            <li><b>Ödeme Sayısı:</b> {ozellikler.get('odeme_sayisi', 0)}</li>
            <li><b>Ortalama Gecikme:</b> {ozellikler.get('ortalama_gecikme', 0):.1f} gün</li>
        </ul>
        
        <p><b>💡 Yorum:</b></p>
        <p style='background:#f9f9ff; padding:10px; border-left:3px solid {self._get_score_color(skor)};'>
        {yorum}
        </p>
        
        <p><b>📋 Tavsiyeler:</b></p>
        <ul>
        {tavsiye}
        </ul>
        
        <p><b>⚠️ Önemli Notlar:</b></p>
        <ul>
        {self._build_tips_html(skor)}
        </ul>
        </div>
        """
        self.detail_text.setHtml(html)

    def _build_tips_html(self, skor):
        if skor >= 80:
            return "<li style='color:#15803d;'>✅ Müşteri güvenilir görünüyor, standart ödeme takvimine devam edin.</li>"
        if skor >= 50:
            return "<li style='color:#f59e0b;'>⚠️ Düzenli hatırlatma ve izleme yapın.</li>"
        return "<li style='color:#dc2626;'>🚨 Peşin veya teminat isteyin; gecikme riski yüksek.</li>"
    
    def _generate_detailed_advice(self, skor, risk, gecikme, ozellikler):
        """Detaylı tavsiyeler oluştur"""
        tavsiyeler = []
        
        if skor >= 80:
            tavsiyeler.append("<li style='color:#15803d;'>✅ Standart ödeme koşulları uygulanabilir.</li>")
            tavsiyeler.append("<li style='color:#15803d;'>✅ Uzun vadeli iş ilişkisi kurulabilir.</li>")
            tavsiyeler.append("<li style='color:#15803d;'>✅ Özel indirim veya avantajlar sunulabilir.</li>")
        elif skor >= 50:
            tavsiyeler.append("<li style='color:#f59e0b;'>⚠️ Vade tarihinden önce hatırlatma yapın.</li>")
            tavsiyeler.append("<li style='color:#f59e0b;'>⚠️ Ödeme planını netleştirin.</li>")
            tavsiyeler.append("<li style='color:#f59e0b;'>⚠️ Düzenli takip ve iletişim kurun.</li>")
            if gecikme > 10:
                tavsiyeler.append("<li style='color:#f59e0b;'>⚠️ Gecikme durumunda erken müdahale yapın.</li>")
        else:
            tavsiyeler.append("<li style='color:#dc2626;'>🚨 Peşin ödeme veya teminat talep edin.</li>")
            tavsiyeler.append("<li style='color:#dc2626;'>🚨 Kısa vadeli ödeme planı uygulayın.</li>")
            tavsiyeler.append("<li style='color:#dc2626;'>🚨 Sıkı takip ve kontrol mekanizması kurun.</li>")
            tavsiyeler.append("<li style='color:#dc2626;'>🚨 Yasal yollara başvurma riskini değerlendirin.</li>")
        
        # Gecikme bazlı ek tavsiyeler
        if gecikme > 30:
            tavsiyeler.append("<li style='color:#dc2626;'>🚨 Kritik: 30+ gün gecikme riski var, acil önlem alın!</li>")
        elif gecikme > 15:
            tavsiyeler.append("<li style='color:#f59e0b;'>⚠️ 15+ gün gecikme bekleniyor, erken uyarı sistemi kurun.</li>")
        
        # Ödeme sayısı bazlı tavsiyeler
        odeme_sayisi = ozellikler.get('odeme_sayisi', 0)
        if odeme_sayisi < 3:
            tavsiyeler.append("<li style='color:#f59e0b;'>⚠️ Az sayıda ödeme geçmişi var, dikkatli olun.</li>")
        
        return "\n".join(tavsiyeler) if tavsiyeler else "<li>Düzenli takip önerilir.</li>"
    
    def _generate_comment(self, skor, risk, gecikme, ozellikler):
        """Detaylı yorum oluştur"""
        ortalama_gecikme = ozellikler.get('ortalama_gecikme', 0)
        odeme_sayisi = ozellikler.get('odeme_sayisi', 0)
        gecikme_std = ozellikler.get('gecikme_std', 0)
        
        yorum_parts = []
        
        # Skor bazlı yorum
        if skor >= 80:
            yorum_parts.append("Bu müşteri güvenilir bir ödeme geçmişine sahip.")
        elif skor >= 50:
            yorum_parts.append("Bu müşterinin ödeme davranışı orta seviyede.")
        else:
            yorum_parts.append("Bu müşteri için ödeme riski yüksek görünüyor.")
        
        # Gecikme bazlı yorum
        if gecikme < 0:
            yorum_parts.append(f"Tahmin edilen ödeme vade tarihinden {abs(gecikme):.1f} gün önce yapılacak.")
        elif gecikme == 0:
            yorum_parts.append("Ödeme vade tarihinde yapılması bekleniyor.")
        else:
            yorum_parts.append(f"Ödeme vade tarihinden {gecikme:.1f} gün sonra yapılması bekleniyor.")
        
        # Ortalama gecikme bazlı yorum
        if ortalama_gecikme < 0:
            yorum_parts.append(f"Geçmişte ortalama {abs(ortalama_gecikme):.1f} gün erken ödeme yapmış.")
        elif ortalama_gecikme > 0:
            yorum_parts.append(f"Geçmişte ortalama {ortalama_gecikme:.1f} gün gecikme yaşanmış.")
        else:
            yorum_parts.append("Geçmişte genellikle zamanında ödeme yapılmış.")
        
        # Tutarlılık bazlı yorum
        if gecikme_std > 15:
            yorum_parts.append("Ödeme davranışında tutarsızlık gözleniyor.")
        elif gecikme_std < 5:
            yorum_parts.append("Ödeme davranışı tutarlı görünüyor.")
        
        # Ödeme sayısı bazlı yorum
        if odeme_sayisi < 3:
            yorum_parts.append(f"Sadece {odeme_sayisi} ödeme geçmişi mevcut, daha fazla veri ile daha doğru tahmin yapılabilir.")
        elif odeme_sayisi >= 10:
            yorum_parts.append(f"{odeme_sayisi} ödeme geçmişi ile güvenilir bir analiz yapılmıştır.")
        
        return " ".join(yorum_parts)
    
    def _get_score_color(self, skor):
        """Skor için renk döndür"""
        if skor >= 80:
            return self.color_success
        elif skor >= 50:
            return self.color_warning
        else:
            return self.color_danger
    
    def _get_risk_color(self, risk):
        """Risk grubu için renk döndür"""
        risk_lower = risk.lower()
        if 'düşük' in risk_lower or 'low' in risk_lower:
            return self.color_success
        elif 'orta' in risk_lower or 'medium' in risk_lower:
            return self.color_warning
        else:
            return self.color_danger
    
    def _get_color_for_risk(self, risk):
        """Risk grubu için QColor döndür"""
        return QColor(self._get_risk_color(risk))

    def show_error(self, message):
        """Hata mesajı göster"""
        QMessageBox.critical(self, "Hata", message)

    def show_success(self, message):
        """Başarı mesajı göster"""
        QMessageBox.information(self, "Başarılı", message)

    def _get_color_for_score(self, skor):
        """Skor için renk belirle"""
        if skor >= 80:
            return QColor(self.color_success)
        elif skor >= 50:
            return QColor(self.color_warning)
        else:
            return QColor(self.color_danger)

    def _group_style(self):
        return f"""
            QGroupBox {{
                background: {self.color_card};
                border: 1px solid {self.color_border};
                border-radius: 4px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 6px;
                color: {self.color_primary_dark};
                font-weight: 700;
            }}
        """

    def _tint(self, hex_color, factor):
        """Hex rengi parlaklaştır/koyulaştır"""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
