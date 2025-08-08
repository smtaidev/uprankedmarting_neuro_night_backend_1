// frontend/scripts/app.js

import { DomainManager } from './modules/domainManager.js';
import { QuestionManager } from './modules/questionManager.js';
import { ConversationManager } from './modules/conversationManager.js';
import { ResultsManager } from './modules/resultsManager.js';
import { UIManager } from './modules/uiManager.js';
import { ApiService } from './services/apiService.js';
import { EventManager } from './utils/eventManager.js';
import { NotificationService } from './services/notificationService.js';

class CallCenterRAGApp {
    constructor() {
        this.currentTab = 'domains';
        this.selectedDomainId = null;
        this.selectedConversationId = null;
        this.domains = [];
        
        // Initialize services
        this.apiService = new ApiService();
        this.notificationService = new NotificationService();
        this.eventManager = new EventManager();
        this.uiManager = new UIManager(this);
        
        // Initialize managers
        this.domainManager = new DomainManager(this);
        this.questionManager = new QuestionManager(this);
        this.conversationManager = new ConversationManager(this);
        this.resultsManager = new ResultsManager(this);
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDomains();
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const tab = e.currentTarget.getAttribute('data-tab');
                this.switchTab(tab);
            });
        });

        // Setup event listeners for all modules
        this.domainManager.setupEventListeners();
        this.questionManager.setupEventListeners();
        this.conversationManager.setupEventListeners();
        this.resultsManager.setupEventListeners();
    }

    switchTab(tabName) {
        this.uiManager.switchTab(tabName);
        this.currentTab = tabName;

        // Load data based on tab
        switch(tabName) {
            case 'domains':
                this.loadDomains();
                break;
            case 'questions':
                this.domainManager.populateDomainSelects();
                break;
            case 'conversations':
                this.domainManager.populateDomainSelects();
                break;
            case 'results':
                this.resultsManager.populateConversationSelect();
                break;
        }
    }

    async loadDomains() {
        try {
            const data = await this.apiService.getDomains();
            this.domains = data.domains;
            this.domainManager.renderDomains();
        } catch (error) {
            console.error('Error loading domains:', error);
        }
    }

    // Public methods that can be called from HTML onclick handlers
    deleteDomain(domainId) {
        return this.domainManager.deleteDomain(domainId);
    }

    manageDomainQuestions(domainId, domainName) {
        this.selectedDomainId = domainId;
        document.getElementById('questions-domain-select').value = domainId;
        this.switchTab('questions');
        this.questionManager.loadDomainQuestions(domainId);
    }

    viewDomainConversations(domainId, domainName) {
        this.selectedDomainId = domainId;
        document.getElementById('conversations-domain-select').value = domainId;
        this.switchTab('conversations');
        this.conversationManager.loadDomainConversations(domainId);
    }

    editQuestion(questionId) {
        return this.questionManager.editQuestion(questionId);
    }

    deleteQuestion(questionId) {
        return this.questionManager.deleteQuestion(questionId);
    }

    processConversation(conversationId) {
        return this.conversationManager.processConversation(conversationId);
    }

    viewResults(conversationId) {
        this.selectedConversationId = conversationId;
        document.getElementById('results-conversation-select').value = conversationId;
        this.switchTab('results');
        this.resultsManager.loadConversationResults(conversationId);
    }

    // Utility method to show notifications
    showNotification(message, type = 'info') {
        this.notificationService.show(message, type);
    }
}

// Initialize the application
const app = new CallCenterRAGApp();

// Make app globally available for HTML onclick handlers
window.app = app;

