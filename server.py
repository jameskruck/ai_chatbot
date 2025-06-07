from flask import Flask, request, jsonify
from openai import OpenAI
from flask_cors import CORS
import os
import json
import random
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
    
    def generate_response(self, user_message, discussion_context, active_peers):
        """Generate response as this specific peer in a study group context"""
        
        # Build context about other peers
        peer_context = ""
        if len(active_peers) > 1:
            other_peers = [p for p in active_peers if p != self.peer_id]
            peer_context = f"Other study group members: {', '.join(other_peers)}. "
        
        peer_prompt = f"""You are {self.name}, a graduate student in a business case study group discussion.

Your Background: {self.background}
Your Personality: {self.personality}
Your Speaking Style: {self.speaking_style}
Your Tendencies/Biases: {self.biases}
Your Expertise: {self.expertise}

Study Group Context: You're discussing the FashionForward customer service case with fellow MBA students. Jessica Martinez (CEO) must decide between:
- AI Chatbot: $87K/2 years, 6-8 weeks implementation, handles 65% of tickets
- Team Expansion: $256K/2 years, 4-6 weeks, personal touch but higher costs  
- Outsourcing: $383K/2 years, 3-4 weeks, professional but expensive

{peer_context}

The student just said: "{user_message}"

Respond authentically as {self.name} would in a real study group:
- Draw on your specific background and experience naturally
- Show your personality and biases without being heavy-handed
- Engage with their ideas and ask follow-up questions
- Reference your expertise when relevant
- Sound like a genuine classmate collaborating, not an AI assistant
- Keep it conversational (1-3 sentences)
- Use "I think...", "In my experience...", "What if..." naturally

Remember: You're a peer figuring this out together, not teaching. Be curious about their perspective while sharing your own insights."""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": peer_prompt}],
                temperature=0.8,  # Higher temperature for more personality
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I'm having connection issues - {self.name}"

class StudyGroupSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.peers = {
            "sarah_chen": VirtualPeer(
                "sarah_chen",
                "Sarah Chen", 
                "Finance MBA from Wharton, 3 years at McKinsey, now Strategic Planning Director at tech startup",
                "Analytical, data-driven, framework-oriented, collaborative but assertive",
                "Professional but warm, uses consulting frameworks, asks probing financial questions",
                "Focuses heavily on ROI and financial metrics, sometimes overlooks emotional/human factors",
                "Financial modeling, ROI analysis, consulting frameworks, strategic planning"
            ),
            "marcus_rodriguez": VirtualPeer(
                "marcus_rodriguez",
                "Marcus Rodriguez",
                "15 years in retail operations, Customer Experience Director at major fashion retailer, MBA from Kellogg", 
                "Practical, customer-focused, experienced with implementation challenges, empathetic",
                "Direct and conversational, uses real examples from experience, passionate about CX",
                "Prioritizes customer satisfaction above all, skeptical of pure technology solutions",
                "Retail operations, customer experience design, implementation management, brand protection"
            ),
            "priya_patel": VirtualPeer(
                "priya_patel", 
                "Priya Patel",
                "Tech entrepreneur, founded and sold AI customer service platform, Stanford MBA",
                "Tech-optimistic, fast-moving, big-picture thinker, enthusiastic about innovation",
                "Energetic, uses startup/tech terminology, focuses on scalability and disruption",
                "Pro-technology solutions, may underestimate implementation complexity, growth-focused",
                "AI/ML implementation, startup scaling, product development, technology adoption"
            )
        }
        self.active_peers = ["sarah_chen"]  # Start with Sarah
        self.discussion_history = []
        self.research_insights = []
        self.complications_used = []
        
        # Realistic complications that peers might discover or share
        self.peer_complications = [
            {
                "type": "experience_share",
                "description": "Marcus just mentioned that when his company implemented a chatbot, customer complaints actually increased 25% in the first month because the bot couldn't handle emotional situations",
                "impact": "significantly challenge",
                "source": "Marcus Rodriguez",
                "peer_context": "Based on real implementation experience"
            },
            {
                "type": "research_finding", 
                "description": "Sarah found a recent McKinsey study showing that 40% of retail AI implementations fail due to poor change management, not technology issues",
                "impact": "potentially affect",
                "source": "Sarah Chen",
                "peer_context": "From consulting research database"
            },
            {
                "type": "industry_insight",
                "description": "Priya shared that newer AI platforms now achieve 85% accuracy vs. 65% two years ago, which could significantly improve the ROI calculations for Jessica",
                "impact": "positively impact", 
                "source": "Priya Patel",
                "peer_context": "From startup ecosystem knowledge"
            },
            {
                "type": "competitive_intel",
                "description": "Marcus heard through industry contacts that FashionForward's main competitor just had a PR disaster with their chatbot giving inappropriate responses to customer complaints",
                "impact": "significantly impact",
                "source": "Marcus Rodriguez", 
                "peer_context": "Industry network intelligence"
            }
        ]

    def get_discussion_context(self):
        return {
            "discussion_history": self.discussion_history[-5:],  # Last 5 exchanges
            "active_peers": self.active_peers,
            "complications": self.complications_used,
            "message_count": len(self.discussion_history)
        }
    
    def should_introduce_complication(self, stage):
        """Decide if a peer should share a complication/insight"""
        return (stage > 3 and 
                len(self.complications_used) < 2 and 
                len(self.active_peers) > 1 and  # Need multiple peers for realistic sharing
                random.random() < 0.35)  # 35% chance after stage 3
    
    def generate_peer_complication(self):
        """Generate a realistic complication from a peer's experience/research"""
        unused_complications = [c for c in self.peer_complications if c not in self.complications_used]
        if not unused_complications:
            return None
            
        # Prefer complications from active peers
        peer_complications = [c for c in unused_complications if any(peer_id in c['source'].lower().replace(' ', '_') for peer_id in self.active_peers)]
        
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
        "message": "Peer collaboration server running"
    })

