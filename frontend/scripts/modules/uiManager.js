// frontend/scripts/modules/uiManager.js

export class UIManager {
    constructor(app) {
        this.app = app;
    }

    switchTab(tabName) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.add('hidden');
        });
        document.getElementById(`tab-${tabName}`).classList.remove('hidden');
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
        }
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
    }

    showLoading(containerId, message = 'Loading...') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="text-center py-8">
                    <div class="loading-spinner mx-auto mb-4"></div>
                    <p class="text-gray-500">${message}</p>
                </div>
            `;
        }
    }

    showError(containerId, message = 'An error occurred') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="text-center py-8">
                    <svg class="mx-auto h-12 w-12 text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                    </svg>
                    <p class="text-red-500">${message}</p>
                </div>
            `;
        }
    }

    showEmpty(containerId, title, subtitle, icon = null) {
        const container = document.getElementById(containerId);
        if (container) {
            const iconSvg = icon || `
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
                </svg>
            `;

            container.innerHTML = `
                <div class="text-center py-8">
                    ${iconSvg}
                    <p class="text-gray-500 mt-2">${title}</p>
                    <p class="text-sm text-gray-400">${subtitle}</p>
                </div>
            `;
        }
    }

    updateElementText(elementId, text) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = text;
        }
    }

    updateElementHTML(elementId, html) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = html;
        }
    }

    toggleElementVisibility(elementId, show = true) {
        const element = document.getElementById(elementId);
        if (element) {
            if (show) {
                element.classList.remove('hidden');
            } else {
                element.classList.add('hidden');
            }
        }
    }

    addFadeInAnimation(element) {
        if (element) {
            element.classList.add('fade-in');
        }
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }

    formatDateTime(dateString) {
        return new Date(dateString).toLocaleString();
    }
}


