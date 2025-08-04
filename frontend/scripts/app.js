// frontend/scripts/app.js

class CallCenterRAGApp {
            constructor() {
                this.currentTab = 'domains';
                this.selectedDomainId = null;
                this.selectedConversationId = null;
                this.currentDomainLeads = null;
                this.domains = [];
                this.questions = [];
                this.conversations = [];
                this.results = [];
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

                // Domain management
                document.getElementById('add-domain-btn').addEventListener('click', this.showDomainModal.bind(this));
                document.getElementById('cancel-domain').addEventListener('click', this.hideDomainModal.bind(this));
                document.getElementById('domain-form').addEventListener('submit', this.createDomain.bind(this));
                document.getElementById('add-question-field').addEventListener('click', this.addQuestionField.bind(this));

                // Question management
                document.getElementById('questions-domain-select').addEventListener('change', this.onQuestionsDomainChange.bind(this));
                document.getElementById('add-question-btn').addEventListener('click', this.showQuestionModal.bind(this));
                document.getElementById('cancel-question').addEventListener('click', this.hideQuestionModal.bind(this));
                document.getElementById('question-form').addEventListener('submit', this.addQuestion.bind(this));
                document.getElementById('generate-leads-btn').addEventListener('click', this.generateLeads.bind(this));

                // Conversation management
                document.getElementById('conversations-domain-select').addEventListener('change', this.onConversationsDomainChange.bind(this));
                document.getElementById('upload-area').addEventListener('click', () => document.getElementById('fileInput').click());
                document.getElementById('upload-area').addEventListener('dragover', this.handleDragOver.bind(this));
                document.getElementById('upload-area').addEventListener('drop', this.handleDrop.bind(this));
                document.getElementById('fileInput').addEventListener('change', this.handleFileSelect.bind(this));

                // Results
                document.getElementById('results-conversation-select').addEventListener('change', this.onResultsConversationChange.bind(this));
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

                this.currentTab = tabName;

                // Load data based on tab
                switch(tabName) {
                    case 'domains':
                        this.loadDomains();
                        break;
                    case 'questions':
                        this.populateDomainSelects();
                        break;
                    case 'conversations':
                        this.populateDomainSelects();
                        break;
                    case 'results':
                        this.populateConversationSelect();
                        break;
                }
            }

            // Domain Management
            async loadDomains() {
                try {
                    const response = await fetch('/api/domains');
                    const data = await response.json();
                    this.domains = data.domains;
                    this.renderDomains();
                } catch (error) {
                    console.error('Error loading domains:', error);
                }
            }

