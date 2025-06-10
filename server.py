from flask import Flask, request, jsonify
from openai import OpenAI
from flask_cors import CORS
import os
import json
import random
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Store conversation histories and session data
conversation_histories = {}
active_study_groups = {}

class VirtualPeer:
    def __init__(self, peer_id, name, background, personality, speaking_style, biases, expertise):
        self.peer_id = peer_id
        self.name = name
        self.background = background
        self.personality = personality
        self.speaking_style = speaking_style
        self.biases = biases
        self.expertise = expertise
        self.conversation_history = []
        self.response_count = 0

    def generate_response(self, user_message, discussion_context, active_peers, is_directly_addressed=False):
        """Generate response with human-first priority and better conversation flow"""

        # Check for meaningless or very short input first
        if self._is_meaningless_input(user_message):
            return self._generate_clarifying_question()

        # Check if user is inviting the peer to share thoughts
        if self._is_direct_invitation(user_message):
            return "Sure, let me expand on that from my perspective!"

        # Build conversation context and response prompt
        conversation_context = self._build_conversation_context(discussion_context)
        response_type = self._analyze_user_input(user_message)

        peer_prompt = f"""You are {self.name} in an MBA study group discussing the FashionForward customer service case.

CASE CONTEXT: Jessica Martinez (CEO) must choose between:
1. AI Chatbot: $87K over 2 years, automates 65% of customer inquiries
2. Team Expansion: $256K over 2 years, maintains human touch
3. Outsourcing: $383K over 2 years, professional but expensive

YOUR IDENTITY:
- Background: {self.background}
- Personality: {self.personality}
- Speaking Style: {self.speaking_style}
- Expertise: {self.expertise}

RECENT CONVERSATION:
{conversation_context}

HUMAN'S INPUT: "{user_message}"
RESPONSE TYPE NEEDED: {response_type}

CRITICAL INSTRUCTIONS:
1. RESPOND DIRECTLY TO THE HUMAN - they just spoke to the group
2. {self._get_response_guidance(response_type, user_message)}
3. Sound like a real MBA student, not a consultant
4. Keep it conversational and natural (1-2 sentences max)
5. Show your {self.personality} perspective
6. {'You were directly addressed by name' if is_directly_addressed else 'Respond as part of group discussion'}

GOOD RESPONSE EXAMPLES:
- "Yeah, good point! From my experience at a major fashion brand, I'd also add..."
- "Hmm, I actually see it differently. What if we considered..."
- "That's exactly what I was thinking! And here's another angle..."
- "Wait, are we sure about that assumption? In my startup we found..."

Your response as {self.name}:"""

        # (Existing OpenAI API call logic follows...)

    def _is_meaningless_input(self, user_message):
        """Detect if the user's input is too short, vague, or uninformative."""
        vague_phrases = ["ok", "okay", "sure", "yup", "yeah", "yes", "hmm", "alright", "fine", "cool", "uh huh", "k", "got it"]
        nonsense_patterns = ["blah", "blah blah", "...", "???", "idk", "huh", "nonsense"]

        input_lower = user_message.lower().strip()

        if input_lower in vague_phrases:
            return True
        if any(phrase in input_lower for phrase in nonsense_patterns):
            return True
        if len(input_lower.split()) <= 2 and len(input_lower) <= 10:
            return True

        return False

    def _is_direct_invitation(self, user_message):
        """Detect if the user is prompting the peer to share insights"""
        invitation_phrases = ["please share", "can you share", "tell me more", "could you explain", "your thoughts", "what’s your take", "what’s your perspective", "can you tell me more"]
        input_lower = user_message.lower().strip()
        return any(phrase in input_lower for phrase in invitation_phrases)

