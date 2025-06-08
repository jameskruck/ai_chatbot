// Enhanced Virtual Study Group Collaboration
// Connects to improved server.py for better conversation flow

class StudyGroupSession {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.activePeers = ['sarah_chen'];
        this.conversationStage = 'opening';
        this.messageCount = 0;
        this.serverUrl = 'http://localhost:5000'; // Update for production
        this.isReadyForImplementation = false;
        
        this.init();
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    init() {
        this.attachEventListeners();
        this.initializeInterface();
    }
    
    attachEventListeners() {
        // Start study group button
        document.getElementById('start-analysis')?.addEventListener('click', () => {
            this.startStudyGroup();
        });
        
        // Send message functionality
        document.getElementById('send-message')?.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Enter key to send message
        document.getElementById('user-input')?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Peer invitation clicks
        document.querySelectorAll('.classmate.available').forEach(peer => {
            peer.addEventListener('click', () => {
                this.invitePeer(peer.dataset.agent);
            });
        });
        
        // Research trigger
        document.getElementById('trigger-research')?.addEventListener('click', () => {
            this.triggerGroupResearch();
        });
        
        // Implementation readiness check
        this.setupImplementationTrigger();
        
        // Step completion tracking
        this.setupStepTracking();
    }
    
    initializeInterface() {
        // Initially disable chat input
        const userInput = document.getElementById('user-input');
        const sendButton = document.getElementById('send-message');
        
        if (userInput) userInput.disabled = true;
        if (sendButton) sendButton.disabled = true;
    }
    
    startStudyGroup() {
        // Show the study group interface
        document.getElementById('ai-consultation').classList.remove('hidden');
        document.getElementById('case-discussion').style.display = 'none';
        
        // Enable chat interface
        const userInput = document.getElementById('user-input');
        const sendButton = document.getElementById('send-message');
        
        if (userInput) userInput.disabled = false;
        if (sendButton) sendButton.disabled = false;
        
        // Add initial welcome message
        this.addWelcomeMessage();
        
        // Focus on input
        if (userInput) userInput.focus();
    }
    
    addWelcomeMessage() {
        const welcomeMessage = {
            speaker: 'Sarah Chen',
            peer_id: 'sarah_chen',
            message: "Hi! I'm Sarah - excited to work through this FashionForward case with you. I've been looking at some similar customer service automation cases in my consulting work. What's your initial take on Jessica's situation?",
            timestamp: new Date().toISOString(),
            was_directly_addressed: false
        };
        
        this.displayMessage(welcomeMessage, 'peer');
        this.messageCount++;
    }
    
