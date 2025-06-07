/**
 * Virtual Study Group Session for AI Chatbot Strategy Course
 * Simulates authentic peer-to-peer case discussion
 */

class VirtualStudyGroup {
  constructor() {
    this.sessionId = this.generateSessionId();
    this.activePeers = ['sarah_chen'];
    this.currentStage = 1;
    this.messageCount = 0;
    this.isWaitingForResponse = false;
    this.caseComplications = [];
    this.researchInsights = [];
    this.discussionHistory = [];
    
    // Server configuration
    this.serverUrl = 'https://ai-chatbot-oise.onrender.com';
    this.connectionStatus = 'checking';
    
    // Peer information
    this.peers = {
      'sarah_chen': {
        name: 'Sarah Chen',
        emoji: '💼',
        title: 'Finance MBA, Ex-McKinsey',
        background: 'Strategic Planning Director at tech company',
        expertise: 'Financial modeling, ROI analysis, consulting frameworks'
      },
      'marcus_rodriguez': {
        name: 'Marcus Rodriguez', 
        emoji: '🎯',
        title: 'Retail Operations Veteran',
        background: 'Customer Experience Director at major fashion brand',
        expertise: 'Retail operations, customer experience, implementation challenges'
      },
      'priya_patel': {
        name: 'Priya Patel',
        emoji: '🚀',
        title: 'Tech Startup Founder',
        background: 'Built and sold AI customer service platform',
        expertise: 'AI implementation, scalability, startup experience'
      }
    };
    
    this.init();
  }
  
  async init() {
    this.initializeEventListeners();
    await this.checkServerConnection();
    this.injectEnhancedStyles();
  }
  
