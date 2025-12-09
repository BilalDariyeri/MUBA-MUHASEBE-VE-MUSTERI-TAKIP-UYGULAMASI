# MUBA - Cari Hesap Yönetim Sistemi

Modern ve kullanıcı dostu bir cari hesap yönetim sistemi. Python PyQt5 ve SQLite ile geliştirilmiştir.

## 🚀 Özellikler

- **Cari Hesap Yönetimi**: Müşteri ve tedarikçi hesaplarını yönetme
- **Fatura Yönetimi**: Satış ve alım faturaları oluşturma, düzenleme ve takip
- **Tahsilat ve Ödemeler**: Gelir ve gider takibi
- **Stok Yönetimi**: Malzeme ve stok hareketleri takibi
- **Finansal Analiz**: Grafikler ve raporlarla finansal analiz
- **AI Ödeme Tahmini**: Makine öğrenmesi ile ödeme davranışı tahmini
- **Dashboard**: KPI'lar ve son hareketler ile anlık durum takibi
- **E-Fatura**: PDF formatında e-fatura oluşturma ve e-posta gönderme

## 📋 Gereksinimler

- Python 3.8 veya üzeri
- SQLite (Python ile birlikte gelir)

## 🔧 Kurulum

### 1. Projeyi Klonlayın

```bash
git clone <repository-url>
cd mvc44/mvc44/mvc
```

### 2. Sanal Ortam Oluşturun (Önerilen)

```bash
python -m venv venv
```

### 3. Sanal Ortamı Aktifleştirin

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

**Not:** PyQt5 kurulumu sırasında bazı sistemlerde ek bağımlılıklar gerekebilir:
- **Windows**: Genellikle sorunsuz çalışır
- **Linux**: `sudo apt-get install python3-pyqt5 python3-pyqt5.qtwebengine`
- **Mac**: `brew install pyqt5`

### 5. Veritabanını Başlatın

Veritabanı otomatik olarak oluşturulur. İlk çalıştırmada `database.db` dosyası proje kök dizininde oluşturulacaktır.

### 6. Admin Kullanıcı Oluşturun (İlk Kurulum)

```bash
python create_admin.py
```

Varsayılan admin bilgileri:
- **Kullanıcı Adı**: admin
- **Şifre**: admin123

⚠️ **ÖNEMLİ**: İlk girişten sonra şifrenizi değiştirmeniz önerilir!

## 🎯 Kullanım

### Native Desktop Uygulaması (Önerilen)

```bash
python desktop_app_native.py
```

veya

```bash
run_native.bat  # Windows
```

Bu komut tamamen PyQt5 widget'ları ile native masaüstü uygulaması açacaktır.

### Web Tabanlı Desktop Uygulaması

```bash
python desktop_app.py
```

veya

```bash
run_desktop.bat  # Windows
```

### Flask Web Uygulaması

```bash
python main.py
```

Uygulama `http://localhost:5000` adresinde çalışacaktır.

## 📁 Proje Yapısı

```
.
├── app/                    # Flask uygulama modülü
│   ├── __init__.py        # Flask uygulama fabrikası
│   └── routes.py          # API route'ları
├── controllers/           # İş mantığı kontrolcüleri
│   ├── cari_hesap_controller.py
│   ├── fatura_controller.py
│   ├── tahsilat_list_controller.py
│   └── ...
├── models/                # Veri modelleri (SQLite)
│   ├── cari_hesap_model.py
│   ├── fatura_model.py
│   ├── tahsilat_model.py
│   └── ...
├── views/                 # PyQt5 görünümleri
│   ├── dashboard_view.py
│   ├── fatura_form_view.py
│   ├── login_view.py
│   └── ...
├── services/              # Servisler
│   ├── email_service.py   # E-posta gönderme
│   ├── fatura_pdf_service.py  # PDF oluşturma
│   ├── payment_predictor.py   # AI ödeme tahmini
│   └── ...
├── static/                # Statik dosyalar (CSS, JS, görseller)
│   ├── css/
│   ├── js/
│   └── assets/
├── templates/             # HTML şablonları (Flask için)
│   ├── dashboard.html
│   ├── fatura_liste.html
│   └── ...
├── logo/                  # Logo ve font dosyaları
│   └── fonts/
├── utils/                 # Yardımcı fonksiyonlar
│   └── validators.py
├── config.py              # Uygulama yapılandırması
├── sql_init.py            # SQLite veritabanı şeması
├── desktop_app_native.py   # Ana native masaüstü uygulaması
├── desktop_app.py          # WebEngineView masaüstü uygulaması
├── main.py                # Flask web uygulaması
├── requirements.txt       # Python bağımlılıkları
└── README.md              # Bu dosya
```

## 🗄️ Veritabanı

Proje SQLite veritabanı kullanmaktadır. Veritabanı dosyası (`database.db`) proje kök dizininde otomatik olarak oluşturulur.

### Tablolar

- `users` - Kullanıcılar
- `cari_hesap` - Cari hesaplar
- `faturalar` - Satış faturaları
- `purchase_invoices` - Alım faturaları
- `tahsilat` - Tahsilatlar
- `odemeler` - Ödemeler
- `malzemeler` - Malzemeler/Stok
- `stock_movements` - Stok hareketleri
- `activity_logs` - Aktivite logları

## ⚙️ Yapılandırma

Uygulama ayarları `config.py` dosyasında bulunur. E-posta gönderme için Gmail ayarlarını yapılandırmanız gerekebilir.

### Ortam Değişkenleri (Opsiyonel)

`.env` dosyası oluşturarak şu değişkenleri ayarlayabilirsiniz:

```env
GMAIL_EMAIL=your-email@gmail.com
GMAIL_PASSWORD=your-app-password
```

## 🔒 Güvenlik Notları

- `database.db` dosyasını Git'e commit etmeyin (`.gitignore`'da olmalı)
- Production ortamında `SECRET_KEY` ve diğer hassas bilgileri güvenli tutun
- `serviceAccountKey.json` gibi hassas dosyaları Git'e eklemeyin
- İlk kurulumdan sonra admin şifresini değiştirin

## 🐛 Sorun Giderme

### PyQt5 Kurulum Sorunları

**Linux:**
```bash
sudo apt-get update
sudo apt-get install python3-pyqt5 python3-pyqt5.qtwebengine
```

**Mac:**
```bash
brew install pyqt5
```

### Veritabanı Sorunları

Veritabanı sıfırlamak için `database.db` dosyasını silin ve uygulamayı yeniden başlatın.

### Font Sorunları

"SF Pro Display" fontu bulunamazsa, sistem otomatik olarak "Arial" fontunu kullanır.

## 📝 Lisans

Bu proje özel kullanım içindir.

## 👥 Katkıda Bulunanlar

- Geliştirici: [Adınız]

## 📞 İletişim

Sorularınız için issue açabilirsiniz.

---

**Not**: Bu proje SQLite kullanmaktadır ve tek kullanıcılı kullanım için uygundur. Çok kullanıcılı bir ortam için PostgreSQL veya MySQL gibi bir veritabanı sunucusu kullanmanız önerilir.