def _generate_clarifying_question(self):
    """Generate a polite clarifying question, tailored to the peer's personality"""
    if self.peer_id == "marcus_rodriguez":
        clarifying_questions = [
            "Could you give me a bit more context there?",
            "Hmm, I'm not quite sure what you mean. Can you clarify that a bit?"
        ]
    elif self.peer_id == "sarah_chen":
        clarifying_questions = [
            "Could you clarify that so we’re on the same page financially?",
            "That’s an interesting point—can you expand on it a bit more for us?"
        ]
    elif self.peer_id == "priya_patel":
        clarifying_questions = [
            "Interesting! Can you tell me more about what you meant?",
            "Oh, could you dive a bit deeper into that idea? I’m curious!"
        ]
    else:
        # Default fallback clarifying questions
        clarifying_questions = [
            "I'm not sure I understand - could you clarify what you meant?",
            "Could you expand on that a bit? What exactly are you thinking about?"
        ]
    
    return random.choice(clarifying_questions)

    # (The rest of your methods here...)



CASE CONTEXT: Jessica Martinez (CEO) must choose between:
1. AI Chatbot: $87K over 2 years, automates 65% of customer inquiries
2. Team Expansion: $256K over 2 years, maintains human touch
3. Outsourcing: $383K over 2 years, professional but expensive

YOUR IDENTITY:
- Background: {self.background}
- Personality: {self.personality} 
- Speaking Style: {self.speaking_style}
- Expertise: {self.expertise}

RECENT CONVERSATION:
{conversation_context}

HUMAN'S INPUT: "{user_message}"
RESPONSE TYPE NEEDED: {response_type}

CRITICAL INSTRUCTIONS:
1. RESPOND DIRECTLY TO THE HUMAN - they just spoke to the group
2. {self._get_response_guidance(response_type, user_message)}
3. Sound like a real MBA student, not a consultant
4. Keep it conversational and natural (1-2 sentences max)
5. Show your {self.personality} perspective
6. {'You were directly addressed by name' if is_directly_addressed else 'Respond as part of group discussion'}

GOOD RESPONSE EXAMPLES:
- "Yeah, good point! From my experience at [company], I'd also add..."
- "Hmm, I actually see it differently. What if we considered..."
- "That's exactly what I was thinking! And here's another angle..."
- "Wait, are we sure about that assumption? In my startup we found..."

Your response as {self.name}:"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": peer_prompt}],
                temperature=0.7,
                max_tokens=100,
                presence_penalty=0.8,
                frequency_penalty=0.5
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Simple cleanup - remove quotes and name attribution
            if response_text.startswith('"') and response_text.endswith('"'):
                response_text = response_text[1:-1]
            if response_text.startswith("'") and response_text.endswith("'"):
                response_text = response_text[1:-1]
            
            # Remove name attribution if present
            name_pattern = self.name + ":"
            if response_text.startswith(name_pattern):
                response_text = response_text[len(name_pattern):].strip()
            
            self.response_count += 1
            return response_text
            
        except Exception as e:
            print(f"Error generating response for {self.name}: {str(e)}")
            # Contextual fallback responses that respond to the human
            fallbacks = {
                "sarah_chen": "Let me think about that from a financial perspective...",
                "marcus_rodriguez": "That's interesting - from a customer experience standpoint...",
                "priya_patel": "Good question! In my startup experience..."
            }
            return fallbacks.get(self.peer_id, "That's a great point - let me consider that.")

    def _analyze_user_input(self, user_message):
        """Analyze what type of response the human is looking for"""
        message_lower = user_message.lower().strip()
        
        # Follow-up questions
        if any(phrase in message_lower for phrase in ['what else', 'what other', 'anything else', 'what about', 'also']):
            return "FOLLOW_UP_QUESTION - Provide additional insights or perspectives on the current topic"
        
        # Direct questions
        if message_lower.endswith('?') or any(word in message_lower for word in ['how', 'what', 'why', 'when', 'where', 'should']):
            return "DIRECT_QUESTION - Answer their specific question directly"
        
        # Agreement/disagreement seeking
        if any(phrase in message_lower for phrase in ['do you think', 'agree', 'thoughts on', 'opinion']):
            return "OPINION_REQUEST - Share your perspective and reasoning"
        
        # Sharing their analysis
        if any(phrase in message_lower for phrase in ['i think', 'i believe', 'my view', 'it seems']):
            return "STUDENT_ANALYSIS - Respond to their analysis with your perspective"
        
        # Challenge or debate
        if any(phrase in message_lower for phrase in ['but', 'however', 'disagree', 'not sure']):
            return "CHALLENGE - Engage with their point and offer your perspective"
        
        return "GENERAL_DISCUSSION - Engage naturally with their contribution"
    
    def _get_response_guidance(self, response_type, user_message):
        """Get specific guidance based on what the human needs"""
        guidance = {
            "FOLLOW_UP_QUESTION": "They want more information - add a new insight or perspective to build on what's already been discussed",
            "DIRECT_QUESTION": "Answer their specific question directly and concisely",
            "OPINION_REQUEST": "Give your clear opinion with brief reasoning from your background",
            "STUDENT_ANALYSIS": "React to their analysis - agree, disagree, or build on it",
            "CHALLENGE": "Engage thoughtfully with their challenge or counterpoint",
            "GENERAL_DISCUSSION": "Respond naturally to their contribution to keep discussion flowing"
        }
        return guidance.get(response_type, "Engage naturally with their input")

    def _build_conversation_context(self, discussion_context):
        """Build conversation context from recent history"""
        if not discussion_context.get("discussion_history"):
            return "This is the start of your discussion."
        
        # Get last 4 exchanges for context
        recent_history = discussion_context["discussion_history"][-4:]
        
        context_lines = []
        for msg in recent_history:
            speaker = msg.get("speaker", "Unknown")
            message = msg.get("message", "")
            
            if speaker == "human":
                context_lines.append(f"STUDENT: {message}")
            else:
                peer_name = speaker.replace(" Rodriguez", "").replace(" Chen", "").replace(" Patel", "")
                context_lines.append(f"{peer_name.upper()}: {message}")
        
        return "\n".join(context_lines) if context_lines else "This is the start of your discussion."

class StudyGroupSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.peers = {
            "sarah_chen": VirtualPeer(
                "sarah_chen",
                "Sarah Chen", 
                "Finance MBA from Wharton, 3 years at McKinsey consulting on retail strategy",
                "Analytical and thorough, likes frameworks but stays practical, good at asking clarifying questions",
                "Professional but approachable, uses consulting terminology naturally, focuses on data and ROI",
                "Defaults to financial analysis first, sometimes misses emotional/customer factors initially",
                "Financial modeling, ROI analysis, consulting frameworks, strategic planning, retail economics"
            ),
            "marcus_rodriguez": VirtualPeer(
                "marcus_rodriguez",
                "Marcus Rodriguez",
                "15 years in retail operations, currently Customer Experience Director at a major fashion brand", 
                "Practical and customer-focused, draws from real experience, protective of brand reputation",
                "Direct and conversational, uses real examples, passionate about customer experience",
                "Prioritizes customer satisfaction over pure efficiency, skeptical of technology that feels impersonal",
                "Retail operations, customer journey mapping, brand management, implementation challenges"
            ),
            "priya_patel": VirtualPeer(
                "priya_patel", 
                "Priya Patel",
                "Founded and sold AI customer service startup to Zendesk, now Stanford MBA focusing on scaling tech solutions",
                "Energetic and solution-oriented, optimistic about technology, thinks in terms of scale and growth",
                "Startup energy, comfortable with tech terminology, focuses on implementation and scalability",
                "Sees technology solutions first, sometimes underestimates change management and adoption challenges",
                "AI/ML implementation, startup scaling, product development, technology adoption"
            )
        }
        self.active_peers = ["sarah_chen"]
        self.discussion_history = []
        self.research_insights = []
        self.complications_used = []
        
        # Peer complications for realistic insights
        self.peer_complications = [
            {
                "type": "implementation_reality",
                "description": "Marcus just mentioned that when his company tried a chatbot, customer complaints increased 30% in month 1 because the bot couldn't handle frustrated customers properly",
                "impact": "significantly challenge your current thinking",
                "source": "Marcus Rodriguez"
            },
            {
                "type": "financial_insight", 
                "description": "Sarah found McKinsey data showing that 60% of retail AI implementations exceed budget by 40%+ due to integration complexity and change management costs",
                "impact": "revise your financial assumptions",
                "source": "Sarah Chen"
            },
            {
                "type": "competitive_intelligence",
                "description": "Priya heard through her network that FashionForward's biggest competitor is about to launch an AI-powered personal stylist feature",
                "impact": "add urgency to your decision",
                "source": "Priya Patel"
            }
        ]

    def determine_responding_peer(self, user_message, stage, discussion_context):
        """Enhanced peer selection with HUMAN-FIRST priority"""
        
        message_lower = user_message.lower()
        recent_speakers = self._get_recent_speakers(discussion_context)
        
        # 1. Check for direct addressing first
        direct_address = self._check_direct_address(message_lower)
        if direct_address and direct_address in self.active_peers:
            return direct_address, True
        
        # 2. Detect follow-up questions that need immediate response
        if self._is_follow_up_question(user_message):
            relevant_peer = self._find_most_relevant_peer_for_followup(discussion_context)
            if relevant_peer and relevant_peer in self.active_peers:
                return relevant_peer, False
        
        # 3. Avoid same peer responding twice in a row
        if recent_speakers and len(recent_speakers) > 0:
            last_speaker_id = recent_speakers[0]
            available_peers = [p for p in self.active_peers if p != last_speaker_id]
            if available_peers:
                peer_pool = available_peers
            else:
                peer_pool = self.active_peers
        else:
            peer_pool = self.active_peers
        
        # 4. Content-based routing with expertise matching
        content_priority = self._analyze_message_content(message_lower)
        
        for topic, peer_id in content_priority:
            if peer_id in peer_pool:
                return peer_id, False
        
        # 5. Default: choose first available peer
        if peer_pool:
            return peer_pool[0], False
        
        return self.active_peers[0], False

    def _check_direct_address(self, message_lower):
        """Check if user directly addressed a specific peer"""
        address_patterns = {
            "sarah_chen": ["sarah", "@sarah", "hey sarah", "sarah,"],
            "marcus_rodriguez": ["marcus", "@marcus", "hey marcus", "marcus,"],
            "priya_patel": ["priya", "@priya", "hey priya", "priya,"]
        }
        
        for peer_id, patterns in address_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return peer_id
        return None

    def _get_recent_speakers(self, discussion_context):
        """Get recent speakers to avoid repetition"""
        if not discussion_context.get("discussion_history"):
            return []
        
        recent_messages = discussion_context["discussion_history"][-3:]
        speakers = []
        
        for msg in recent_messages:
            if msg.get("speaker") != "human":
                peer_id = msg.get("peer_id")
                if peer_id:
                    speakers.append(peer_id)
        
        return speakers

    def _analyze_message_content(self, message_lower):
        """Analyze message content and return priority list of (topic, peer_id)"""
        content_routing = []
        
        # Financial/business topics
        if any(word in message_lower for word in ["roi", "cost", "budget", "revenue", "profit", "financial", "money"]):
            content_routing.append(("financial", "sarah_chen"))
        
        # Customer experience topics  
        if any(word in message_lower for word in ["customer", "experience", "satisfaction", "service", "brand"]):
            content_routing.append(("customer_experience", "marcus_rodriguez"))
        
        # Technology/implementation topics
        if any(word in message_lower for word in ["technology", "ai", "implementation", "integration", "platform"]):
            content_routing.append(("technology", "priya_patel"))
        
        return content_routing

    def _is_follow_up_question(self, user_message):
        """Detect if this is a follow-up question that needs direct response"""
        message_lower = user_message.lower().strip()
        
        follow_up_indicators = [
            'what else', 'what other', 'anything else', 'what about',
            'also', 'and', 'plus', 'additionally', 'furthermore'
        ]
        
        return any(indicator in message_lower for indicator in follow_up_indicators)
    
    def _find_most_relevant_peer_for_followup(self, discussion_context):
        """Find the peer most relevant to continue the current discussion"""
        if not discussion_context.get("discussion_history"):
            return "sarah_chen"
        
        # Look at the last few peer messages
        recent_peer_messages = []
        for msg in discussion_context["discussion_history"][-3:]:
            if msg.get("speaker") != "human" and msg.get("peer_id"):
                recent_peer_messages.append(msg.get("peer_id"))
        
        if recent_peer_messages:
            return recent_peer_messages[-1]
        
        return "sarah_chen"

    def get_discussion_context(self):
        """Get comprehensive discussion context"""
        return {
            "discussion_history": self.discussion_history,
            "active_peers": self.active_peers,
            "complications": self.complications_used,
            "message_count": len(self.discussion_history)
        }
    
    def should_introduce_complication(self, stage):
        """Smart timing for introducing complications"""
        return (len(self.complications_used) < 2 and 
                len(self.discussion_history) > 6 and
                random.random() < 0.35)
    
    def generate_peer_complication(self):
        """Generate realistic complications from peer experience"""
        unused = [c for c in self.peer_complications if c not in self.complications_used]
        if not unused:
            return None
            
        # Filter by active peers
        suitable = []
        for comp in unused:
            source_peer_id = self._get_peer_id_from_source(comp['source'])
            if source_peer_id in self.active_peers:
                suitable.append(comp)
        
        if suitable:
            complication = random.choice(suitable)
            self.complications_used.append(complication)
            return complication
        
        return None

    def _get_peer_id_from_source(self, source_name):
        """Convert source name to peer ID"""
        name_mapping = {
            "Sarah Chen": "sarah_chen",
            "Marcus Rodriguez": "marcus_rodriguez", 
            "Priya Patel": "priya_patel"
        }
        return name_mapping.get(source_name)

