"""
Hesap Makinesi Dialog - MUBA teması
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class HesapMakinesiDialog(QDialog):
    """Basit hesap makinesi dialog'u"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hesap Makinesi")
        self.setFixedSize(320, 420)
        self.current = "0"
        self.total = 0
        self.operation = None
        self.init_ui()
    
    def init_ui(self):
        """UI'yi başlat"""
        self.setStyleSheet("""
            QDialog { background: #e7e3ff; }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Ekran
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setText("0")
        self.display.setAlignment(Qt.AlignRight)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.display.setFont(font)
        self.display.setStyleSheet("""
            QLineEdit {
                background-color: #0f112b;
                color: #ffffff;
                border: 1px solid #233568;
                border-radius: 6px;
                padding: 12px;
                font-size: 20px;
            }
        """)
        layout.addWidget(self.display)
        
        # Butonlar
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(6)
        
        buttons = [
            ('C', 0, 0), ('CE', 0, 1), ('⌫', 0, 2), ('÷', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('±', 4, 0), ('0', 4, 1), ('.', 4, 2), ('=', 4, 3),
        ]
        
        for text, row, col in buttons:
            btn = self.create_button(text)
            buttons_layout.addWidget(btn, row, col)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def create_button(self, text):
        """Buton oluştur"""
        btn = QPushButton(text)
        btn.setMinimumHeight(52)
        if text.isdigit() or text == '.':
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #233568;
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    font-size: 16px;
                    font-weight: 600;
                }
                QPushButton:hover { background-color: #1d2b56; }
                QPushButton:pressed { background-color: #182347; }
            """)
        elif text in ['+', '-', '×', '÷', '=']:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f48c06;
                    color: #0f112b;
                    border: none;
                    border-radius: 6px;
                    font-size: 16px;
                    font-weight: 700;
                }
                QPushButton:hover { background-color: #d87c05; }
                QPushButton:pressed { background-color: #bf6d04; }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f1f9;
                    color: #1e2a4c;
                    border: 1px solid #d0d4f2;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover { background-color: #e2e5f5; }
                QPushButton:pressed { background-color: #d6daf0; }
            """)
        
        btn.clicked.connect(lambda checked, t=text: self.on_button_clicked(t))
        return btn
    
    def on_button_clicked(self, text):
        """Buton tıklandığında"""
        if text.isdigit():
            if self.current == "0":
                self.current = text
            else:
                self.current += text
            self.update_display()
        
        elif text == '.':
            if '.' not in self.current:
                self.current += '.'
                self.update_display()
        
        elif text in ['+', '-', '×', '÷']:
            if self.operation:
                self.calculate()
            self.total = float(self.current)
            self.operation = text
            self.current = "0"
        
        elif text == '=':
            if self.operation:
                self.calculate()
                self.operation = None
        
        elif text == 'C':
            self.current = "0"
            self.total = 0
            self.operation = None
            self.update_display()
        
        elif text == 'CE':
            self.current = "0"
            self.update_display()
        
        elif text == '⌫':
            if len(self.current) > 1:
                self.current = self.current[:-1]
            else:
                self.current = "0"
            self.update_display()
        
        elif text == '±':
            if self.current != "0":
                if self.current.startswith('-'):
                    self.current = self.current[1:]
                else:
                    self.current = '-' + self.current
                self.update_display()
    
    def calculate(self):
        """Hesaplama yap"""
        try:
            current_value = float(self.current)
            
            if self.operation == '+':
                result = self.total + current_value
            elif self.operation == '-':
                result = self.total - current_value
            elif self.operation == '×':
                result = self.total * current_value
            elif self.operation == '÷':
                if current_value == 0:
                    self.display.setText("Hata")
                    self.current = "0"
                    return
                result = self.total / current_value
            else:
                result = current_value
            
            if result == int(result):
                self.current = str(int(result))
            else:
                self.current = str(result)
            
            self.total = result
            self.update_display()
        except:
            self.display.setText("Hata")
            self.current = "0"
    
    def update_display(self):
        """Ekranı güncelle"""
        self.display.setText(self.current)