    async sendMessage() {
        const userInput = document.getElementById('user-input');
        const message = userInput.value.trim();
        
        if (!message) return;
        
        // Disable input while processing
        userInput.disabled = true;
        document.getElementById('send-message').disabled = true;
        
        // Display user message immediately
        this.displayMessage({
            speaker: 'You',
            message: message,
            timestamp: new Date().toISOString()
        }, 'user');
        
        // Clear input
        userInput.value = '';
        this.messageCount++;
        
        // Check if user is indicating readiness for implementation
        this.checkImplementationReadiness(message);
        
        try {
            // Send to enhanced server
            const response = await fetch(`${this.serverUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.sessionId,
                    message: message,
                    stage: this.getConversationStage(),
                    session_type: 'enhanced_peer_discussion'
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Display peer response
            this.displayMessage(data, 'peer');
            
            // Handle any complications or insights
            if (data.complication) {
                this.handleComplication(data.complication);
            }
            
            if (data.research_insight) {
                this.handleResearchInsight(data.research_insight);
            }
            
            // Update conversation stage
            if (data.conversation_stage) {
                this.conversationStage = data.conversation_stage;
                this.updateProgressIndicator();
            }
            
            this.messageCount++;
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.displayErrorMessage();
        } finally {
            // Re-enable input
            userInput.disabled = false;
            document.getElementById('send-message').disabled = false;
            userInput.focus();
        }
    }
    
    displayMessage(messageData, type) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        
        if (type === 'user') {
            messageDiv.className = 'user-message';
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="message-header">
                        <span class="sender">You</span>
                        <span class="timestamp">${this.formatTime(messageData.timestamp)}</span>
                    </div>
                    <div class="message-text">${this.escapeHtml(messageData.message)}</div>
                </div>
            `;
        } else {
            messageDiv.className = 'peer-message';
            const peerInfo = this.getPeerInfo(messageData.peer_id);
            
            messageDiv.innerHTML = `
                <div class="peer-message-content">
                    <div class="peer-message-header">
                        <span class="peer-sender">${messageData.speaker}</span>
                        <span class="peer-expertise">${peerInfo.expertise}</span>
                        <span class="timestamp">${this.formatTime(messageData.timestamp)}</span>
                    </div>
                    <div class="message-text">${this.escapeHtml(messageData.message)}</div>
                </div>
            `;
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    getPeerInfo(peerId) {
        const peerMapping = {
            'sarah_chen': { expertise: 'Finance & Strategy' },
            'marcus_rodriguez': { expertise: 'Customer Experience' },
            'priya_patel': { expertise: 'Technology & Implementation' }
        };
        return peerMapping[peerId] || { expertise: 'MBA Student' };
    }
    
    async invitePeer(peerId) {
        const peerElement = document.querySelector(`[data-agent="${peerId}"]`);
        
        if (peerElement.classList.contains('active')) {
            return; // Already active
        }
        
        try {
            const response = await fetch(`${this.serverUrl}/invite_peer`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.sessionId,
                    peer_id: peerId
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Update UI
                peerElement.classList.remove('available');
                peerElement.classList.add('active');
                peerElement.innerHTML = peerElement.innerHTML.replace('Invite to discuss', 'Active');
                
                // Add peer to active list
                this.activePeers.push(peerId);
                
                // Display introduction message
                this.displayMessage({
                    speaker: data.peer_name,
                    peer_id: peerId,
                    message: data.introduction,
                    timestamp: new Date().toISOString()
                }, 'peer');
                
                // Update active count
                this.updateActivePeerCount();
                
            } else {
                console.error('Failed to invite peer:', data.error);
            }
            
        } catch (error) {
            console.error('Error inviting peer:', error);
        }
    }
    
    async triggerGroupResearch() {
        const researchButton = document.getElementById('trigger-research');
        const researchStatus = document.getElementById('research-status');
        
        researchButton.disabled = true;
        researchStatus.textContent = 'Researching together...';
        
        try {
            const response = await fetch(`${this.serverUrl}/trigger_research`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.sessionId,
                    topic: 'chatbot_implementations',
                    research_type: 'group_research'
                })
            });
            
            const data = await response.json();
            
            // Display research findings
            this.displayResearchFindings(data.research);
            
            researchStatus.textContent = 'Research complete!';
            setTimeout(() => {
                researchStatus.textContent = '';
            }, 3000);
            
        } catch (error) {
            console.error('Error triggering research:', error);
            researchStatus.textContent = 'Research failed - try again';
        } finally {
            researchButton.disabled = false;
        }
    }
    