@app.route("/")
def home():
    return jsonify({
        "status": "healthy",
        "service": "Enhanced Virtual Study Group API",
        "message": "Human-first conversation flow active",
        "version": "4.0 - Human-Responsive"
    })

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "Enhanced Virtual Study Group API",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "active_study_groups": len(active_study_groups),
        "improvements": [
            "Human-first response priority",
            "Follow-up question detection", 
            "Better conversation flow",
            "Simplified peer personality",
            "Enhanced message routing"
        ]
    })

@app.route("/chat", methods=["POST"])
def peer_discussion():
    """Enhanced peer discussion with human-first priority"""
    data = request.json
    user_id = data.get("user_id", "default")
    user_message = data.get("message", "")
    stage = data.get("stage", 1)

    # Initialize study group session if needed
    if user_id not in active_study_groups:
        active_study_groups[user_id] = StudyGroupSession(user_id)
    
    session = active_study_groups[user_id]
    
    # Store human input
    session.discussion_history.append({
        "speaker": "human",
        "message": user_message,
        "timestamp": datetime.now().isoformat(),
        "stage": stage
    })

    try:
        # Enhanced peer selection with conversation context
        discussion_context = session.get_discussion_context()
        responding_peer_id, is_directly_addressed = session.determine_responding_peer(
            user_message, stage, discussion_context
        )
        
        # Fallback safety check
        if responding_peer_id not in session.active_peers:
            responding_peer_id = session.active_peers[0]
            is_directly_addressed = False
        
        peer = session.peers[responding_peer_id]
        
        # Generate enhanced peer response
        peer_response = peer.generate_response(
            user_message, 
            discussion_context,
            session.active_peers,
            is_directly_addressed
        )
        
        # Store peer response
        session.discussion_history.append({
            "speaker": peer.name,
            "peer_id": responding_peer_id,
            "message": peer_response,
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "was_directly_addressed": is_directly_addressed
        })

        response_data = {
            "response": peer_response,
            "speaker": peer.name,
            "peer_id": responding_peer_id,
            "was_directly_addressed": is_directly_addressed
        }
        
        # Maybe add a peer complication
        if session.should_introduce_complication(stage):
            complication = session.generate_peer_complication()
            if complication:
                response_data["complication"] = complication
        
        return jsonify(response_data)

    except Exception as e:
        print(f"Error in enhanced peer discussion: {str(e)}")
        # Provide contextual error response
        error_peer = session.peers[session.active_peers[0]]
        return jsonify({
            "response": "Sorry, I'm having technical difficulties right now. But let's keep discussing this case - what other aspects should we consider?",
            "speaker": error_peer.name,
            "peer_id": session.active_peers[0],
            "error": "connection_issue"
        }), 200

