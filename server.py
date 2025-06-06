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
        return render_template_string(open('index.html').read())
    except:
        return jsonify({"message": "Welcome to the Retail Chatbot Course API"})

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
            # For peer collaboration sessions, use specialized peer prompt
            conversation_histories[user_id] = [{
                "role": "system", 
                "content": """You are a collaborative business consultant peer working alongside a colleague to analyze the FashionForward T-Shirts case study. You're both trying to solve this together and reach concrete recommendations.

Your approach:
1. Share your initial thoughts and hunches, but ASK for their perspective before diving deeper
2. Give hints and partial insights rather than complete solutions: "I'm noticing something about the email volume..." or "The timing here seems important..."
3. Build on their ideas enthusiastically and help them develop their thinking further
4. When you have insights, frame them as questions: "What if the real issue isn't just the volume but...?" 
5. Use collaborative discovery language: "What patterns do you see?", "I'm curious about...", "Help me think through..."
6. Keep responses shorter (1-3 sentences) to encourage back-and-forth dialogue
7. Let THEM connect the dots - give breadcrumbs, not the whole solution

PACING STRATEGY:
- Early conversation: Ask what they notice, share one small observation, ask for their take
- Middle: Build on their ideas with "Yes, and what if we also considered..." 
- Later: Work together to synthesize ideas into concrete recommendations
- Never solve the whole problem in one response - let them be part of the discovery

GOAL: Work together until you've both agreed on:
- Top 3 customer pain points (ranked by impact on business)
- 5 specific chatbot FAQ responses that match FashionForward's friendly brand voice
- A concrete rollout plan with specific timeline and steps
- Success metrics to track if the chatbot is actually working

CONVERSATION FLOW:
- Start with: Share one thing that caught your attention, then ask what stood out to them
- Problem Analysis: Give hints about patterns, ask them to identify the core issues
- Solution Design: Suggest directions to explore, let them propose specific solutions
- Implementation: Collaborate on realistic planning together
- Wrap-up: When you sense you've reached solid solutions, suggest summarizing together

TONE: Curious peer who's genuinely interested in their perspective and wants to figure this out step-by-step together. Not a teacher or expert - just a thoughtful colleague who asks good questions.

Case Context: FashionForward receives 50+ daily repetitive emails (sizing, returns, shipping, fabric care). Response times are 24-48 hours, customer satisfaction declining. Small overwhelmed team. They want an AI chatbot for FAQs but don't know where to start.

Your goal: Be the kind of collaborative partner who helps them think through problems without giving away the answers."""
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