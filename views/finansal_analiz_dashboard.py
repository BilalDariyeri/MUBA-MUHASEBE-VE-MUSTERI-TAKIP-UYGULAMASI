"""
Finansal Analiz ve Raporlama Dashboard
Profesyonel Finans Uzmanı Seviyesinde Detaylı Analiz ve Raporlama
"""
import tkinter as tk
from tkinter import ttk, messagebox, font
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import font_manager
from datetime import datetime, timedelta
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# Python path'ini ayarla (models modülünü bulabilmek için)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Matplotlib stil ayarı (profesyonel görünüm)
try:
    plt.style.use('seaborn-v0_8-whitegrid')
except:
    try:
        plt.style.use('seaborn-whitegrid')
    except:
        plt.style.use('ggplot')

# MUBA renk paleti (tasarım sabit, sadece renk/font güncellendi)
COLORS = {
    'primary': '#233568',       # MUBA koyu mavi
    'primary_dark': '#0f112b',  # Daha koyu vurgu
    'accent': '#f48c06',        # Portakal turuncusu
    'success': '#16a34a',
    'danger': '#ef4444',
    'warning': '#d97706',
    'info': '#2563eb',
    'dark': '#1e2a4c',
    'light': '#f5f6fb',         # Nötr açık arka plan
    'white': '#ffffff',
    'border': '#d0d4f2',
    'muted': '#666a87',
    'pink': '#db2777'
}
BRAND_FONT = "SF Pro Display"


def _load_fonts_for_matplotlib():
    """Matplotlib için fontları yükle"""
    try:
        # Font dosyalarının bulunduğu dizin
        current_dir = os.path.dirname(os.path.abspath(__file__))
        fonts_dir = os.path.join(os.path.dirname(current_dir), "logo", "fonts")
        
        if os.path.isdir(fonts_dir):
            # Matplotlib font manager'a fontları ekle
            for file in os.listdir(fonts_dir):
                if file.lower().endswith((".otf", ".ttf")):
                    font_path = os.path.join(fonts_dir, file)
                    try:
                        font_manager.fontManager.addfont(font_path)
                    except Exception:
                        pass
    except Exception:
        pass


# Fontları yükle
_load_fonts_for_matplotlib()