@app.route("/invite_peer", methods=["POST"])  
def invite_peer():
    """Invite a new peer with enhanced introduction"""
    data = request.json
    user_id = data.get("user_id", "")
    peer_id = data.get("peer_id", "")
    
    if user_id not in active_study_groups:
        return jsonify({"error": "Study group not found"}), 404
    
    session = active_study_groups[user_id]
    
    if peer_id not in session.peers:
        return jsonify({"error": "Peer not available"}), 400
    
    if peer_id in session.active_peers:
        return jsonify({"error": "Peer already in discussion"}), 400
    
    # Add peer with context-aware introduction
    session.active_peers.append(peer_id)
    peer = session.peers[peer_id]
    
    # Generate contextual introduction
    intro_messages = {
        "marcus_rodriguez": "Hey everyone! Marcus here - I couldn't help but overhear your discussion about FashionForward. This actually reminds me of some customer experience challenges we faced when evaluating automation options. Mind if I share some insights from the retail side?",
        "priya_patel": "Hi all! Priya jumping in - I caught part of your conversation and this case is really similar to what I dealt with when building my AI platform. I've seen both the wins and spectacular failures in customer service automation. Happy to share some technical perspective!",
        "sarah_chen": "Hi team! Sarah here - I've been looking at some similar cases and have some McKinsey benchmark data that might be relevant to your FashionForward analysis. Should we dive into the financial modeling?"
    }
    
    introduction = intro_messages.get(peer_id, f"Hi everyone! {peer.name} here. Looking forward to working through this case with you all!")
    
    return jsonify({
        "peer_joined": peer_id,
        "peer_name": peer.name,
        "introduction": introduction,
        "active_peers": session.active_peers
    })

