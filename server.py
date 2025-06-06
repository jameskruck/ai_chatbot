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
    return render_template_string(open('index.html').read())

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
            # For tutoring sessions, use specialized tutor prompt
            conversation_histories[user_id] = [{
                "role": "system", 
                "content": """You are an expert AI tutor specializing in retail technology and business case analysis. You're guiding a learner through the FashionForward T-Shirts chatbot case study.

Your teaching approach:
1. Use Socratic questioning - ask one focused question at a time
2. Build on the learner's responses to deepen understanding
3. Be encouraging and supportive while challenging their thinking
4. Keep responses conversational and engaging (2-4 sentences max usually)
5. Guide them through: problem analysis → solution prioritization → chatbot design → implementation planning
6. Adapt your questions based on their responses and learning progress

Case Context: FashionForward receives 50+ daily repetitive emails (sizing, returns, shipping, fabric care). Response times are 24-48 hours, customer satisfaction declining. They want an AI chatbot for FAQs.

Your goal: Help them think like a business consultant analyzing this case systematically."""
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
        )        response = client.chat.completions.create(
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
    return jsonify({"status": "healthy", "service": "Retail Chatbot Course API"})

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