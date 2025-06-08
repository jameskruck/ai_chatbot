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
        """Generate response with MUCH better conversation context and human-first priority"""
        
        # Always prioritize responding to the human's input
        conversation_context = self._build_conversation_context(discussion_context)
        stage_info = self._analyze_conversation_stage(discussion_context)
        
        # Analyze what type of response the human needs
        response_type = self._analyze_user_input(user_message)
        
        # Create a more sophisticated prompt that maintains conversation flow
        peer_prompt = f"""You are {self.name} in an MBA study group discussing the FashionForward customer service case.

CASE CONTEXT: Jessica Martinez (CEO) must choose between:
1. AI Chatbot: $87K over 2 years, automates 65% of customer inquiries
2. Team Expansion: $256K over 2 years, maintains human touch
3. Outsourcing: $383K over 2 years, professional but expensive

YOUR IDENTITY & PERSPECTIVE:
- Background: {self.background}
- Personality: {self.personality} 
- Speaking Style: {self.speaking_style}
- Natural Biases: {self.biases}
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
                temperature=0.7,  # Balanced for natural but consistent responses
                max_tokens=100,   # Shorter for more natural conversation
                presence_penalty=0.8,  # Encourage new topics and perspectives
                frequency_penalty=0.5  # Reduce repetitive phrases
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean up response - remove any quotes or attribution
            response_text = re.sub(r'^["\']|["\']$', '', response_text)

    def _build_conversation_context(self, discussion_context):
        """Build rich conversation context from recent history"""
        if not discussion_context.get("discussion_history"):
            return "This is the start of your discussion."
        
        # Get last 4-6 exchanges for context (not too much to overwhelm)
        recent_history = discussion_context["discussion_history"][-6:]
        
        context_lines = []
        for msg in recent_history:
            speaker = msg.get("speaker", "Unknown")
            message = msg.get("message", "")
            
            # Format differently for human vs peer messages
            if speaker == "human":
                context_lines.append(f"STUDENT: {message}")
            else:
                # Clean peer name for context
                peer_name = speaker.replace(" Rodriguez", "").replace(" Chen", "").replace(" Patel", "")
                context_lines.append(f"{peer_name.upper()}: {message}")
        
        return "\n".join(context_lines) if context_lines else "This is the start of your discussion."

    def _analyze_conversation_stage(self, discussion_context):
        """Analyze what stage the conversation is in and provide context"""
        message_count = len(discussion_context.get("discussion_history", []))
        
        if message_count < 3:
            return "The discussion is just getting started - focus on initial analysis"
        elif message_count < 8:
            return "You're in the exploration phase - dig into different perspectives"
        elif message_count < 15:
            return "The group is building analysis - connect ideas and add depth"
        else:
            return "You're moving toward conclusions - help synthesize and decide"

    def _format_active_peers(self, active_peers):
        """Format active peer list for context"""
        peer_names = []
        for peer_id in active_peers:
            if peer_id != self.peer_id:  # Don't include self
                if peer_id == "sarah_chen":
                    peer_names.append("Sarah (Finance)")
                elif peer_id == "marcus_rodriguez": 
                    peer_names.append("Marcus (Retail Ops)")
                elif peer_id == "priya_patel":
                    peer_names.append("Priya (Tech)")
        
        return ", ".join(peer_names) if peer_names else "just you"

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
                "15 years in retail operations, currently Customer Experience Director at major fashion retailer", 
                "Practical and customer-focused, draws from real experience, protective of brand reputation",
                "Direct and conversational, uses real examples, passionate about customer experience",
                "Prioritizes customer satisfaction over pure efficiency, skeptical of technology that feels impersonal",
                "Retail operations, customer journey mapping, brand management, implementation challenges, front-line operations"
            ),
            "priya_patel": VirtualPeer(
                "priya_patel", 
                "Priya Patel",
                "Founded and sold AI customer service startup to Zendesk, now Stanford MBA focusing on scaling tech solutions",
                "Energetic and solution-oriented, optimistic about technology, thinks in terms of scale and growth",
                "Startup energy, comfortable with tech terminology, focuses on implementation and scalability",
                "Sees technology solutions first, sometimes underestimates change management and adoption challenges",
                "AI/ML implementation, startup scaling, product development, technology adoption, integration challenges"
            )
        }
        self.active_peers = ["sarah_chen"]  # Start with Sarah
        self.discussion_history = []
        self.research_insights = []
        self.complications_used = []
        self.conversation_themes = []  # Track recurring themes
        
        # Enhanced peer complications with better context
        self.peer_complications = [
            {
                "type": "implementation_reality",
                "description": "Marcus just mentioned that when his company tried a chatbot, customer complaints increased 30% in month 1 because the bot couldn't handle frustrated customers properly - they had to add extensive human escalation rules",
                "impact": "significantly challenge your current thinking",
                "source": "Marcus Rodriguez",
                "timing": "after_initial_analysis"
            },
            {
                "type": "financial_insight", 
                "description": "Sarah found McKinsey data showing that 60% of retail AI implementations exceed budget by 40%+ due to integration complexity and change management costs not included in initial estimates",
                "impact": "revise your financial assumptions",
                "source": "Sarah Chen", 
                "timing": "during_detailed_analysis"
            },
            {
                "type": "competitive_intelligence",
                "description": "Priya heard through her network that FashionForward's biggest competitor is about to launch an AI-powered personal stylist feature - this could change the competitive landscape significantly",
                "impact": "add urgency to your decision",
                "source": "Priya Patel",
                "timing": "mid_conversation"
            }
        ]

    def determine_responding_peer(self, user_message, stage, discussion_context):
        """Enhanced peer selection with HUMAN-FIRST priority"""
        
        message_lower = user_message.lower()
        recent_speakers = self._get_recent_speakers(discussion_context)
        
        # 1. ALWAYS check for direct addressing first
        direct_address = self._check_direct_address(message_lower)
        if direct_address and direct_address in self.active_peers:
            return direct_address, True
        
        # 2. Detect follow-up questions that need immediate response
        if self._is_follow_up_question(user_message):
            # For follow-ups, choose the most relevant peer based on recent topic
            relevant_peer = self._find_most_relevant_peer_for_followup(discussion_context)
            if relevant_peer and relevant_peer in self.active_peers:
                return relevant_peer, False
        
        # 3. Avoid same peer responding twice in a row (unless directly addressed)
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
        
        # 5. Conversation flow routing - who would naturally respond?
        flow_priority = self._determine_conversation_flow(discussion_context, peer_pool)
        if flow_priority:
            return flow_priority, False
        
        # 6. Default: choose peer who hasn't spoken recently
        if peer_pool:
            return peer_pool[0], False
        
        return self.active_peers[0], False

    def _is_follow_up_question(self, user_message):
        """Detect if this is a follow-up question that needs direct response"""
        message_lower = user_message.lower().strip()
        
        follow_up_indicators = [
            'what else', 'what other', 'anything else', 'what about',
            'also', 'and', 'plus', 'additionally', 'furthermore',
            'what if', 'how about', 'what do you think about'
        ]
        
        return any(indicator in message_lower for indicator in follow_up_indicators)
    
    def _find_most_relevant_peer_for_followup(self, discussion_context):
        """Find the peer most relevant to continue the current discussion"""
        if not discussion_context.get("discussion_history"):
            return "sarah_chen"  # Default to Sarah
        
        # Look at the last few peer messages to see who was discussing the topic
        recent_peer_messages = []
        for msg in discussion_context["discussion_history"][-3:]:
            if msg.get("speaker") != "human" and msg.get("peer_id"):
                recent_peer_messages.append(msg.get("peer_id"))
        
        if recent_peer_messages:
            # Return the most recent peer who spoke (they're likely most relevant)
            return recent_peer_messages[-1]
        
        return "sarah_chen"

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
        if any(word in message_lower for word in ["roi", "cost", "budget", "revenue", "profit", "financial", "money", "pricing", "investment"]):
            content_routing.append(("financial", "sarah_chen"))
        
        # Customer experience topics  
        if any(word in message_lower for word in ["customer", "experience", "satisfaction", "service", "brand", "reputation", "feedback", "complaints"]):
            content_routing.append(("customer_experience", "marcus_rodriguez"))
        
        # Technology/implementation topics
        if any(word in message_lower for word in ["technology", "ai", "implementation", "integration", "platform", "technical", "setup", "scaling"]):
            content_routing.append(("technology", "priya_patel"))
        
        # Strategic/consulting topics
        if any(word in message_lower for word in ["strategy", "framework", "analysis", "recommendation", "consulting", "approach"]):
            content_routing.append(("strategy", "sarah_chen"))
        
        # Operations topics
        if any(word in message_lower for word in ["operations", "process", "workflow", "staff", "training", "change management"]):
            content_routing.append(("operations", "marcus_rodriguez"))
        
        return content_routing

    def _determine_conversation_flow(self, discussion_context, available_peers):
        """Determine who should naturally respond based on conversation flow"""
        if not discussion_context.get("discussion_history"):
            return None
        
        last_message = discussion_context["discussion_history"][-1]
        last_speaker = last_message.get("peer_id")
        last_content = last_message.get("message", "").lower()
        
        # If someone just made a strong point, someone with different expertise should respond
        if last_speaker == "sarah_chen" and ("marcus_rodriguez" in available_peers or "priya_patel" in available_peers):
            # After Sarah's financial analysis, Marcus or Priya should respond with different perspective
            return "marcus_rodriguez" if "marcus_rodriguez" in available_peers else "priya_patel"
        
        elif last_speaker == "marcus_rodriguez" and "priya_patel" in available_peers:
            # After Marcus talks customer experience, Priya can offer tech perspective
            return "priya_patel"
        
        elif last_speaker == "priya_patel" and "sarah_chen" in available_peers:
            # After Priya talks tech, Sarah can bring it back to business case
            return "sarah_chen"
        
        return None

    def get_discussion_context(self):
        """Get comprehensive discussion context"""
        return {
            "discussion_history": self.discussion_history,
            "active_peers": self.active_peers,
            "complications": self.complications_used,
            "message_count": len(self.discussion_history),
            "conversation_themes": self.conversation_themes,
            "stage": self._determine_stage()
        }
    
    def _determine_stage(self):
        """Determine what stage the conversation is in"""
        message_count = len(self.discussion_history)
        if message_count < 4:
            return "opening"
        elif message_count < 10:
            return "exploration" 
        elif message_count < 16:
            return "analysis"
        else:
            return "synthesis"
    
    def should_introduce_complication(self, stage):
        """Smart timing for introducing complications"""
        return (len(self.complications_used) < 2 and 
                len(self.discussion_history) > 6 and
                stage in ["exploration", "analysis"] and
                random.random() < 0.35)
    
    def generate_peer_complication(self):
        """Generate realistic complications from peer experience"""
        unused = [c for c in self.peer_complications if c not in self.complications_used]
        if not unused:
            return None
            
        # Filter by active peers and timing
        stage = self._determine_stage()
        suitable = []
        
        for comp in unused:
            source_peer_id = self._get_peer_id_from_source(comp['source'])
            timing_match = (
                comp.get('timing', 'any') == 'any' or 
                comp.get('timing') == stage or
                (comp.get('timing') == 'after_initial_analysis' and stage in ['exploration', 'analysis'])
            )
            
            if source_peer_id in self.active_peers and timing_match:
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
        "message": "Improved conversation flow and peer collaboration",
        "version": "3.0 - Enhanced Conversations"
    })

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "Enhanced Virtual Study Group API",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "active_study_groups": len(active_study_groups),
        "improvements": [
            "Enhanced conversation context management",
            "Smarter peer response routing", 
            "Better conversation flow continuity",
            "Improved peer personality consistency",
            "Advanced message content analysis"
        ]
    })

@app.route("/chat", methods=["POST"])
def peer_discussion():
    """Enhanced peer discussion with better conversation flow"""
    data = request.json
    user_id = data.get("user_id", "default")
    user_message = data.get("message", "")
    stage = data.get("stage", 1)

    # Initialize study group session if needed
    if user_id not in active_study_groups:
        active_study_groups[user_id] = StudyGroupSession(user_id)
    
    session = active_study_groups[user_id]
    
    # Store human input with enhanced metadata
    session.discussion_history.append({
        "speaker": "human",
        "message": user_message,
        "timestamp": datetime.now().isoformat(),
        "stage": stage,
        "message_type": "user_input"
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
        
        # Store peer response with enhanced metadata
        session.discussion_history.append({
            "speaker": peer.name,
            "peer_id": responding_peer_id,
            "message": peer_response,
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "was_directly_addressed": is_directly_addressed,
            "message_type": "peer_response"
        })

        response_data = {
            "response": peer_response,
            "speaker": peer.name,
            "peer_id": responding_peer_id,
            "was_directly_addressed": is_directly_addressed,
            "conversation_stage": discussion_context["stage"]
        }
        
        # Smart complication timing
        if session.should_introduce_complication(discussion_context["stage"]):
            complication = session.generate_peer_complication()
            if complication:
                response_data["complication"] = complication
        
        return jsonify(response_data)

    except Exception as e:
        print(f"Error in enhanced peer discussion: {str(e)}")
        # Provide contextual error response
        error_peer = session.peers[session.active_peers[0]]
        return jsonify({
            "response": f"Sorry, I'm having technical difficulties right now. But let's keep discussing this case - I think there are some important factors we need to consider here.",
            "speaker": error_peer.name,
            "peer_id": session.active_peers[0],
            "error": "connection_issue"
        }), 200  # Return 200 to keep conversation flowing

# [Rest of the routes remain the same but with enhanced error handling]
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
    
    # Generate contextual introduction based on current discussion
    stage = session._determine_stage()
    discussion_context = session.get_discussion_context()
    
    intro_messages = {
        "marcus_rodriguez": f"Hey everyone! Marcus here - I couldn't help but overhear your discussion about FashionForward. This actually reminds me of some customer experience challenges we faced when evaluating automation. Mind if I share some insights from the retail side?",
        "priya_patel": f"Hi all! Priya jumping in - I caught part of your conversation and this case is really similar to what I dealt with when building my AI platform. I've seen both the wins and spectacular failures in customer service automation. Happy to share some technical perspective!",
        "sarah_chen": f"Hi team! Sarah here - I've been looking at some similar cases and have some McKinsey benchmark data that might be relevant to your FashionForward analysis. Should we dive into the financial modeling?"
    }
    
    introduction = intro_messages.get(peer_id, f"Hi everyone! {peer.name} here. Excited to contribute to this discussion!")
    
    # Add introduction to conversation history
    session.discussion_history.append({
        "speaker": peer.name,
        "peer_id": peer_id,
        "message": introduction,
        "timestamp": datetime.now().isoformat(),
        "message_type": "peer_introduction"
    })
    
    return jsonify({
        "peer_joined": peer_id,
        "peer_name": peer.name,
        "introduction": introduction,
        "active_peers": session.active_peers,
        "conversation_stage": stage
    })

@app.route("/trigger_research", methods=["POST"])
def trigger_group_research():
    """Enhanced collaborative research simulation"""
    data = request.json
    user_id = data.get("user_id", "")
    
    # Enhanced research with peer context
    research_insights = {
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
    
    return jsonify({"research": research_insights, "research_type": "collaborative"})

@app.route("/reset_conversation", methods=["POST"])
def reset_study_group():
    """Reset with enhanced cleanup"""
    data = request.json
    user_id = data.get("user_id", "default")
    
    if user_id in conversation_histories:
        del conversation_histories[user_id]
    
    if user_id in active_study_groups:
        del active_study_groups[user_id]
    
    return jsonify({"message": "Study group session reset successfully", "version": "3.0"})

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key before running the server.")
    
    print("🚀 Starting Enhanced Virtual Study Group API v3.0")
    print("✨ Improvements: Better context, smarter routing, natural flow")
    
    app.run(
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    ), '', response_text)
            response_text = re.sub(r'^' + re.escape(self.name) + r':\s*', '', response_text)
            
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
            return fallbacks.get(self.peer_id, f"That's a great point - let me consider that.")

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
        """Build rich conversation context from recent history"""
        if not discussion_context.get("discussion_history"):
            return "This is the start of your discussion."
        
        # Get last 4-6 exchanges for context (not too much to overwhelm)
        recent_history = discussion_context["discussion_history"][-6:]
        
        context_lines = []
        for msg in recent_history:
            speaker = msg.get("speaker", "Unknown")
            message = msg.get("message", "")
            
            # Format differently for human vs peer messages
            if speaker == "human":
                context_lines.append(f"STUDENT: {message}")
            else:
                # Clean peer name for context
                peer_name = speaker.replace(" Rodriguez", "").replace(" Chen", "").replace(" Patel", "")
                context_lines.append(f"{peer_name.upper()}: {message}")
        
        return "\n".join(context_lines) if context_lines else "This is the start of your discussion."

    def _analyze_conversation_stage(self, discussion_context):
        """Analyze what stage the conversation is in and provide context"""
        message_count = len(discussion_context.get("discussion_history", []))
        
        if message_count < 3:
            return "The discussion is just getting started - focus on initial analysis"
        elif message_count < 8:
            return "You're in the exploration phase - dig into different perspectives"
        elif message_count < 15:
            return "The group is building analysis - connect ideas and add depth"
        else:
            return "You're moving toward conclusions - help synthesize and decide"

    def _format_active_peers(self, active_peers):
        """Format active peer list for context"""
        peer_names = []
        for peer_id in active_peers:
            if peer_id != self.peer_id:  # Don't include self
                if peer_id == "sarah_chen":
                    peer_names.append("Sarah (Finance)")
                elif peer_id == "marcus_rodriguez": 
                    peer_names.append("Marcus (Retail Ops)")
                elif peer_id == "priya_patel":
                    peer_names.append("Priya (Tech)")
        
        return ", ".join(peer_names) if peer_names else "just you"

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
                "15 years in retail operations, currently Customer Experience Director at major fashion retailer", 
                "Practical and customer-focused, draws from real experience, protective of brand reputation",
                "Direct and conversational, uses real examples, passionate about customer experience",
                "Prioritizes customer satisfaction over pure efficiency, skeptical of technology that feels impersonal",
                "Retail operations, customer journey mapping, brand management, implementation challenges, front-line operations"
            ),
            "priya_patel": VirtualPeer(
                "priya_patel", 
                "Priya Patel",
                "Founded and sold AI customer service startup to Zendesk, now Stanford MBA focusing on scaling tech solutions",
                "Energetic and solution-oriented, optimistic about technology, thinks in terms of scale and growth",
                "Startup energy, comfortable with tech terminology, focuses on implementation and scalability",
                "Sees technology solutions first, sometimes underestimates change management and adoption challenges",
                "AI/ML implementation, startup scaling, product development, technology adoption, integration challenges"
            )
        }
        self.active_peers = ["sarah_chen"]  # Start with Sarah
        self.discussion_history = []
        self.research_insights = []
        self.complications_used = []
        self.conversation_themes = []  # Track recurring themes
        
        # Enhanced peer complications with better context
        self.peer_complications = [
            {
                "type": "implementation_reality",
                "description": "Marcus just mentioned that when his company tried a chatbot, customer complaints increased 30% in month 1 because the bot couldn't handle frustrated customers properly - they had to add extensive human escalation rules",
                "impact": "significantly challenge your current thinking",
                "source": "Marcus Rodriguez",
                "timing": "after_initial_analysis"
            },
            {
                "type": "financial_insight", 
                "description": "Sarah found McKinsey data showing that 60% of retail AI implementations exceed budget by 40%+ due to integration complexity and change management costs not included in initial estimates",
                "impact": "revise your financial assumptions",
                "source": "Sarah Chen", 
                "timing": "during_detailed_analysis"
            },
            {
                "type": "competitive_intelligence",
                "description": "Priya heard through her network that FashionForward's biggest competitor is about to launch an AI-powered personal stylist feature - this could change the competitive landscape significantly",
                "impact": "add urgency to your decision",
                "source": "Priya Patel",
                "timing": "mid_conversation"
            }
        ]

    def determine_responding_peer(self, user_message, stage, discussion_context):
        """Enhanced peer selection based on conversation flow and content"""
        
        message_lower = user_message.lower()
        recent_speakers = self._get_recent_speakers(discussion_context)
        
        # 1. Check for direct addressing first
        direct_address = self._check_direct_address(message_lower)
        if direct_address and direct_address in self.active_peers:
            return direct_address, True
        
        # 2. Avoid same peer responding twice in a row (unless directly addressed)
        if recent_speakers and len(recent_speakers) > 0:
            last_speaker_id = recent_speakers[0]
            available_peers = [p for p in self.active_peers if p != last_speaker_id]
            if available_peers:
                peer_pool = available_peers
            else:
                peer_pool = self.active_peers
        else:
            peer_pool = self.active_peers
        
        # 3. Content-based routing with expertise matching
        content_priority = self._analyze_message_content(message_lower)
        
        for topic, peer_id in content_priority:
            if peer_id in peer_pool:
                return peer_id, False
        
        # 4. Conversation flow routing - who would naturally respond?
        flow_priority = self._determine_conversation_flow(discussion_context, peer_pool)
        if flow_priority:
            return flow_priority, False
        
        # 5. Default: rotate among available peers
        if peer_pool:
            return peer_pool[len(self.discussion_history) % len(peer_pool)], False
        
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
        if any(word in message_lower for word in ["roi", "cost", "budget", "revenue", "profit", "financial", "money", "pricing", "investment"]):
            content_routing.append(("financial", "sarah_chen"))
        
        # Customer experience topics  
        if any(word in message_lower for word in ["customer", "experience", "satisfaction", "service", "brand", "reputation", "feedback", "complaints"]):
            content_routing.append(("customer_experience", "marcus_rodriguez"))
        
        # Technology/implementation topics
        if any(word in message_lower for word in ["technology", "ai", "implementation", "integration", "platform", "technical", "setup", "scaling"]):
            content_routing.append(("technology", "priya_patel"))
        
        # Strategic/consulting topics
        if any(word in message_lower for word in ["strategy", "framework", "analysis", "recommendation", "consulting", "approach"]):
            content_routing.append(("strategy", "sarah_chen"))
        
        # Operations topics
        if any(word in message_lower for word in ["operations", "process", "workflow", "staff", "training", "change management"]):
            content_routing.append(("operations", "marcus_rodriguez"))
        
        return content_routing

    def _determine_conversation_flow(self, discussion_context, available_peers):
        """Determine who should naturally respond based on conversation flow"""
        if not discussion_context.get("discussion_history"):
            return None
        
        last_message = discussion_context["discussion_history"][-1]
        last_speaker = last_message.get("peer_id")
        last_content = last_message.get("message", "").lower()
        
        # If someone just made a strong point, someone with different expertise should respond
        if last_speaker == "sarah_chen" and ("marcus_rodriguez" in available_peers or "priya_patel" in available_peers):
            # After Sarah's financial analysis, Marcus or Priya should respond with different perspective
            return "marcus_rodriguez" if "marcus_rodriguez" in available_peers else "priya_patel"
        
        elif last_speaker == "marcus_rodriguez" and "priya_patel" in available_peers:
            # After Marcus talks customer experience, Priya can offer tech perspective
            return "priya_patel"
        
        elif last_speaker == "priya_patel" and "sarah_chen" in available_peers:
            # After Priya talks tech, Sarah can bring it back to business case
            return "sarah_chen"
        
        return None

    def get_discussion_context(self):
        """Get comprehensive discussion context"""
        return {
            "discussion_history": self.discussion_history,
            "active_peers": self.active_peers,
            "complications": self.complications_used,
            "message_count": len(self.discussion_history),
            "conversation_themes": self.conversation_themes,
            "stage": self._determine_stage()
        }
    
    def _determine_stage(self):
        """Determine what stage the conversation is in"""
        message_count = len(self.discussion_history)
        if message_count < 4:
            return "opening"
        elif message_count < 10:
            return "exploration" 
        elif message_count < 16:
            return "analysis"
        else:
            return "synthesis"
    
    def should_introduce_complication(self, stage):
        """Smart timing for introducing complications"""
        return (len(self.complications_used) < 2 and 
                len(self.discussion_history) > 6 and
                stage in ["exploration", "analysis"] and
                random.random() < 0.35)
    
    def generate_peer_complication(self):
        """Generate realistic complications from peer experience"""
        unused = [c for c in self.peer_complications if c not in self.complications_used]
        if not unused:
            return None
            
        # Filter by active peers and timing
        stage = self._determine_stage()
        suitable = []
        
        for comp in unused:
            source_peer_id = self._get_peer_id_from_source(comp['source'])
            timing_match = (
                comp.get('timing', 'any') == 'any' or 
                comp.get('timing') == stage or
                (comp.get('timing') == 'after_initial_analysis' and stage in ['exploration', 'analysis'])
            )
            
            if source_peer_id in self.active_peers and timing_match:
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
        "message": "Improved conversation flow and peer collaboration",
        "version": "3.0 - Enhanced Conversations"
    })

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "Enhanced Virtual Study Group API",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "active_study_groups": len(active_study_groups),
        "improvements": [
            "Enhanced conversation context management",
            "Smarter peer response routing", 
            "Better conversation flow continuity",
            "Improved peer personality consistency",
            "Advanced message content analysis"
        ]
    })

@app.route("/chat", methods=["POST"])
def peer_discussion():
    """Enhanced peer discussion with better conversation flow"""
    data = request.json
    user_id = data.get("user_id", "default")
    user_message = data.get("message", "")
    stage = data.get("stage", 1)

    # Initialize study group session if needed
    if user_id not in active_study_groups:
        active_study_groups[user_id] = StudyGroupSession(user_id)
    
    session = active_study_groups[user_id]
    
    # Store human input with enhanced metadata
    session.discussion_history.append({
        "speaker": "human",
        "message": user_message,
        "timestamp": datetime.now().isoformat(),
        "stage": stage,
        "message_type": "user_input"
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
        
        # Store peer response with enhanced metadata
        session.discussion_history.append({
            "speaker": peer.name,
            "peer_id": responding_peer_id,
            "message": peer_response,
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "was_directly_addressed": is_directly_addressed,
            "message_type": "peer_response"
        })

        response_data = {
            "response": peer_response,
            "speaker": peer.name,
            "peer_id": responding_peer_id,
            "was_directly_addressed": is_directly_addressed,
            "conversation_stage": discussion_context["stage"]
        }
        
        # Smart complication timing
        if session.should_introduce_complication(discussion_context["stage"]):
            complication = session.generate_peer_complication()
            if complication:
                response_data["complication"] = complication
        
        return jsonify(response_data)

    except Exception as e:
        print(f"Error in enhanced peer discussion: {str(e)}")
        # Provide contextual error response
        error_peer = session.peers[session.active_peers[0]]
        return jsonify({
            "response": f"Sorry, I'm having technical difficulties right now. But let's keep discussing this case - I think there are some important factors we need to consider here.",
            "speaker": error_peer.name,
            "peer_id": session.active_peers[0],
            "error": "connection_issue"
        }), 200  # Return 200 to keep conversation flowing

# [Rest of the routes remain the same but with enhanced error handling]
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
    
    # Generate contextual introduction based on current discussion
    stage = session._determine_stage()
    discussion_context = session.get_discussion_context()
    
    intro_messages = {
        "marcus_rodriguez": f"Hey everyone! Marcus here - I couldn't help but overhear your discussion about FashionForward. This actually reminds me of some customer experience challenges we faced when evaluating automation. Mind if I share some insights from the retail side?",
        "priya_patel": f"Hi all! Priya jumping in - I caught part of your conversation and this case is really similar to what I dealt with when building my AI platform. I've seen both the wins and spectacular failures in customer service automation. Happy to share some technical perspective!",
        "sarah_chen": f"Hi team! Sarah here - I've been looking at some similar cases and have some McKinsey benchmark data that might be relevant to your FashionForward analysis. Should we dive into the financial modeling?"
    }
    
    introduction = intro_messages.get(peer_id, f"Hi everyone! {peer.name} here. Excited to contribute to this discussion!")
    
    # Add introduction to conversation history
    session.discussion_history.append({
        "speaker": peer.name,
        "peer_id": peer_id,
        "message": introduction,
        "timestamp": datetime.now().isoformat(),
        "message_type": "peer_introduction"
    })
    
    return jsonify({
        "peer_joined": peer_id,
        "peer_name": peer.name,
        "introduction": introduction,
        "active_peers": session.active_peers,
        "conversation_stage": stage
    })

@app.route("/trigger_research", methods=["POST"])
def trigger_group_research():
    """Enhanced collaborative research simulation"""
    data = request.json
    user_id = data.get("user_id", "")
    
    # Enhanced research with peer context
    research_insights = {
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
    
    return jsonify({"research": research_insights, "research_type": "collaborative"})

@app.route("/reset_conversation", methods=["POST"])
def reset_study_group():
    """Reset with enhanced cleanup"""
    data = request.json
    user_id = data.get("user_id", "default")
    
    if user_id in conversation_histories:
        del conversation_histories[user_id]
    
    if user_id in active_study_groups:
        del active_study_groups[user_id]
    
    return jsonify({"message": "Study group session reset successfully", "version": "3.0"})

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key before running the server.")
    
    print("🚀 Starting Enhanced Virtual Study Group API v3.0")
    print("✨ Improvements: Better context, smarter routing, natural flow")
    
    app.run(
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )