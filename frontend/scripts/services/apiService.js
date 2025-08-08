// frontend/scripts/services/apiService.js

export class ApiService {
    constructor() {
        this.baseURL = '';
    }

    async request(url, options = {}) {
        const response = await fetch(url, options);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Request failed');
        }

        return data;
    }

    // Domain API methods
    async getDomains() {
        return this.request('/api/domains');
    }

    async createDomain(domainData) {
        return this.request('/api/domains', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(domainData)
        });
    }

    async deleteDomain(domainId) {
        return this.request(`/api/domains/${domainId}`, {
            method: 'DELETE'
        });
    }

    // Question API methods
    async getDomainQuestions(domainId) {
        return this.request(`/api/domains/${domainId}/questions`);
    }

    async addQuestion(domainId, questionData) {
        return this.request(`/api/domains/${domainId}/questions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(questionData)
        });
    }

    async updateQuestion(questionId, questionData) {
        return this.request(`/api/questions/${questionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(questionData)
        });
    }

    async deleteQuestion(questionId) {
        return this.request(`/api/questions/${questionId}`, {
            method: 'DELETE'
        });
    }

    // Conversation API methods
    async getDomainConversations(domainId) {
        return this.request(`/api/domains/${domainId}/conversations`);
    }

    async uploadConversation(domainId, file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`/api/domains/${domainId}/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Upload failed');
        }

        return data;
    }

    async processConversation(conversationId) {
        return this.request(`/api/conversations/${conversationId}/process`, {
            method: 'POST'
        });
    }

    // Results API methods
    async getConversationResults(conversationId) {
        return this.request(`/api/conversations/${conversationId}/results`);
    }
}