    displayResearchFindings(research) {
        const chatMessages = document.getElementById('chat-messages');
        const researchDiv = document.createElement('div');
        researchDiv.className = 'system-message';
        
        let researchContent = '<strong>📚 Group Research Findings:</strong><br><br>';
        
        if (research.recent_implementations) {
            researchContent += '<strong>Recent Retail Implementations:</strong><br>';
            research.recent_implementations.forEach(impl => {
                researchContent += `• ${impl.company}: ${impl.outcome}<br>`;
            });
            researchContent += '<br>';
        }
        
        if (research.financial_benchmarks) {
            researchContent += '<strong>Financial Insights:</strong><br>';
            research.financial_benchmarks.forEach(benchmark => {
                researchContent += `• ${benchmark}<br>`;
            });
            researchContent += '<br>';
        }
        
        if (research.peer_contributions) {
            researchContent += '<strong>Your Study Group\'s Insights:</strong><br>';
            research.peer_contributions.forEach(contribution => {
                researchContent += `• ${contribution}<br>`;
            });
        }
        
        researchDiv.innerHTML = `
            <div class="message-content">
                ${researchContent}
            </div>
        `;
        
        chatMessages.appendChild(researchDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    checkImplementationReadiness(message) {
        const readinessKeywords = [
            'ready to build', 'let\'s build', 'start building', 'ready for implementation',
            'let\'s implement', 'move to implementation', 'build the chatbot',
            'ready to create', 'time to build', 'let\'s start building'
        ];
        
        const messageLower = message.toLowerCase();
        const isReady = readinessKeywords.some(keyword => messageLower.includes(keyword));
        
        if (isReady && !this.isReadyForImplementation) {
            this.isReadyForImplementation = true;
            this.showImplementationTransition();
        }
    }
    
    showImplementationTransition() {
        // Show the transition section
        const transitionSection = document.getElementById('implementation-transition');
        if (transitionSection) {
            transitionSection.classList.remove('hidden');
            
            // Populate strategy summary based on conversation
            this.populateStrategySummary();
            
            // Setup the "Start Building" button
            document.getElementById('start-building')?.addEventListener('click', () => {
                this.showImplementationContent();
            });
            
            // Scroll to transition
            transitionSection.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    populateStrategySummary() {
        const strategySummary = document.getElementById('strategy-summary');
        const collaborationHighlights = document.getElementById('collaboration-highlights');
        
        if (strategySummary) {
            strategySummary.innerHTML = `
                <p><strong>Your Group's Recommendation:</strong> Implement an AI chatbot solution for FashionForward's customer service, with a phased approach focusing on the top FAQ categories your group identified.</p>
                <p><strong>Key Decision Factors:</strong> ROI potential, customer experience impact, and implementation feasibility based on your collaborative analysis.</p>
            `;
        }
        
        if (collaborationHighlights) {
            const highlights = [
                `📊 Financial analysis from Sarah's consulting experience`,
                `🎯 Customer experience insights from Marcus's retail background`, 
                `🚀 Implementation guidance from Priya's startup experience`,
                `🤝 Collaborative decision-making through authentic peer discussion`
            ];
            
            if (this.activePeers.length > 1) {
                highlights.push(`👥 Multi-perspective analysis with ${this.activePeers.length} different viewpoints`);
            }
            
            collaborationHighlights.innerHTML = `
                <ul>
                    ${highlights.map(highlight => `<li>${highlight}</li>`).join('')}
                </ul>
            `;
        }
    }
    
    showImplementationContent() {
        // Show all implementation content
        document.getElementById('implementation-content').classList.remove('hidden');
        document.getElementById('final-navigation').classList.remove('hidden');
        
        // Hide the transition section
        document.getElementById('implementation-transition').style.display = 'none';
        
        // Smooth scroll to implementation content
        document.getElementById('implementation-content').scrollIntoView({ behavior: 'smooth' });
    }
    
    setupImplementationTrigger() {
        // This will be called when user clicks "Start Building" button
        // Already handled in showImplementationTransition()
    }
    
    setupStepTracking() {
        // Track implementation step completion
        const checkboxes = document.querySelectorAll('.step-check input[type="checkbox"]');
        let completedSteps = 0;
        
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                if (checkbox.checked) {
                    completedSteps++;
                } else {
                    completedSteps--;
                }
                
                // Show completion section when all steps are done
                if (completedSteps === checkboxes.length) {
                    document.getElementById('completion-section').classList.remove('hidden');
                    document.getElementById('completion-section').scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
        
        // Handle analysis submission
        document.getElementById('submit-analysis')?.addEventListener('click', () => {
            this.handleAnalysisSubmission();
        });
        
        // Handle completion
        document.getElementById('complete-session')?.addEventListener('click', () => {
            window.location.href = 'reflection.html';
        });
    }
    
    handleAnalysisSubmission() {
        const risks = document.getElementById('risks-analysis').value.trim();
        const metrics = document.getElementById('success-metrics').value.trim();
        const brandVoice = document.getElementById('brand-voice').value.trim();
        
        const feedback = document.getElementById('analysis-feedback');
        
        if (!risks || !metrics || !brandVoice) {
            feedback.innerHTML = '<p style="color: #dc2626;">Please complete all three analysis questions before continuing.</p>';
            feedback.classList.remove('hidden');
            return;
        }
        
        // Provide positive feedback
        feedback.innerHTML = `
            <div style="background: #dcfce7; border: 1px solid #16a34a; padding: 15px; border-radius: 6px; margin-top: 15px;">
                <h4 style="color: #16a34a; margin: 0 0 10px 0;">✅ Excellent Strategic Analysis!</h4>
                <p style="margin: 0; color: #15803d;">You've demonstrated strong strategic thinking across risk assessment, success measurement, and brand alignment. You're ready to move to implementation!</p>
            </div>
        `;
        feedback.classList.remove('hidden');
        
        // Scroll down to show the implementation steps
        setTimeout(() => {
            const implementationHeader = document.querySelector('#implementation-content h2');
            if (implementationHeader) {
                implementationHeader.scrollIntoView({ behavior: 'smooth' });
            }
        }, 1000);
    }
    
    handleComplication(complication) {
        const chatMessages = document.getElementById('chat-messages');
        const complicationDiv = document.createElement('div');
        complicationDiv.className = 'system-message';
        
        complicationDiv.innerHTML = `
            <div class="message-content" style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px;">
                <strong>💡 New perspective from ${complication.source}!</strong><br><br>
                <strong>Insight:</strong> ${complication.description}<br><br>
                <em>This could ${complication.impact} your current thinking. How should the group respond?</em>
            </div>
        `;
        
        chatMessages.appendChild(complicationDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    handleResearchInsight(insight) {
        const chatMessages = document.getElementById('chat-messages');
        const insightDiv = document.createElement('div');
        insightDiv.className = 'system-message';
        
        let content = '<strong>🔍 Research Discovery:</strong><br><br>';
        
        if (insight.chatbot_implementations) {
            content += '<strong>New Implementation Data:</strong><br>';
            insight.chatbot_implementations.forEach(impl => {
                content += `• ${impl.company} (${impl.year}): ${impl.outcome}<br>`;
            });
        }
        
        if (insight.latest_trends) {
            content += '<br><strong>Latest Trends:</strong><br>';
            insight.latest_trends.forEach(trend => {
                content += `• ${trend}<br>`;
            });
        }
        
        content += `<br><em>${insight.discovery_context}</em>`;
        
        insightDiv.innerHTML = `
            <div class="message-content">
                ${content}
            </div>
        `;
        
        chatMessages.appendChild(insightDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    displayErrorMessage() {
        const errorMessage = {
            speaker: 'System',
            message: 'Sorry, there seems to be a connection issue. Please try again.',
            timestamp: new Date().toISOString()
        };
        
        const chatMessages = document.getElementById('chat-messages');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'system-message';
        errorDiv.innerHTML = `
            <div class="message-content" style="color: #dc2626;">
                ⚠️ ${errorMessage.message}
            </div>
        `;
        
        chatMessages.appendChild(errorDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    getConversationStage() {
        if (this.messageCount < 4) return 1;
        if (this.messageCount < 10) return 2;
        if (this.messageCount < 16) return 3;
        return 4;
    }
    
    updateProgressIndicator() {
        const indicator = document.getElementById('progress-indicator');
        if (!indicator) return;
        
        const stages = {
            'opening': 'Getting Started',
            'exploration': 'Exploring Options', 
            'analysis': 'Deep Analysis',
            'synthesis': 'Reaching Conclusions'
        };
        
        indicator.textContent = stages[this.conversationStage] || 'Strategic Analysis';
    }
    
    updateActivePeerCount() {
        const counter = document.getElementById('active-agents-count');
        if (counter) {
            const count = this.activePeers.length;
            counter.textContent = `${count} Study Partner${count === 1 ? '' : 's'} Active`;
        }
    }
    
    formatTime(timestamp) {
        return new Date(timestamp).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
    
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new StudyGroupSession();
});

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StudyGroupSession;
}