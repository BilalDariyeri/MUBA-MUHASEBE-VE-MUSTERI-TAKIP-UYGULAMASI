"""
Admin Panel View - Sistem yönetimi ve log görüntüleme (MUBA teması)
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QComboBox, QGroupBox, QFormLayout, QLineEdit, QDateEdit,
    QTextEdit, QDialog, QDialogButtonBox, QTabWidget
)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from datetime import datetime
from services.logging_service import LoggingService
from models.user_model import UserModel


class AdminLogsWorker(QThread):
    """Log verilerini yükleyen worker thread"""
    logs_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, filters=None):
        super().__init__()
        self.filters = filters or {}
        self.logging_service = LoggingService()

    def run(self):
        """Thread'de çalışacak işlem"""
        try:
            logs = self.logging_service.get_logs(
                user_id=self.filters.get('user_id'),
                entity_type=self.filters.get('entity_type'),
                action=self.filters.get('action'),
                limit=self.filters.get('limit', 100)
            )
            self.logs_loaded.emit(logs)
        except Exception as e:
            self.error_occurred.emit(str(e))


class AddUserDialog(QDialog):
    """Kullanıcı ekleme dialog'u"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Kullanıcı Ekle")
        self.setFixedSize(400, 350)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Yeni Kullanıcı Ekle")
        title.setFont(QFont("", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ad Soyad")
        self.name_input.setMinimumHeight(35)
        form.addRow("Ad Soyad *:", self.name_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ornek@email.com")
        self.email_input.setMinimumHeight(35)
        form.addRow("E-posta *:", self.email_input)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("kullaniciadi (opsiyonel)")
        self.username_input.setMinimumHeight(35)
        form.addRow("Kullanıcı Adı:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("En az 6 karakter")
        self.password_input.setMinimumHeight(35)
        form.addRow("Şifre *:", self.password_input)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "staff", "admin"])
        self.role_combo.setMinimumHeight(35)
        form.addRow("Rol:", self.role_combo)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def validate_and_accept(self):
        """Form validasyonu ve kabul"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Uyarı", "Ad Soyad gereklidir!")
            return
        if not self.email_input.text().strip():
            QMessageBox.warning(self, "Uyarı", "E-posta gereklidir!")
            return
        if '@' not in self.email_input.text():
            QMessageBox.warning(self, "Uyarı", "Geçerli bir e-posta adresi giriniz!")
            return
        if not self.password_input.text() or len(self.password_input.text()) < 6:
            QMessageBox.warning(self, "Uyarı", "Şifre en az 6 karakter olmalıdır!")
            return
        self.accept()

    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'email': self.email_input.text().strip(),
            'username': self.username_input.text().strip() or None,
            'password': self.password_input.text(),
            'role': self.role_combo.currentText()
        }


