// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', function() {
    // Form validasyonu
    const form = document.querySelector('.cari-form-container');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            kaydetCariHesap();
        });
    }
});

// Cari Hesap kaydetme fonksiyonu
async function kaydetCariHesap() {
    // Form verilerini topla
    const isim = document.getElementById('isim').value.trim();
    const vergiNo = document.getElementById('vergi-no').value.trim();
    const telefon = document.getElementById('telefon').value.trim();
    const email = document.getElementById('email').value.trim();
    const adres = document.getElementById('adres').value.trim();
    
    // Validasyon
    if (!isim) {
        NotificationSystem.error('Lütfen İsim / Şirket Adı alanını doldurun!', true);
        document.getElementById('isim').focus();
        return;
    }
    
    if (!vergiNo) {
        NotificationSystem.error('Lütfen Vergi Numarası alanını doldurun!', true);
        document.getElementById('vergi-no').focus();
        return;
    }
    
    if (!telefon) {
        NotificationSystem.error('Lütfen Telefon alanını doldurun!', true);
        document.getElementById('telefon').focus();
        return;
    }
    
    if (!email) {
        NotificationSystem.error('Lütfen E-Posta alanını doldurun!', true);
        document.getElementById('email').focus();
        return;
    }
    
    if (!adres) {
        NotificationSystem.error('Lütfen Adres alanını doldurun!', true);
        document.getElementById('adres').focus();
        return;
    }
    
    // Email format kontrolü
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        NotificationSystem.error('Lütfen geçerli bir e-posta adresi girin!', true);
        document.getElementById('email').focus();
        return;
    }
    
    const sehir = document.getElementById('sehir').value.trim();
    
    if (!sehir) {
        NotificationSystem.error('Lütfen Şehir seçiniz!', true);
        document.getElementById('sehir').focus();
        return;
    }
    
    const formData = {
        unvani: isim,
        vergiNo: vergiNo,
        telefon: telefon,
        email: email,
        adres: adres,
        sehir: sehir,  // Model'de sehir doğrudan alan olarak kaydediliyor
        iletisim: {
            il: sehir,
            ulke: 'TÜRKİYE'
        },
        statusu: 'Kullanımda',
        olusturmaTarihi: new Date().toISOString()
    };
    
    try {
        // API'ye gönder
        const response = await fetch('/api/cari-hesap', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            NotificationSystem.success('Cari hesap başarıyla kaydedildi!', false);
            // Cari Hesap modülüne yönlendir
            setTimeout(() => {
                window.location.href = '/cari-hesap';
            }, 1500);
        } else {
            NotificationSystem.error('Hata: ' + result.error, true);
        }
    } catch (error) {
        console.error('Hata:', error);
        NotificationSystem.error('Bir hata oluştu: ' + error.message, true);
    }
}