@app.route("/health", methods=["GET"])
def health_check():
    """Detailed health check"""
    return jsonify({
        "status": "healthy", 
        "service": "Virtual Study Group API",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "active_study_groups": len(active_study_groups),
        "available_endpoints": ["/chat", "/invite_peer", "/trigger_research", "/health"]
    })

@app.route("/chat", methods=["POST"])
def peer_discussion():
    """Handle peer-to-peer case discussion"""
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
        # Determine which peer should respond (rotate or choose based on context)
        if len(session.active_peers) == 1:
            responding_peer_id = session.active_peers[0]
        else:
            # Simple rotation among active peers
            peer_index = (len(session.discussion_history) - 1) % len(session.active_peers)
            responding_peer_id = session.active_peers[peer_index]
        
        peer = session.peers[responding_peer_id]
        
        # Generate peer response
        peer_response = peer.generate_response(
            user_message, 
            session.get_discussion_context(),
            session.active_peers
        )
        
        # Store peer response
        session.discussion_history.append({
            "speaker": peer.name,
            "peer_id": responding_peer_id,
            "message": peer_response,
            "timestamp": datetime.now().isoformat(),
            "stage": stage
        })

        response_data = {
            "response": peer_response,
            "speaker": peer.name,
            "peer_id": responding_peer_id
        }
        
        # Maybe add a peer complication/insight
        if session.should_introduce_complication(stage):
            complication = session.generate_peer_complication()
            if complication:
                response_data["complication"] = complication
        
        # Occasionally add research insights (simulate group research)
        if stage > 2 and len(session.research_insights) < 2 and random.random() < 0.25:
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
    
    # Generate realistic joining messages based on peer personality
    intro_messages = {
        "marcus_rodriguez": f"Mind if I jump in? I'm {peer.name} - I've been running customer experience at a major fashion retailer for the past few years. This case actually reminds me of some challenges we faced when we were looking at automation options. I have some war stories that might be relevant!",
        "priya_patel": f"Hey everyone! {peer.name} here - I actually built and sold an AI customer service startup, so this hits really close to home. I'm probably biased toward the tech solution, but I've definitely seen both the incredible wins and the spectacular failures. Excited to dig into this with you all!",
        "sarah_chen": f"Hi! {peer.name} joining the discussion. I spent a few years at McKinsey working on operational strategy cases just like this one. I tend to dive into the financial modeling first - hope that's helpful for the group's analysis!"
    }
    
    introduction = intro_messages.get(peer_id, f"Hi everyone! I'm {peer.name}. Looking forward to working through this case with you!")
    
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
            {"company": "Sephora", "year": 2019, "outcome": "25% email reduction, but 15% increase in phone calls - customers escalated when bot couldn't help"},
            {"company": "H&M", "year": 2020, "outcome": "60% FAQ automation success, improved CSAT by training bot on actual customer language"},
            {"company": "ASOS", "year": 2021, "outcome": "45% faster response times, mixed satisfaction - younger customers loved it, older customers frustrated"},
            {"company": "Zara", "year": 2022, "outcome": "Strong ROI after 8 months, key was hybrid model with easy human handoff"},
            {"company": "Uniqlo", "year": 2023, "outcome": "Multilingual success in Asia, 40% cost reduction, but required 6 months of training data prep"}
        ],
        "latest_trends": [
            "Hybrid AI-human models showing 40% better satisfaction than pure automation",
            "Personalization engines reducing repeat questions by 55% when trained on customer history", 
            "Voice-enabled chatbots gaining traction in mobile commerce, especially with Gen Z",
            "Real-time sentiment analysis improving escalation decisions by 35%",
            "Integration with social media platforms becoming standard for fashion brands"
        ],
        "industry_insights": [
            "87% of fashion retailers plan AI customer service investments in 2024-2025",
            "Average implementation time decreased from 6 months to 6-8 weeks with modern platforms",
            "ROI typically achieved within 8-12 months for fashion retail specifically",
            "Customer acceptance rates 25% higher when chatbot personality matches brand voice",
            "Mobile-first implementations show 30% better engagement than desktop-first"
        ],
        "peer_contributions": [
            "Sarah's consulting network provided benchmark data from similar fashion retailers",
            "Marcus shared insights from his company's vendor evaluation process",
            "Priya contributed technical feasibility assessments from startup experience"
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
        }
    ]
    
    return random.choice(base_insights)

if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key before running the server.")
    
    # Run the Flask app
    app.run(
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 5000)),
        debug=False  # Set to False for production on Render
    )