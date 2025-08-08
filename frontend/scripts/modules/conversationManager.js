// frontend/scripts/modules/conversationManager.js

export class ConversationManager {
    constructor(app) {
        this.app = app;
        this.conversations = [];
    }

    setupEventListeners() {
        // Conversation management
        document.getElementById('conversations-domain-select').addEventListener('change', this.onConversationsDomainChange.bind(this));
        document.getElementById('upload-area').addEventListener('click', () => document.getElementById('fileInput').click());
        document.getElementById('upload-area').addEventListener('dragover', this.handleDragOver.bind(this));
        document.getElementById('upload-area').addEventListener('drop', this.handleDrop.bind(this));
        document.getElementById('fileInput').addEventListener('change', this.handleFileSelect.bind(this));
    }

    async onConversationsDomainChange(e) {
        const domainId = e.target.value;
        if (domainId) {
            this.app.selectedDomainId = domainId;
            await this.loadDomainConversations(domainId);
            document.getElementById('conversations-section').classList.remove('hidden');
        } else {
            document.getElementById('conversations-section').classList.add('hidden');
        }
    }

    async loadDomainConversations(domainId) {
        try {
            const data = await this.app.apiService.getDomainConversations(domainId);
            this.conversations = data.conversations;
            this.renderConversations();
        } catch (error) {
            console.error('Error loading conversations:', error);
        }
    }

    renderConversations() {
        const container = document.getElementById('conversations-container');
        container.innerHTML = '';

        if (this.conversations.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                    </svg>
                    <p class="text-gray-500 mt-2">No conversations uploaded yet</p>
                    <p class="text-sm text-gray-400">Upload a conversation file to get started</p>
                </div>
            `;
            return;
        }

        this.conversations.forEach(conversation => {
            const conversationCard = this.createConversationCard(conversation);
            container.appendChild(conversationCard);
        });
    }

    createConversationCard(conversation) {
        const card = document.createElement('div');
        const statusColor = conversation.processed ? 'green' : 'yellow';
        const statusText = conversation.processed ? 'Processed' : 'Pending';

        card.className = 'conversation-card bg-white p-4 rounded-md border fade-in overflow-hidden';
        card.innerHTML = `
            <div class="flex justify-between items-start mb-3">
                <div class="flex-grow pr-4">
                    <h4 class="font-medium text-gray-900 mb-1 truncate">${conversation.filename}</h4>
                    <div class="flex items-center text-xs text-gray-500 mb-2 flex-wrap">
                        <span class="px-2 py-1 bg-${statusColor}-100 text-${statusColor}-800 rounded text-xs mr-2 mb-1">${statusText}</span>
                        <span class="mr-2">${conversation.result_count} results</span>
                        <span>${new Date(conversation.created_at).toLocaleDateString()}</span>
                    </div>
                    <p class="text-xs text-gray-400 truncate max-w-full">${conversation.content_preview}</p>
                </div>
                <div class="flex-shrink-0 flex gap-2">
                    ${!conversation.processed ? 
                        `<button onclick="app.processConversation('${conversation.conversation_id}')" class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-xs transition-colors whitespace-nowrap">Process</button>` : 
                        `<button onclick="app.viewResults('${conversation.conversation_id}')" class="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-xs transition-colors whitespace-nowrap">View Results</button>`
                    }
                </div>
            </div>
        `;
        return card;
    }

    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('border-blue-400');
    }

    handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('border-blue-400');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.uploadFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.uploadFile(file);
        }
    }

    async uploadFile(file) {
        if (!this.app.selectedDomainId) {
            alert('Please select a domain first');
            return;
        }

        const statusDiv = document.getElementById('upload-status');
        statusDiv.innerHTML = '<div class="flex items-center text-blue-600"><div class="loading-spinner mr-2"></div>Uploading...</div>';
        statusDiv.classList.remove('hidden');

        try {
            const data = await this.app.apiService.uploadConversation(this.app.selectedDomainId, file);
            statusDiv.innerHTML = `<div class="text-green-600">✓ ${data.message}</div>`;
            this.loadDomainConversations(this.app.selectedDomainId);
            this.app.showNotification('File uploaded successfully - Click Process to analyze', 'success');
        } catch (error) {
            statusDiv.innerHTML = `<div class="text-red-600">✗ Upload failed: ${error.message}</div>`;
        }
    }

    async processConversation(conversationId) {
        try {
            const data = await this.app.apiService.processConversation(conversationId);
            this.loadDomainConversations(this.app.selectedDomainId);
            this.app.showNotification(`Conversation processed successfully! ${data.questions_processed} questions analyzed.`, 'success');
        } catch (error) {
            alert('Failed to process conversation: ' + error.message);
        }
    }

    debugConversation(conversationId) {
        const conv = this.conversations.find(c => c.conversation_id === conversationId);
        console.log('Conversation debug:', conv);
        console.log('Processed status:', conv?.processed);
    }
}

