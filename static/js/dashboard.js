// Kısayol kartlarına tıklama işlevi
function navigateTo(module) {
    console.log(`${module} modülüne yönlendiriliyor...`);
    
    // Gelecekte burada API çağrıları yapılabilir
    switch(module) {
        case 'satis-faturalari':
            window.location.href = '/satis-faturalari';
            break;
        case 'cari-hesap':
            window.location.href = '/cari-hesap';
            break;
        case 'malzemeler':
            window.location.href = '/malzemeler';
            break;
        case 'admin-logs':
            window.location.href = '/admin/logs';
            break;
        default:
            console.log('Bilinmeyen modül');
    }
}

// Arama işlevi
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-input');
    
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const searchTerm = this.value;
                console.log('Arama yapılıyor:', searchTerm);
                // Gelecekte burada arama API çağrısı yapılabilir
            }
        });
    }
    
    // Kısayol kartlarına hover efekti
    const shortcutCards = document.querySelectorAll('.shortcut-card');
    shortcutCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = 'translateY(0)';
            }
        });
    });

    // Admin kontrolü ve admin sekmesini göster
    checkAdminStatus();
});

// Admin kontrolü
let currentUser = null;
let isAdmin = false;

async function checkAdminStatus() {
    try {
        const response = await fetch('/api/auth/me');
        const data = await response.json();
        
        if (data.success && data.user) {
            currentUser = data.user;
            isAdmin = data.user.is_admin || false;
            
            if (isAdmin) {
                // Admin ise admin sekmesini göster
                const adminSection = document.getElementById('admin-section');
                if (adminSection) {
                    adminSection.style.display = 'block';
                }
                
                // Kullanıcı ekleme bölümünü göster
                const userManagementSection = document.getElementById('user-management-section');
                if (userManagementSection) {
                    userManagementSection.style.display = 'block';
                    loadUsers();
                }
            }
        }
    } catch (error) {
        console.error('Admin kontrolü hatası:', error);
    }
}

// Kullanıcıları yükle
async function loadUsers() {
    try {
        const response = await fetch('/api/users');
        const data = await response.json();
        
        if (data.success) {
            displayUsers(data.users || []);
        }
    } catch (error) {
        console.error('Kullanıcılar yüklenirken hata:', error);
    }
}

// Kullanıcıları göster
function displayUsers(users) {
    const usersList = document.getElementById('users-list');
    if (!usersList) return;
    
    if (users.length === 0) {
        usersList.innerHTML = '<p style="color: #6c757d; text-align: center;">Henüz kullanıcı eklenmemiş</p>';
        return;
    }
    
    const table = `
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                    <th style="padding: 12px; text-align: left;">E-posta</th>
                    <th style="padding: 12px; text-align: left;">İsim</th>
                    <th style="padding: 12px; text-align: left;">Rol</th>
                    <th style="padding: 12px; text-align: center;">İşlemler</th>
                </tr>
            </thead>
            <tbody>
                ${users.map(user => `
                    <tr style="border-bottom: 1px solid #dee2e6;">
                        <td style="padding: 12px;">${user.email || '-'}</td>
                        <td style="padding: 12px;">${user.name || '-'}</td>
                        <td style="padding: 12px;">
                            <span style="padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; 
                                background: ${(user.username || '').toLowerCase() === 'admin' || (user.role || '').toLowerCase() === 'admin' ? '#dc3545' : '#6c757d'}; 
                                color: white;">
                                ${(user.username || '').toLowerCase() === 'admin' || (user.role || '').toLowerCase() === 'admin' ? 'Admin' : 'Kullanıcı'}
                            </span>
                        </td>
                        <td style="padding: 12px; text-align: center;">
                            <button onclick="deleteUser('${user.id}')" style="background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">
                                <i class="fas fa-trash"></i> Sil
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    usersList.innerHTML = table;
}

// Kullanıcı ekleme dialog'u
function showAddUserDialog() {
    const email = prompt('E-posta:');
    if (!email) return;
    
    const name = prompt('İsim:');
    if (!name) return;
    
    const password = prompt('Şifre (en az 6 karakter):');
    if (!password || password.length < 6) {
        alert('Şifre en az 6 karakter olmalıdır!');
        return;
    }
    
    const username = prompt('Kullanıcı adı (boş bırakılabilir):') || '';
    
    createUser({ email, name, password, username });
}

// Kullanıcı oluştur
async function createUser(userData) {
    try {
        const response = await fetch('/api/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (typeof NotificationSystem !== 'undefined') {
                NotificationSystem.success('Kullanıcı başarıyla eklendi!', false);
            } else {
                alert('Kullanıcı başarıyla eklendi!');
            }
            loadUsers();
        } else {
            if (typeof NotificationSystem !== 'undefined') {
                NotificationSystem.error('Hata: ' + data.error, true);
            } else {
                alert('Hata: ' + data.error);
            }
        }
    } catch (error) {
        console.error('Kullanıcı oluşturma hatası:', error);
        if (typeof NotificationSystem !== 'undefined') {
            NotificationSystem.error('Kullanıcı oluşturulurken hata oluştu', true);
        } else {
            alert('Kullanıcı oluşturulurken hata oluştu');
        }
    }
}

// Kullanıcı sil
async function deleteUser(userId) {
    if (!confirm('Bu kullanıcıyı silmek istediğinize emin misiniz?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/users/${userId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (typeof NotificationSystem !== 'undefined') {
                NotificationSystem.success('Kullanıcı başarıyla silindi!', false);
            } else {
                alert('Kullanıcı başarıyla silindi!');
            }
            loadUsers();
        } else {
            if (typeof NotificationSystem !== 'undefined') {
                NotificationSystem.error('Hata: ' + data.error, true);
            } else {
                alert('Hata: ' + data.error);
            }
        }
    } catch (error) {
        console.error('Kullanıcı silme hatası:', error);
        if (typeof NotificationSystem !== 'undefined') {
            NotificationSystem.error('Kullanıcı silinirken hata oluştu', true);
        } else {
            alert('Kullanıcı silinirken hata oluştu');
        }
    }
}

