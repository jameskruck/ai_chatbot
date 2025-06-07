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
active_sessions = {}

class AIAgent:
    def __init__(self, persona, background, biases):
        self.persona = persona
        self.background = background
        self.biases = biases
        self.conversation_history = []
    
    def generate_perspective(self, topic, context):
        """Generate this agent's unique perspective on a topic"""
        prompt = f"""
        You are {self.persona} with background: {self.background}
        Your cognitive biases: {self.biases}
        
        Topic: {topic}
        Context: {context}
        
        Generate YOUR unique perspective. Be opinionated, show your biases, 
        disagree if it fits your persona. Don't be diplomatic.
        Keep response under 100 words.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I have thoughts on this, but I'm having trouble expressing them right now. [Error: {str(e)}]"

class CollaborativeSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.agents = {
            "financial_analyst": AIAgent(
                persona="CFO with startup background",
                background="10 years scaling companies, burned by expensive outsourcing",
                biases="Cost-first thinking, skeptical of new tech ROI"
            ),
            "cx_expert": AIAgent(
                persona="Customer Experience Director", 
                background="Retail veteran, saw chatbots fail at previous company",
                biases="Human-first, worried about brand damage"
            ),
            "tech_optimist": AIAgent(
                persona="CTO from tech company",
                background="AI early adopter, built several chatbot systems", 
                biases="Tech-solutionist, underestimates implementation complexity"
            )
        }
        self.active_agents = ["financial_analyst"]  # Start with one
        self.session_memory = []
        self.complications_used = []
        self.research_count = 0
        
        # Potential plot twists
        self.plot_twists = [
            "Competitor just launched similar AI chatbot with mixed customer reviews",
            "Major fashion influencer criticized automated customer service on social media",
            "Jessica's biggest client threatened to leave over recent service delays",
            "Customer service team discovered 40% of complaints are about product quality, not response time",
            "New data shows competitor's chatbot increased customer complaints by 15%"
        ]
    
    def get_context(self):
        return {
            "session_memory": self.session_memory[-5:],  # Last 5 exchanges
            "active_agents": self.active_agents,
            "complications": self.complications_used,
            "message_count": len(self.session_memory)
        }
    
    def should_introduce_complication(self, stage):
        """Decide if we should add a plot twist"""
        return (stage > 3 and 
                len(self.complications_used) < 2 and 
                random.random() < 0.3)  # 30% chance after stage 3
    
    def generate_complication(self, user_message):
        """Generate a realistic complication"""
        unused_twists = [t for t in self.plot_twists if t not in self.complications_used]
        if not unused_twists:
            return None
            
        twist = random.choice(unused_twists)
        self.complications_used.append(twist)
        
        return {
            "type": "complication",
            "description": twist,
            "impact": "significantly impact" if "competitor" in twist.lower() else "potentially affect",
            "new_considerations": "How does this change your team's recommendation?"
        }

@app.route("/")
def home():
    """Health check and basic info"""
    return jsonify({
        "status": "healthy",
        "service": "AI Chatbot Strategy Course API",
        "message": "Enhanced collaboration server running"
    })

@app.route("/health", methods=["GET"])
def health_check():
    """Detailed health check"""
    return jsonify({
        "status": "healthy", 
        "service": "AI Chatbot Strategy Course API",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "active_sessions": len(active_sessions),
        "available_endpoints": ["/chat", "/introduce_agent", "/trigger_research", "/health"]
    })

@app.route("/chat", methods=["POST"])
def enhanced_chat():
    """Enhanced chat with multi-agent collaboration"""
    data = request.json
    user_id = data.get("user_id", "default")
    user_message = data.get("message", "")
    stage = data.get("stage", 1)

    # Initialize session if needed
    if user_id not in active_sessions:
        active_sessions[user_id] = CollaborativeSession(user_id)
    
    session = active_sessions[user_id]
    
    # Initialize conversation history if needed
    if user_id not in conversation_histories:
        if "enhanced_session" in user_id:
            conversation_histories[user_id] = [{
                "role": "system", 
                "content": """You are part of a business analyst team working on the FashionForward case. Multiple AI agents with different expertise are collaborating with a human colleague.

Your role: Facilitate collaborative thinking, NOT teaching. You're thinking through this together.

Current team members may include:
- Financial Analyst (cost-focused, startup experience)
- CX Expert (customer experience focused, seen chatbot failures)  
- Tech Specialist (AI optimist, implementation focused)

Key behaviors:
1. Show genuine collaboration between agents with different viewpoints
2. Express uncertainty and explore ideas together
3. Ask the human to help resolve disagreements between agents
4. Build on each other's insights
5. Keep responses conversational (2-3 sentences max)
6. Show agents discovering insights together

Case: Jessica Martinez, FashionForward CEO, must choose by April 11:
- AI Chatbot: $87K/2 years, 6-8 weeks, handles 65% of tickets
- Team Expansion: $256K/2 years, 4-6 weeks, personal touch
- Outsourcing: $383K/2 years, 3-4 weeks, professional but expensive

Crisis: 4.2→3.1 CSAT, 8→31hr response time, $156K quarterly revenue at risk

