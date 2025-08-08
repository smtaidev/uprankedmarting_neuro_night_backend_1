// frontend/scripts/modules/resultsManager.js

export class ResultsManager {
    constructor(app) {
        this.app = app;
        this.results = [];
    }

    setupEventListeners() {
        // Results
        document.getElementById('results-conversation-select').addEventListener('change', this.onResultsConversationChange.bind(this));
    }

    async populateConversationSelect() {
        const select = document.getElementById('results-conversation-select');
        select.innerHTML = '<option value="">Select a processed conversation...</option>';

        // Get all processed conversations across all domains
        try {
            for (const domain of this.app.domains) {
                const data = await this.app.apiService.getDomainConversations(domain.id);
                
                data.conversations.forEach(conv => {
                    if (conv.processed) {
                        const option = document.createElement('option');
                        option.value = conv.conversation_id;
                        option.textContent = `${domain.domain_name} - ${conv.filename}`;
                        select.appendChild(option);
                    }
                });
            }
        } catch (error) {
            console.error('Error loading processed conversations:', error);
        }
    }

    async onResultsConversationChange(e) {
        const conversationId = e.target.value;
        if (conversationId) {
            this.app.selectedConversationId = conversationId;
            await this.loadConversationResults(conversationId);
            document.getElementById('results-section').classList.remove('hidden');
        } else {
            document.getElementById('results-section').classList.add('hidden');
        }
    }

    async loadConversationResults(conversationId) {
        try {
            const data = await this.app.apiService.getConversationResults(conversationId);
            this.results = data.results;
            this.renderResults(data);
        } catch (error) {
            console.error('Error loading results:', error);
        }
    }

    renderResults(data) {
        const summaryDiv = document.getElementById('results-summary');
        summaryDiv.innerHTML = `
            <div class="text-center">
                <div class="text-lg font-semibold">${data.domain_name}</div>
                <div class="text-sm">${data.filename}</div>
                <div class="text-xs text-gray-500">${data.total_results} results</div>
            </div>
        `;

        const container = document.getElementById('results-container');
        container.innerHTML = '';

        if (this.results.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8">
                    <p class="text-gray-500">No results found</p>
                </div>
            `;
            return;
        }

        this.results.forEach(result => {
            const resultCard = this.createResultCard(result);
            container.appendChild(resultCard);
        });
    }

    createResultCard(result) {
        const card = document.createElement('div');
        const confidence = result.confidence;
        const confidenceClass = confidence > 0.7 ? 'confidence-high' : 
                               confidence > 0.4 ? 'confidence-medium' : 'confidence-low';
        
        card.className = 'result-card bg-white p-4 rounded-md border fade-in';
        card.innerHTML = `
            <div class="mb-3">
                <h4 class="font-medium text-gray-900 mb-1">Question:</h4>
                <p class="text-sm text-gray-700">${result.question_text}</p>
            </div>
            
            <div class="mb-3">
                <h4 class="font-medium text-gray-900 mb-1">Detected Leads:</h4>
                <div class="flex flex-wrap gap-1">
                    ${result.leads.map(lead => `<span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">${lead}</span>`).join('')}
                </div>
            </div>
            
            <div class="mb-3">
                <h4 class="font-medium text-gray-900 mb-1">Answer:</h4>
                <p class="text-sm text-gray-700">${result.answer}</p>
            </div>
            
            <div class="flex justify-between items-center text-xs text-gray-500">
                <span class="${confidenceClass} font-medium">
                    Confidence: ${(confidence * 100).toFixed(1)}%
                </span>
                <span>
                    ${new Date(result.created_at).toLocaleString()}
                </span>
            </div>
        `;
        return card;
    }
}

