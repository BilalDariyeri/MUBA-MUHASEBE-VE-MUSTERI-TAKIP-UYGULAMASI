"""
Email Service - E-posta gönderme servisi
Gmail SMTP ile e-posta gönderme
Kalıcı bağlantı ve otomatik onay ile
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
from typing import List, Optional
import os


class EmailService:
    """E-posta gönderme servisi - Kalıcı Gmail bağlantısı"""
    
    _instance = None
    _server = None
    
    def __new__(cls, smtp_server: str = None, smtp_port: int = None, 
                 email: str = None, password: str = None):
        """Singleton pattern - Tek bir instance"""
        if cls._instance is None:
            cls._instance = super(EmailService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, smtp_server: str = None, smtp_port: int = None, 
                 email: str = None, password: str = None):
        """Email servisi başlat"""
        from config import Config
        
        # Sadece bir kez initialize et
        if hasattr(self, '_initialized'):
            return
        
        self.smtp_server = smtp_server or os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.environ.get('SMTP_PORT', '587'))
        # Önce parametre, sonra env, sonra config'den al
        self.email = email or os.environ.get('GMAIL_EMAIL') or getattr(Config, 'GMAIL_EMAIL', '')
        self.password = password or os.environ.get('GMAIL_PASSWORD') or getattr(Config, 'GMAIL_PASSWORD', '')
        # Şifredeki boşlukları kaldır (uygulama şifreleri boşluksuz olmalı)
        if self.password:
            self.password = self.password.replace(' ', '')
        self.use_tls = self.smtp_port == 587
        self._initialized = True
    
    def _get_connection(self):
        """SMTP bağlantısı oluştur - Uygulama şifresi ile onay istemez"""
        try:
            # Her seferinde yeni bağlantı kur (daha güvenli ve temiz)
            # Uygulama şifresi kullanıldığı için onay istemez
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30)
            
            # Giriş yap - Uygulama şifresi kullanıldığı için onay istemez
            # Normal şifre kullanılırsa Google güvenlik uyarısı verir
            server.login(self.email, self.password)
            
            return server
        except smtplib.SMTPAuthenticationError as e:
            raise Exception(
                f"Gmail kimlik doğrulama hatası!\n\n"
                f"Lütfen şunları kontrol edin:\n"
                f"1. 2 Adımlı Doğrulama açık mı?\n"
                f"2. Uygulama şifresi kullanıyor musunuz? (Normal şifre değil!)\n"
                f"3. Uygulama şifresi doğru mu?\n\n"
                f"Hata: {str(e)}"
            )
        except Exception as e:
            raise Exception(f"SMTP bağlantı hatası: {str(e)}")
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   attachments: List[str] = None, is_html: bool = False) -> bool:
        """E-posta gönder - Türkçe karakter desteği ile UTF-8 encoding"""
        """E-posta gönder - Kalıcı bağlantı ile, onay istemez"""
        try:
            if not self.email or not self.password:
                raise ValueError("Gmail e-posta ve şifre ayarlanmamış. Lütfen config.py veya .env dosyasında ayarlayın.")
            
            # E-posta mesajı oluştur (Türkçe karakter desteği ile: ı, ş, ö, ü, ğ, ç)
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = to_email
            # Subject'i UTF-8 encoding ile encode et (Türkçe karakterler için)
            msg['Subject'] = Header(subject, 'utf-8')
            
            # Mesaj gövdesi (Türkçe karakter desteği ile UTF-8)
            if is_html:
                html_part = MIMEText(body, 'html', 'utf-8')
                html_part.set_charset('utf-8')
                msg.attach(html_part)
            else:
                plain_part = MIMEText(body, 'plain', 'utf-8')
                plain_part.set_charset('utf-8')
                msg.attach(plain_part)
            
            # Ekler
            if attachments:
                for filepath in attachments:
                    if os.path.exists(filepath):
                        with open(filepath, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        filename = os.path.basename(filepath)
                        # Türkçe karakterler için filename'i encode et
                        import urllib.parse
                        encoded_filename = urllib.parse.quote(filename.encode('utf-8'))
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename*=UTF-8\'\'{encoded_filename}'
                        )
                        msg.attach(part)
            
            # SMTP bağlantısını kullan (uygulama şifresi ile onay istemez)
            server = self._get_connection()
            server.send_message(msg)
            
            # Bağlantıyı kapat (her gönderimden sonra temiz bağlantı)
            # Uygulama şifresi kullanıldığı için bir sonraki gönderimde onay istemez
            self._close_connection()
            
            return True
        except Exception as e:
            # Hata durumunda bağlantıyı kapat
            self._close_connection()
            raise Exception(f"E-posta gönderme hatası: {str(e)}")
    
    def _close_connection(self):
        """SMTP bağlantısını kapat"""
        try:
            if self._server:
                self._server.quit()
        except:
            pass
        finally:
            self._server = None
    
    def __del__(self):
        """Nesne silindiğinde bağlantıyı kapat"""
        self._close_connection()
    
    def send_fatura_email(self, to_email: str, fatura_data: dict, pdf_path: str) -> bool:
        """Fatura e-postası gönder"""
        try:
            cari_hesap = fatura_data.get('cariHesap', {})
            if isinstance(cari_hesap, str):
                import json
                try:
                    cari_hesap = json.loads(cari_hesap)
                except:
                    cari_hesap = {}
            
            fatura_no = fatura_data.get('faturaNo', '-')
            unvan = cari_hesap.get('unvani', 'Sayın Müşteri')
            # Toplam tutarları hesapla
            net_tutar = float(fatura_data.get('netTutar', 0) or fatura_data.get('net_tutar', 0) or 0)
            kdv_tutari = float(fatura_data.get('kdvTutari', 0) or fatura_data.get('kdv_tutari', 0) or 0)
            toplam = float(fatura_data.get('toplam', 0) or 0)
            
            # Eğer net tutar ve KDV yoksa, toplamdan hesapla
            if net_tutar == 0 and kdv_tutari == 0 and toplam > 0:
                # Genellikle %18 KDV varsayılıyor
                net_tutar = toplam / 1.18
                kdv_tutari = toplam - net_tutar
            
            subject = f"E-Fatura: {fatura_no} - MUBA"
            
            # HTML e-posta içeriği - E-Fatura formatında (Türkçe karakter desteği)
            body = f"""
            <!DOCTYPE html>
            <html lang="tr">
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                <meta charset="UTF-8">
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        margin: 0; 
                        padding: 0; 
                        background-color: #f5f5f5;
                    }}
                    .email-container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: white;
                    }}
                    .header {{ 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; 
                        padding: 30px 20px; 
                        text-align: center; 
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 24px;
                    }}
                    .content {{ 
                        padding: 30px 20px; 
                        line-height: 1.6;
                    }}
                    .fatura-info {{
                        background-color: #f8f9fa;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                        border-left: 4px solid #667eea;
                    }}
                    .fatura-info p {{
                        margin: 5px 0;
                    }}
                    .footer {{ 
                        background-color: #f5f5f5; 
                        padding: 20px; 
                        text-align: center; 
                        font-size: 12px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="header">
                        <h1>MUBA - E-Fatura</h1>
                        <p style="margin: 10px 0 0 0; font-size: 14px;">Mali İşler Yönetim Sistemi</p>
                    </div>
                    <div class="content">
                        <p>Sayın <strong>{unvan}</strong>,</p>
                        <p>Faturanız ektedir. Lütfen ekteki PDF dosyasını inceleyiniz.</p>
                        
                        <div class="fatura-info">
                            <p><strong>Fatura No:</strong> {fatura_no}</p>
                            <p><strong>Fatura Tarihi:</strong> {fatura_data.get('tarih', '-')}</p>
                            <p><strong>Net Tutar:</strong> {net_tutar:,.2f} ₺</p>
                            <p><strong>KDV Tutarı:</strong> {kdv_tutari:,.2f} ₺</p>
                            <p style="font-size: 16px; font-weight: bold; margin-top: 10px; padding-top: 10px; border-top: 2px solid #667eea;">
                                <strong>Toplam Tutar:</strong> {toplam:,.2f} ₺
                            </p>
                        </div>
                        
                        <p>Fatura detayları için ekteki PDF dosyasını inceleyebilirsiniz.</p>
                        <p>Herhangi bir sorunuz olursa lütfen bizimle iletişime geçiniz.</p>
                        
                        <p style="margin-top: 30px;">
                            Saygılarımızla,<br/>
                            <strong>MUBA</strong><br/>
                            <small>dariyeribilal3@gmail.com</small>
                        </p>
                    </div>
                    <div class="footer">
                        <p>Bu e-posta otomatik olarak <strong>dariyeribilal3@gmail.com</strong> adresinden gönderilmiştir.</p>
                        <p>MUBA - Mali İşler Yönetim Sistemi</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self.send_email(to_email, subject, body, [pdf_path], is_html=True)
        except Exception as e:
            raise Exception(f"Fatura e-postası gönderme hatası: {str(e)}")