  generateSessionId() {
    return 'study_group_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }
  
  // ====== SERVER CONNECTION ======
  async checkServerConnection() {
    try {
      console.log('Connecting to study group server...');
      const response = await fetch(`${this.serverUrl}/health`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        this.connectionStatus = 'connected';
        this.showConnectionStatus('✅ Study group connected - ready to collaborate', 'success');
        console.log('Study group server connected:', data);
      } else {
        throw new Error(`Server responded with status: ${response.status}`);
      }
    } catch (error) {
      console.error('Study group connection failed:', error);
      this.connectionStatus = 'disconnected';
      this.showConnectionStatus('⚠️ Study group starting up - please wait 30-60 seconds', 'warning');
      setTimeout(() => this.retryConnection(), 10000);
    }
  }
  
  async retryConnection() {
    if (this.connectionStatus === 'disconnected') {
      console.log('Retrying study group connection...');
      await this.checkServerConnection();
    }
  }
  
  showConnectionStatus(message, type) {
    const existingStatus = document.querySelector('.connection-status');
    if (existingStatus) existingStatus.remove();
    
    const statusDiv = document.createElement('div');
    statusDiv.className = `connection-status ${type}`;
    statusDiv.innerHTML = `
      <div class="status-content">
        <span class="status-icon">${type === 'success' ? '✅' : '⚠️'}</span>
        <span class="status-message">${message}</span>
        ${type === 'warning' ? '<small>Virtual classmates are joining - just like real study groups!</small>' : ''}
      </div>
    `;
    
    const studyGroupPanel = document.querySelector('.study-group-panel');
    const main = document.querySelector('main');
    const targetElement = studyGroupPanel || main;
    
    if (targetElement) {
      targetElement.insertBefore(statusDiv, targetElement.firstChild);
    }
    
    if (type === 'success') {
      setTimeout(() => {
        if (statusDiv.parentNode) statusDiv.remove();
      }, 5000);
    }
  }
  
  // ====== EVENT LISTENERS ======
  initializeEventListeners() {
    const startButton = document.getElementById('start-analysis');
    if (startButton) {
      startButton.addEventListener('click', () => this.startStudyGroupSession());
    }
    
    const sendButton = document.getElementById('send-message');
    if (sendButton) {
      sendButton.addEventListener('click', () => this.shareWithGroup());
    }
    
    const userInput = document.getElementById('user-input');
    if (userInput) {
      userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.shareWithGroup();
        }
      });
    }
    
    // FIXED: Peer invitation listeners - use correct class and event delegation
    const classmateList = document.querySelector('.classmate-list');
    if (classmateList) {
      classmateList.addEventListener('click', (e) => {
        const classmate = e.target.closest('.classmate');
        if (classmate && classmate.classList.contains('available')) {
          const agentId = classmate.dataset.agent;
          if (agentId) {
            this.invitePeerToDiscussion(agentId);
          }
        }
      });
      
      // Also handle keyboard events for accessibility
      classmateList.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          const classmate = e.target.closest('.classmate');
          if (classmate && classmate.classList.contains('available')) {
            e.preventDefault();
            const agentId = classmate.dataset.agent;
            if (agentId) {
              this.invitePeerToDiscussion(agentId);
            }
          }
        }
      });
    }
    
    // Group research listener
    const researchButton = document.getElementById('trigger-research');
    if (researchButton) {
      researchButton.addEventListener('click', () => this.triggerGroupResearch());
    }
    
    const buildButton = document.getElementById('start-building');
    if (buildButton) {
      buildButton.addEventListener('click', () => this.startBuildingPhase());
    }
    
    // Build step checkboxes
    const buildCheckboxes = document.querySelectorAll('.build-step input[type="checkbox"]');
    buildCheckboxes.forEach(checkbox => {
      checkbox.addEventListener('change', () => this.updateProgress());
    });
    
    const completeButton = document.getElementById('complete-session');
    if (completeButton) {
      completeButton.addEventListener('click', () => {
        window.location.href = 'reflection.html';
      });
    }
  }
  
  // ====== STUDY GROUP SESSION FLOW ======
  async startStudyGroupSession() {
    const caseDiscussion = document.getElementById('case-discussion');
    const aiConsultation = document.getElementById('ai-consultation');
    
    if (caseDiscussion) caseDiscussion.style.display = 'none';
    if (aiConsultation) aiConsultation.classList.remove('hidden');
    
    // Update UI labels for peer context
    this.updateUIForPeerContext();
    
    // Enable input
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-message');
    
    if (userInput) {
      userInput.disabled = false;
      userInput.placeholder = "Share your thoughts with your study group...";
    }
    if (sendButton) sendButton.disabled = false;
    
    await this.sendInitialPeerMessage();
  }
  
  updateUIForPeerContext() {
    // Update session status indicators
    const sessionStatus = document.getElementById('session-status');
    const progressIndicator = document.getElementById('progress-indicator');
    const activeCount = document.getElementById('active-agents-count');
    
    if (sessionStatus) sessionStatus.textContent = 'Study Group Discussion';
    if (progressIndicator) progressIndicator.textContent = 'Case Analysis';
    if (activeCount) activeCount.textContent = `${this.activePeers.length} Peer${this.activePeers.length > 1 ? 's' : ''} Active`;
    
    // Update chat header
    const chatHeader = document.querySelector('.chat-header h3');
    if (chatHeader) chatHeader.textContent = '💬 FashionForward Case Discussion';
    
    // Update input hints
    const inputHints = document.querySelector('.input-hints small');
    if (inputHints) inputHints.textContent = '💡 Your study group partners may have different perspectives - engage with their ideas!';
  }
  
  async sendInitialPeerMessage() {
    const initialPrompt = `You are Sarah Chen, starting a study group discussion about the FashionForward case. Introduce yourself briefly and ask for the human's initial reaction to Jessica's situation. Keep it natural and conversational - you're a peer, not a teacher.`;
    await this.callPeerDiscussion(initialPrompt, true);
  }
  
  async shareWithGroup() {
    const userInput = document.getElementById('user-input');
    const message = userInput?.value?.trim();
    
    if (!message || this.isWaitingForResponse) return;
    
    this.addMessageToChat('user', message);
    userInput.value = '';
    
    // Store in discussion history
    this.discussionHistory.push({
      speaker: 'human',
      message: message,
      timestamp: new Date().toISOString()
    });
    
    await this.callPeerDiscussion(message, false);
  }
  
  // ====== PEER COMMUNICATION ======
  async callPeerDiscussion(message, isInitial = false) {
    this.isWaitingForResponse = true;
    this.updateSendButton(true);
    
    if (!isInitial) {
      this.addTypingIndicator();
    }
    
    try {
      const response = await fetch(`${this.serverUrl}/chat`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          user_id: this.sessionId,
          message: message,
          stage: this.currentStage,
          session_type: 'peer_discussion'
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      this.removeTypingIndicator();
      
      // Handle peer response
      const peerName = data.speaker || this.peers[this.activePeers[0]]?.name || 'Study Partner';
      const peerId = data.peer_id || this.activePeers[0];
      
      this.addPeerMessage(peerId, peerName, data.response || 'Let me think about that...');
      
      // Store peer response
      this.discussionHistory.push({
        speaker: peerName,
        peer_id: peerId,
        message: data.response,
        timestamp: new Date().toISOString()
      });
      
      // Handle complications and insights
      if (data.complication) {
        setTimeout(() => this.displayComplication(data.complication), 3000);
      }
      
      if (data.research_insight) {
        setTimeout(() => this.displayResearchResults(data.research_insight), 5000);
      }
      
      this.messageCount++;
      this.currentStage++;
      
      if (this.messageCount >= 5) {
        this.checkForTransitionReadiness(data.response || '');
      }
      
    } catch (error) {
      this.removeTypingIndicator();
      console.error('Peer discussion failed:', error);
      
      let errorMessage = 'Having trouble connecting with the study group right now.';
      if (error.message.includes('500')) {
        errorMessage += ' The server might be busy - please try again in a moment.';
      } else if (error.message.includes('fetch')) {
        errorMessage += ' Please check your connection and try again.';
      }
      
      this.addMessageToChat('system', errorMessage);
    }
    
    this.isWaitingForResponse = false;
    this.updateSendButton(false);
  }
  
  // ====== PEER MANAGEMENT ======
  async invitePeerToDiscussion(peerId) {
    console.log('Inviting peer:', peerId); // Debug log
    
    if (this.activePeers.includes(peerId)) {
      console.log('Peer already active');
      return;
    }
    
    // Update UI immediately for better UX
    const peerElement = document.querySelector(`[data-agent="${peerId}"]`);
    if (peerElement) {
      peerElement.classList.remove('available');
      peerElement.classList.add('joining');
      peerElement.innerHTML = peerElement.innerHTML.replace('Invite to discuss', 'Joining...');
    }
    
    try {
      this.showLoadingState(`Inviting ${this.peers[peerId]?.name} to join...`);
      
      const response = await fetch(`${this.serverUrl}/invite_peer`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          user_id: this.sessionId,
          peer_id: peerId
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.peer_joined) {
        if (peerElement) {
          peerElement.classList.remove('joining');
          peerElement.classList.add('active');
          peerElement.innerHTML = peerElement.innerHTML.replace('Joining...', 'Active');
          peerElement.setAttribute('aria-pressed', 'true');
        }
        
        this.addPeerIntroduction(peerId, data.peer_name, data.introduction);
        this.activePeers.push(peerId);
        this.updateActivePeersCount();
      }
      
    } catch (error) {
      console.error('Failed to invite peer:', error);
      
      // Revert UI changes on error
      if (peerElement) {
        peerElement.classList.remove('joining');
        peerElement.classList.add('available');
        peerElement.innerHTML = peerElement.innerHTML.replace('Joining...', 'Invite to discuss');
      }
      
      this.addMessageToChat('system', 
        `❌ Unable to connect with ${this.peers[peerId]?.name}. ` +
        'They might be in another study group - please try again.'
      );
    } finally {
      this.hideLoadingState();
    }
  }
  
  // ====== GROUP RESEARCH ======
  async triggerGroupResearch() {
    const researchButton = document.getElementById('trigger-research');
    const researchStatus = document.getElementById('research-status');
    
    if (researchButton) {
      researchButton.disabled = true;
      researchButton.innerHTML = '📚 Researching together...';
    }
    if (researchStatus) researchStatus.textContent = 'Group is gathering market data...';
    
    try {
      const response = await fetch(`${this.serverUrl}/trigger_research`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          user_id: this.sessionId,
          topic: 'chatbot_implementations',
          research_type: 'group_research'
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.research) {
        this.displayGroupResearchResults(data.research);
        if (researchStatus) researchStatus.textContent = 'Research complete!';
      } else {
        throw new Error('No research data received');
      }
      
    } catch (error) {
      console.error('Group research failed:', error);
      if (researchStatus) researchStatus.textContent = 'Using available data';
      this.simulateGroupResearch();
    } finally {
      if (researchButton) {
        researchButton.disabled = false;
        researchButton.innerHTML = '📚 Let\'s research this together';
      }
      setTimeout(() => {
        if (researchStatus) researchStatus.textContent = '';
      }, 3000);
    }
  }
  
  simulateGroupResearch() {
    const cachedResearch = {
      chatbot_implementations: [
        {company: "Sephora", year: 2019, outcome: "25% email reduction, 15% phone increase"},
        {company: "H&M", year: 2020, outcome: "60% FAQ automation, improved CSAT"},
        {company: "ASOS", year: 2021, outcome: "45% faster response times, mixed satisfaction"}
      ],
      latest_trends: [
        "Hybrid AI-human models showing 40% better satisfaction than pure AI",
        "Personalization engines reducing repeat questions by 55%"
      ],
      peer_insights: [
        "This reminds me of Marcus's experience with implementation challenges",
        "Sarah's ROI framework could help evaluate these examples",
        "Priya might have insights on the technical feasibility"
      ]
    };
    
    this.displayGroupResearchResults(cachedResearch);
  }
  
  // ====== UI MANAGEMENT ======
  addMessageToChat(sender, message) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    let senderDisplay = '';
    switch(sender) {
      case 'user': senderDisplay = '👤 You'; break;
      case 'system': senderDisplay = '💻 System'; break;
      default: senderDisplay = sender;
    }
    
    messageDiv.innerHTML = `
      <div class="message-content">
        <div class="message-header">
          <span class="sender">${senderDisplay}</span>
          <span class="timestamp">${timestamp}</span>
        </div>
        <div class="message-text">${message.replace(/\n/g, '<br>')}</div>
      </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  
  addPeerMessage(peerId, peerName, message) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const peer = this.peers[peerId];
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message peer-message';
    
    const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    messageDiv.innerHTML = `
      <div class="peer-message-content">
        <div class="peer-message-header">
          <span class="peer-sender">${peer?.emoji || '👤'} ${peerName}</span>
          <span class="peer-expertise">${peer?.title || ''}</span>
          <span class="timestamp">${timestamp}</span>
        </div>
        <div class="message-text">${message.replace(/\n/g, '<br>')}</div>
      </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  
  addPeerIntroduction(peerId, peerName, introduction) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const peer = this.peers[peerId];
    const introDiv = document.createElement('div');
    introDiv.className = 'message peer-introduction';
    
    introDiv.innerHTML = `
      <div class="peer-intro-content">
        <div class="peer-avatar">${peer?.emoji || '👤'}</div>
        <div class="intro-text">
          <div class="peer-name">${peerName} joins the discussion</div>
          <div class="peer-background">${peer?.background || ''}</div>
          <div class="intro-message">${introduction}</div>
        </div>
      </div>
    `;
    
    chatMessages.appendChild(introDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  
  displayGroupResearchResults(research) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const researchDiv = document.createElement('div');
    researchDiv.className = 'message group-research-results';
    
    let researchHTML = '';
    if (research.chatbot_implementations) {
      researchHTML += '<h5>📊 What we found together:</h5><ul>';
      research.chatbot_implementations.forEach(impl => {
        researchHTML += `<li><strong>${impl.company}</strong> (${impl.year}): ${impl.outcome}</li>`;
      });
      researchHTML += '</ul>';
    }
    
    if (research.latest_trends) {
      researchHTML += '<h5>📈 Industry trends:</h5><ul>';
      research.latest_trends.forEach(trend => {
        researchHTML += `<li>${trend}</li>`;
      });
      researchHTML += '</ul>';
    }
    
    researchDiv.innerHTML = `
      <div class="research-content">
        <div class="research-header">
          <span class="research-icon">📚</span>
          <span class="research-title">Group Research Session</span>
        </div>
        <div class="research-data">${researchHTML}</div>
      </div>
    `;
    
    chatMessages.appendChild(researchDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    this.researchInsights.push(research);
    
    // Peer reactions to research
    setTimeout(() => {
      const activePeer = this.peers[this.activePeers[0]];
      this.addPeerMessage(
        this.activePeers[0], 
        activePeer?.name || 'Study Partner',
        `This research definitely changes things! The ${research.chatbot_implementations?.[0]?.company || 'implementation'} data is particularly interesting. How does this shift everyone's thinking?`
      );
    }, 2000);
  }
  
  displayComplication(complication) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const compDiv = document.createElement('div');
    compDiv.className = 'message complication-alert';
    
    const sourcePeer = complication.source || 'Study group';
    
    compDiv.innerHTML = `
      <div class="complication-content">
        <div class="complication-header">
          <span class="alert-icon">💡</span>
          <span class="alert-title">New perspective from ${sourcePeer}!</span>
        </div>
        <div class="complication-text">
          <p><strong>Insight:</strong> ${complication.description}</p>
          <p><em>This could ${complication.impact} your current thinking. How should the group respond?</em></p>
        </div>
      </div>
    `;
    
    chatMessages.appendChild(compDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    this.caseComplications.push(complication);
  }
  
  // ====== UTILITY METHODS ======
  addTypingIndicator() {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message peer-message typing-indicator';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
      <div class="message-content">
        <div class="message-header">
          <span class="sender">💭 Someone is typing...</span>
        </div>
        <div class="typing-animation">
          <span></span><span></span><span></span>
        </div>
      </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  
  removeTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) typingIndicator.remove();
  }
  
  updateSendButton(isLoading) {
    const sendButton = document.getElementById('send-message');
    const userInput = document.getElementById('user-input');
    
    if (sendButton) sendButton.disabled = isLoading;
    if (userInput) userInput.disabled = isLoading;
    
    if (sendButton) {
      if (isLoading) {
        sendButton.innerHTML = '<span class="loading-spinner">⏳</span>';
      } else {
        sendButton.innerHTML = '<span class="send-text">Share</span><span class="send-icon">📤</span>';
      }
    }
  }
  
  showLoadingState(message) {
    this.hideLoadingState();
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loading-state';
    loadingDiv.className = 'loading-state';
    loadingDiv.innerHTML = `
      <div class="loading-content">
        <span class="loading-spinner">⏳</span>
        <span class="loading-message">${message}</span>
      </div>
    `;
    
    const studyGroupPanel = document.querySelector('.study-group-panel');
    if (studyGroupPanel) studyGroupPanel.appendChild(loadingDiv);
  }
  
  hideLoadingState() {
    const loadingState = document.getElementById('loading-state');
    if (loadingState) loadingState.remove();
  }
  
  updateActivePeersCount() {
    const countElement = document.getElementById('active-agents-count');
    if (countElement) {
      const count = this.activePeers.length;
      countElement.textContent = `${count} Peer${count > 1 ? 's' : ''} Active`;
    }
  }
  
  // ====== TRANSITION MANAGEMENT ======
  checkForTransitionReadiness(response) {
    const transitionCues = [
      'ready to build',
      'start implementing',
      'move to implementation',
      'consensus',
      'decision made',
      'agreed on',
      'let\'s build'
    ];
    
    const hasTransitionCue = transitionCues.some(cue => 
      response.toLowerCase().includes(cue)
    );
    
    if (this.messageCount >= 5 && !document.getElementById('ready-to-build-btn')) {
      this.showReadyButton();
    }
    
    if (hasTransitionCue && this.messageCount >= 6) {
      setTimeout(() => this.transitionToBuilding(), 2000);
    }
  }
  
  showReadyButton() {
    const chatContainer = document.querySelector('.chat-input-container');
    if (!chatContainer || document.getElementById('ready-to-build-btn')) return;
    
    const readyButton = document.createElement('button');
    readyButton.id = 'ready-to-build-btn';
    readyButton.className = 'btn-secondary';
    readyButton.style.marginTop = '10px';
    readyButton.style.width = '100%';
    readyButton.innerHTML = '🛠️ Study Group Ready to Build';
    readyButton.onclick = () => {
      this.addMessageToChat('user', 'I think our study group has analyzed this thoroughly. Let\'s start building the solution!');
      setTimeout(() => this.transitionToBuilding(), 1000);
    };
    chatContainer.appendChild(readyButton);
  }
  
  async transitionToBuilding() {
    const aiConsultation = document.getElementById('ai-consultation');
    const implementationTransition = document.getElementById('implementation-transition');
    
    if (aiConsultation) aiConsultation.style.display = 'none';
    if (implementationTransition) implementationTransition.classList.remove('hidden');
    
    const summaryDiv = document.getElementById('strategy-summary');
    const highlightsDiv = document.getElementById('collaboration-highlights');
    
    if (summaryDiv) summaryDiv.innerHTML = '<div class="loading">📊 Summarizing group insights...</div>';
    if (highlightsDiv) highlightsDiv.innerHTML = '<div class="loading">🤝 Analyzing peer collaboration...</div>';
    
    try {
      const response = await fetch(`${this.serverUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.sessionId + '_summary',
          message: `Generate a brief summary of the study group's strategic analysis and key insights discovered through peer collaboration.`
        })
      });
      
      const data = await response.json();
      if (summaryDiv) summaryDiv.innerHTML = `<div class="strategy-recap">${data.response}</div>`;
      
    } catch (error) {
      if (summaryDiv) summaryDiv.innerHTML = '<div class="strategy-recap">Your study group analysis identified key strategic insights and reached consensus on the optimal approach through collaborative discussion.</div>';
    }
    
    const highlights = [
      `🎯 Multi-perspective analysis with ${this.activePeers.length} study partners`,
      `🔍 ${this.researchInsights.length} collaborative research sessions completed`,
      `⚠️ ${this.caseComplications.length} peer insights and complications navigated`,
      `💡 Authentic peer-to-peer learning achieved`
    ];
    
    if (highlightsDiv) {
      highlightsDiv.innerHTML = `<ul>${highlights.map(h => `<li>${h}</li>`).join('')}</ul>`;
    }
  }
  
  startBuildingPhase() {
    const implementationTransition = document.getElementById('implementation-transition');
    const chatbotBuilding = document.getElementById('chatbot-building');
    
    if (implementationTransition) implementationTransition.style.display = 'none';
    if (chatbotBuilding) {
      chatbotBuilding.classList.remove('hidden');
      chatbotBuilding.scrollIntoView({ behavior: 'smooth' });
    }
  }
  
  updateProgress() {
    const checkboxes = document.querySelectorAll('.build-step input[type="checkbox"]');
    const completionSection = document.getElementById('completion-section');
    if (!completionSection) return;
    
    const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);
    
    if (allChecked) {
      // Show the completion section
      completionSection.classList.remove('hidden');
      completionSection.scrollIntoView({ behavior: 'smooth' });
      
      // Enable the complete button
      const completeButton = document.getElementById('complete-session');
      if (completeButton) completeButton.disabled = false;
    } else {
      // Hide the completion section if not all checked
      completionSection.classList.add('hidden');
    }
  }
  
  // ====== ENHANCED STYLES INJECTION ======
  injectEnhancedStyles() {
    const peerStyles = `
      /* Peer-specific message styling */
      .peer-message .peer-message-content {
        margin-right: auto;
        background: linear-gradient(135deg, #f0f8ff, #e6f3ff);
        border: 1px solid #007bff;
        max-width: 80%;
        border-radius: 12px;
        padding: 15px;
      }
      
      .peer-message-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 8px;
        font-size: 0.85em;
      }
      
      .peer-sender {
        font-weight: 600;
        color: #0056b3;
      }
      
      .peer-expertise {
        background: rgba(0, 123, 255, 0.1);
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8em;
        color: #0056b3;
      }
      
      .peer-introduction {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        border-left: 4px solid #ffc107;
        margin: 20px 0;
        border-radius: 8px;
        animation: slideInFromRight 0.5s ease-out;
      }
      
      .peer-intro-content {
        display: flex;
        align-items: flex-start;
        gap: 20px;
        padding: 20px;
      }
      
      .peer-avatar {
        font-size: 2.5em;
        background: white;
        border-radius: 50%;
        width: 70px;
        height: 70px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        flex-shrink: 0;
      }
      
      .peer-name {
        font-weight: 600;
        color: var(--primary-color);
        margin-bottom: 4px;
        font-size: 1.1em;
      }
      
      .peer-background {
        font-size: 0.9em;
        color: #666;
        margin-bottom: 8px;
        font-style: italic;
      }
      
      .intro-message {
        color: #856404;
        line-height: 1.5;
      }
      
      .group-research-results {
        background: linear-gradient(135deg, #e7f3ff, #cce7ff);
        border-left: 4px solid #007bff;
        margin: 20px 0;
        border-radius: 8px;
        animation: slideInFromLeft 0.5s ease-out;
      }
      
      .complication-alert .alert-title {
        color: #007bff;
      }
      
      .complication-alert .alert-icon {
        color: #007bff;
      }
      
      .complication-alert {
        background: linear-gradient(135deg, #e7f3ff, #cce7ff);
        border-left: 4px solid #007bff;
      }
      
      /* Classmate interaction states */
      .classmate.joining {
        background: #fff3cd;
        border: 2px solid #ffc107;
        color: #856404;
        cursor: wait;
      }
      
      .classmate.joining:hover {
        transform: none;
        box-shadow: none;
      }
      
      /* Loading states */
      .loading-state {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        text-align: center;
      }
      
      .loading-content {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
      }
      
      .loading-spinner {
        animation: spin 1s linear infinite;
      }
      
      @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
      
      /* Connection status styling */
      .connection-status {
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        border-left: 4px solid;
      }
      
      .connection-status.success {
        background: #d4edda;
        border-color: #28a745;
        color: #155724;
      }
      
      .connection-status.warning {
        background: #fff3cd;
        border-color: #ffc107;
        color: #856404;
      }
      
      .connection-status.info {
        background: #cce7ff;
        border-color: #007bff;
        color: #004085;
      }
      
      .status-content {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
      }
      
      .status-content small {
        display: block;
        width: 100%;
        margin-top: 5px;
        font-style: italic;
      }
      
      /* Study group specific animations */
      @keyframes slideInFromRight {
        from { 
          opacity: 0; 
          transform: translateX(30px); 
        }
        to { 
          opacity: 1; 
          transform: translateX(0); 
        }
      }
      
      @keyframes slideInFromLeft {
        from { 
          opacity: 0; 
          transform: translateX(-30px); 
        }
        to { 
          opacity: 1; 
          transform: translateX(0); 
        }
      }
      
      /* Typing indicator */
      .typing-animation {
        display: flex;
        gap: 3px;
        align-items: center;
      }
      
      .typing-animation span {
        width: 8px;
        height: 8px;
        background: #007bff;
        border-radius: 50%;
        animation: typing 1.4s infinite ease-in-out;
      }
      
      .typing-animation span:nth-child(1) { animation-delay: -0.32s; }
      .typing-animation span:nth-child(2) { animation-delay: -0.16s; }
      .typing-animation span:nth-child(3) { animation-delay: 0s; }
      
      @keyframes typing {
        0%, 80%, 100% {
          transform: scale(0.8);
          opacity: 0.5;
        }
        40% {
          transform: scale(1);
          opacity: 1;
        }
      }
      
      /* Mobile responsive for peer messages */
      @media (max-width: 768px) {
        .peer-intro-content {
          flex-direction: column;
          text-align: center;
          gap: 15px;
        }
        
        .peer-message-header {
          flex-direction: column;
          align-items: flex-start;
          gap: 4px;
        }
        
        .peer-message .peer-message-content {
          max-width: 95%;
        }
        
        .status-content {
          flex-direction: column;
          align-items: flex-start;
        }
        
        .loading-content {
          flex-direction: column;
          gap: 8px;
        }
      }
      
      /* Reduced motion support */
      @media (prefers-reduced-motion: reduce) {
        .peer-introduction,
        .group-research-results {
          animation: none;
        }
        
        .loading-spinner {
          animation: none;
        }
        
        .typing-animation span {
          animation: none;
          opacity: 1;
          transform: scale(1);
        }
      }
    `;

    // Inject the peer-specific CSS
    const peerStyleSheet = document.createElement('style');
    peerStyleSheet.textContent = peerStyles;
    document.head.appendChild(peerStyleSheet);
  }
}

// Initialize when DOM is loaded
window.addEventListener('DOMContentLoaded', () => {
  window.studyGroup = new VirtualStudyGroup();
  console.log('Virtual Study Group initialized');
});