// frontend/scripts/modules/questionManager.js

export class QuestionManager {
    constructor(app) {
        this.app = app;
        this.questions = [];
    }

    setupEventListeners() {
        // Question management
        document.getElementById('questions-domain-select').addEventListener('change', this.onQuestionsDomainChange.bind(this));
        document.getElementById('add-question-btn').addEventListener('click', this.showQuestionModal.bind(this));
        document.getElementById('cancel-question').addEventListener('click', this.hideQuestionModal.bind(this));
        document.getElementById('question-form').addEventListener('submit', this.addQuestion.bind(this));
    }

    async onQuestionsDomainChange(e) {
        const domainId = e.target.value;
        if (domainId) {
            this.app.selectedDomainId = domainId;
            await this.loadDomainQuestions(domainId);
            document.getElementById('questions-section').classList.remove('hidden');
        } else {
            document.getElementById('questions-section').classList.add('hidden');
        }
    }

    async loadDomainQuestions(domainId) {
        try {
            const data = await this.app.apiService.getDomainQuestions(domainId);
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
                <div class="flex flex-col items-end ml-4">
                    <!-- Question Leads Display -->
                        ${question.question_lead && Array.isArray(question.question_lead) && question.question_lead.length > 0 ? `
                            <div class="mb-2 flex flex-wrap gap-1 justify-end max-w-48">
                                ${question.question_lead.map(lead => `<span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">${lead}</span>`).join('')}
                            </div>
                        ` : ''}
                    <!-- Action Buttons -->
                    <div class="flex space-x-2">
                        <button onclick="app.editQuestion('${question.id}')" class="text-blue-500 hover:text-blue-700 text-sm">Edit</button>
                        <button onclick="app.deleteQuestion('${question.id}')" class="text-red-500 hover:text-red-700 text-sm">Delete</button>
                    </div>
                </div>
            </div>
        `;
        return card;
    }

    showQuestionModal() {
        if (!this.app.selectedDomainId) {
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
            const data = await this.app.apiService.addQuestion(this.app.selectedDomainId, {
                question_text: questionText
            });

            // Check the response message to determine what happened
            if (data.message === "Same type of question already exists") {
                this.hideQuestionModal();
                this.app.showNotification('Question already exists - no duplicate added', 'info');
            } else if (data.message === "Provide a relevant Question") {
                // Don't hide modal for irrelevant questions so user can try again
                this.app.showNotification('Please provide a more relevant question', 'error');
            } else if (data.message === "Question added successfully") {
                this.hideQuestionModal();
                this.loadDomainQuestions(this.app.selectedDomainId);
                this.app.showNotification('Question added successfully', 'success');
            } else {
                // Handle any other success messages
                this.hideQuestionModal();
                this.loadDomainQuestions(this.app.selectedDomainId);
                this.app.showNotification(data.message || 'Question processed successfully', 'success');
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
            await this.app.apiService.deleteQuestion(questionId);
            this.loadDomainQuestions(this.app.selectedDomainId);
            this.app.showNotification('Question deleted successfully', 'success');
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
            await this.app.apiService.updateQuestion(questionId, {
                question_text: newText.trim()
            });

            this.loadDomainQuestions(this.app.selectedDomainId);
            this.app.showNotification('Question updated successfully', 'success');
        } catch (error) {
            alert('Failed to update question: ' + error.message);
        }
    }
}

