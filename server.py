from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Store conversation histories for different evaluation sessions
conversation_histories = {}

@app.route("/")
def home():
    """Serve the main course page"""
    try:
        return render_template_string(open('prep-work.html').read())
    except:
        return jsonify({"message": "Welcome to the AI Chatbot Strategy Course API"})

@app.route("/chat", methods=["POST"])
def chat():
    """Handle AI tutoring and evaluation requests"""
    data = request.json
    user_id = data.get("user_id", "default")
    user_message = data.get("message", "")
    session_data = data.get("session_data", {})

    # Initialize conversation history if it doesn't exist
    if user_id not in conversation_histories:
        if "session_" in user_id:
            # For strategic consultation sessions
            conversation_histories[user_id] = [{
                "role": "system", 
                "content": """You are a business analyst peer working alongside a colleague to think through the FashionForward case. You're both consultants trying to figure this out together - you're NOT a teacher or expert.

Critical peer behavior:
1. NEVER give direct answers or recommendations 
2. Share observations and ask "what do you think?" frequently
3. Express uncertainty and explore ideas together: "I'm wondering if...", "That's interesting, but I'm not sure about..."
4. Build on their ideas rather than leading them
5. Keep responses very short (1-2 sentences max)
6. If you have insights, frame as questions: "Could it be that the real issue is...?" rather than stating facts

WRONG (too direct): "The chatbot option is best because it's scalable and cost-effective."
RIGHT (peer-like): "Hmm, I keep coming back to that scalability thing with the chatbot... but I'm torn about the customer experience piece. What's your gut feeling on that trade-off?"

WRONG: "You should consider the board timeline pressure."
RIGHT: "I wonder if that 3-day deadline changes how we should think about this? What do you make of that timing?"

Your goal: Help them think WITHOUT giving answers. Be genuinely curious about their perspective. Express your own uncertainty and thinking process.

Case Context: Jessica Martinez, CEO of FashionForward T-Shirts, must choose by April 11, 2024:
- AI Chatbot: $87K/2 years, 6-8 weeks, handles 65% of tickets, scalable but limited empathy
- Team Expansion: $256K/2 years, 4-6 weeks, personal touch but higher costs  
- Outsourcing: $383K/2 years, 3-4 weeks, professional but expensive & less brand control

Current crisis: 4.2→3.1 customer satisfaction, 8→31 hour response times, $156K quarterly revenue at risk, 1,850 monthly tickets (34% sizing questions).

TRANSITION AWARENESS: After 5-6 exchanges, if they seem to have reached a decision or recommendation, you can naturally suggest "Sounds like we're ready to start building this solution!" or "Should we move forward with implementing this?"

Remember: You're thinking through this together, not teaching them."""
            }]
        elif "evaluator" in user_id or "summary" in user_id:
            # For evaluation requests, use a specialized system prompt
            conversation_histories[user_id] = [{
                "role": "system", 
                "content": """You are an expert instructional designer and chatbot consultant specializing in retail customer service. 

Your role is to evaluate chatbot responses for educational purposes. When evaluating responses:

1. Be constructive and encouraging while providing honest feedback
2. Focus on practical improvements that a non-technical learner can implement
3. Consider brand voice, customer experience, and business objectives
4. Provide specific, actionable suggestions
5. Use a friendly, professional tone appropriate for adult learners
6. Format your responses clearly with headers and bullet points where helpful

Remember: You're helping learners improve their chatbot design skills, not critiquing them harshly."""
            }]
        else:
            # Default system prompt for general chat
            conversation_histories[user_id] = [{
                "role": "system", 
                "content": "You are a helpful AI assistant specialized in retail technology and customer service."
            }]

    # Add session context for tutoring sessions
    if session_data and "session_" in user_id:
        context_message = f"""
Session Context:
- Current stage: {session_data.get('stage', 'unknown')}
- Message count: {session_data.get('messageCount', 0)}
- Previous responses: {len(session_data.get('userResponses', []))}

User Message: {user_message}"""
        user_message = context_message

    # Add user message to conversation history
    conversation_histories[user_id].append({"role": "user", "content": user_message})

    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_histories[user_id],
            temperature=0.7,
            max_tokens=300 if "session_" in user_id else 500  # Shorter responses for tutoring
        )

        ai_response = response.choices[0].message.content
        
        # Add AI response to conversation history
        conversation_histories[user_id].append({"role": "assistant", "content": ai_response})

        return jsonify({"response": ai_response})

    except Exception as e:
        # Log the error for debugging
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": f"AI service temporarily unavailable: {str(e)}"}), 500

@app.route("/get_session_data", methods=["POST"])
def get_session_data():
    """Retrieve session data for analytics"""
    data = request.json
    user_id = data.get("user_id", "")
    
    if user_id in conversation_histories:
        return jsonify({
            "session_data": conversation_histories[user_id],
            "message_count": len(conversation_histories[user_id])
        })
    else:
        return jsonify({"error": "Session not found"}), 404

@app.route("/reset_conversation", methods=["POST"])
def reset_conversation():
    """Reset conversation history for a specific user"""
    data = request.json
    user_id = data.get("user_id", "default")
    
    if user_id in conversation_histories:
        del conversation_histories[user_id]
    
    return jsonify({"message": "Conversation reset successfully"})

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "AI Chatbot Strategy Course API"})

if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key before running the server.")
    
    # Run the Flask app
    app.run(
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 5000)),
        debug=True  # Remove in production
    )