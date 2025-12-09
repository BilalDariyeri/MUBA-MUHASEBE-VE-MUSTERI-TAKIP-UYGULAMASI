// Sayfa yüklendiğinde cari hesapları getir
document.addEventListener('DOMContentLoaded', function() {
    yukleCariHesaplar();
    checkAdminAndEnableEdit();
});

// Admin kontrolü ve düzenleme özelliğini aktifleştir
async function checkAdminAndEnableEdit() {
    try {
        const response = await fetch('/api/auth/me');
        const data = await response.json();
        
        if (data.success && data.user && data.user.is_admin) {
            // Admin ise düzenleme özelliği aktif
            window.isAdmin = true;
        } else {
            window.isAdmin = false;
        }
    } catch (error) {
        console.error('Admin kontrolü hatası:', error);
        window.isAdmin = false;
    }
}

// Cari hesapları yükle
async function yukleCariHesaplar() {
    const loading = document.getElementById('loading');
    const tbody = document.getElementById('cari-tbody');
    const noResults = document.getElementById('no-results');
    const tableWrapper = document.querySelector('.table-wrapper');
    
    try {
        loading.style.display = 'block';
        if (tbody) tbody.innerHTML = '';
        if (noResults) noResults.style.display = 'none';
        if (tableWrapper) tableWrapper.style.display = 'none';
        
        const response = await fetch('/api/cari-hesap');
        const result = await response.json();
        
        loading.style.display = 'none';
        
        if (result.success && result.cari_hesap && result.cari_hesap.length > 0) {
            if (tbody) {
                tbody.innerHTML = '';
                result.cari_hesap.forEach((cari, index) => {
                    tbody.appendChild(olusturCariItem(cari, index));
                });
            }
            if (tableWrapper) tableWrapper.style.display = 'block';
            if (noResults) noResults.style.display = 'none';
            
            // Tüm cari hesapları sakla (filtreleme için)
            tumCariHesaplar = result.cari_hesap;
            
            // Checkbox event listener'ları ekle
            ekleCheckboxListeners();
        } else {
            if (tableWrapper) tableWrapper.style.display = 'none';
            if (noResults) noResults.style.display = 'block';
        }
    } catch (error) {
        console.error('Hata:', error);
        loading.style.display = 'none';
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="13" style="text-align: center; padding: 20px; color: #dc3545;">Bir hata oluştu. Lütfen sayfayı yenileyin.</td></tr>';
        }
    }
}

// Checkbox event listener'ları
function ekleCheckboxListeners() {
    // Tümünü seç checkbox'ı
    const selectAll = document.getElementById('select-all');
    if (selectAll) {
        selectAll.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.row-checkbox');
            checkboxes.forEach(cb => {
                cb.checked = this.checked;
                const row = cb.closest('tr');
                if (this.checked) {
                    row.classList.add('selected');
                } else {
                    row.classList.remove('selected');
                }
            });
        });
    }
    
    // Satır checkbox'ları
    const rowCheckboxes = document.querySelectorAll('.row-checkbox');
    rowCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const row = this.closest('tr');
            if (this.checked) {
                row.classList.add('selected');
            } else {
                row.classList.remove('selected');
                if (selectAll) selectAll.checked = false;
            }
        });
    });
}

// Cari hesap satırı oluştur
function olusturCariItem(cari, index) {
    const row = document.createElement('tr');
    row.dataset.cariId = cari.id;
    row.onclick = function(e) {
        if (e.target.type !== 'checkbox') {
            // Sadece admin ise düzenleme modal'ını aç
            if (window.isAdmin) {
                duzenleCari(cari.id);
            }
        }
    };
    
    const iletisim = cari.iletisim || {};
    
    // Bakiye hesaplama
    const bakiye = hesaplaBakiye(cari);
    const bakiyeClass = bakiye.deger >= 0 ? 'positive' : 'negative';
    const bakiyeGosterim = bakiye.deger !== 0 
        ? `${formatPara(bakiye.deger)} (${bakiye.harf})` 
        : 'Hayır';
    
    row.innerHTML = `
        <td class="checkbox-col">
            <input type="checkbox" class="row-checkbox" data-cari-id="${cari.id}">
        </td>
        <td class="kodu-col">${maskVergiNo(cari.vergiNoHash || cari.vergiNo || '-')}</td>
        <td class="aciklama-col">${cari.unvani || 'Unvan belirtilmemiş'}</td>
        <td class="bakiye-col ${bakiyeClass}">${bakiyeGosterim}</td>
        <td class="anonim-col">Hayır</td>
        <td class="sehir-col">${iletisim.il || '-'}</td>
        <td class="ulke-col">${iletisim.ulke || 'TÜRKİYE'}</td>
        <td class="efatura-col">Hayır</td>
        <td class="not-col not-clickable" onclick="acNotModal('${cari.id}')" title="Not eklemek/düzenlemek için tıklayın">
            ${cari.notlar && cari.notlar.not1 ? (cari.notlar.not1.length > 50 ? escapeHtml(cari.notlar.not1.substring(0, 50)) + '...' : escapeHtml(cari.notlar.not1)) : '-'}
            <i class="fas fa-edit" style="margin-left: 5px; opacity: 0.5;"></i>
        </td>
    `;
    
    return row;
}

