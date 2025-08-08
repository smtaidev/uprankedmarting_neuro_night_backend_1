// frontend/scripts/services/notificationService.js

export class NotificationService {
    constructor() {
        this.notifications = [];
    }

    show(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 px-4 py-2 rounded-md text-white fade-in ${
            type === 'success' ? 'bg-green-500' : 
            type === 'error' ? 'bg-red-500' : 
            type === 'warning' ? 'bg-yellow-500' : 
            'bg-blue-500'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        this.notifications.push(notification);
        
        // Auto remove after duration
        setTimeout(() => {
            this.remove(notification);
        }, duration);

        // Add click to dismiss
        notification.addEventListener('click', () => {
            this.remove(notification);
        });
    }

    remove(notification) {
        if (notification && notification.parentNode) {
            notification.remove();
            this.notifications = this.notifications.filter(n => n !== notification);
        }
    }

    clear() {
        this.notifications.forEach(notification => {
            this.remove(notification);
        });
        this.notifications = [];
    }
}