            renderDomains() {
                const container = document.getElementById('domains-container');
                container.innerHTML = '';

                if (this.domains.length === 0) {
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

                this.domains.forEach(domain => {
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
                    const response = await fetch('/api/domains', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            domain_name: domainName,
                            questions: questions
                        })
                    });

                    const data = await response.json();

                    if (response.ok) {
                        this.hideDomainModal();
                        this.loadDomains();
                        this.showNotification(`Domain "${domainName}" created successfully with ${data.questions_added} questions`, 'success');
                    } else {
                        alert(data.detail);
                    }
                } catch (error) {
                    alert('Failed to create domain: ' + error.message);
                }
            }

            async deleteDomain(domainId) {
                if (!confirm('Are you sure you want to delete this domain? This will also delete all associated questions, conversations, and results.')) {
                    return;
                }

                try {
                    const response = await fetch(`/api/domains/${domainId}`, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        this.loadDomains();
                        this.showNotification('Domain deleted successfully', 'success');
                    } else {
                        const data = await response.json();
                        alert(data.detail);
                    }
                } catch (error) {
                    alert('Failed to delete domain: ' + error.message);
                }
            }

            manageDomainQuestions(domainId, domainName) {
                this.selectedDomainId = domainId;
                document.getElementById('questions-domain-select').value = domainId;
                this.switchTab('questions');
                this.loadDomainQuestions(domainId);
            }

            viewDomainConversations(domainId, domainName) {
                this.selectedDomainId = domainId;
                document.getElementById('conversations-domain-select').value = domainId;
                this.switchTab('conversations');
                this.loadDomainConversations(domainId);
            }

            // Question Management
            async populateDomainSelects() {
                const selects = ['questions-domain-select', 'conversations-domain-select'];
                
                selects.forEach(selectId => {
                    const select = document.getElementById(selectId);
                    select.innerHTML = '<option value="">Select a domain...</option>';
                    
                    this.domains.forEach(domain => {
                        const option = document.createElement('option');
                        option.value = domain.id;
                        option.textContent = domain.domain_name;
                        select.appendChild(option);
                    });
                });
            }

            async onQuestionsDomainChange(e) {
                const domainId = e.target.value;
                if (domainId) {
                    this.selectedDomainId = domainId;
                    await this.loadDomainQuestions(domainId);
                    
                    // Clear leads when switching domains
                    const existingLeads = document.getElementById('generated-leads');
                    if (existingLeads) {
                        existingLeads.remove();
                    }
                    this.currentDomainLeads = null;
                    
                    document.getElementById('questions-section').classList.remove('hidden');
                } else {
                    document.getElementById('questions-section').classList.add('hidden');
                }
            }

            async loadDomainQuestions(domainId) {
                try {
                    const response = await fetch(`/api/domains/${domainId}/questions`);
                    const data = await response.json();
                    this.questions = data.questions;
                    this.renderQuestions();
                } catch (error) {
                    console.error('Error loading questions:', error);
                }
            }

            renderQuestions() {
                const container = document.getElementById('questions-container');
                container.innerHTML = '';

                if (this.questions.length === 0) {
                    container.innerHTML = `
                        <div class="text-center py-8">
                            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            <p class="text-gray-500 mt-2">No questions added yet</p>
                            <p class="text-sm text-gray-400">Click "Add Question" to get started</p>
                        </div>
                    `;
                    return;
                }

                this.questions.forEach(question => {
                    const questionCard = this.createQuestionCard(question);
                    container.appendChild(questionCard);
                });
            }

            createQuestionCard(question) {
                const card = document.createElement('div');
                card.className = 'question-card bg-white p-4 rounded-md border fade-in';
                card.innerHTML = `
                    <div class="flex justify-between items-start">
                        <div class="flex-grow">
                            <p class="text-sm font-medium text-gray-900 mb-1">${question.question_text}</p>
                            <div class="flex items-center text-xs text-gray-500">
                                <span>${new Date(question.created_at).toLocaleDateString()}</span>
                            </div>
                        </div>
                        <div class="flex space-x-2 ml-4">
                            <button onclick="app.editQuestion('${question.id}')" class="text-blue-500 hover:text-blue-700 text-sm">Edit</button>
                            <button onclick="app.deleteQuestion('${question.id}')" class="text-red-500 hover:text-red-700 text-sm">Delete</button>
                        </div>
                    </div>
                `;
                return card;
            }

            showQuestionModal() {
                if (!this.selectedDomainId) {
                    alert('Please select a domain first');
                    return;
                }
                document.getElementById('question-modal').classList.remove('hidden');
                document.getElementById('question-modal').classList.add('flex');
            }

            hideQuestionModal() {
                document.getElementById('question-modal').classList.add('hidden');
                document.getElementById('question-modal').classList.remove('flex');
                document.getElementById('question-form').reset();
            }

            async addQuestion(e) {
                e.preventDefault();
                
                const questionText = document.getElementById('question-text').value.trim();
                if (!questionText) {
                    alert('Please enter a question text');
                    return;
                }

                try {
                    const response = await fetch(`/api/domains/${this.selectedDomainId}/questions`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            question_text: questionText
                        })
                    });

                    const data = await response.json();

                    if (response.ok) {
                        this.hideQuestionModal();
                        this.loadDomainQuestions(this.selectedDomainId);
                        this.showNotification('Question added successfully', 'success');
                    } else {
                        alert(data.detail);
                    }
                } catch (error) {
                    alert('Failed to add question: ' + error.message);
                }
            }

            async deleteQuestion(questionId) {
                if (!confirm('Are you sure you want to delete this question?')) {
                    return;
                }

                try {
                    const response = await fetch(`/api/questions/${questionId}`, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        this.loadDomainQuestions(this.selectedDomainId);
                        this.showNotification('Question deleted successfully', 'success');
                    } else {
                        const data = await response.json();
                        alert(data.detail);
                    }
                } catch (error) {
                    alert('Failed to delete question: ' + error.message);
                }
            }

            async editQuestion(questionId) {
                const question = this.questions.find(q => q.id === questionId);
                if (!question) return;

                const newText = prompt('Edit question:', question.question_text);
                if (!newText || newText.trim() === question.question_text) return;

                try {
                    const response = await fetch(`/api/questions/${questionId}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            question_text: newText.trim()
                        })
                    });

                    if (response.ok) {
                        this.loadDomainQuestions(this.selectedDomainId);
                        this.showNotification('Question updated successfully', 'success');
                    } else {
                        const data = await response.json();
                        alert(data.detail);
                    }
                } catch (error) {
                    alert('Failed to update question: ' + error.message);
                }
            }


            async generateLeads() {
                if (!this.selectedDomainId) {
                    alert('Please select a domain first');
                    return;
                }

                try {
                    const response = await fetch(`/api/domains/${this.selectedDomainId}/generate-leads`, {
                        method: 'POST'
                    });

                    const data = await response.json();

                    if (response.ok) {
                        this.displayLeads(data.leads);
                        this.showNotification(`Generated ${data.leads.length} key leads`, 'success');
                    } else {
                        alert(data.detail);
                    }
                } catch (error) {
                    alert('Failed to generate leads: ' + error.message);
                }
            }

            displayLeads(leads) {
                const questionsSection = document.getElementById('questions-section');
                
                // Remove existing leads if any
                const existingLeads = document.getElementById('generated-leads');
                if (existingLeads) {
                    existingLeads.remove();
                }
                
                // Store leads for current domain
                this.currentDomainLeads = {
                    domainId: this.selectedDomainId,
                    leads: leads
                };
                
                // Create leads display
                const leadsDiv = document.createElement('div');
                leadsDiv.id = 'generated-leads';
                leadsDiv.className = 'bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6';
                leadsDiv.innerHTML = `
                    <h4 class="font-medium text-purple-800 mb-2">Generated Key Leads</h4>
                    <div class="flex flex-wrap gap-2">
                        ${leads.map(lead => `<span class="px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full">${lead}</span>`).join('')}
                    </div>
                `;
                
                // Insert after the header
                const header = questionsSection.querySelector('.flex.justify-between');
                header.parentNode.insertBefore(leadsDiv, header.nextSibling);
            }


            // Conversation Management
            async onConversationsDomainChange(e) {
                const domainId = e.target.value;
                if (domainId) {
                    this.selectedDomainId = domainId;
                    await this.loadDomainConversations(domainId);
                    document.getElementById('conversations-section').classList.remove('hidden');
                } else {
                    document.getElementById('conversations-section').classList.add('hidden');
                }
            }

            async loadDomainConversations(domainId) {
                try {
                    const response = await fetch(`/api/domains/${domainId}/conversations`);
                    const data = await response.json();
                    this.conversations = data.conversations;
                    this.renderConversations();
                } catch (error) {
                    console.error('Error loading conversations:', error);
                }
            }

            debugConversation(conversationId) {
                const conv = this.conversations.find(c => c.conversation_id === conversationId);
                console.log('Conversation debug:', conv);
                console.log('Processed status:', conv?.processed);
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
                if (!this.selectedDomainId) {
                    alert('Please select a domain first');
                    return;
                }

                const formData = new FormData();
                formData.append('file', file);

                const statusDiv = document.getElementById('upload-status');
                statusDiv.innerHTML = '<div class="flex items-center text-blue-600"><div class="loading-spinner mr-2"></div>Uploading...</div>';
                statusDiv.classList.remove('hidden');

                try {
                    const response = await fetch(`/api/domains/${this.selectedDomainId}/upload`, {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();

                    if (response.ok) {
                        statusDiv.innerHTML = `<div class="text-green-600">✓ ${data.message}</div>`;
                        this.loadDomainConversations(this.selectedDomainId);
                        this.showNotification('File uploaded successfully - Click Process to analyze', 'success');
                    } else {
                        statusDiv.innerHTML = `<div class="text-red-600">✗ ${data.detail}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="text-red-600">✗ Upload failed: ${error.message}</div>`;
                }
            }

            async processConversation(conversationId) {
                try {
                    const response = await fetch(`/api/conversations/${conversationId}/process`, {
                        method: 'POST'
                    });

                    const data = await response.json();

                    if (response.ok) {
                        this.loadDomainConversations(this.selectedDomainId);
                        this.showNotification(`Conversation processed successfully! ${data.questions_processed} questions analyzed.`, 'success');
                    } else {
                        alert(data.detail);
                    }
                } catch (error) {
                    alert('Failed to process conversation: ' + error.message);
                }
            }

            // Results Management
            async populateConversationSelect() {
                const select = document.getElementById('results-conversation-select');
                select.innerHTML = '<option value="">Select a processed conversation...</option>';

                // Get all processed conversations across all domains
                try {
                    for (const domain of this.domains) {
                        const response = await fetch(`/api/domains/${domain.id}/conversations`);
                        const data = await response.json();
                        
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
                    this.selectedConversationId = conversationId;
                    await this.loadConversationResults(conversationId);
                    document.getElementById('results-section').classList.remove('hidden');
                } else {
                    document.getElementById('results-section').classList.add('hidden');
                }
            }

            async loadConversationResults(conversationId) {
                try {
                    const response = await fetch(`/api/conversations/${conversationId}/results`);
                    const data = await response.json();
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

            viewResults(conversationId) {
                this.selectedConversationId = conversationId;
                document.getElementById('results-conversation-select').value = conversationId;
                this.switchTab('results');
                this.loadConversationResults(conversationId);
            }

            // Utility Methods
            showNotification(message, type = 'info') {
                // Simple notification system
                const notification = document.createElement('div');
                notification.className = `fixed top-4 right-4 z-50 px-4 py-2 rounded-md text-white fade-in ${
                    type === 'success' ? 'bg-green-500' : 
                    type === 'error' ? 'bg-red-500' : 'bg-blue-500'
                }`;
                notification.textContent = message;
                
                document.body.appendChild(notification);
                
                setTimeout(() => {
                    notification.remove();
                }, 3000);
            }
        }

        // Initialize the application
        const app = new CallCenterRAGApp();