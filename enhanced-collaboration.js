// Enhanced Virtual Study Group Collaboration
// Connects to improved server.py for better conversation flow

class StudyGroupSession {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.activePeers = ['sarah_chen'];
        this.conversationStage = 'opening';
        this.messageCount = 0;
        this.serverUrl = 'https://ai-chatbot-oise.onrender.com'; // Your Render deployment
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
        
        // Peer invitation clicks - Fixed to use event delegation
        document.addEventListener('click', (e) => {
            if (e.target.closest('.classmate.available')) {
                const classmate = e.target.closest('.classmate');
                const agentId = classmate.dataset.agent;
                if (agentId) {
                    this.invitePeer(agentId);
                }
            }
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
            
            // Debug logging
            console.log('Server response:', data);
            
            // SAFETY CHECK: Make sure we have something to display
            if (data && (data.response || data.message)) {
                // Create proper message object for display
                const messageToDisplay = {
                    speaker: data.speaker || 'Study Partner',
                    peer_id: data.peer_id || 'sarah_chen',
                    message: data.response || data.message,
                    timestamp: new Date().toISOString(),
                    was_directly_addressed: data.was_directly_addressed || false
                };
                
                this.displayMessage(messageToDisplay, 'peer');
                
                // Handle any complications or insights
                if (data.complication) {
                    setTimeout(() => this.handleComplication(data.complication), 2000);
                }
                
                if (data.research_insight) {
                    setTimeout(() => this.handleResearchInsight(data.research_insight), 3000);
                }
                
                // Update conversation stage
                if (data.conversation_stage) {
                    this.conversationStage = data.conversation_stage;
                    this.updateProgressIndicator();
                }
                
                this.messageCount++;
                
                // Check if we should show the ready button after enough discussion
                this.checkForReadyButton();
                
            } else {
                console.error('Invalid server response:', data);
                this.displayErrorMessage('The study partner seems to be thinking. Please try again.');
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.displayErrorMessage('Connection issue with study group. Please try again.');
        } finally {
            // Re-enable input
            userInput.disabled = false;
            document.getElementById('send-message').disabled = false;
            userInput.focus();
        }
    }
    
    displayMessage(messageData, type) {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;
        
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
            
            // DEFENSIVE CODING - handle missing properties
            const speaker = messageData.speaker || 'Study Partner';
            const peerId = messageData.peer_id || 'sarah_chen';
            const message = messageData.message || 'Let me think about that...';
            const timestamp = messageData.timestamp || new Date().toISOString();
            
            const peerInfo = this.getPeerInfo(peerId);
            
            messageDiv.innerHTML = `
                <div class="peer-message-content">
                    <div class="peer-message-header">
                        <span class="peer-sender">${this.escapeHtml(speaker)}</span>
                        <span class="peer-expertise">${this.escapeHtml(peerInfo.expertise)}</span>
                        <span class="timestamp">${this.formatTime(timestamp)}</span>
                    </div>
                    <div class="message-text">${this.escapeHtml(message)}</div>
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
        
        if (!peerElement || peerElement.classList.contains('active')) {
            return; // Already active or not found
        }
        
        // Update UI immediately for better UX
        peerElement.classList.remove('available');
        peerElement.classList.add('joining');
        peerElement.innerHTML = peerElement.innerHTML.replace('Invite to discuss', 'Joining...');
        
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
            
            console.log('Invite peer response:', data);
            
            if (response.ok && data.peer_joined) {
                // Update UI to active state
                peerElement.classList.remove('joining');
                peerElement.classList.add('active');
                peerElement.innerHTML = peerElement.innerHTML.replace('Joining...', 'Active');
                
                // Add peer to active list
                this.activePeers.push(peerId);
                
                // Display introduction message
                if (data.introduction) {
                    this.displayMessage({
                        speaker: data.peer_name || this.getPeerName(peerId),
                        peer_id: peerId,
                        message: data.introduction,
                        timestamp: new Date().toISOString()
                    }, 'peer');
                }
                
                // Update active count
                this.updateActivePeerCount();
                
            } else {
                throw new Error(data.error || 'Failed to invite peer');
            }
            
        } catch (error) {
            console.error('Error inviting peer:', error);
            
            // Revert UI changes on error
            peerElement.classList.remove('joining');
            peerElement.classList.add('available');
            peerElement.innerHTML = peerElement.innerHTML.replace('Joining...', 'Invite to discuss');
            
            this.displayErrorMessage(`Unable to connect with ${this.getPeerName(peerId)}. Please try again.`);
        }
    }
    
    getPeerName(peerId) {
        const peerNames = {
            'sarah_chen': 'Sarah Chen',
            'marcus_rodriguez': 'Marcus Rodriguez',
            'priya_patel': 'Priya Patel'
        };
        return peerNames[peerId] || 'Study Partner';
    }
    
    async triggerGroupResearch() {
        const researchButton = document.getElementById('trigger-research');
        const researchStatus = document.getElementById('research-status');
        
        if (researchButton) {
            researchButton.disabled = true;
            researchButton.textContent = 'Researching together...';
        }
        if (researchStatus) researchStatus.textContent = 'Group is gathering market data...';
        
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
            
            if (response.ok && data.research) {
                this.displayResearchFindings(data.research);
                if (researchStatus) researchStatus.textContent = 'Research complete!';
            } else {
                throw new Error('No research data received');
            }
            
        } catch (error) {
            console.error('Error triggering research:', error);
            if (researchStatus) researchStatus.textContent = 'Using available data';
            
            // Fallback research data
            this.displayResearchFindings({
                recent_implementations: [
                    {company: "Sephora", outcome: "25% email reduction, 15% phone increase"},
                    {company: "H&M", outcome: "60% FAQ automation, improved CSAT"},
                    {company: "ASOS", outcome: "45% faster response times, mixed satisfaction"}
                ],
                financial_benchmarks: [
                    "Average fashion retail sees 35% cost reduction in year 2",
                    "Hidden costs: Training (20-30%), integration (15-25%), change management (10-15%)"
                ],
                peer_contributions: [
                    "Group research session completed",
                    "Multiple industry perspectives gathered"
                ]
            });
        } finally {
            if (researchButton) {
                researchButton.disabled = false;
                researchButton.textContent = '📚 Let\'s research this together';
            }
            setTimeout(() => {
                if (researchStatus) researchStatus.textContent = '';
            }, 3000);
        }
    }
    
    displayResearchFindings(research) {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;
        
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
        console.log('Checking readiness for:', message, 'Message count:', this.messageCount);
        
        const readinessKeywords = [
            'ready to build', 'let\'s build', 'start building', 'ready for implementation',
            'let\'s implement', 'move to implementation', 'build the chatbot',
            'ready to create', 'time to build', 'let\'s start building'
        ];
        
        const messageLower = message.toLowerCase();
        const isReady = readinessKeywords.some(keyword => messageLower.includes(keyword));
        
        if (isReady && !this.isReadyForImplementation) {
            this.isReadyForImplementation = true;
            setTimeout(() => this.showImplementationTransition(), 1000);
        }
    }
    
    checkForReadyButton() {
        console.log('Checking for ready button. Message count:', this.messageCount, 'Ready for implementation:', this.isReadyForImplementation);
        
        // Show ready button after 5 messages if not already shown
        if (this.messageCount >= 5 && !this.isReadyForImplementation && !document.getElementById('ready-to-build-btn')) {
            this.showReadyButton();
        }
    }
    
    showReadyButton() {
        const chatContainer = document.querySelector('.chat-input-container');
        if (!chatContainer || document.getElementById('ready-to-build-btn')) return;
        
        console.log('Creating ready button');
        
        const readyButton = document.createElement('button');
        readyButton.id = 'ready-to-build-btn';
        readyButton.className = 'btn-secondary';
        readyButton.style.marginTop = '10px';
        readyButton.style.width = '100%';
        readyButton.innerHTML = '🛠️ Study Group Ready to Build';
        readyButton.onclick = () => {
            console.log('Ready button clicked');
            this.displayMessage({
                speaker: 'You',
                message: 'I think our study group has analyzed this thoroughly. Let\'s start building the solution!',
                timestamp: new Date().toISOString()
            }, 'user');
            this.isReadyForImplementation = true;
            setTimeout(() => this.showImplementationTransition(), 1000);
        };
        chatContainer.appendChild(readyButton);
    }
    
    showImplementationTransition() {
        // Show the transition section
        const transitionSection = document.getElementById('implementation-transition');
        if (transitionSection) {
            transitionSection.classList.remove('hidden');
            
            // Populate strategy summary based on conversation
            this.populateStrategySummary();
            
            // Setup the "Start Building" button - Remove any existing listeners first
            const startBuildingBtn = document.getElementById('start-building');
            if (startBuildingBtn) {
                startBuildingBtn.replaceWith(startBuildingBtn.cloneNode(true));
                document.getElementById('start-building').addEventListener('click', () => {
                    this.showImplementationContent();
                });
            }
            
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
        const implementationContent = document.getElementById('implementation-content');
        const finalNavigation = document.getElementById('final-navigation');
        const implementationTransition = document.getElementById('implementation-transition');
        
        if (implementationContent) {
            implementationContent.classList.remove('hidden');
            implementationContent.scrollIntoView({ behavior: 'smooth' });
        }
        
        if (finalNavigation) {
            finalNavigation.classList.remove('hidden');
        }
        
        // Hide the transition section
        if (implementationTransition) {
            implementationTransition.style.display = 'none';
        }
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
                    const completionSection = document.getElementById('completion-section');
                    if (completionSection) {
                        completionSection.classList.remove('hidden');
                        completionSection.scrollIntoView({ behavior: 'smooth' });
                    }
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
        const risks = document.getElementById('risks-analysis')?.value.trim() || '';
        const metrics = document.getElementById('success-metrics')?.value.trim() || '';
        const brandVoice = document.getElementById('brand-voice')?.value.trim() || '';
        
        const feedback = document.getElementById('analysis-feedback');
        if (!feedback) return;
        
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
        if (!chatMessages) return;
        
        const complicationDiv = document.createElement('div');
        complicationDiv.className = 'system-message';
        
        complicationDiv.innerHTML = `
            <div class="message-content" style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px;">
                <strong>💡 New perspective from ${this.escapeHtml(complication.source || 'Study Group')}!</strong><br><br>
                <strong>Insight:</strong> ${this.escapeHtml(complication.description || 'Interesting development')}<br><br>
                <em>This could ${this.escapeHtml(complication.impact || 'affect')} your current thinking. How should the group respond?</em>
            </div>
        `;
        
        chatMessages.appendChild(complicationDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    handleResearchInsight(insight) {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;
        
        const insightDiv = document.createElement('div');
        insightDiv.className = 'system-message';
        
        let content = '<strong>🔍 Research Discovery:</strong><br><br>';
        
        if (insight.chatbot_implementations) {
            content += '<strong>New Implementation Data:</strong><br>';
            insight.chatbot_implementations.forEach(impl => {
                content += `• ${this.escapeHtml(impl.company)} (${impl.year}): ${this.escapeHtml(impl.outcome)}<br>`;
            });
        }
        
        if (insight.latest_trends) {
            content += '<br><strong>Latest Trends:</strong><br>';
            insight.latest_trends.forEach(trend => {
                content += `• ${this.escapeHtml(trend)}<br>`;
            });
        }
        
        if (insight.discovery_context) {
            content += `<br><em>${this.escapeHtml(insight.discovery_context)}</em>`;
        }
        
        insightDiv.innerHTML = `
            <div class="message-content">
                ${content}
            </div>
        `;
        
        chatMessages.appendChild(insightDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    displayErrorMessage(customMessage = null) {
        const errorMessage = customMessage || 'Sorry, there seems to be a connection issue. Please try again.';
        
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'system-message';
        errorDiv.innerHTML = `
            <div class="message-content" style="color: #dc2626;">
                ⚠️ ${this.escapeHtml(errorMessage)}
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
        try {
            return new Date(timestamp).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        } catch (error) {
            return new Date().toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        }
    }
    
    escapeHtml(text) {
        // SAFETY CHECK: Handle undefined/null values
        if (!text || typeof text !== 'string') {
            return String(text || ''); // Convert to string or return empty string
        }
        
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
// Add this function to your enhanced-collaboration.js file

function copyToClipboard(button) {
    const textToCopy = button.getAttribute('data-copy');
    
    // Use the modern clipboard API if available
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(textToCopy).then(() => {
            showCopySuccess(button);
        }).catch(err => {
            // Fallback for older browsers
            fallbackCopyTextToClipboard(textToCopy, button);
        });
    } else {
        // Fallback for older browsers
        fallbackCopyTextToClipboard(textToCopy, button);
    }
}

function fallbackCopyTextToClipboard(text, button) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    
    // Avoid scrolling to bottom
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";
    
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showCopySuccess(button);
        }
    } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
    }
    
    document.body.removeChild(textArea);
}

