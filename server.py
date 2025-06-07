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
        """Generate response as this specific peer in a study group context"""
        
        # Get recent conversation history
        recent_history = ""
        if discussion_context.get("discussion_history"):
            recent_messages = discussion_context["discussion_history"][-3:]  # Last 3 exchanges
            for msg in recent_messages:
                speaker = msg.get("speaker", "Unknown")
                message = msg.get("message", "")
                recent_history += f"{speaker}: {message}\n"
        
        # Build context about other peers
        peer_context = ""
        if len(active_peers) > 1:
            other_peers = [p for p in active_peers if p != self.peer_id]
            peer_names = []
            for peer_id in other_peers:
                if peer_id == "marcus_rodriguez":
                    peer_names.append("Marcus")
                elif peer_id == "priya_patel":
                    peer_names.append("Priya")
                elif peer_id == "sarah_chen":
                    peer_names.append("Sarah")
            if peer_names:
                peer_context = f"Other group members: {', '.join(peer_names)}. "
        
        # Create varied response styles based on response count
        response_variety = [
            "Be analytical and ask a follow-up question",
            "Share a brief personal insight or experience", 
            "Challenge or build on their point",
            "Ask for clarification or more details",
            "Bring up a new angle or consideration"
        ]
        
        current_style = response_variety[self.response_count % len(response_variety)]
        
        # Determine tone based on user message
        user_tone = "casual" if any(word in user_message.lower() for word in ["hey", "dude", "what's up", "yeah", "cool"]) else "professional"
        
        peer_prompt = f"""You are {self.name}, an MBA student in a study group discussing the FashionForward case.

Your Background: {self.background}
Your Personality: {self.personality}
Your Speaking Style: {self.speaking_style}

Case Context: Jessica Martinez (CEO of FashionForward) needs to choose between:
- AI Chatbot: $87K/2 years, handles 65% of tickets
- Team Expansion: $256K/2 years, more personal touch  
- Outsourcing: $383K/2 years, professional but expensive

Recent conversation:
{recent_history}

{peer_context}

The student just said: "{user_message}"

Response Instructions:
- Tone: Match their {user_tone} style
- Length: 1-2 sentences maximum
- Style: {current_style}
- Sound like a real grad student, not a consultant
- Use natural speech patterns ("I think...", "Yeah...", "What if...")
- Show your personality but don't overdo it
- {'Respond directly since they addressed you' if is_directly_addressed else 'Engage naturally as a peer'}

Examples of good responses:
- "Yeah, I see your point about ROI. But what about the customer lifetime value impact?"
- "Interesting! When we did similar cases at McKinsey, timing was everything."
- "Hold up - are we sure about those implementation timelines?"
- "I'm actually leaning toward option 2. Here's why..."

Respond naturally as {self.name}:"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": peer_prompt}],
                temperature=0.9,  # Higher temperature for more personality variation
                max_tokens=150,   # Shorter responses
                presence_penalty=0.6,  # Encourage new topics
                frequency_penalty=0.3  # Reduce repetition
            )
            
            self.response_count += 1
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback responses based on peer personality
            fallbacks = {
                "sarah_chen": "Sorry, having connection issues! But I'm thinking about the financial implications here.",
                "marcus_rodriguez": "Connection's spotty, but from a customer experience perspective...",
                "priya_patel": "Tech issues on my end! But this reminds me of my startup experience."
            }
            return fallbacks.get(self.peer_id, f"Sorry, I'm having connection issues - {self.name}")

class StudyGroupSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.peers = {
            "sarah_chen": VirtualPeer(
                "sarah_chen",
                "Sarah Chen", 
                "Finance MBA from Wharton, 3 years at McKinsey, now Strategic Planning Director at tech startup",
                "Analytical, collaborative, sometimes overthinks but genuinely curious about different perspectives",
                "Professional but warm, asks good questions, likes frameworks but not rigid about them",
                "Focuses on financial metrics but learning to consider customer emotions more",
                "Financial modeling, ROI analysis, consulting frameworks, strategic planning"
            ),
            "marcus_rodriguez": VirtualPeer(
                "marcus_rodriguez",
                "Marcus Rodriguez",
                "15 years in retail operations, Customer Experience Director at major fashion retailer, MBA from Kellogg", 
                "Practical, customer-obsessed, storyteller, protective of brand reputation",
                "Direct, uses real examples, passionate about customers, sometimes skeptical of pure tech solutions",
                "Prioritizes customer satisfaction, worries about implementation risks based on experience",
                "Retail operations, customer experience design, implementation management, brand protection"
            ),
            "priya_patel": VirtualPeer(
                "priya_patel", 
                "Priya Patel",
                "Tech entrepreneur, founded and sold AI customer service platform, Stanford MBA",
                "Energetic, optimistic about tech, fast-moving, sees big picture opportunities",
                "Startup energy, tech terminology but explains it well, focuses on scale and growth",
                "Pro-innovation, sometimes underestimates implementation complexity, growth-focused",
                "AI/ML implementation, startup scaling, product development, technology adoption"
            )
        }
        self.active_peers = ["sarah_chen"]  # Start with Sarah
        self.discussion_history = []
        self.research_insights = []
        self.complications_used = []
        
        # Enhanced peer complications with more variety
        self.peer_complications = [
            {
                "type": "experience_share",
                "description": "Marcus just shared that when his company implemented a chatbot, customer complaints actually increased 25% in the first month because the bot couldn't handle emotional situations properly",
                "impact": "significantly challenge",
                "source": "Marcus Rodriguez",
                "peer_context": "Based on real implementation experience"
            },
            {
                "type": "research_finding", 
                "description": "Sarah found a recent McKinsey study showing that 43% of retail AI implementations fail due to poor change management and staff resistance, not technology issues",
                "impact": "potentially affect",
                "source": "Sarah Chen",
                "peer_context": "From consulting research database"
            },
            {
                "type": "industry_insight",
                "description": "Priya mentioned that newer AI platforms now achieve 87% accuracy vs. 65% two years ago, and integration APIs have gotten much simpler - this could significantly improve the ROI calculations",
                "impact": "positively impact", 
                "source": "Priya Patel",
                "peer_context": "From startup ecosystem knowledge"
            },
            {
                "type": "competitive_intel",
                "description": "Marcus heard through industry contacts that FashionForward's main competitor just had a PR disaster with their chatbot giving tone-deaf responses to upset customers about lost packages",
                "impact": "significantly impact",
                "source": "Marcus Rodriguez", 
                "peer_context": "Industry network intelligence"
            },
            {
                "type": "financial_insight",
                "description": "Sarah realized that if Jessica's board is expecting 20% growth next year, the customer service costs could balloon with current staffing - making automation more urgent than it initially appeared",
                "impact": "reframe",
                "source": "Sarah Chen",
                "peer_context": "Strategic planning analysis"
            },
            {
                "type": "tech_update",
                "description": "Priya just remembered that her former AI platform actually offers a 6-month pilot program for fashion retailers - this could reduce Jessica's implementation risk significantly",
                "impact": "open new options for",
                "source": "Priya Patel",
                "peer_context": "Startup network connections"
            }
        ]

    def determine_responding_peer(self, user_message, stage):
        """Determine which peer should respond based on message content and context"""
        
        # Check if user directly addressed someone
        message_lower = user_message.lower()
        
        # Direct addressing patterns
        if any(pattern in message_lower for pattern in ["sarah", "sarah,", "hey sarah"]):
            return "sarah_chen", True
        elif any(pattern in message_lower for pattern in ["marcus", "marcus,", "hey marcus"]):
            if "marcus_rodriguez" in self.active_peers:
                return "marcus_rodriguez", True
        elif any(pattern in message_lower for pattern in ["priya", "priya,", "hey priya"]):
            if "priya_patel" in self.active_peers:
                return "priya_patel", True
        
        # Topic-based routing (when not directly addressed)
        if any(word in message_lower for word in ["roi", "financial", "cost", "money", "budget", "revenue"]):
            return "sarah_chen", False
        elif any(word in message_lower for word in ["customer", "experience", "satisfaction", "brand", "service"]):
            if "marcus_rodriguez" in self.active_peers:
                return "marcus_rodriguez", False
        elif any(word in message_lower for word in ["tech", "ai", "implementation", "platform", "startup"]):
            if "priya_patel" in self.active_peers:
                return "priya_patel", False
        
        # Default rotation among active peers
        peer_index = (len(self.discussion_history)) % len(self.active_peers)
        return self.active_peers[peer_index], False

    def get_discussion_context(self):
        return {
            "discussion_history": self.discussion_history[-6:],  # Last 6 exchanges
            "active_peers": self.active_peers,
            "complications": self.complications_used,
            "message_count": len(self.discussion_history)
        }
    
    def should_introduce_complication(self, stage):
        """Decide if a peer should share a complication/insight"""
        return (stage > 2 and 
                len(self.complications_used) < 3 and 
                len(self.discussion_history) > 4 and  # After some discussion
                random.random() < 0.4)  # 40% chance
    
    def generate_peer_complication(self):
        """Generate a realistic complication from a peer's experience/research"""
        unused_complications = [c for c in self.peer_complications if c not in self.complications_used]
        if not unused_complications:
            return None
            
        # Prefer complications from active peers
        peer_complications = []
        for comp in unused_complications:
            source_peer_id = None
            if "Marcus Rodriguez" in comp['source']:
                source_peer_id = "marcus_rodriguez"
            elif "Sarah Chen" in comp['source']:
                source_peer_id = "sarah_chen"
            elif "Priya Patel" in comp['source']:
                source_peer_id = "priya_patel"
            
            if source_peer_id and source_peer_id in self.active_peers:
                peer_complications.append(comp)
        
        if peer_complications:
            complication = random.choice(peer_complications)
        else:
            complication = random.choice(unused_complications)
            
        self.complications_used.append(complication)
        return complication