// Bakiye hesaplama
function hesaplaBakiye(cari) {
    // Bakiye bilgisi SQLite veritabanından gelecek
    // Şimdilik rastgele değerler döndürüyoruz
    const rastgele = Math.random();
    if (rastgele < 0.3) {
        return { deger: 0, harf: '' };
    } else if (rastgele < 0.65) {
        return { deger: Math.random() * 100000, harf: 'A' };
    } else {
        return { deger: -(Math.random() * 50000), harf: 'B' };
    }
}

// Para formatı
function formatPara(miktar) {
    return new Intl.NumberFormat('tr-TR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(miktar);
}

// Para formatı (currency ile)
function formatCurrency(num) {
    return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(num);
}

// Cari hesap filtreleme
let tumCariHesaplar = [];

function filtreleCariHesaplar(aramaMetni) {
    const tbody = document.getElementById('cari-tbody');
    const noResults = document.getElementById('no-results');
    const tableWrapper = document.querySelector('.table-wrapper');
    
    if (!aramaMetni || aramaMetni.trim() === '') {
        if (tbody) {
            tbody.innerHTML = '';
            tumCariHesaplar.forEach((cari, index) => {
                tbody.appendChild(olusturCariItem(cari, index));
            });
        }
        if (tableWrapper) tableWrapper.style.display = tumCariHesaplar.length > 0 ? 'block' : 'none';
        if (noResults) noResults.style.display = tumCariHesaplar.length === 0 ? 'block' : 'none';
        ekleCheckboxListeners();
        return;
    }
    
    const filtrelenmis = tumCariHesaplar.filter(cari => {
        const arama = aramaMetni.toLowerCase();
        const iletisim = cari.iletisim || {};
        return (
            (cari.kodu && cari.kodu.toLowerCase().includes(arama)) ||
            (cari.unvani && cari.unvani.toLowerCase().includes(arama)) ||
            (iletisim.email && iletisim.email.toLowerCase().includes(arama)) ||
            (iletisim.telefon && iletisim.telefon.includes(arama)) ||
            (iletisim.il && iletisim.il.toLowerCase().includes(arama))
        );
    });
    
    if (tbody) {
        tbody.innerHTML = '';
        if (filtrelenmis.length > 0) {
            filtrelenmis.forEach((cari, index) => {
                tbody.appendChild(olusturCariItem(cari, index));
            });
            if (tableWrapper) tableWrapper.style.display = 'block';
            if (noResults) noResults.style.display = 'none';
            ekleCheckboxListeners();
        } else {
            if (tableWrapper) tableWrapper.style.display = 'none';
            if (noResults) {
                noResults.style.display = 'block';
                noResults.querySelector('p').textContent = 'Arama sonucu bulunamadı';
            }
        }
    }
}

// Cari hesap düzenleme
async function duzenleCari(cariId) {
    // Admin kontrolü
    if (!window.isAdmin) {
        try {
            const userResponse = await fetch('/api/auth/me');
            const userData = await userResponse.json();
            
            if (!userData.success || !userData.user || !userData.user.is_admin) {
                NotificationSystem.error('Bu işlem için admin yetkisi gereklidir!', true);
                return;
            }
            window.isAdmin = true;
        } catch (error) {
            NotificationSystem.error('Yetki kontrolü yapılamadı!', true);
            return;
        }
    }
    
    // Mevcut cari hesabı bul
    const cari = tumCariHesaplar.find(c => c.id === cariId);
    
    if (!cari) {
        NotificationSystem.error('Cari hesap bulunamadı', true);
        return;
    }
    
    // Modal'ı doldur
    document.getElementById('edit-cari-id').value = cari.id;
    document.getElementById('edit-unvani').value = cari.unvani || '';
    document.getElementById('edit-vergi-no').value = cari.vergiNo || '';
    document.getElementById('edit-telefon').value = cari.telefon || '';
    document.getElementById('edit-email').value = cari.email || '';
    document.getElementById('edit-adres').value = cari.adres || '';
    
    // Şehir bilgisini al (iletisim içinden veya doğrudan sehir alanından)
    const sehir = cari.sehir || (cari.iletisim && cari.iletisim.il) || '';
    document.getElementById('edit-sehir').value = sehir;
    
    // Modal'ı göster
    document.getElementById('edit-cari-modal').style.display = 'block';
}

function kapatEditCariModal() {
    document.getElementById('edit-cari-modal').style.display = 'none';
    document.getElementById('edit-cari-form').reset();
}

async function kaydetEditCari() {
    // Admin kontrolü
    if (!window.isAdmin) {
        try {
            const userResponse = await fetch('/api/auth/me');
            const userData = await userResponse.json();
            
            if (!userData.success || !userData.user || !userData.user.is_admin) {
                NotificationSystem.error('Bu işlem için admin yetkisi gereklidir!', true);
                return;
            }
            window.isAdmin = true;
        } catch (error) {
            NotificationSystem.error('Yetki kontrolü yapılamadı!', true);
            return;
        }
    }
    
    const cariId = document.getElementById('edit-cari-id').value;
    
    if (!cariId) {
        NotificationSystem.error('Hata: Cari hesap ID bulunamadı', true);
        return;
    }
    
    // Form verilerini topla
    const unvani = document.getElementById('edit-unvani').value.trim();
    const vergiNo = document.getElementById('edit-vergi-no').value.trim();
    const telefon = document.getElementById('edit-telefon').value.trim();
    const email = document.getElementById('edit-email').value.trim();
    const adres = document.getElementById('edit-adres').value.trim();
    const sehir = document.getElementById('edit-sehir').value.trim();
    
    // Validasyon
    if (!unvani || !vergiNo || !telefon || !email || !adres || !sehir) {
        NotificationSystem.error('Lütfen tüm zorunlu alanları doldurun!', true);
        return;
    }
    
    // Email format kontrolü
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        NotificationSystem.error('Lütfen geçerli bir e-posta adresi girin!', true);
        document.getElementById('edit-email').focus();
        return;
    }
    
    const formData = {
        unvani: unvani,
        vergiNo: vergiNo,
        telefon: telefon,
        email: email,
        adres: adres,
        sehir: sehir,
        iletisim: {
            il: sehir,
            ulke: 'TÜRKİYE'
        }
    };
    
    try {
        const response = await fetch(`/api/cari-hesap/${cariId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            NotificationSystem.success('Cari hesap başarıyla güncellendi!', false);
            kapatEditCariModal();
            // Listeyi yenile
            yukleCariHesaplar();
        } else {
            NotificationSystem.error('Hata: ' + result.error, true);
        }
    } catch (error) {
        console.error('Hata:', error);
        NotificationSystem.error('Bir hata oluştu: ' + error.message, true);
    }
}

// Cari hesap silme
async function silCari(cariId) {
    // Admin kontrolü
    try {
        const userResponse = await fetch('/api/auth/me');
        const userData = await userResponse.json();
        
        if (!userData.success || !userData.user || !userData.user.is_admin) {
            NotificationSystem.error('Bu işlem için admin yetkisi gereklidir!', true);
            return;
        }
    } catch (error) {
        NotificationSystem.error('Yetki kontrolü yapılamadı!', true);
        return;
    }
    
    const cari = tumCariHesaplar.find(c => c.id === cariId);
    if (!cari) {
        NotificationSystem.error('Cari hesap bulunamadı', true);
        return;
    }
    
    const details = [
        { label: 'Unvan', value: cari.unvani || '-' },
        { label: 'Vergi No', value: maskVergiNo(cari.vergiNo) || '-' },
        { label: 'Şehir', value: cari.sehir || '-' },
        { label: 'Bakiye', value: formatCurrency(hesaplaBakiye(cari)) }
    ];

    showDeleteModal(
        'Cari Hesabı Sil',
        'Bu cari hesabı silmek istediğinize emin misiniz?',
        details,
        async (id) => {
            try {
                const response = await fetch(`/api/cari-hesap/${id}`, {
                    method: 'DELETE'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    NotificationSystem.success('Cari hesap başarıyla silindi', false);
                    // Tüm cari hesapları güncelle
                    tumCariHesaplar = tumCariHesaplar.filter(c => c.id !== id);
                    yukleCariHesaplar();
                } else {
                    NotificationSystem.error('Hata: ' + result.error, true);
                }
            } catch (error) {
                console.error('Hata:', error);
                NotificationSystem.error('Bir hata oluştu: ' + error.message, true);
            }
        },
        cariId
    );
}

// HTML escape fonksiyonu
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Vergi numarasını maskele (hash'in ilk 6 karakterini göster)
function maskVergiNo(vergiNo) {
    if (!vergiNo || vergiNo === '-') return '-';
    // Eğer hash ise (uzun string), ilk 6 karakterini göster
    if (vergiNo.length > 10) {
        return vergiNo.substring(0, 6) + '****';
    }
    // Eğer normal vergi numarası ise (eski kayıtlar için)
    return vergiNo;
}

// Not Modal İşlevleri
let mevcutCariId = null;

function acNotModal(cariId) {
    mevcutCariId = cariId;
    
    // Mevcut cari hesabı bul
    const cari = tumCariHesaplar.find(c => c.id === cariId);
    
    if (!cari) {
        NotificationSystem.error('Cari hesap bulunamadı', true);
        return;
    }
    
    // Modal başlığını güncelle
    document.getElementById('modal-cari-kodu').textContent = cari.kodu || 'Kod yok';
    document.getElementById('modal-cari-unvan').textContent = cari.unvani || 'Unvan yok';
    
    // Not alanlarını doldur
    if (cari.notlar) {
        document.getElementById('modal-not1').value = cari.notlar.not1 || '';
        document.getElementById('modal-not2').value = cari.notlar.not2 || '';
        document.getElementById('modal-not3').value = cari.notlar.not3 || '';
        document.getElementById('modal-ozel-not').value = cari.notlar.ozelNot || '';
    } else {
        document.getElementById('modal-not1').value = '';
        document.getElementById('modal-not2').value = '';
        document.getElementById('modal-not3').value = '';
        document.getElementById('modal-ozel-not').value = '';
    }
    
    // Modal'ı göster
    document.getElementById('not-modal').style.display = 'block';
}

function kapatNotModal() {
    document.getElementById('not-modal').style.display = 'none';
    mevcutCariId = null;
}

async function kaydetNot() {
    if (!mevcutCariId) {
        NotificationSystem.error('Hata: Cari hesap bulunamadı', true);
        return;
    }
    
    const notlar = {
        not1: document.getElementById('modal-not1').value,
        not2: document.getElementById('modal-not2').value,
        not3: document.getElementById('modal-not3').value,
        ozelNot: document.getElementById('modal-ozel-not').value
    };
    
    try {
        // Önce mevcut cari hesabı getir
        const cari = tumCariHesaplar.find(c => c.id === mevcutCariId);
        if (!cari) {
            NotificationSystem.error('Cari hesap bulunamadı', true);
            return;
        }
        
        // Notları ekle/güncelle
        const guncellenmisCari = {
            ...cari,
            notlar: notlar
        };
        
        // API'ye güncelleme gönder
        const response = await fetch(`/api/cari-hesap/${mevcutCariId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(guncellenmisCari)
        });
        
        const result = await response.json();
        
        if (result.success) {
            NotificationSystem.success('Notlar başarıyla kaydedildi', false);
            kapatNotModal();
            // Listeyi yenile
            yukleCariHesaplar();
        } else {
            NotificationSystem.error('Hata: ' + result.error, true);
        }
    } catch (error) {
        console.error('Hata:', error);
        NotificationSystem.error('Bir hata oluştu: ' + error.message, true);
    }
}

// Modal dışına tıklayınca kapat
window.onclick = function(event) {
    const notModal = document.getElementById('not-modal');
    const editModal = document.getElementById('edit-cari-modal');
    
    if (event.target === notModal) {
        kapatNotModal();
    }
    if (event.target === editModal) {
        kapatEditCariModal();
    }
}

