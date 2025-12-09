"""
Fatura PDF Service - E-Fatura formatında PDF oluşturma servisi
Gümüş Teknik formatına göre düzenlenmiş
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
import os
import json
import uuid

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class FaturaPDFService:
    """E-Fatura formatında PDF oluşturma servisi"""
    
    def __init__(self):
        # Türkçe karakter desteği için Arial fontunu yükle
        self._register_turkish_fonts()
    
    def _register_turkish_fonts(self):
        """Türkçe karakter desteği için fontları kaydet"""
        try:
            import platform
            system = platform.system()
            
            # Windows için Arial font yolu
            if system == 'Windows':
                arial_paths = [
                    r'C:\Windows\Fonts\arial.ttf',
                    r'C:\Windows\Fonts\ARIAL.TTF',
                    r'C:\Windows\Fonts\arialbd.ttf',  # Bold
                    r'C:\Windows\Fonts\ARIALBD.TTF',
                ]
            else:
                # Linux/Mac için alternatif yollar
                arial_paths = [
                    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                    '/System/Library/Fonts/Supplemental/Arial.ttf',
                ]
            
            # Arial Regular
            arial_regular = None
            for path in arial_paths:
                if os.path.exists(path):
                    try:
                        pdfmetrics.registerFont(TTFont('Arial', path))
                        arial_regular = 'Arial'
                        break
                    except:
                        continue
            
            # Arial Bold
            arial_bold = None
            if system == 'Windows':
                bold_paths = [
                    r'C:\Windows\Fonts\arialbd.ttf',
                    r'C:\Windows\Fonts\ARIALBD.TTF',
                ]
            else:
                bold_paths = [
                    '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                ]
            
            for path in bold_paths:
                if os.path.exists(path):
                    try:
                        pdfmetrics.registerFont(TTFont('Arial-Bold', path))
                        arial_bold = 'Arial-Bold'
                        break
                    except:
                        continue
            
            # Eğer Arial bulunamazsa, DejaVu Sans dene (Linux için)
            if not arial_regular:
                dejavu_paths = [
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                    '/usr/share/fonts/TTF/DejaVuSans.ttf',
                ]
                for path in dejavu_paths:
                    if os.path.exists(path):
                        try:
                            pdfmetrics.registerFont(TTFont('Arial', path))
                            arial_regular = 'Arial'
                            break
                        except:
                            continue
            
            # Font kayıt durumunu sakla
            self.font_regular = arial_regular or 'Helvetica'
            self.font_bold = arial_bold or 'Helvetica-Bold'
            
        except Exception as e:
            # Hata durumunda varsayılan fontları kullan
            print(f"Font yükleme hatası: {e}")
            self.font_regular = 'Helvetica'
            self.font_bold = 'Helvetica-Bold'
    
    def generate_efatura_pdf(self, fatura_data: Dict, filename: Optional[str] = None) -> str:
        """E-Fatura formatında PDF oluştur - Gümüş Teknik formatına göre"""
        try:
            if not filename:
                fatura_no = fatura_data.get('faturaNo', 'FATURA')
                filename = f"Fatura_{fatura_no}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # PDF oluştur
            doc = SimpleDocTemplate(filename, pagesize=A4,
                                    rightMargin=10*mm, leftMargin=10*mm,
                                    topMargin=10*mm, bottomMargin=10*mm)
            
            story = []
            styles = getSampleStyleSheet()
            
            # Özel Stiller - Türkçe karakter desteği ile
            style_normal = ParagraphStyle(
                name='NormalYz', 
                parent=styles['Normal'], 
                fontSize=8, 
                leading=10,
                fontName=self.font_regular
            )
            style_bold = ParagraphStyle(
                name='BoldYz', 
                parent=styles['Normal'], 
                fontSize=8, 
                leading=10, 
                fontName=self.font_bold
            )
            style_small = ParagraphStyle(
                name='SmallYz', 
                parent=styles['Normal'], 
                fontSize=7, 
                leading=8,
                fontName=self.font_regular
            )
            
            # Cari hesap bilgilerini al
            cari_hesap = fatura_data.get('cariHesap', {})
            if isinstance(cari_hesap, str):
                try:
                    cari_hesap = json.loads(cari_hesap)
                except:
                    cari_hesap = {}
            
            # Eğer cari hesap içinde email yoksa veritabanından çek
            if not cari_hesap.get('email'):
                cari_id = fatura_data.get('cariId', '')
                if cari_id:
                    try:
                        from models.cari_hesap_model import CariHesapModel
                        cari_model = CariHesapModel()
                        cari_data = cari_model.get_by_id(cari_id)
                        if cari_data:
                            cari_hesap['email'] = cari_data.get('email', '')
                            cari_hesap['adres'] = cari_data.get('adres', cari_hesap.get('adres', ''))
                            cari_hesap['telefon'] = cari_data.get('telefon', cari_hesap.get('telefon', ''))
                            cari_hesap['vergiNo'] = cari_data.get('vergiNo', cari_hesap.get('vergiNo', ''))
                            cari_hesap['vergiDairesi'] = cari_data.get('vergiDairesi', cari_hesap.get('vergiDairesi', ''))
                            cari_hesap['sehir'] = cari_data.get('sehir', cari_hesap.get('sehir', ''))
                    except:
                        pass
            
            # Gönderici bilgileri (Config'den al)
            from config import Config
            sender_unvan = Config.COMPANY_NAME
            sender_adres = Config.COMPANY_ADDRESS
            sender_sehir = Config.COMPANY_CITY
            sender_tel = Config.COMPANY_PHONE
            sender_fax = Config.COMPANY_FAX
            sender_web = Config.COMPANY_WEBSITE
            sender_email = Config.COMPANY_EMAIL
            sender_vergi_dairesi = Config.COMPANY_TAX_OFFICE
            sender_vkn = Config.COMPANY_TAX_NUMBER
            sender_mersis = Config.COMPANY_MERSIS
            sender_ticaret_sicil = Config.COMPANY_TRADE_REGISTRY
            
            # Sol Taraf: Gönderici Bilgileri (Türkçe karakter desteği ile)
            sender_text = f"""
            <b>{sender_unvan}</b><br/>
            {sender_adres}<br/>
            {sender_sehir}<br/>
            Tel: {sender_tel} Faks: {sender_fax}<br/>
            Web Sitesi: {sender_web if sender_web else ''}<br/>
            E-posta: {sender_email}<br/>
            Vergi Dairesi: {sender_vergi_dairesi}<br/>
            VKN: {sender_vkn}<br/>
            Mersis No: {sender_mersis}<br/>
            Ticaret Sicil No: {sender_ticaret_sicil}
            """
            p_sender = Paragraph(sender_text, style_normal)
            
            # Orta: e-Fatura Logosu ve Yazısı
            # E-fatura logosu için GİB'in resmi logosu kullanılabilir veya placeholder
            efatura_logo_placeholder = Table([["e-FATURA<br/>LOGO"]], colWidths=[20*mm], rowHeights=[20*mm])
            efatura_logo_placeholder.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#0066CC')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0066CC')),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
                ('FONTNAME', (0,0), (-1,-1), self.font_bold),
                ('FONTSIZE', (0,0), (-1,-1), 8)
            ]))
            p_efatura = Paragraph("<br/>e-FATURA", ParagraphStyle(name='CenterBold', parent=style_bold, alignment=1))
            
            # Sağ Taraf: Uygulama Logosu ve Fatura Bilgileri Tablosu
            # Logo dosyasını logo klasöründen yükle
            base_dir = os.path.dirname(os.path.dirname(__file__))
            app_logo_paths = [
                os.path.join(base_dir, 'logo', 'muba-1.png'),
                os.path.join(base_dir, 'logo', 'muba-2.png'),
                os.path.join(base_dir, 'logo', 'muba-3.png'),
                os.path.join(base_dir, 'logo', 'Screenshot_1.png')
            ]
            
            app_logo = None
            for logo_path in app_logo_paths:
                if os.path.exists(logo_path):
                    try:
                        app_logo = Image(logo_path, width=40*mm, height=15*mm)
                        break
                    except Exception as e:
                        print(f"Logo yükleme hatası ({logo_path}): {e}")
                        continue
            
            # Logo yoksa placeholder göster
            if app_logo is None:
                company_logo_placeholder = Table([["GO WINGS"]], colWidths=[40*mm], rowHeights=[15*mm])
                company_logo_placeholder.setStyle(TableStyle([
                    ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#667eea')),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
                    ('FONTNAME', (0,0), (-1,-1), self.font_bold),
                    ('FONTSIZE', (0,0), (-1,-1), 10)
                ]))
                company_logo = company_logo_placeholder
            else:
                company_logo = app_logo
            
            # Fatura Meta Verisi Tablosu
            fatura_no = fatura_data.get('faturaNo', '-')
            fatura_tarih_str = fatura_data.get('tarih', datetime.now().strftime('%Y-%m-%d'))
            
            # Tarih formatını dönüştür (YYYY-MM-DD -> DD-MM-YYYY)
            try:
                if '-' in fatura_tarih_str:
                    parts = fatura_tarih_str.split('-')
                    if len(parts) == 3:
                        if len(parts[0]) == 4:  # YYYY-MM-DD formatı
                            fatura_tarih = f"{parts[2]}-{parts[1]}-{parts[0]}"
                        else:  # DD-MM-YYYY formatı
                            fatura_tarih = fatura_tarih_str
                    else:
                        fatura_tarih = fatura_tarih_str
                else:
                    fatura_tarih = fatura_tarih_str
            except:
                fatura_tarih = datetime.now().strftime('%d-%m-%Y')
            
            duzenleme_tarih = datetime.now().strftime('%d-%m-%Y')
            duzenleme_saat = datetime.now().strftime('%H:%M:%S')
            
            meta_data = [
                [Paragraph("Özelleştirme No:", style_bold), Paragraph("TR1.2", style_normal)],
                [Paragraph("Senaryo:", style_bold), Paragraph("TEMELFATURA", style_normal)],
                [Paragraph("Fatura Tipi:", style_bold), Paragraph("SATIŞ", style_normal)],
                [Paragraph("Fatura No:", style_bold), Paragraph(fatura_no, style_normal)],
                [Paragraph("Fatura Tarihi:", style_bold), Paragraph(fatura_tarih, style_normal)],
                [Paragraph("Düzenleme Tarihi:", style_bold), Paragraph(duzenleme_tarih, style_normal)],
                [Paragraph("Düzenleme Saati:", style_bold), Paragraph(duzenleme_saat, style_normal)]
            ]
            
            t_meta = Table(meta_data, colWidths=[35*mm, 40*mm])
            t_meta.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1, colors.black),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
                ('FONTSIZE', (0,0), (-1,-1), 7),
                ('FONTNAME', (0,0), (0,-1), self.font_bold),
                ('FONTNAME', (1,0), (1,-1), self.font_regular),
                ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('PADDING', (0,0), (-1,-1), 2),
            ]))
            
            # Header Düzeni (3 Sütunlu Ana Tablo)
            header_layout_data = [[
                p_sender,
                [efatura_logo_placeholder, p_efatura],
                [company_logo, Spacer(1, 2*mm), t_meta]
            ]]
            
            t_header = Table(header_layout_data, colWidths=[80*mm, 30*mm, 80*mm])
            t_header.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(t_header)
            
            # Çizgi
            story.append(Spacer(1, 2*mm))
            story.append(Table([[""]], colWidths=[190*mm], style=TableStyle([('LINEBELOW', (0,0), (-1,-1), 2, colors.black)])))
            story.append(Spacer(1, 2*mm))
            
            # --- 2. BÖLÜM: ALICI BİLGİLERİ ---
            alici_unvan = cari_hesap.get('unvani', '-')
            alici_adres = cari_hesap.get('adres', '-')
            alici_sehir = cari_hesap.get('sehir', '')
            alici_ulke = "TÜRKİYE"
            alici_email = cari_hesap.get('email', '')
            alici_tel = cari_hesap.get('telefon', '')
            alici_fax = cari_hesap.get('fax', '')
            alici_vergi_dairesi = cari_hesap.get('vergiDairesi', '-')
            alici_vkn = cari_hesap.get('vergiNo', '-')
            
            recipient_text = f"""
            <u><b>SAYIN</b></u><br/>
            {alici_unvan}<br/>
            {alici_adres}, {alici_sehir}<br/>
            {alici_sehir if alici_sehir else ''} / {alici_ulke}<br/>
            {alici_ulke}<br/>
            E-Posta: {alici_email if alici_email else '-'}<br/>
            Tel: {alici_tel if alici_tel else '-'} Faks: {alici_fax if alici_fax else '-'}<br/>
            Vergi Dairesi: {alici_vergi_dairesi}<br/>
            VKN: {alici_vkn}
            """
            p_recipient = Paragraph(recipient_text, style_normal)
            story.append(p_recipient)
            
            # ETTN ve Çizgi
            ettn = str(uuid.uuid4()).upper()
            ettn_text = f"<b>ETTN:</b> {ettn}"
            story.append(Paragraph(ettn_text, style_small))
            story.append(Table([[""]], colWidths=[190*mm], style=TableStyle([('LINEBELOW', (0,0), (-1,-1), 1.5, colors.black)])))
            story.append(Spacer(1, 2*mm))
            
            # --- 3. BÖLÜM: ANA FATURA TABLOSU ---
            # Başlıklar (Türkçe karakter desteği için Paragraph kullan)
            data = [
                [
                    Paragraph('Sıra', style_bold),
                    Paragraph('Malzeme Kodu', style_bold),
                    Paragraph('Açıklama', style_bold),
                    Paragraph('Miktar', style_bold),
                    Paragraph('Birim', style_bold),
                    Paragraph('Birim Fiyat', style_bold),
                    Paragraph('Tutar', style_bold)
                ]
            ]
            
            # Satırları ekle
            satirlar = fatura_data.get('satirlar', [])
            if isinstance(satirlar, str):
                try:
                    satirlar = json.loads(satirlar)
                except:
                    satirlar = []
            
            for idx, satir in enumerate(satirlar, 1):
                if not satir:
                    continue
                
                malzeme_kodu = satir.get('malzemeKodu') or satir.get('stokKodu') or ''
                malzeme_ismi = satir.get('malzemeIsmi') or satir.get('aciklama') or ''
                miktar = float(satir.get('miktar', 0) or 0)
                birim = satir.get('birim', 'Adet')
                birim_fiyat = float(satir.get('birimFiyat', 0) or 0)
                kdv_orani = float(satir.get('kdvOrani', 0) or 0)
                
                # Tutar alanından KDV dahil tutarı al (yeni kayıtlarda KDV dahil tutar var)
                # Eğer tutar alanı yoksa veya 0 ise hesapla
                tutar_kdv_dahil = float(satir.get('tutar', 0) or satir.get('netTutar', 0) or 0)
                if tutar_kdv_dahil == 0:
                    # Eski kayıtlar için hesaplama yap
                    tutar_kdv_haric = miktar * birim_fiyat
                    kdv_tutari = tutar_kdv_haric * (kdv_orani / 100)
                    tutar_kdv_dahil = tutar_kdv_haric + kdv_tutari
                
                # Miktar formatı (Türkçe format)
                if birim.upper() in ['ADET', '']:
                    miktar_text = f"{int(miktar)}"
                else:
                    miktar_text = f"{miktar:.2f}".replace('.', ',')
                
                # Birim fiyat formatı (Türkçe format: nokta binlik, virgül ondalık)
                birim_fiyat_formatted = f"{birim_fiyat:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                birim_fiyat_text = f"{birim_fiyat_formatted} TL"
                
                # Tutar formatı (KDV dahil - Türkçe format)
                tutar_formatted = f"{tutar_kdv_dahil:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                tutar_text = f"{tutar_formatted} TL"
                
                # Türkçe karakter desteği için string'leri Paragraph'a çevir
                data.append([
                    str(idx),
                    Paragraph(malzeme_kodu, style_normal) if malzeme_kodu else '',
                    Paragraph(malzeme_ismi, style_normal) if malzeme_ismi else '',
                    miktar_text,
                    Paragraph(birim, style_normal) if birim else '',
                    birim_fiyat_text,
                    tutar_text
                ])
            
            # Sütun Genişlikleri (7 sütun)
            col_widths = [10*mm, 25*mm, 70*mm, 15*mm, 15*mm, 25*mm, 30*mm]
            
            t_main = Table(data, colWidths=col_widths, repeatRows=1)
            t_main.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('FONTSIZE', (0,0), (-1,-1), 7),
                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                ('ALIGN', (3,1), (-1,-1), 'RIGHT'),  # Sayılar sağa
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
                ('FONTNAME', (0,0), (-1,0), self.font_bold),
                ('FONTNAME', (0,1), (-1,-1), self.font_regular),
                ('PADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(t_main)
            
            # --- 4. BÖLÜM: TOPLAM TABLOSU (SAĞ ALT) ---
            # Veritabanından gelen değerler (artık doğru formatlanmış)
            net_tutar_kdv_haric = float(fatura_data.get('netTutar', 0) or 0)  # KDV hariç toplam
            toplam_kdv = float(fatura_data.get('toplamKDV', 0) or 0)  # KDV tutarı
            toplam_kdv_dahil = float(fatura_data.get('toplam', 0) or 0)  # KDV dahil toplam
            
            # Eğer değerler eksikse, satırlardan hesapla
            if net_tutar_kdv_haric == 0 and toplam_kdv == 0 and toplam_kdv_dahil == 0:
                net_tutar_kdv_haric = 0
                toplam_kdv = 0
                for satir in satirlar:
                    miktar = float(satir.get('miktar', 0) or 0)
                    birim_fiyat = float(satir.get('birimFiyat', satir.get('birim_fiyat', 0)) or 0)
                    kdv_orani_satir = float(satir.get('kdvOrani', satir.get('kdv_orani', 0)) or 0)
                    if miktar > 0 and birim_fiyat > 0:
                        net_tutar_satir = miktar * birim_fiyat
                        kdv_tutari_satir = net_tutar_satir * (kdv_orani_satir / 100)
                        net_tutar_kdv_haric += net_tutar_satir
                        toplam_kdv += kdv_tutari_satir
                toplam_kdv_dahil = net_tutar_kdv_haric + toplam_kdv
            elif toplam_kdv_dahil == 0:
                # Sadece netTutar ve KDV var, toplamı hesapla
                toplam_kdv_dahil = net_tutar_kdv_haric + toplam_kdv
            elif net_tutar_kdv_haric == 0:
                # Sadece toplam ve KDV var, netTutar'ı hesapla
                net_tutar_kdv_haric = toplam_kdv_dahil - toplam_kdv
            
            # Format: Türk Lirası formatı (nokta binlik, virgül ondalık)
            def format_tl(value):
                return f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') + ' TL'
            
            # KDV oranını hesapla
            kdv_orani = 20.00
            if net_tutar_kdv_haric > 0:
                kdv_orani = (toplam_kdv / net_tutar_kdv_haric) * 100
            
            # Toplam tablosunda doğru tutarları göster
            total_data = [
                [Paragraph('Mal / Hizmet Toplam Tutarı', style_bold), format_tl(net_tutar_kdv_haric)],
                [Paragraph('Hesaplanan KDV (% {:.2f})'.format(kdv_orani), style_bold), format_tl(toplam_kdv)],
                [Paragraph('Vergiler Dahil Toplam Tutar', style_bold), format_tl(toplam_kdv_dahil)],
                [Paragraph('Ödenecek Tutar', style_bold), format_tl(toplam_kdv_dahil)]
            ]
            
            t_total = Table(total_data, colWidths=[50*mm, 25*mm])
            t_total.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                ('FONTSIZE', (0,0), (-1,-1), 7),
                ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
                ('ALIGN', (0,0), (0,-1), 'RIGHT'),
                ('FONTNAME', (0,0), (-1,-1), self.font_bold),
                ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
            ]))
            
            # Toplam tablosunu sağa yaslamak için container tablo
            t_total_container = Table([[None, t_total]], colWidths=[115*mm, 75*mm])
            story.append(t_total_container)
            
            story.append(Spacer(1, 5*mm))
            
            # --- 5. BÖLÜM: ALT BİLGİ VE BANKA ---
            # Banka bilgileri Config'den al
            from config import Config
            bank_name = Config.BANK_NAME
            bank_account = Config.BANK_ACCOUNT_NAME
            bank_iban = Config.BANK_IBAN
            
            # Ödeme Koşulu ve Notlar
            # Vade hesaplama
            odeme_plani = cari_hesap.get('odemePlani', '30 GÜN')
            if not odeme_plani or odeme_plani == 'Peşin':
                vade_gun = 0
            elif '30' in odeme_plani:
                vade_gun = 30
            elif '60' in odeme_plani:
                vade_gun = 60
            elif '90' in odeme_plani:
                vade_gun = 90
            elif '120' in odeme_plani:
                vade_gun = 120
            else:
                vade_gun = 30
            
            # Son ödeme tarihini hesapla
            try:
                fatura_tarih_obj = datetime.strptime(fatura_tarih, '%d-%m-%Y')
            except:
                try:
                    # YYYY-MM-DD formatını dene
                    fatura_tarih_obj = datetime.strptime(fatura_tarih_str, '%Y-%m-%d')
                except:
                    fatura_tarih_obj = datetime.now()
            
            son_odeme_tarihi = (fatura_tarih_obj + timedelta(days=vade_gun)).strftime('%d.%m.%Y')
            tutar_yazıyla = self._number_to_words_tl(toplam_kdv_dahil)
            
            # Ödeme koşulu metni
            if vade_gun == 0:
                odeme_kosulu = "Peşin / Havale"
            else:
                odeme_kosulu = f"{vade_gun} GÜN VADELİ"
            
            notes_content = f"""
            <b>Ödeme Koşulu:</b> {odeme_kosulu}<br/><br/>
            <b>Banka Hesap Bilgileri:</b><br/>
            {bank_name} - {bank_account}<br/>
            IBAN: {bank_iban}<br/><br/>
            # {tutar_yazıyla} #<br/>
            <b>Son Ödeme Tarihi:</b> {son_odeme_tarihi if vade_gun > 0 else 'Peşin'}
            """
            
            # Notlar Kutusu ve Teslim Alan
            p_notes = Paragraph(notes_content, style_small)
            
            # Footer Container (Notlar ve Teslim Alan)
            footer_table_data = [
                [p_notes, 'TESLİM ALAN\n\n..................']
            ]
            
            t_footer = Table(footer_table_data, colWidths=[140*mm, 50*mm])
            t_footer.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1, colors.black),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('PADDING', (0,0), (-1,-1), 5),
            ]))
            
            story.append(t_footer)
            
            # En Alt Yazı
            story.append(Spacer(1, 2*mm))
            story.append(Paragraph("Bu belge Vergi Usul Kanunu hükümlerine göre düzenlenmiştir.", ParagraphStyle('CenterSmall', parent=style_small, alignment=1, textColor=colors.gray)))
            
            # PDF Oluştur
            doc.build(story)
            return filename
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(f"E-Fatura PDF oluşturma hatası: {str(e)}")
    
    def _number_to_words_tl(self, num: float) -> str:
        """Sayıyı Türkçe yazıya çevir (TL formatında)"""
        import math
        
        # Tam kısım ve kuruş
        tam_kisim = int(num)
        kurus = int((num - tam_kisim) * 100)
        
        # Tam kısmı yazıya çevir
        tam_text = self._number_to_words(tam_kisim)
        
        # Kuruş kısmı
        if kurus > 0:
            kurus_text = self._number_to_words(kurus)
            return f"{tam_text} TL {kurus_text} kuruş"
        else:
            return f"{tam_text} TL"
    
    def _number_to_words(self, num: int) -> str:
        """Sayıyı Türkçe yazıya çevir"""
        birler = ['', 'Bir', 'İki', 'Üç', 'Dört', 'Beş', 'Altı', 'Yedi', 'Sekiz', 'Dokuz']
        onlar = ['', 'On', 'Yirmi', 'Otuz', 'Kırk', 'Elli', 'Altmış', 'Yetmiş', 'Seksen', 'Doksan']
        
        if num == 0:
            return 'Sıfır'
        
        if num < 10:
            return birler[num]
        elif num < 100:
            return onlar[num // 10] + birler[num % 10]
        elif num < 1000:
            yuzler = num // 100
            kalan = num % 100
            if yuzler == 1:
                yuz_text = 'Yüz'
            else:
                yuz_text = birler[yuzler] + 'Yüz'
            if kalan > 0:
                return yuz_text + self._number_to_words(kalan)
            return yuz_text
        elif num < 1000000:
            binler = num // 1000
            kalan = num % 1000
            if binler == 1:
                bin_text = 'Bin'
            else:
                bin_text = self._number_to_words(binler) + 'Bin'
            if kalan > 0:
                return bin_text + self._number_to_words(kalan)
            return bin_text
        elif num < 1000000000:
            milyonlar = num // 1000000
            kalan = num % 1000000
            milyon_text = self._number_to_words(milyonlar) + 'Milyon'
            if kalan > 0:
                return milyon_text + self._number_to_words(kalan)
            return milyon_text
        else:
            return str(num)