class FinansalAnalizDashboard:
    """Finansal Analiz Dashboard - Profesyonel Finans Uzmanı Seviyesinde"""
    
    def __init__(self, root=None):
        # Pencere kapanırken temizlik yapmak için
        self._cleanup_done = False
        """Dashboard'u başlat"""
        # Matplotlib yazı tipini markaya çek (yoksa Arial)
        try:
            # Matplotlib'de font var mı kontrol et
            available_fonts = [f.name for f in font_manager.fontManager.ttflist]
            if BRAND_FONT in available_fonts:
                plt.rcParams['font.family'] = BRAND_FONT
            else:
                plt.rcParams['font.family'] = 'Arial'
        except Exception:
            plt.rcParams['font.family'] = 'Arial'

        self.root = root if root else tk.Tk()
        self.root.title("MUBA - Profesyonel Finansal Analiz ve Raporlama Dashboard")
        self.root.geometry("1280x820")
        self.root.configure(bg=COLORS['light'])
        
        # Profesyonel fontlar
        family = BRAND_FONT if BRAND_FONT in font.families() else "Arial"
        self.title_font = font.Font(family=family, size=18, weight="bold")
        self.kpi_font = font.Font(family=family, size=12, weight="bold")
        self.kpi_value_font = font.Font(family=family, size=20, weight="bold")
        self.kpi_sub_font = font.Font(family=family, size=10)
        self.label_font = font.Font(family=family, size=10)
        
        # Veri setini oluştur
        self.df = self.generate_sample_data()
        
        # UI'yi oluştur
        self.init_ui()
        
        # Grafikleri çiz
        self.update_all_charts()
    
    def generate_sample_data(self):
        """Gerçek veritabanından Gelir/Gider verilerini çek"""
        try:
            from models.fatura_model import FaturaModel
            from models.purchase_invoice_model import PurchaseInvoiceModel
            from models.malzeme_model import MalzemeModel
            
            fatura_model = FaturaModel()
            purchase_model = PurchaseInvoiceModel()
            malzeme_model = MalzemeModel()
            
            satis_faturalari = fatura_model.get_all()
            alis_faturalari = purchase_model.get_all()
            malzemeler = malzeme_model.get_all()
            malzeme_dict = {m['id']: m for m in malzemeler}
            
            end_date = datetime.now()
            dates = [end_date - timedelta(days=30*i) for i in range(11, -1, -1)]
            
            monthly_data = {}
            for date in dates:
                month_key = date.strftime('%Y-%m')
                monthly_data[month_key] = {
                    'Gelir': 0,
                    'Gider': 0,
                    'Kategori': {}
                }
            
            # Satış faturalarından gelir hesapla (netTutar kullan)
            for fatura in satis_faturalari:
                try:
                    tarih_str = fatura.get('tarih', '')
                    if not tarih_str:
                        continue
                    
                    # Tarihi parse et
                    if isinstance(tarih_str, str):
                        try:
                            tarih = datetime.strptime(tarih_str, '%Y-%m-%d')
                        except:
                            try:
                                tarih = datetime.strptime(tarih_str, '%Y-%m-%d %H:%M:%S')
                            except:
                                continue
                    else:
                        continue
                    
                    month_key = tarih.strftime('%Y-%m')
                    if month_key in monthly_data:
                        # Net tutarı gelir olarak ekle (KDV dahil toplam)
                        net_tutar = float(fatura.get('netTutar', 0) or 0)
                        # Eğer netTutar yoksa toplam + KDV kullan
                        if net_tutar == 0:
                            toplam = float(fatura.get('toplam', 0) or 0)
                            kdv = float(fatura.get('toplamKDV', 0) or 0)
                            net_tutar = toplam + kdv
                        
                        monthly_data[month_key]['Gelir'] += net_tutar
                        
                        # Satırlardan malzeme maliyetini hesapla (COGS - Cost of Goods Sold)
                        satirlar = fatura.get('satirlar', [])
                        if isinstance(satirlar, list):
                            for satir in satirlar:
                                if not isinstance(satir, dict):
                                    continue
                                
                                malzeme_id = satir.get('malzemeId', '')
                                malzeme_kodu = satir.get('malzemeKodu', '') or satir.get('stokKodu', '')
                                miktar = float(satir.get('miktar', 0) or 0)
                                
                                if miktar <= 0:
                                    continue
                                
                                malzeme = None
                                if malzeme_id and malzeme_id in malzeme_dict:
                                    malzeme = malzeme_dict[malzeme_id]
                                elif malzeme_kodu:
                                    for m in malzemeler:
                                        if m.get('kod', '').upper() == malzeme_kodu.upper():
                                            malzeme = m
                                            break
                                
                                if malzeme:
                                    # Geliş fiyatını kullan (alış fiyatı)
                                    gelis_fiyati = float(malzeme.get('current_buy_price', 0) or malzeme.get('average_cost', 0) or 0)
                                    if gelis_fiyati > 0:
                                        maliyet = miktar * gelis_fiyati
                                        monthly_data[month_key]['Gider'] += maliyet
                                        if 'Malzeme' not in monthly_data[month_key]['Kategori']:
                                            monthly_data[month_key]['Kategori']['Malzeme'] = 0
                                        monthly_data[month_key]['Kategori']['Malzeme'] += maliyet
                except Exception as e:
                    print(f"Satış faturası işleme hatası: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Alış faturalarından gider hesapla (net_tutar kullan)
            for alis_fatura in alis_faturalari:
                try:
                    tarih_str = alis_fatura.get('fatura_tarihi', '')
                    if not tarih_str:
                        continue
                    
                    # Tarihi parse et
                    if isinstance(tarih_str, str):
                        try:
                            tarih = datetime.strptime(tarih_str, '%Y-%m-%d')
                        except:
                            try:
                                tarih = datetime.strptime(tarih_str, '%Y-%m-%d %H:%M:%S')
                            except:
                                continue
                    else:
                        continue
                    
                    month_key = tarih.strftime('%Y-%m')
                    if month_key in monthly_data:
                        # Net tutarı gider olarak ekle
                        net_tutar = float(alis_fatura.get('net_tutar', 0) or 0)
                        # Eğer net_tutar yoksa toplam + KDV kullan
                        if net_tutar == 0:
                            toplam = float(alis_fatura.get('toplam', 0) or 0)
                            kdv = float(alis_fatura.get('toplam_kdv', 0) or 0)
                            net_tutar = toplam + kdv
                        
                        monthly_data[month_key]['Gider'] += net_tutar
                        if 'Malzeme' not in monthly_data[month_key]['Kategori']:
                            monthly_data[month_key]['Kategori']['Malzeme'] = 0
                        monthly_data[month_key]['Kategori']['Malzeme'] += net_tutar
                except Exception as e:
                    print(f"Alış faturası işleme hatası: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Cari hesapların borçlarını gider olarak ekle (OPTİMİZE EDİLDİ - Sadece son 6 ay)
            # Bu kısım çok yavaş olduğu için optimize edildi - sadece son 6 ay için tarih filtresi uygulanıyor
            try:
                from models.cari_hesap_model import CariHesapModel
                cari_model = CariHesapModel()
                
                # Sadece son 6 ay için tarih filtresi
                baslangic_tarih = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
                
                # Tüm cari hesaplar için tek seferde ekstre al (daha hızlı)
                try:
                    ekstre_data = cari_model.get_ekstre({
                        'cari_ids': [],  # Tümü
                        'baslangic_tarih': baslangic_tarih,
                        'bitis_tarih': datetime.now().strftime('%Y-%m-%d')
                    })
                    
                    hareketler = ekstre_data.get('hareketler', [])
                    
                    for hareket in hareketler:
                        try:
                            tarih_str = hareket.get('tarih', '')
                            if not tarih_str:
                                continue
                            
                            # Tarihi parse et
                            if isinstance(tarih_str, str):
                                try:
                                    tarih = datetime.strptime(tarih_str, '%Y-%m-%d')
                                except:
                                    try:
                                        tarih = datetime.strptime(tarih_str, '%Y-%m-%d %H:%M:%S')
                                    except:
                                        continue
                            else:
                                continue
                            
                            month_key = tarih.strftime('%Y-%m')
                            if month_key not in monthly_data:
                                continue
                            
                            # Borç tutarını al
                            borc = float(hareket.get('borc', 0) or 0)
                            
                            if borc > 0:
                                # Borcu gider olarak ekle (Cari Hesap Borçları kategorisi)
                                monthly_data[month_key]['Gider'] += borc
                                if 'Cari Hesap Borçları' not in monthly_data[month_key]['Kategori']:
                                    monthly_data[month_key]['Kategori']['Cari Hesap Borçları'] = 0
                                monthly_data[month_key]['Kategori']['Cari Hesap Borçları'] += borc
                        except Exception as e:
                            continue
                except Exception as e:
                    # Ekstre çekme hatası - devam et, kritik değil
                    pass
            except Exception as e:
                # Cari hesap işleme hatası - devam et, kritik değil
                pass
            
            data = []
            # Kategorileri dinamik olarak oluştur (mevcut kategoriler + varsayılanlar)
            all_kategoriler = set()
            for month_data in monthly_data.values():
                all_kategoriler.update(month_data['Kategori'].keys())
            
            # Varsayılan kategorileri ekle
            default_kategoriler = ['Malzeme', 'Personel', 'Kira', 'Ulaşım', 'Diğer', 'Cari Hesap Borçları']
            all_kategoriler.update(default_kategoriler)
            kategoriler = sorted(list(all_kategoriler))
            
            for date in dates:
                month_key = date.strftime('%Y-%m')
                if month_key in monthly_data:
                    month_data = monthly_data[month_key]
                    gelir = month_data['Gelir']
                    kategori_giderleri = month_data['Kategori']
                    
                    # Gelir sadece bir kez eklenir (Malzeme kategorisi için)
                    gelir_added = False
                    
                    for kategori in kategoriler:
                        gider = kategori_giderleri.get(kategori, 0)
                        if gider == 0 and kategori != 'Malzeme':
                            continue
                        
                        # Gelir sadece ilk kategoride eklenir
                        gelir_value = gelir if not gelir_added and kategori == 'Malzeme' else 0
                        if gelir_value > 0:
                            gelir_added = True
                        
                        data.append({
                            'Tarih': date,
                            'Gelir': gelir_value,
                            'Gider': gider,
                            'Kategori': kategori
                        })
            
            df = pd.DataFrame(data)
            
            if df.empty:
                df = self._generate_fallback_data(dates)
            
            return df
        except Exception as e:
            try:
                print(f"Veri cekme hatasi: {e}")
            except UnicodeEncodeError:
                print(f"Data fetch error: {e}")
            import traceback
            traceback.print_exc()
            end_date = datetime.now()
            dates = [end_date - timedelta(days=30*i) for i in range(11, -1, -1)]
            return self._generate_fallback_data(dates)
    
    def _generate_fallback_data(self, dates):
        """Fallback veri oluştur"""
        np.random.seed(42)
        base_gelir = 50000
        gelir_trend = np.linspace(0, 20000, 12)
        gelir_noise = np.random.normal(0, 5000, 12)
        gelir = base_gelir + gelir_trend + gelir_noise
        gelir = np.maximum(gelir, 30000)
        
        base_gider = 35000
        gider_trend = np.linspace(0, 10000, 12)
        gider_noise = np.random.normal(0, 3000, 12)
        gider = base_gider + gider_trend + gider_noise
        gider = np.maximum(gider, 25000)
        
        kategoriler = ['Personel', 'Kira', 'Malzeme', 'Ulaşım', 'Diğer']
        kategori_weights = [0.35, 0.25, 0.20, 0.10, 0.10]
        
        data = []
        for i, date in enumerate(dates):
            for j, kategori in enumerate(kategoriler):
                gider_portion = gider[i] * kategori_weights[j]
                gider_noise = np.random.normal(0, gider_portion * 0.1)
                data.append({
                    'Tarih': date,
                    'Gelir': gelir[i] if j == 0 else 0,
                    'Gider': max(0, gider_portion + gider_noise),
                    'Kategori': kategori
                })
        
        df = pd.DataFrame(data)
        df.loc[df['Kategori'] != 'Personel', 'Gelir'] = 0
        df['Gelir'] = df.groupby(df['Tarih'].dt.to_period('M'))['Gelir'].transform('first')
        return df
    
    def init_ui(self):
        """UI'yi başlat - Profesyonel tasarım"""
        # Scrollable canvas
        canvas = tk.Canvas(self.root, bg=COLORS['light'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['light'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Ana container
        main_frame = tk.Frame(scrollable_frame, bg=COLORS['light'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        title_frame = tk.Frame(main_frame, bg=COLORS['primary'], relief=tk.FLAT)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="📊 MUBA - Profesyonel Finansal Analiz ve Raporlama Dashboard",
            bg=COLORS['primary'],
            fg=COLORS['white'],
            font=self.title_font,
            pady=20
        )
        title_label.pack()
        
        # Üst Kısım - Genişletilmiş KPI Kartları
        self.create_extended_kpi_cards(main_frame)
        
        # İkinci Satır - Ek Metrikler
        self.create_additional_metrics(main_frame)
        
        # Grafikler Bölümü
        charts_section = tk.LabelFrame(
            main_frame,
            text="📈 Detaylı Grafik Analizleri",
            font=self.kpi_font,
            bg=COLORS['light'],
            fg=COLORS['dark']
        )
        charts_section.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Üst Grafikler Satırı
        top_charts_frame = tk.Frame(charts_section, bg=COLORS['light'])
        top_charts_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Sol: Zaman Serisi Grafiği
        left_container = tk.Frame(top_charts_frame, bg=COLORS['white'], relief=tk.RAISED, bd=2)
        left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        left_title = tk.Label(
            left_container,
            text="📈 Gelir/Gider Trend Analizi ve Gelecek Projeksiyonu",
            bg=COLORS['white'],
            fg=COLORS['dark'],
            font=self.kpi_font,
            pady=12
        )
        left_title.pack()
        
        left_frame = tk.Frame(left_container, bg=COLORS['white'])
        left_frame.pack(fill=tk.BOTH, expand=True)
        left_frame.pack_configure(padx=10)
        left_frame.pack_configure(pady=(0, 10))
        
        self.create_time_series_chart(left_frame)
        
        # Sağ: Donut Chart
        right_container = tk.Frame(top_charts_frame, bg=COLORS['white'], relief=tk.RAISED, bd=2)
        right_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        right_container.pack_configure(padx=(10, 0))
        right_container.config(width=400)
        
        right_title = tk.Label(
            right_container,
            text="🍩 Gider Kategorileri Dağılımı",
            bg=COLORS['white'],
            fg=COLORS['dark'],
            font=self.kpi_font
        )
        right_title.pack(pady=12)
        
        right_frame = tk.Frame(right_container, bg=COLORS['white'])
        right_frame.pack(fill=tk.BOTH, expand=True)
        right_frame.pack_configure(padx=10)
        right_frame.pack_configure(pady=(0, 10))
        
        self.create_donut_chart(right_frame)
        
        # Alt Grafikler Satırı
        bottom_charts_frame = tk.Frame(charts_section, bg=COLORS['light'])
        bottom_charts_frame.pack(fill=tk.BOTH, expand=True)
        bottom_charts_frame.pack_configure(pady=(10, 0))
        
        # Sol: Bar Chart - Aylık Karşılaştırma
        bar_container = tk.Frame(bottom_charts_frame, bg=COLORS['white'], relief=tk.RAISED, bd=2)
        bar_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        bar_container.pack_configure(padx=(0, 10))
        
        bar_title = tk.Label(
            bar_container,
            text="📊 Aylık Gelir/Gider Karşılaştırması",
            bg=COLORS['white'],
            fg=COLORS['dark'],
            font=self.kpi_font,
            pady=12
        )
        bar_title.pack()
        
        bar_frame = tk.Frame(bar_container, bg=COLORS['white'])
        bar_frame.pack(fill=tk.BOTH, expand=True)
        bar_frame.pack_configure(padx=10)
        bar_frame.pack_configure(pady=(0, 10))
        
        self.create_bar_chart(bar_frame)
        
        # Sağ: Stacked Bar Chart - Kategori Analizi
        stacked_container = tk.Frame(bottom_charts_frame, bg=COLORS['white'], relief=tk.RAISED, bd=2)
        stacked_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        stacked_container.pack_configure(padx=(10, 0))
        
        stacked_title = tk.Label(
            stacked_container,
            text="📊 Kategori Bazlı Gider Analizi",
            bg=COLORS['white'],
            fg=COLORS['dark'],
            font=self.kpi_font,
            pady=12
        )
        stacked_title.pack()
        
        stacked_frame = tk.Frame(stacked_container, bg=COLORS['white'])
        stacked_frame.pack(fill=tk.BOTH, expand=True)
        stacked_frame.pack_configure(padx=10)
        stacked_frame.pack_configure(pady=(0, 10))
        
        self.create_stacked_bar_chart(stacked_frame)
    
    def create_extended_kpi_cards(self, parent):
        """Genişletilmiş KPI kartları - Daha fazla metrik"""
        kpi_frame = tk.Frame(parent, bg=COLORS['light'])
        kpi_frame.pack(fill=tk.X, pady=(0, 15))
        
        # KPI verilerini hesapla - Gerçek verilerden
        try:
            monthly_gelir = self.df.groupby(self.df['Tarih'].dt.to_period('M'))['Gelir'].first()
            monthly_gider = self.df.groupby(self.df['Tarih'].dt.to_period('M'))['Gider'].sum()
            
            toplam_ciro = float(monthly_gelir.sum())
            toplam_gider = float(monthly_gider.sum())
            net_kar = toplam_ciro - toplam_gider
        except Exception as e:
            print(f"KPI hesaplama hatası: {e}")
            toplam_ciro = 0
            toplam_gider = 0
            net_kar = 0
            monthly_gelir = pd.Series()
            monthly_gider = pd.Series()
        
        # İleri seviye metrikler
        try:
            if len(monthly_gelir) >= 6:
                ilk_3_ay_gelir = float(monthly_gelir.iloc[:3].mean())
                son_3_ay_gelir = float(monthly_gelir.iloc[-3:].mean())
                buyume_gelir = ((son_3_ay_gelir - ilk_3_ay_gelir) / ilk_3_ay_gelir * 100) if ilk_3_ay_gelir > 0 else 0
                
                ilk_3_ay_gider = float(monthly_gider.iloc[:3].mean())
                son_3_ay_gider = float(monthly_gider.iloc[-3:].mean())
                buyume_gider = ((son_3_ay_gider - ilk_3_ay_gider) / ilk_3_ay_gider * 100) if ilk_3_ay_gider > 0 else 0
                
                yil_sonu_projeksiyon = buyume_gelir * 1.2
            elif len(monthly_gelir) >= 3:
                # En az 3 ay varsa basit karşılaştırma
                ilk_ay = float(monthly_gelir.iloc[0])
                son_ay = float(monthly_gelir.iloc[-1])
                buyume_gelir = ((son_ay - ilk_ay) / ilk_ay * 100) if ilk_ay > 0 else 0
                yil_sonu_projeksiyon = buyume_gelir * 1.2
            else:
                buyume_gelir = 0
                buyume_gider = 0
                yil_sonu_projeksiyon = 0
        except Exception as e:
            print(f"Büyüme hesaplama hatası: {e}")
            buyume_gelir = 0
            buyume_gider = 0
            yil_sonu_projeksiyon = 0
        
        kar_marji = (net_kar / toplam_ciro * 100) if toplam_ciro > 0 else 0
        gider_orani = (toplam_gider / toplam_ciro * 100) if toplam_ciro > 0 else 0
        ortalama_aylik_gelir = monthly_gelir.mean() if len(monthly_gelir) > 0 else 0
        ortalama_aylik_gider = monthly_gider.mean() if len(monthly_gider) > 0 else 0
        ortalama_aylik_kar = ortalama_aylik_gelir - ortalama_aylik_gider
        
        # KPI kartları - 5 adet (ROI kaldırıldı)
        kpis = [
            ("💰 Toplam Ciro", f"{toplam_ciro:,.2f} ₺", f"Ortalama: {ortalama_aylik_gelir:,.2f} ₺/ay", COLORS['success'], "📈"),
            ("💸 Toplam Gider", f"{toplam_gider:,.2f} ₺", f"Ortalama: {ortalama_aylik_gider:,.2f} ₺/ay", COLORS['danger'], "📉"),
            ("💵 Net Kâr", f"{net_kar:,.2f} ₺", f"Kâr Marjı: {kar_marji:.2f}%", COLORS['info'], "💰"),
            ("📈 Büyüme Oranı", f"{buyume_gelir:.2f}%", f"Son 3 ay vs İlk 3 ay", COLORS['warning'], "📈"),
            ("🎯 Yıl Sonu Tahmini", f"{yil_sonu_projeksiyon:.2f}%", f"Trend bazlı projeksiyon", COLORS['pink'], "🎯")
        ]
        
        for i, (title, value, subtitle, color, icon) in enumerate(kpis):
            card = tk.Frame(
                kpi_frame,
                bg=COLORS['white'],
                relief=tk.RAISED,
                bd=2,
                highlightbackground=color,
                highlightthickness=3
            )
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6)
            
            header_frame = tk.Frame(card, bg=color)
            header_frame.pack(fill=tk.X)
            
            title_label = tk.Label(
                header_frame,
                text=f"{icon} {title}",
                bg=color,
                fg=COLORS['white'],
                font=self.kpi_font,
                pady=10,
                padx=10
            )
            title_label.pack()
            
            value_label = tk.Label(
                card,
                text=value,
                bg=COLORS['white'],
                fg=COLORS['dark'],
                font=self.kpi_value_font,
                pady=8
            )
            value_label.pack()
            
            subtitle_label = tk.Label(
                card,
                text=subtitle,
                bg=COLORS['white'],
                fg=COLORS['dark'],
                font=self.kpi_sub_font
            )
            subtitle_label.pack(pady=(0, 10))
    
    def create_additional_metrics(self, parent):
        """Ek finansal metrikler"""
        metrics_frame = tk.LabelFrame(
            parent,
            text="📋 Detaylı Finansal Metrikler",
            font=self.kpi_font,
            bg=COLORS['light'],
            fg=COLORS['dark'],
            padx=10,
            pady=10
        )
        metrics_frame.pack(fill=tk.X, pady=(0, 15))
        
        monthly_gelir = self.df.groupby(self.df['Tarih'].dt.to_period('M'))['Gelir'].first()
        monthly_gider = self.df.groupby(self.df['Tarih'].dt.to_period('M'))['Gider'].sum()
        monthly_kar = monthly_gelir - monthly_gider
        
        toplam_ciro = monthly_gelir.sum()
        toplam_gider = monthly_gider.sum()
        net_kar = toplam_ciro - toplam_gider
        
        # İstatistikler
        max_gelir = monthly_gelir.max()
        min_gelir = monthly_gelir.min()
        max_gider = monthly_gider.max()
        min_gider = monthly_gider.min()
        max_kar = monthly_kar.max()
        min_kar = monthly_kar.min()
        
        # Standart sapma
        std_gelir = monthly_gelir.std()
        std_gider = monthly_gider.std()
        
        metrics_text = f"""
En Yüksek Gelir: {max_gelir:,.0f} ₺  |  En Düşük Gelir: {min_gelir:,.0f} ₺  |  Gelir Standart Sapma: {std_gelir:,.0f} ₺
En Yüksek Gider: {max_gider:,.0f} ₺  |  En Düşük Gider: {min_gider:,.0f} ₺  |  Gider Standart Sapma: {std_gider:,.0f} ₺
En Yüksek Kâr: {max_kar:,.0f} ₺  |  En Düşük Kâr: {min_kar:,.0f} ₺  |  Toplam İşlem Sayısı: {len(monthly_gelir)} ay
        """
        
        metrics_label = tk.Label(
            metrics_frame,
            text=metrics_text.strip(),
            bg=COLORS['white'],
            fg=COLORS['dark'],
            font=self.label_font,
            justify=tk.LEFT,
            padx=15,
            pady=10
        )
        metrics_label.pack(fill=tk.X)
    
    def create_time_series_chart(self, parent):
        """Zaman serisi grafiği - Profesyonel"""
        try:
            self.fig_time = Figure(figsize=(8, 3.8), dpi=90, facecolor=COLORS['white'])
            self.ax_time = self.fig_time.add_subplot(111)
            self.fig_time.patch.set_facecolor(COLORS['white'])
            
            self.canvas_time = FigureCanvasTkAgg(self.fig_time, parent)
            self.canvas_time.draw()
            self.canvas_time.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
            toolbar_frame = tk.Frame(parent, bg=COLORS['white'])
            toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
            toolbar = NavigationToolbar2Tk(self.canvas_time, toolbar_frame)
            toolbar.update()
        except Exception as e:
            print(f"Zaman serisi grafiği oluşturma hatası: {e}")
    
    def create_donut_chart(self, parent):
        """Donut chart - Profesyonel"""
        try:
            self.fig_donut = Figure(figsize=(3.6, 3.6), dpi=90, facecolor=COLORS['white'])
            self.ax_donut = self.fig_donut.add_subplot(111)
            self.fig_donut.patch.set_facecolor(COLORS['white'])
            
            self.canvas_donut = FigureCanvasTkAgg(self.fig_donut, parent)
            self.canvas_donut.draw()
            self.canvas_donut.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        except Exception as e:
            print(f"Donut chart oluşturma hatası: {e}")
    
    def create_bar_chart(self, parent):
        """Bar chart - Aylık karşılaştırma"""
        try:
            self.fig_bar = Figure(figsize=(7.2, 3.0), dpi=90, facecolor=COLORS['white'])
            self.ax_bar = self.fig_bar.add_subplot(111)
            self.fig_bar.patch.set_facecolor(COLORS['white'])
            
            self.canvas_bar = FigureCanvasTkAgg(self.fig_bar, parent)
            self.canvas_bar.draw()
            self.canvas_bar.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        except Exception as e:
            print(f"Bar chart oluşturma hatası: {e}")
    
    def create_stacked_bar_chart(self, parent):
        """Stacked bar chart - Kategori analizi"""
        try:
            self.fig_stacked = Figure(figsize=(7.2, 3.0), dpi=90, facecolor=COLORS['white'])
            self.ax_stacked = self.fig_stacked.add_subplot(111)
            self.fig_stacked.patch.set_facecolor(COLORS['white'])
            
            self.canvas_stacked = FigureCanvasTkAgg(self.fig_stacked, parent)
            self.canvas_stacked.draw()
            self.canvas_stacked.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        except Exception as e:
            print(f"Stacked bar chart oluşturma hatası: {e}")
    
    def update_all_charts(self):
        """Tüm grafikleri güncelle"""
        try:
            self.update_time_series_chart()
            self.update_donut_chart()
            self.update_bar_chart()
            self.update_stacked_bar_chart()
        except Exception as e:
            print(f"Grafik güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def update_time_series_chart(self):
        """Zaman serisi grafiğini güncelle - Profesyonel"""
        try:
            self.ax_time.clear()
            
            monthly_data = self.df.groupby(self.df['Tarih'].dt.to_period('M')).agg({
                'Gelir': 'first',
                'Gider': 'sum'
            }).reset_index()
            monthly_data['Tarih'] = pd.to_datetime(monthly_data['Tarih'].astype(str))
            monthly_data = monthly_data.sort_values('Tarih')
            monthly_data['Kâr'] = monthly_data['Gelir'] - monthly_data['Gider']
            
            dates_numeric = np.arange(len(monthly_data))
            
            # Gelir çizgisi
            self.ax_time.plot(
                dates_numeric, monthly_data['Gelir'], 'o-',
                label='Gelir', color=COLORS['success'],
                linewidth=2.5, markersize=8,
                markerfacecolor=COLORS['success'],
                markeredgecolor=COLORS['white'],
                markeredgewidth=1.5, zorder=3
            )
            
            # Gider çizgisi
            self.ax_time.plot(
                dates_numeric, monthly_data['Gider'], 's-',
                label='Gider', color=COLORS['danger'],
                linewidth=2.5, markersize=8,
                markerfacecolor=COLORS['danger'],
                markeredgecolor=COLORS['white'],
                markeredgewidth=1.5, zorder=3
            )
            
            # Kâr çizgisi
            self.ax_time.plot(
                dates_numeric, monthly_data['Kâr'], '^-',
                label='Net Kâr', color=COLORS['info'],
                linewidth=2, markersize=7,
                markerfacecolor=COLORS['info'],
                markeredgecolor=COLORS['white'],
                markeredgewidth=1.5, zorder=3
            )
            
            # Kâr/Zarar alanları
            self.ax_time.fill_between(
                dates_numeric, monthly_data['Gider'], monthly_data['Gelir'],
                where=(monthly_data['Gelir'] >= monthly_data['Gider']),
                alpha=0.3, color=COLORS['success'], label='Kâr Alanı', interpolate=True
            )
            self.ax_time.fill_between(
                dates_numeric, monthly_data['Gider'], monthly_data['Gelir'],
                where=(monthly_data['Gelir'] < monthly_data['Gider']),
                alpha=0.3, color=COLORS['danger'], label='Zarar Alanı', interpolate=True
            )
            
            # Trend çizgisi ve projeksiyon
            if len(monthly_data) >= 3:
                x = dates_numeric
                y = monthly_data['Gelir'].values
                coeffs = np.polyfit(x, y, 2)
                trend_line = np.poly1d(coeffs)
                
                trend_x = np.linspace(x.min(), x.max(), 100)
                trend_y = trend_line(trend_x)
                self.ax_time.plot(
                    trend_x, trend_y, '--',
                    color=COLORS['info'], linewidth=2.5,
                    alpha=0.8, label='Trend Çizgisi'
                )
                
                future_months = 3
                future_x = np.arange(len(monthly_data), len(monthly_data) + future_months)
                future_y = trend_line(future_x)
                
                self.ax_time.plot(
                    future_x, future_y, '--',
                    color=COLORS['warning'], linewidth=3.5,
                    alpha=0.9, label=f'Gelecek {future_months} Ay Tahmini'
                )
                
                self.ax_time.scatter(
                    future_x, future_y,
                    color=COLORS['warning'], s=120,
                    marker='*', edgecolors=COLORS['dark'],
                    linewidths=1.5, zorder=5, label='Tahmin Noktaları'
                )
            
            # X ekseni
            date_labels = [d.strftime('%b %Y') for d in monthly_data['Tarih']]
            self.ax_time.set_xticks(dates_numeric)
            self.ax_time.set_xticklabels(date_labels, rotation=45, ha='right', fontsize=8)
            
            # Grafik ayarları
            self.ax_time.set_xlabel('Tarih', fontsize=11, fontweight='bold', color=COLORS['dark'])
            self.ax_time.set_ylabel('Tutar (₺)', fontsize=11, fontweight='bold', color=COLORS['dark'])
            self.ax_time.set_title(
                'Gelir/Gider Trend Analizi ve Gelecek Projeksiyonu',
                fontsize=13, fontweight='bold', pad=15, color=COLORS['dark']
            )
            
            self.ax_time.legend(
                loc='upper left', fontsize=9,
                framealpha=0.95, fancybox=True, shadow=True
            )
            
            self.ax_time.grid(True, alpha=0.4, linestyle='--', linewidth=0.8)
            self.ax_time.set_facecolor(COLORS['white'])
            self.ax_time.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
            
            self.ax_time.spines['top'].set_visible(False)
            self.ax_time.spines['right'].set_visible(False)
            self.ax_time.spines['left'].set_color(COLORS['dark'])
            self.ax_time.spines['bottom'].set_color(COLORS['dark'])
            
            self.fig_time.tight_layout()
            self.canvas_time.draw()
        except Exception as e:
            print(f"Zaman serisi grafiği güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def update_donut_chart(self):
        """Donut chart'ı güncelle - Profesyonel"""
        try:
            self.ax_donut.clear()
            
            kategori_gider = self.df.groupby('Kategori')['Gider'].sum().sort_values(ascending=False)
            
            colors = [
                COLORS['danger'], COLORS['info'], COLORS['warning'],
                COLORS['success'], COLORS['primary']
            ]
            
            wedges, texts, autotexts = self.ax_donut.pie(
                kategori_gider.values,
                labels=kategori_gider.index,
                autopct=lambda pct: f'{pct:.1f}%\n({pct/100*kategori_gider.sum():,.0f} ₺)',
                startangle=90,
                colors=colors[:len(kategori_gider)],
                pctdistance=0.85,
                textprops={'fontsize': 8, 'fontweight': 'bold', 'color': COLORS['dark']},
                labeldistance=1.15,
                explode=[0.05] * len(kategori_gider)
            )
            
            centre_circle = plt.Circle((0, 0), 0.70, fc=COLORS['white'], ec=COLORS['dark'], linewidth=2.5)
            self.ax_donut.add_artist(centre_circle)
            
            total_gider = kategori_gider.sum()
            self.ax_donut.text(
                0, -0.15, 'Toplam Gider',
                ha='center', va='center',
                fontsize=10, fontweight='bold', color=COLORS['dark']
            )
            self.ax_donut.text(
                0, 0.1, f'{total_gider:,.0f} ₺',
                ha='center', va='center',
                fontsize=12, fontweight='bold', color=COLORS['primary']
            )
            
            self.ax_donut.set_facecolor(COLORS['white'])
            self.fig_donut.tight_layout()
            self.canvas_donut.draw()
        except Exception as e:
            print(f"Donut chart güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def update_bar_chart(self):
        """Bar chart'ı güncelle - Aylık karşılaştırma"""
        try:
            self.ax_bar.clear()
            
            monthly_data = self.df.groupby(self.df['Tarih'].dt.to_period('M')).agg({
                'Gelir': 'first',
                'Gider': 'sum'
            }).reset_index()
            monthly_data['Tarih'] = pd.to_datetime(monthly_data['Tarih'].astype(str))
            monthly_data = monthly_data.sort_values('Tarih')
            monthly_data['Kâr'] = monthly_data['Gelir'] - monthly_data['Gider']
            
            dates_numeric = np.arange(len(monthly_data))
            width = 0.25
            
            self.ax_bar.bar(
                dates_numeric - width, monthly_data['Gelir'], width,
                label='Gelir', color=COLORS['success'], alpha=0.9
            )
            self.ax_bar.bar(
                dates_numeric, monthly_data['Gider'], width,
                label='Gider', color=COLORS['danger'], alpha=0.9
            )
            self.ax_bar.bar(
                dates_numeric + width, monthly_data['Kâr'], width,
                label='Net Kâr', color=COLORS['info'], alpha=0.9
            )
            
            date_labels = [d.strftime('%b\n%Y') for d in monthly_data['Tarih']]
            self.ax_bar.set_xticks(dates_numeric)
            self.ax_bar.set_xticklabels(date_labels, fontsize=7)
            
            self.ax_bar.set_xlabel('Tarih', fontsize=10, fontweight='bold', color=COLORS['dark'])
            self.ax_bar.set_ylabel('Tutar (₺)', fontsize=10, fontweight='bold', color=COLORS['dark'])
            self.ax_bar.set_title(
                'Aylık Gelir/Gider/Kâr Karşılaştırması',
                fontsize=12, fontweight='bold', pad=15, color=COLORS['dark']
            )
            
            self.ax_bar.legend(fontsize=9, framealpha=0.95, fancybox=True, shadow=True)
            self.ax_bar.grid(True, alpha=0.3, linestyle='--', axis='y')
            self.ax_bar.set_facecolor(COLORS['white'])
            self.ax_bar.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
            
            self.ax_bar.spines['top'].set_visible(False)
            self.ax_bar.spines['right'].set_visible(False)
            
            self.fig_bar.tight_layout()
            self.canvas_bar.draw()
        except Exception as e:
            print(f"Bar chart güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def update_stacked_bar_chart(self):
        """Stacked bar chart'ı güncelle - Kategori analizi"""
        try:
            self.ax_stacked.clear()
            
            monthly_data = self.df.groupby([self.df['Tarih'].dt.to_period('M'), 'Kategori'])['Gider'].sum().unstack(fill_value=0)
            monthly_data.index = pd.to_datetime(monthly_data.index.astype(str))
            monthly_data = monthly_data.sort_index()
            
            dates_numeric = np.arange(len(monthly_data))
            
            kategoriler = monthly_data.columns.tolist()
            colors_map = {
                'Malzeme': COLORS['warning'],
                'Personel': COLORS['danger'],
                'Kira': COLORS['info'],
                'Ulaşım': COLORS['success'],
                'Diğer': COLORS['primary']
            }
            
            bottom = np.zeros(len(monthly_data))
            for kategori in kategoriler:
                self.ax_stacked.bar(
                    dates_numeric, monthly_data[kategori],
                    bottom=bottom, label=kategori,
                    color=colors_map.get(kategori, COLORS['primary']),
                    alpha=0.85
                )
                bottom += monthly_data[kategori]
            
            date_labels = [d.strftime('%b\n%Y') for d in monthly_data.index]
            self.ax_stacked.set_xticks(dates_numeric)
            self.ax_stacked.set_xticklabels(date_labels, fontsize=7)
            
            self.ax_stacked.set_xlabel('Tarih', fontsize=10, fontweight='bold', color=COLORS['dark'])
            self.ax_stacked.set_ylabel('Gider (₺)', fontsize=10, fontweight='bold', color=COLORS['dark'])
            self.ax_stacked.set_title(
                'Kategori Bazlı Aylık Gider Dağılımı',
                fontsize=12, fontweight='bold', pad=15, color=COLORS['dark']
            )
            
            self.ax_stacked.legend(fontsize=8, framealpha=0.95, fancybox=True, shadow=True, loc='upper left')
            self.ax_stacked.grid(True, alpha=0.3, linestyle='--', axis='y')
            self.ax_stacked.set_facecolor(COLORS['white'])
            self.ax_stacked.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
            
            self.ax_stacked.spines['top'].set_visible(False)
            self.ax_stacked.spines['right'].set_visible(False)
            
            self.fig_stacked.tight_layout()
            self.canvas_stacked.draw()
        except Exception as e:
            print(f"Stacked bar chart güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Dashboard'u çalıştır"""
        try:
            # Pencere kapanırken temizlik yapmak için callback ekle
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            self.root.mainloop()
        except Exception as e:
            print(f"Dashboard çalıştırma hatası: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._cleanup()
    
    def _on_closing(self):
        """Pencere kapanırken çağrılır"""
        self._cleanup()
        try:
            self.root.destroy()
        except:
            pass
    
    def _cleanup(self):
        """Temizlik işlemleri - Image ve diğer kaynakları temizle"""
        if self._cleanup_done:
            return
        
        try:
            # Matplotlib figure'ları temizle
            import matplotlib.pyplot as plt
            if hasattr(self, 'fig_gelir_gider'):
                try:
                    plt.close(self.fig_gelir_gider)
                except:
                    pass
            if hasattr(self, 'fig_stacked'):
                try:
                    plt.close(self.fig_stacked)
                except:
                    pass
            if hasattr(self, 'fig_trend'):
                try:
                    plt.close(self.fig_trend)
                except:
                    pass
            
            # Canvas'ları temizle
            if hasattr(self, 'canvas_gelir_gider'):
                try:
                    self.canvas_gelir_gider.get_tk_widget().destroy()
                except:
                    pass
            if hasattr(self, 'canvas_stacked'):
                try:
                    self.canvas_stacked.get_tk_widget().destroy()
                except:
                    pass
            if hasattr(self, 'canvas_trend'):
                try:
                    self.canvas_trend.get_tk_widget().destroy()
                except:
                    pass
            
            self._cleanup_done = True
        except Exception as e:
            # Temizlik sırasında hata olsa bile devam et
            print(f"Temizlik hatası (görmezden gelinebilir): {e}")


def main():
    """Ana fonksiyon"""
    try:
        root = tk.Tk()
        app = FinansalAnalizDashboard(root)
        app.run()
    except Exception as e:
        try:
            print(f"Uygulama baslatma hatasi: {e}")
        except UnicodeEncodeError:
            print(f"Application startup error: {e}")
        import traceback
        traceback.print_exc()
        try:
            messagebox.showerror("Hata", f"Uygulama baslatilirken hata olustu:\n{str(e)}")
        except:
            messagebox.showerror("Error", f"Application startup error:\n{str(e)}")


if __name__ == "__main__":
    main()