@app.route("/")
def home():
    """Health check and basic info"""
    return jsonify({
        "status": "healthy",
        "service": "Virtual Study Group API",
        "message": "Peer collaboration server running",
        "version": "2.0 - Enhanced Conversations"
    })

@app.route("/health", methods=["GET"])
def health_check():
    """Detailed health check"""
    return jsonify({
        "status": "healthy", 
        "service": "Virtual Study Group API",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "active_study_groups": len(active_study_groups),
        "available_endpoints": ["/chat", "/invite_peer", "/trigger_research", "/health"],
        "improvements": [
            "Better peer routing",
            "More natural conversations", 
            "Varied response styles",
            "Enhanced complications"
        ]
    })

@app.route("/chat", methods=["POST"])
def peer_discussion():
    """Handle peer-to-peer case discussion with improved routing and responses"""
    data = request.json
    user_id = data.get("user_id", "default")
    user_message = data.get("message", "")
    stage = data.get("stage", 1)
    session_type = data.get("session_type", "peer_discussion")

    # Initialize study group session if needed
    if user_id not in active_study_groups:
        active_study_groups[user_id] = StudyGroupSession(user_id)
    
    session = active_study_groups[user_id]
    
    # Store human input in discussion history
    session.discussion_history.append({
        "speaker": "human",
        "message": user_message,
        "timestamp": datetime.now().isoformat(),
        "stage": stage
    })

    try:
        # Determine which peer should respond using improved logic
        responding_peer_id, is_directly_addressed = session.determine_responding_peer(user_message, stage)
        
        # Fallback to Sarah if determined peer isn't active
        if responding_peer_id not in session.active_peers:
            responding_peer_id = session.active_peers[0]
            is_directly_addressed = False
        
        peer = session.peers[responding_peer_id]
        
        # Generate peer response with improved context
        peer_response = peer.generate_response(
            user_message, 
            session.get_discussion_context(),
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
        
        # Maybe add a peer complication/insight
        if session.should_introduce_complication(stage):
            complication = session.generate_peer_complication()
            if complication:
                response_data["complication"] = complication
        
        # Occasionally add research insights (simulate group research)
        if stage > 3 and len(session.research_insights) < 2 and random.random() < 0.25:
            research_insight = generate_group_research_insight(session.active_peers)
            response_data["research_insight"] = research_insight
            session.research_insights.append(research_insight)
        
        return jsonify(response_data)

    except Exception as e:
        print(f"Error in peer discussion: {str(e)}")
        return jsonify({"error": f"Study group connection issue: {str(e)}"}), 500

@app.route("/invite_peer", methods=["POST"])  
def invite_peer():
    """Invite a new peer to join the study group discussion"""
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
    
    # Add peer to active discussion
    session.active_peers.append(peer_id)
    peer = session.peers[peer_id]
    
    # Generate more natural joining messages
    intro_messages = {
        "marcus_rodriguez": f"Mind if I jump in? This case actually reminds me of some challenges we faced when evaluating automation options at my company. I've got some real-world perspective that might be helpful!",
        "priya_patel": f"Hey! {peer.name} here - I actually built an AI customer service platform before B-school, so this hits close to home. I'm probably biased toward the tech solution, but I've seen both the wins and the epic fails!",
        "sarah_chen": f"Hi everyone! I worked on some similar cases at McKinsey, especially around operational strategy for retail. Happy to dive into the financial modeling if that's helpful!"
    }
    
    introduction = intro_messages.get(peer_id, f"Hi! I'm {peer.name}. Looking forward to working through this case with you all!")
    
    return jsonify({
        "peer_joined": peer_id,
        "peer_name": peer.name,
        "introduction": introduction,
        "active_peers": session.active_peers
    })

@app.route("/trigger_research", methods=["POST"])
def trigger_group_research():
    """Simulate collaborative research session"""
    data = request.json
    user_id = data.get("user_id", "")
    topic = data.get("topic", "chatbot_implementations")
    research_type = data.get("research_type", "group_research")
    
    # Enhanced research data with peer context
    group_research_data = {
        "chatbot_implementations": [
            {"company": "Sephora", "year": 2019, "outcome": "25% email reduction, but 15% increase in phone calls - customers escalated when bot couldn't help with complex issues"},
            {"company": "H&M", "year": 2020, "outcome": "60% FAQ automation success, improved CSAT by training bot on actual customer language patterns"},
            {"company": "ASOS", "year": 2021, "outcome": "45% faster response times, mixed satisfaction - Gen Z loved it, older customers found it frustrating"},
            {"company": "Zara", "year": 2022, "outcome": "Strong ROI after 8 months, key was hybrid model with seamless human handoff"},
            {"company": "Uniqlo", "year": 2023, "outcome": "Multilingual success in Asia, 40% cost reduction, but required 6 months of training data preparation"}
        ],
        "latest_trends": [
            "Hybrid AI-human models showing 40% better satisfaction than pure automation",
            "Personalization engines reducing repeat questions by 55% when trained on purchase history", 
            "Voice-enabled chatbots gaining traction in mobile commerce, especially with Gen Z shoppers",
            "Real-time sentiment analysis improving escalation decisions by 35%",
            "Integration with social media platforms becoming standard for fashion brands"
        ],
        "industry_insights": [
            "87% of fashion retailers plan AI customer service investments in 2024-2025",
            "Average implementation time decreased from 6 months to 6-8 weeks with modern platforms",
            "ROI typically achieved within 8-12 months for fashion retail specifically",
            "Customer acceptance rates 25% higher when chatbot personality matches brand voice",
            "Mobile-first implementations show 30% better engagement than desktop-first approaches"
        ],
        "peer_contributions": [
            "Sarah's consulting network provided benchmark data from 3 similar fashion retailers",
            "Marcus shared insights from his company's recent vendor evaluation process",
            "Priya contributed technical feasibility assessments from her startup experience"
        ]
    }
    
    return jsonify({"research": group_research_data})

@app.route("/reset_conversation", methods=["POST"])
def reset_study_group():
    """Reset study group session for a specific user"""
    data = request.json
    user_id = data.get("user_id", "default")
    
    if user_id in conversation_histories:
        del conversation_histories[user_id]
    
    if user_id in active_study_groups:
        del active_study_groups[user_id]
    
    return jsonify({"message": "Study group session reset successfully"})

@app.route("/get_session_data", methods=["POST"])
def get_study_group_data():
    """Retrieve study group session data for analytics"""
    data = request.json
    user_id = data.get("user_id", "")
    
    if user_id in active_study_groups:
        session = active_study_groups[user_id]
        return jsonify({
            "session_data": {
                "active_peers": session.active_peers,
                "complications_used": session.complications_used,
                "research_count": len(session.research_insights),
                "discussion_length": len(session.discussion_history)
            },
            "discussion_history": session.discussion_history
        })
    else:
        return jsonify({"error": "Study group not found"}), 404

def generate_group_research_insight(active_peers):
    """Generate research insights that feel like collaborative discovery"""
    base_insights = [
        {
            "chatbot_implementations": [
                {"company": "Target", "year": 2023, "outcome": "Successful hybrid model with 35% cost savings and improved CSAT"},
                {"company": "Nordstrom", "year": 2022, "outcome": "Premium customer base required high-touch approach - bot handled basics only"}
            ],
            "discovery_context": "Found through group research on recent retail implementations"
        },
        {
            "latest_trends": [
                "Emotional AI becoming critical - bots that detect frustration and escalate immediately",
                "Integration with inventory systems allowing real-time product availability responses"
            ],
            "discovery_context": "Emerging trends identified through peer network research"
        },
        {
            "competitive_analysis": [
                "Fashion retailers using AI see 23% faster resolution times but 18% more escalations",
                "Brands with strong social media presence have 40% better chatbot adoption rates"
            ],
            "discovery_context": "Cross-industry analysis from group's combined networks"
        }
    ]
    
    return random.choice(base_insights)

if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key before running the server.")
    
    print("Starting Virtual Study Group API v2.0")
    print("Improvements: Better peer routing, natural conversations, varied responses")
    
    # Run the Flask app
    app.run(
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 5000)),
        debug=False  # Set to False for production on Render
    )