@app.route("/trigger_research", methods=["POST"])
def trigger_group_research():
    """Enhanced collaborative research simulation"""
    data = request.json
    user_id = data.get("user_id", "")
    
    # Enhanced research data
    research_data = {
        "recent_implementations": [
            {"company": "Zara", "outcome": "40% FAQ automation, but required 6 months of language training for international customers"},
            {"company": "H&M", "outcome": "Successful hybrid model - bot for basics, immediate human escalation for emotions"},
            {"company": "ASOS", "outcome": "Mixed results - Gen Z loved it, millennials preferred chat, boomers called customer service"}
        ],
        "financial_benchmarks": [
            "Average fashion retail sees 35% cost reduction in year 2 (not year 1)",
            "Hidden costs: Training (20-30% of budget), integration (15-25%), change management (10-15%)",
            "Success requires 3-month pilot minimum - rushing implementation increases failure rate by 60%"
        ],
        "peer_contributions": [
            "Sarah's analysis: Board will expect 6-month ROI proof, need staged approach",
            "Marcus's insight: Customer satisfaction dips first 60 days, plan for extra human support",
            "Priya's experience: API integrations always take 2x longer than estimated"
        ]
    }
    
    return jsonify({"research": research_data})

@app.route("/reset_conversation", methods=["POST"])
def reset_study_group():
    """Reset with enhanced cleanup"""
    data = request.json
    user_id = data.get("user_id", "default")
    
    if user_id in conversation_histories:
        del conversation_histories[user_id]
    
    if user_id in active_study_groups:
        del active_study_groups[user_id]
    
    return jsonify({"message": "Study group session reset successfully"})

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key before running the server.")
    
    print("🚀 Starting Enhanced Virtual Study Group API v4.0")
    print("✨ Human-first responses, follow-up detection, natural conversation flow")
    
    app.run(
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )