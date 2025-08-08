// frontend/scripts/modules/domainManager.js

export class DomainManager {
    constructor(app) {
        this.app = app;
    }

    setupEventListeners() {
        // Domain management
        document.getElementById('add-domain-btn').addEventListener('click', this.showDomainModal.bind(this));
        document.getElementById('cancel-domain').addEventListener('click', this.hideDomainModal.bind(this));
        document.getElementById('domain-form').addEventListener('submit', this.createDomain.bind(this));
        document.getElementById('add-question-field').addEventListener('click', this.addQuestionField.bind(this));
    }

    renderDomains() {
        const container = document.getElementById('domains-container');
        container.innerHTML = '';

        if (this.app.domains.length === 0) {
            container.innerHTML = `
                <div class="col-span-full text-center py-12">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-4m-5 0H3m2 0h3M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                    </svg>
                    <p class="text-gray-500 mt-2">No domains created yet</p>
                    <p class="text-sm text-gray-400">Click "Add Domain" to get started</p>
                </div>
            `;
            return;
        }

        this.app.domains.forEach(domain => {
            const domainCard = this.createDomainCard(domain);
            container.appendChild(domainCard);
        });
    }

    createDomainCard(domain) {
        const card = document.createElement('div');
        card.className = 'domain-card bg-white rounded-lg shadow-md p-6 fade-in';
        card.innerHTML = `
            <div class="flex justify-between items-start mb-4">
                <h3 class="text-xl font-semibold text-gray-800">${domain.domain_name}</h3>
                <button onclick="app.deleteDomain('${domain.id}')" class="text-red-500 hover:text-red-700 text-sm">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                </button>
            </div>
            <div class="text-sm text-gray-600 mb-4">
                <div class="flex items-center mb-1">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    ${domain.question_count} questions
                </div>
                <div class="flex items-center text-xs text-gray-400">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Created ${new Date(domain.created_at).toLocaleDateString()}
                </div>
            </div>
            <div class="flex space-x-2">
                <button onclick="app.manageDomainQuestions('${domain.id}', '${domain.domain_name}')" class="flex-1 bg-blue-500 hover:bg-blue-600 text-white px-3 py-2 rounded text-sm transition-colors">
                    Manage Questions
                </button>
                <button onclick="app.viewDomainConversations('${domain.id}', '${domain.domain_name}')" class="flex-1 bg-green-500 hover:bg-green-600 text-white px-3 py-2 rounded text-sm transition-colors">
                    Conversations
                </button>
            </div>
        `;
        return card;
    }

    showDomainModal() {
        document.getElementById('domain-modal').classList.remove('hidden');
        document.getElementById('domain-modal').classList.add('flex');
    }

    hideDomainModal() {
        document.getElementById('domain-modal').classList.add('hidden');
        document.getElementById('domain-modal').classList.remove('flex');
        document.getElementById('domain-form').reset();
        // Reset question fields to just one
        const container = document.getElementById('initial-questions-container');
        container.innerHTML = `
            <div class="question-input-group mb-2">
                <input type="text" class="initial-question w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Enter a question...">
            </div>
        `;
    }

    addQuestionField() {
        const container = document.getElementById('initial-questions-container');
        const questionField = document.createElement('div');
        questionField.className = 'question-input-group mb-2 flex';
        questionField.innerHTML = `
            <input type="text" class="initial-question flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Enter a question...">
            <button type="button" onclick="this.parentElement.remove()" class="ml-2 text-red-500 hover:text-red-700">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        `;
        container.appendChild(questionField);
    }

    async createDomain(e) {
        e.preventDefault();
        
        const domainName = document.getElementById('domain-name').value.trim();
        const questionInputs = document.querySelectorAll('.initial-question');
        const questions = Array.from(questionInputs)
            .map(input => input.value.trim())
            .filter(q => q.length > 0);

        if (!domainName) {
            alert('Please enter a domain name');
            return;
        }

        try {
            const data = await this.app.apiService.createDomain({
                domain_name: domainName,
                questions: questions
            });

            this.hideDomainModal();
            this.app.loadDomains();
            this.app.showNotification(`Domain "${domainName}" created successfully with ${data.questions_added} questions`, 'success');
        } catch (error) {
            alert('Failed to create domain: ' + error.message);
        }
    }

    async deleteDomain(domainId) {
        if (!confirm('Are you sure you want to delete this domain? This will also delete all associated questions, conversations, and results.')) {
            return;
        }

        try {
            await this.app.apiService.deleteDomain(domainId);
            this.app.loadDomains();
            this.app.showNotification('Domain deleted successfully', 'success');
        } catch (error) {
            alert('Failed to delete domain: ' + error.message);
        }
    }

    async populateDomainSelects() {
        const selects = ['questions-domain-select', 'conversations-domain-select'];
        
        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            select.innerHTML = '<option value="">Select a domain...</option>';
            
            this.app.domains.forEach(domain => {
                const option = document.createElement('option');
                option.value = domain.id;
                option.textContent = domain.domain_name;
                select.appendChild(option);
            });
        });
    }
}