class AdminPanelView(QWidget):
    """Admin Panel görünümü - Sistem logları ve yönetim"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._init_colors()
        self.logs = []
        self.logging_service = LoggingService()
        self.user_model = UserModel()
        self.init_ui()
        self.load_logs()

    def _init_colors(self):
        self.color_bg = "#e7e3ff"
        self.color_card = "#ffffff"
        self.color_border = "#d0d4f2"
        self.color_primary = "#233568"
        self.color_primary_dark = "#0f112b"
        self.color_accent = "#f48c06"
        self.color_success = "#16a34a"
        self.color_danger = "#ef4444"
        self.color_muted = "#6b7280"
        self.color_text = "#1e2a4c"

    def _style_btn(self, btn, bg, fg="#ffffff"):
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {fg};
                border: none;
                padding: 10px 14px;
                font-weight: 700;
                border-radius: 4px;
            }}
            QPushButton:hover {{ background: {self._tint(bg, 1.07)}; }}
            QPushButton:pressed {{ background: {self._tint(bg, 0.9)}; }}
        """)

    def _tint(self, hex_color, factor):
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def init_ui(self):
        """UI'yi başlat"""
        self.setObjectName("admin_root")
        self.setStyleSheet(f"""
            QWidget#admin_root {{
                background: {self.color_bg};
            }}
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
            QTableWidget {{
                background: {self.color_card};
                border: 1px solid {self.color_border};
                alternate-background-color: #f8f9ff;
            }}
            QHeaderView::section {{
                background-color: #f3f4ff;
                padding: 8px;
                border: 1px solid {self.color_border};
                font-weight: bold;
                color: {self.color_text};
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Başlık ve geri butonu
        header_layout = QHBoxLayout()
        self.btn_geri = QPushButton("← Geri")
        self._style_btn(self.btn_geri, self.color_primary)
        self.btn_geri.clicked.connect(self.on_geri)
        header_layout.addWidget(self.btn_geri)

        title = QLabel("Admin Paneli")
        title.setFont(QFont("", 18, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        tabs = QTabWidget()

        logs_tab = self.create_logs_tab()
        tabs.addTab(logs_tab, "Sistem Logları")

        users_tab = self.create_users_tab()
        tabs.addTab(users_tab, "Kullanıcı Yönetimi")

        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_logs_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(10, 10, 10, 10)

        toolbar = QHBoxLayout()

        self.btn_sil = QPushButton("🗑 Seçili Logları Sil")
        self._style_btn(self.btn_sil, self.color_danger)
        self.btn_sil.clicked.connect(self.delete_selected_logs)
        toolbar.addWidget(self.btn_sil)

        self.btn_tumu_sil = QPushButton("⚠ Tüm Logları Sil")
        self._style_btn(self.btn_tumu_sil, "#c2410c")
        self.btn_tumu_sil.clicked.connect(self.delete_all_logs)
        toolbar.addWidget(self.btn_tumu_sil)

        toolbar.addStretch()

        self.btn_yenile = QPushButton("🔄 Yenile")
        self._style_btn(self.btn_yenile, self.color_success)
        self.btn_yenile.clicked.connect(self.load_logs)
        toolbar.addWidget(self.btn_yenile)
        layout.addLayout(toolbar)

        # Filtreler
        filter_group = QGroupBox("Filtreler")
        filter_layout = QHBoxLayout()

        self.entity_filter = QComboBox()
        self.entity_filter.addItem("Tümü", None)
        self.entity_filter.addItem("Cari Hesap", "cari_hesap")
        self.entity_filter.addItem("Fatura", "fatura")
        self.entity_filter.addItem("Malzeme", "malzeme")
        self.entity_filter.addItem("Kullanıcı", "user")
        self.entity_filter.addItem("Tahsilat", "tahsilat")
        self.entity_filter.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(QLabel("İşlem Tipi:"))
        filter_layout.addWidget(self.entity_filter)

        self.action_filter = QComboBox()
        self.action_filter.addItem("Tümü", None)
        self.action_filter.addItem("Oluşturma", "CREATE")
        self.action_filter.addItem("Güncelleme", "UPDATE")
        self.action_filter.addItem("Silme", "DELETE")
        self.action_filter.addItem("Giriş", "LOGIN")
        self.action_filter.addItem("Çıkış", "LOGOUT")
        self.action_filter.addItem("E-posta Gönder", "SEND_EMAIL")
        self.action_filter.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(QLabel("Aksiyon:"))
        filter_layout.addWidget(self.action_filter)

        filter_layout.addStretch()
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Log tablosu
        logs_group = QGroupBox("Sistem Logları")
        logs_layout = QVBoxLayout()

        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(7)
        self.logs_table.setHorizontalHeaderLabels([
            "Tarih/Saat", "Kullanıcı", "Aksiyon", "İşlem Tipi", "Kayıt ID", "Detay", "IP Adresi"
        ])
        self.logs_table.horizontalHeader().setStretchLastSection(True)
        self.logs_table.setAlternatingRowColors(True)
        self.logs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.logs_table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.logs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.logs_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.logs_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.logs_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.logs_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        logs_layout.addWidget(self.logs_table)
        logs_group.setLayout(logs_layout)
        layout.addWidget(logs_group)

        # İstatistikler
        stats_group = QGroupBox("İstatistikler")
        stats_layout = QHBoxLayout()

        self.stats_label = QLabel("Toplam Log: 0")
        self.stats_label.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {self.color_text};")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        widget.setLayout(layout)
        return widget

    def create_users_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(10, 10, 10, 10)

        toolbar = QHBoxLayout()

        self.btn_add_user = QPushButton("Yeni Kullanıcı")
        self._style_btn(self.btn_add_user, self.color_success)
        self.btn_add_user.clicked.connect(self.add_user)
        toolbar.addWidget(self.btn_add_user)

        self.btn_delete_user = QPushButton("Seçili Kullanıcıyı Sil")
        self._style_btn(self.btn_delete_user, self.color_danger)
        self.btn_delete_user.clicked.connect(self.delete_user)
        toolbar.addWidget(self.btn_delete_user)

        toolbar.addStretch()

        self.btn_refresh_users = QPushButton("Yenile")
        self._style_btn(self.btn_refresh_users, self.color_primary)
        self.btn_refresh_users.clicked.connect(self.load_users)
        toolbar.addWidget(self.btn_refresh_users)

        layout.addLayout(toolbar)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["ID", "Ad Soyad", "E-Posta", "Rol"])
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setSelectionMode(QTableWidget.SingleSelection)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.users_table)

        widget.setLayout(layout)
        self.load_users()
        return widget

    # --- Log fonksiyonları ---
    def on_filter_changed(self):
        self.load_logs()

    def load_logs(self):
        try:
            worker = AdminLogsWorker({
                'entity_type': self.entity_filter.currentData(),
                'action': self.action_filter.currentData(),
                'limit': 200
            })
            worker.logs_loaded.connect(self.on_logs_loaded)
            worker.error_occurred.connect(lambda msg: QMessageBox.critical(self, "Hata", msg))
            worker.start()
            self.worker = worker
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Loglar yüklenirken hata oluştu:\n{str(e)}")

    def on_logs_loaded(self, logs):
        self.logs = logs or []
        self.refresh_logs_table()

    def refresh_logs_table(self):
        self.logs_table.setRowCount(len(self.logs))
        for i, log in enumerate(self.logs):
            self.logs_table.setItem(i, 0, QTableWidgetItem(str(log.get('created_at', ''))))
            self.logs_table.setItem(i, 1, QTableWidgetItem(str(log.get('user_name', '-'))))
            self.logs_table.setItem(i, 2, QTableWidgetItem(str(log.get('action', '-'))))
            self.logs_table.setItem(i, 3, QTableWidgetItem(str(log.get('entity_type', '-'))))
            self.logs_table.setItem(i, 4, QTableWidgetItem(str(log.get('entity_id', '-'))))
            self.logs_table.setItem(i, 5, QTableWidgetItem(str(log.get('detail', '-'))))
            self.logs_table.setItem(i, 6, QTableWidgetItem(str(log.get('ip_address', '-'))))
        self.stats_label.setText(f"Toplam Log: {len(self.logs)}")

    def delete_selected_logs(self):
        selected_rows = set([idx.row() for idx in self.logs_table.selectionModel().selectedRows()])
        if not selected_rows:
            QMessageBox.information(self, "Bilgi", "Silmek için log seçiniz.")
            return
        log_ids = []
        for row in selected_rows:
            try:
                log_id = self.logs[row].get('id')
                if log_id:
                    log_ids.append(log_id)
            except IndexError:
                continue

        if not log_ids:
            QMessageBox.information(self, "Bilgi", "Seçili logların ID bilgisi bulunamadı.")
            return

        reply = QMessageBox.question(
            self, 'Onay',
            f'{len(log_ids)} adet log kaydını silmek istediğinize emin misiniz?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                deleted_count = self.logging_service.delete_logs(log_ids)
                QMessageBox.information(self, "Başarılı", f"{deleted_count} adet log kaydı başarıyla silindi!")
                self.load_logs()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Loglar silinirken hata oluştu:\n{str(e)}")

    def delete_all_logs(self):
        reply = QMessageBox.warning(
            self, 'DİKKAT!',
            'TÜM log kayıtlarını silmek istediğinize emin misiniz?\n\nBu işlem geri alınamaz!',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            reply2 = QMessageBox.warning(
                self, 'SON ONAY',
                'Bu işlem TÜM log kayıtlarını kalıcı olarak silecektir!\n\nDevam etmek istiyor musunuz?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply2 == QMessageBox.Yes:
                try:
                    deleted_count = self.logging_service.delete_all_logs()
                    QMessageBox.information(self, "Başarılı", f"{deleted_count} adet log kaydı başarıyla silindi!")
                    self.load_logs()
                except Exception as e:
                    QMessageBox.critical(self, "Hata", f"Loglar silinirken hata oluştu:\n{str(e)}")

    # --- Kullanıcı işlemleri ---
    def load_users(self):
        try:
            users = self.user_model.get_all_users()
            self.users_table.setRowCount(len(users))
            for i, u in enumerate(users):
                self.users_table.setItem(i, 0, QTableWidgetItem(str(u.get('id', '-'))))
                self.users_table.setItem(i, 1, QTableWidgetItem(str(u.get('name', '-'))))
                self.users_table.setItem(i, 2, QTableWidgetItem(str(u.get('email', '-'))))
                self.users_table.setItem(i, 3, QTableWidgetItem(str(u.get('role', '-'))))
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kullanıcılar yüklenirken hata oluştu:\n{str(e)}")

    def add_user(self):
        dialog = AddUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.user_model.create_user(
                    name=data['name'],
                    email=data['email'],
                    password=data['password'],
                    role=data['role'],
                    username=data['username']
                )
                QMessageBox.information(self, "Başarılı", "Kullanıcı başarıyla eklendi.")
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Kullanıcı eklenirken hata oluştu:\n{str(e)}")

    def delete_user(self):
        selected_rows = self.users_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Bilgi", "Silmek için kullanıcı seçiniz.")
            return
        row = selected_rows[0].row()
        user_id_item = self.users_table.item(row, 0)
        if not user_id_item:
            return
        user_id = user_id_item.text()

        reply = QMessageBox.question(
            self, 'Onay',
            f"ID {user_id} olan kullanıcıyı silmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.user_model.delete_user(user_id)
                QMessageBox.information(self, "Başarılı", "Kullanıcı silindi.")
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Kullanıcı silinirken hata oluştu:\n{str(e)}")

    # --- Genel ---
    def on_geri(self):
        if self.parent_window and hasattr(self.parent_window, 'show_dashboard'):
            self.parent_window.show_dashboard()

