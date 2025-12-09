// Modern Notification System
// Toast ve Modal bildirimleri için

class NotificationSystem {
    constructor() {
        this.init();
    }

    init() {
        // Toast container oluştur
        if (!document.getElementById('toast-container')) {
            const toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }

        // Modal container oluştur
        if (!document.getElementById('notification-modal')) {
            const modal = document.createElement('div');
            modal.id = 'notification-modal';
            modal.className = 'notification-modal';
            modal.innerHTML = `
                <div class="notification-modal-content">
                    <div class="notification-modal-header">
                        <span class="notification-icon"></span>
                        <h3 class="notification-title"></h3>
                        <button class="notification-close" onclick="NotificationSystem.closeModal()">&times;</button>
                    </div>
                    <div class="notification-modal-body">
                        <p class="notification-message"></p>
                    </div>
                    <div class="notification-modal-footer">
                        <button class="notification-btn-ok" onclick="NotificationSystem.closeModal()">Tamam</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }

        // Confirm modal container oluştur
        if (!document.getElementById('confirm-modal')) {
            const confirmModal = document.createElement('div');
            confirmModal.id = 'confirm-modal';
            confirmModal.className = 'notification-modal confirm-modal';
            confirmModal.innerHTML = `
                <div class="notification-modal-content">
                    <div class="notification-modal-header">
                        <span class="notification-icon"></span>
                        <h3 class="notification-title"></h3>
                        <button class="notification-close" onclick="NotificationSystem.closeConfirmModal()">&times;</button>
                    </div>
                    <div class="notification-modal-body">
                        <p class="notification-message"></p>
                    </div>
                    <div class="notification-modal-footer confirm-footer">
                        <button class="notification-btn-cancel" onclick="NotificationSystem.closeConfirmModal()">İptal</button>
                        <button class="notification-btn-confirm" onclick="NotificationSystem.confirmResult(true)">Tamam</button>
                    </div>
                </div>
            `;
            document.body.appendChild(confirmModal);
        }
    }

    static showToast(message, type = 'info', duration = 3000) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };

        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas ${icons[type] || icons.info}"></i>
                <span class="toast-message">${message}</span>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
        `;

        container.appendChild(toast);

        // Animasyon için
        setTimeout(() => {
            toast.classList.add('toast-show');
        }, 10);

        // Otomatik kapat
        if (duration > 0) {
            setTimeout(() => {
                toast.classList.remove('toast-show');
                setTimeout(() => {
                    if (toast.parentElement) {
                        toast.remove();
                    }
                }, 300);
            }, duration);
        }
    }

    static showModal(message, title = 'Bilgi', type = 'info') {
        const modal = document.getElementById('notification-modal');
        if (!modal) return;

        const iconEl = modal.querySelector('.notification-icon');
        const titleEl = modal.querySelector('.notification-title');
        const messageEl = modal.querySelector('.notification-message');
        const headerEl = modal.querySelector('.notification-modal-header');

        const configs = {
            success: {
                icon: 'fa-check-circle',
                color: '#28a745',
                bg: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)'
            },
            error: {
                icon: 'fa-exclamation-circle',
                color: '#dc3545',
                bg: 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)'
            },
            warning: {
                icon: 'fa-exclamation-triangle',
                color: '#ffc107',
                bg: 'linear-gradient(135deg, #ffc107 0%, #ff9800 100%)'
            },
            info: {
                icon: 'fa-info-circle',
                color: '#17a2b8',
                bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            }
        };

        const config = configs[type] || configs.info;

        iconEl.innerHTML = `<i class="fas ${config.icon}"></i>`;
        titleEl.textContent = title;
        messageEl.textContent = message;
        headerEl.style.background = config.bg;

        modal.style.display = 'block';
        setTimeout(() => {
            modal.classList.add('modal-show');
        }, 10);
    }

    static closeModal() {
        const modal = document.getElementById('notification-modal');
        if (!modal) return;

        modal.classList.remove('modal-show');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }

    static showConfirm(message, title = 'Onay', type = 'warning') {
        return new Promise((resolve) => {
            const modal = document.getElementById('confirm-modal');
            if (!modal) {
                resolve(false);
                return;
            }

            // Resolve fonksiyonunu sakla
            NotificationSystem._confirmResolve = resolve;

            const iconEl = modal.querySelector('.notification-icon');
            const titleEl = modal.querySelector('.notification-title');
            const messageEl = modal.querySelector('.notification-message');
            const headerEl = modal.querySelector('.notification-modal-header');

            const configs = {
                success: {
                    icon: 'fa-check-circle',
                    bg: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)'
                },
                error: {
                    icon: 'fa-exclamation-circle',
                    bg: 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)'
                },
                warning: {
                    icon: 'fa-exclamation-triangle',
                    bg: 'linear-gradient(135deg, #ffc107 0%, #ff9800 100%)'
                },
                info: {
                    icon: 'fa-info-circle',
                    bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                }
            };

            const config = configs[type] || configs.warning;

            iconEl.innerHTML = `<i class="fas ${config.icon}"></i>`;
            titleEl.textContent = title;
            messageEl.textContent = message;
            headerEl.style.background = config.bg;

            modal.style.display = 'block';
            setTimeout(() => {
                modal.classList.add('modal-show');
            }, 10);
        });
    }

    static confirmResult(result) {
        if (NotificationSystem._confirmResolve) {
            NotificationSystem._confirmResolve(result);
            NotificationSystem._confirmResolve = null;
        }
        NotificationSystem.closeConfirmModal();
    }

    static closeConfirmModal() {
        const modal = document.getElementById('confirm-modal');
        if (!modal) return;

        // İptal edildi
        if (NotificationSystem._confirmResolve) {
            NotificationSystem._confirmResolve(false);
            NotificationSystem._confirmResolve = null;
        }

        modal.classList.remove('modal-show');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }

    // Kolay kullanım için static metodlar
    static success(message, useModal = false) {
        if (useModal) {
            this.showModal(message, 'Başarılı', 'success');
        } else {
            this.showToast(message, 'success', 3000);
        }
    }

    static error(message, useModal = true) {
        if (useModal) {
            this.showModal(message, 'Hata', 'error');
        } else {
            this.showToast(message, 'error', 5000);
        }
    }

    static warning(message, useModal = false) {
        if (useModal) {
            this.showModal(message, 'Uyarı', 'warning');
        } else {
            this.showToast(message, 'warning', 4000);
        }
    }

    static info(message, useModal = false) {
        if (useModal) {
            this.showModal(message, 'Bilgi', 'info');
        } else {
            this.showToast(message, 'info', 3000);
        }
    }
}

// Global kullanım için
window.showNotification = NotificationSystem.showToast.bind(NotificationSystem);
window.showNotificationModal = NotificationSystem.showModal.bind(NotificationSystem);
window.showConfirm = NotificationSystem.showConfirm.bind(NotificationSystem);
window.NotificationSystem = NotificationSystem;

// Sayfa yüklendiğinde başlat
document.addEventListener('DOMContentLoaded', function() {
    new NotificationSystem();
});

// Modal dışına tıklanınca kapat
window.addEventListener('click', function(event) {
    const modal = document.getElementById('notification-modal');
    if (event.target === modal) {
        NotificationSystem.closeModal();
    }
});

// ESC tuşu ile kapat
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const confirmModal = document.getElementById('confirm-modal');
        if (confirmModal && confirmModal.style.display === 'block') {
            NotificationSystem.closeConfirmModal();
        } else {
            NotificationSystem.closeModal();
        }
    }
});

// Confirm modal dışına tıklanınca kapat
window.addEventListener('click', function(event) {
    const confirmModal = document.getElementById('confirm-modal');
    if (event.target === confirmModal) {
        NotificationSystem.closeConfirmModal();
    }
});