function showCopySuccess(button) {
    const originalText = button.textContent;
    button.textContent = 'Copied!';
    button.classList.add('copied');
    
    setTimeout(() => {
        button.textContent = originalText;
        button.classList.remove('copied');
    }, 2000);
}
// Enhanced feedback for application ability
document.querySelectorAll('input[name="application-ability"]').forEach(radio => {
  radio.addEventListener('change', function() {
    const feedbackDiv = document.getElementById('application-feedback');
    let message = '';
    let className = '';
    
    switch (this.value) {
      case 'not-able':
        message = "🔄 That's honest feedback. Consider revisiting the hands-on sections or reaching out for additional support. Learning complex topics often requires multiple exposures.";
        className = 'concerning';
        break;
      case 'understand-need-support':
        message = "💪 Good self-awareness! Understanding concepts is the first step. Consider practicing with a colleague or seeking mentorship to build your application skills.";
        className = 'needs-improvement';
        break;
      case 'some-confidence':
        message = "✅ Great progress! You have a solid foundation. The best way to build more confidence is through practice and real-world application.";
        className = 'good';
        break;
      case 'confident-use':
        message = "🎉 Excellent! You're ready to implement what you've learned. Consider sharing your knowledge with others to reinforce your learning.";
        className = 'excellent';
        break;
    }
    
    feedbackDiv.textContent = message;
    feedbackDiv.className = `feedback-message ${className} show`;
  });
});

// Enhanced feedback for retention likelihood
document.querySelectorAll('input[name="retention-likelihood"]').forEach(radio => {
  radio.addEventListener('change', function() {
    const feedbackDiv = document.getElementById('retention-feedback');
    let message = '';
    let className = '';
    
    switch (this.value) {
      case 'forget-most':
        message = "📚 Consider creating a personal summary or action plan to help retain key concepts. Spaced repetition and practical application are key to long-term retention.";
        className = 'concerning';
        break;
      case 'general-ideas':
        message = "🧠 That's very normal! Most people benefit from refreshers. Consider bookmarking key resources or setting up periodic review reminders.";
        className = 'needs-improvement';
        break;
      case 'key-concepts':
        message = "💡 Strong retention! You've internalized the core concepts. Try explaining them to someone else to further solidify your understanding.";
        className = 'good';
        break;
      case 'confident-apply':
        message = "🌟 Outstanding! Your confidence in retention suggests excellent learning integration. You're well-positioned to be a knowledge leader in this area.";
        className = 'excellent';
        break;
    }
    
    feedbackDiv.textContent = message;
    feedbackDiv.className = `feedback-message ${className} show`;
  });
});