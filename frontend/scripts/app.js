//  frontend/scripts/app.js
class CallCenterRAGApp {
    constructor() {
        this.userId = null;
        this.questions = [];
        this.results = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // File upload
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));

        // Question management
        document.getElementById('add-question-btn').addEventListener('click', this.showQuestionModal.bind(this));
        document.getElementById('cancel-question').addEventListener('click', this.hideQuestionModal.bind(this));
        document.getElementById('question-form').addEventListener('submit', this.addQuestion.bind(this));

        // Processing
        document.getElementById('process-btn').addEventListener('click', this.processQuestions.bind(this));
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
        const formData = new FormData();
        formData.append('file', file);

        const statusDiv = document.getElementById('upload-status');
        statusDiv.innerHTML = '<div class="flex items-center text-blue-600"><div class="loading-spinner mr-2"></div>Uploading...</div>';
        statusDiv.classList.remove('hidden');

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                this.userId = data.user_id;
                statusDiv.innerHTML = `<div class="text-green-600">✓ ${data.message}</div>`;
                this.showMainContent();
            } else {
                statusDiv.innerHTML = `<div class="text-red-600">✗ ${data.detail}</div>`;
            }
        } catch (error) {
            statusDiv.innerHTML = `<div class="text-red-600">✗ Upload failed: ${error.message}</div>`;
        }
    }

    showMainContent() {
        document.getElementById('main-content').classList.remove('hidden');
        this.updateProcessButton();
    }

    showQuestionModal() {
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
        
        const text = document.getElementById('question-text').value.trim();
        const category = document.getElementById('question-category').value;

        if (!text) {
            alert('Please enter a question text');
            return;
        }

        try {
            const response = await fetch(`/api/questions/${this.userId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    category: category
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.questions.push(data.question);
                this.renderQuestions();
                this.hideQuestionModal();
                this.updateProcessButton();
            } else {
                alert(data.detail);
            }
        } catch (error) {
            alert('Failed to add question: ' + error.message);
        }
    }

    renderQuestions() {
        const container = document.getElementById('questions-container');
        container.innerHTML = '';

        this.questions.forEach(question => {
            const questionCard = this.createQuestionCard(question);
            container.appendChild(questionCard);
        });
    }

    createQuestionCard(question) {
        const card = document.createElement('div');
        card.className = 'question-card bg-gray-50 p-4 rounded-md border fade-in';
        card.innerHTML = `
            <div class="flex justify-between items-start">
                <div class="flex-grow">
                    <p class="text-sm font-medium text-gray-900">${question.text}</p>
                    <p class="text-xs text-gray-500 mt-1">Category: ${question.category}</p>
                </div>
                <div class="flex space-x-2 ml-4">
                    <button onclick="app.editQuestion('${question.id}')" class="text-blue-500 hover:text-blue-700 text-sm">Edit</button>
                    <button onclick="app.deleteQuestion('${question.id}')" class="text-red-500 hover:text-red-700 text-sm">Delete</button>
                </div>
            </div>
        `;
        return card;
    }

    async deleteQuestion(questionId) {
        if (!confirm('Are you sure you want to delete this question?')) {
            return;
        }

        try {
            const response = await fetch(`/api/questions/${this.userId}/${questionId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.questions = this.questions.filter(q => q.id !== questionId);
                this.renderQuestions();
                this.updateProcessButton();
            } else {
                const data = await response.json();
                alert(data.detail);
            }
        } catch (error) {
            alert('Failed to delete question: ' + error.message);
        }
    }

    updateProcessButton() {
        const processBtn = document.getElementById('process-btn');
        processBtn.disabled = this.questions.length === 0;
    }

    async processQuestions() {
        if (!this.userId || this.questions.length === 0) {
            return;
        }

        const processBtn = document.getElementById('process-btn');
        processBtn.disabled = true;
        processBtn.innerHTML = '<div class="flex items-center justify-center"><div class="loading-spinner mr-2"></div>Processing...</div>';

        try {
            const response = await fetch(`/api/process/${this.userId}`, {
                method: 'POST'
            });

            const data = await response.json();

            if (response.ok) {
                this.results = data.results;
                this.renderResults();
                processBtn.innerHTML = 'Process Questions';
                processBtn.disabled = false;
            } else {
                alert(data.detail);
                processBtn.innerHTML = 'Process Questions';
                processBtn.disabled = false;
            }
        } catch (error) {
            alert('Processing failed: ' + error.message);
            processBtn.innerHTML = 'Process Questions';
            processBtn.disabled = false;
        }
    }

    renderResults() {
        const container = document.getElementById('results-container');
        container.innerHTML = '';

        if (this.results.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-8">No results yet</p>';
            return;
        }

        this.results.forEach(result => {
            const resultCard = this.createResultCard(result);
            container.appendChild(resultCard);
        });
    }

    createResultCard(result) {
        const card = document.createElement('div');
        const confidence = result.confidence_score;
        const confidenceClass = confidence > 0.7 ? 'confidence-high' : 
                               confidence > 0.4 ? 'confidence-medium' : 'confidence-low';
        
        card.className = 'result-card bg-gray-50 p-4 rounded-md border fade-in';
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
                <p class="text-sm text-gray-700">${result.extracted_values.answer}</p>
            </div>
            
            <div class="flex justify-between items-center text-xs text-gray-500">
                <span class="${confidenceClass} font-medium">
                    Confidence: ${(confidence * 100).toFixed(1)}%
                </span>
                <span>
                    Context chunks: ${result.extracted_values.context_used || 0}
                </span>
            </div>
        `;
        return card;
    }

    async editQuestion(questionId) {
        const question = this.questions.find(q => q.id === questionId);
        if (!question) return;

        const newText = prompt('Edit question:', question.text);
        if (!newText || newText.trim() === question.text) return;

        try {
            const response = await fetch(`/api/questions/${this.userId}/${questionId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: newText.trim()
                })
            });

            const data = await response.json();

            if (response.ok) {
                const index = this.questions.findIndex(q => q.id === questionId);
                this.questions[index] = data.question;
                this.renderQuestions();
            } else {
                alert(data.detail);
            }
        } catch (error) {
            alert('Failed to update question: ' + error.message);
        }
    }
}

// Initialize the application
const app = new CallCenterRAGApp();