After 5-6 exchanges, transition toward implementation if consensus emerges."""
            }]
        else:
            conversation_histories[user_id] = [{
                "role": "system", 
                "content": "You are a helpful AI assistant specialized in retail technology and customer service."
            }]

    # Add user message to conversation
    conversation_histories[user_id].append({"role": "user", "content": user_message})
    
    # Store in session memory
    session.session_memory.append({
        "user": user_message,
        "timestamp": datetime.now().isoformat(),
        "stage": stage,
        "active_agents": session.active_agents.copy()
    })

    try:
        # Generate main response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_histories[user_id],
            temperature=0.7,
            max_tokens=300
        )

        ai_response = response.choices[0].message.content
        conversation_histories[user_id].append({"role": "assistant", "content": ai_response})

        # Prepare response data
        response_data = {"response": ai_response}
        
        # Maybe add a complication
        if session.should_introduce_complication(stage):
            complication = session.generate_complication(user_message)
            if complication:
                response_data["complication"] = complication
        
        # Maybe add research insight (simulate for now)
        if stage > 2 and session.research_count < 2 and random.random() < 0.2:
            response_data["research_insight"] = {
                "chatbot_implementations": [
                    {"company": "Zara", "year": 2022, "outcome": "50% reduction in email volume, 20% improvement in CSAT"},
                    {"company": "Target", "year": 2023, "outcome": "Mixed results - faster responses but higher escalation rates"}
                ],
                "latest_trends": ["AI-human hybrid models showing 35% better satisfaction than pure automation"]
            }
            session.research_count += 1

        return jsonify(response_data)

    except Exception as e:
        print(f"Error in enhanced chat: {str(e)}")
        return jsonify({"error": f"AI collaboration temporarily unavailable: {str(e)}"}), 500

@app.route("/introduce_agent", methods=["POST"])
def introduce_agent():
    """Add a new AI agent to the conversation"""
    data = request.json
    user_id = data.get("user_id", "")
    agent_type = data.get("agent_type", "")
    
    if user_id not in active_sessions:
        return jsonify({"error": "Session not found"}), 404
    
    session = active_sessions[user_id]
    
    if agent_type not in session.agents:
        return jsonify({"error": "Unknown agent type"}), 400
    
    if agent_type in session.active_agents:
        return jsonify({"error": "Agent already active"}), 400
    
    # Add agent to active list
    session.active_agents.append(agent_type)
    
    # Generate introduction based on agent persona
    agent = session.agents[agent_type]
    
    intro_prompts = {
        "cx_expert": f"Hi team! I'm {agent.persona}. {agent.background}. I couldn't help but overhear your discussion about FashionForward's customer service crisis. Mind if I jump in with a customer experience perspective?",
        "tech_optimist": f"Hey everyone! {agent.persona} here. {agent.background}. This FashionForward case is right up my alley - I'd love to share some insights about AI implementation if that's helpful!"
    }
    
    introduction = intro_prompts.get(agent_type, f"Hi! I'm the {agent.persona}. Happy to contribute to this FashionForward analysis!")
    
    return jsonify({
        "agent_introduced": agent_type,
        "introduction": introduction,
        "active_agents": session.active_agents
    })

@app.route("/trigger_research", methods=["POST"])
def trigger_research():
    """Simulate live research for demonstration"""
    data = request.json
    user_id = data.get("user_id", "")
    topic = data.get("topic", "chatbot_implementations")
    
    # Simulate research data - in reality, this would call external APIs
    research_data = {
        "chatbot_implementations": [
            {"company": "Sephora", "year": 2019, "outcome": "25% email reduction, 15% phone increase"},
            {"company": "H&M", "year": 2020, "outcome": "60% FAQ automation, improved CSAT"},
            {"company": "ASOS", "year": 2021, "outcome": "45% faster response times, mixed satisfaction"},
            {"company": "Nike", "year": 2022, "outcome": "Strong mobile performance, 30% self-service rate"},
            {"company": "Uniqlo", "year": 2023, "outcome": "Multilingual success, reduced support costs by 40%"}
        ],
        "latest_trends": [
            "Hybrid AI-human models showing 40% better satisfaction than pure AI",
            "Personalization engines reducing repeat questions by 55%",
            "Voice-enabled chatbots gaining traction in mobile commerce",
            "Integration with social media platforms becoming standard",
            "Real-time sentiment analysis improving escalation decisions"
        ],
        "industry_insights": [
            "87% of fashion retailers plan AI customer service investments in 2024",
            "Average implementation time has decreased from 6 months to 6-8 weeks",
            "ROI typically achieved within 8-12 months for fashion retail"
        ]
    }
    
    return jsonify({"research": research_data})

@app.route("/reset_conversation", methods=["POST"])
def reset_conversation():
    """Reset conversation history for a specific user"""
    data = request.json
    user_id = data.get("user_id", "default")
    
    if user_id in conversation_histories:
        del conversation_histories[user_id]
    
    if user_id in active_sessions:
        del active_sessions[user_id]
    
    return jsonify({"message": "Session reset successfully"})

@app.route("/get_session_data", methods=["POST"])
def get_session_data():
    """Retrieve session data for analytics"""
    data = request.json
    user_id = data.get("user_id", "")
    
    if user_id in active_sessions:
        session = active_sessions[user_id]
        return jsonify({
            "session_data": {
                "active_agents": session.active_agents,
                "complications_used": session.complications_used,
                "research_count": session.research_count,
                "message_count": len(session.session_memory)
            },
            "conversation_history": conversation_histories.get(user_id, [])
        })
    else:
        return jsonify({"error": "Session not found"}), 404

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