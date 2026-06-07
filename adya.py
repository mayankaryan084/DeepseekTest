import streamlit as st
import requests
import json
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="Customer Support Agent - DeepSeek",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for the exact look
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Configuration section */
    .config-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        border: 1px solid #e0e0e0;
    }
    
    .config-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #333;
    }
    
    /* Chat message styling */
    .user-message {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        margin-left: 20%;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: white;
        padding: 1rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        margin-right: 20%;
        border-left: 4px solid #4caf50;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Header styling */
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Input area */
    .stTextInput > div > div > input {
        border-radius: 2rem;
        padding: 1rem;
        font-size: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 2rem;
        padding: 0.5rem 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Welcome message */
    .welcome-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Persona badge */
    .persona-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        background-color: #e8f5e9;
        color: #2e7d32;
        border-radius: 2rem;
        font-size: 0.875rem;
        margin-bottom: 1rem;
    }
    
    /* Delivery possibility section */
    .delivery-section {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 2rem;
        border-left: 4px solid #ff9800;
    }
    
    /* Creative winter styling */
    .creative-footer {
        background-color: #1a1a2e;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        margin-top: 2rem;
    }
    
    /* Timer styling */
    .timer {
        font-family: monospace;
        font-size: 0.875rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False
if 'use_secrets' not in st.session_state:
    st.session_state.use_secrets = False

# Persona configurations
PERSONAS = {
    "customer_support": {
        "name": "Customer Support Agent",
        "icon": "🎧",
        "welcome": "Hello! I'm now your Customer Support Agent. How can I assist you today?",
        "system_prompt": """You are a professional Customer Support Agent. Your expertise includes:
- Troubleshooting technical issues
- Handling customer complaints professionally
- Providing step-by-step solutions
- Being empathetic and patient
- Explaining policies clearly
- Offering alternative solutions when needed

When responding:
1. Be polite, patient, and empathetic
2. Acknowledge the customer's frustration when applicable
3. Provide clear, step-by-step instructions
4. Ask clarifying questions to better understand issues
5. Offer to help further at the end of responses
6. Use a warm, friendly tone with occasional emojis
7. Confirm understanding before proceeding with solutions

Always prioritize customer satisfaction while providing accurate information."""
    }
}

# API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def validate_api_key(api_key):
    """Validate OpenRouter API key format"""
    if not api_key:
        return False
    pattern = r'^sk-or-v1-[a-zA-Z0-9]+$'
    return bool(re.match(pattern, api_key))

def test_api_key(api_key):
    """Test if API key works"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    data = {
        "model": "openrouter/free",
        "messages": [{"role": "user", "content": "Test"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=10)
        return response.status_code == 200
    except:
        return False

def send_message(message, api_key):
    """Send message to OpenRouter API with customer support persona"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://customer-support-app.streamlit.app",
        "X-Title": "Customer Support Agent"
    }
    
    # Build messages with system prompt
    messages = [
        {
            "role": "system",
            "content": PERSONAS["customer_support"]["system_prompt"]
        }
    ]
    
    # Add conversation history
    for msg in st.session_state.messages:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    data = {
        "model": "openrouter/free",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        with st.spinner("Customer Support Agent is typing..."):
            response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            return assistant_message, None
        else:
            return None, f"API Error: {response.status_code}"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

# ==================== MAIN UI ====================

# Header
st.markdown("""
<div class="chat-header">
    <h1>🎧 Customer Support Agent</h1>
    <p>Powered by DeepSeek AI | 24/7 Professional Support</p>
</div>
""", unsafe_allow_html=True)

# Configuration Section
with st.expander("⚙️ Configuration", expanded=not st.session_state.api_key_valid):
    st.markdown("### API Key")
    
    # API Key Source
    api_source = st.radio(
        "API Key Source",
        ["Enter manually", "Use from secrets.toml"],
        index=0 if not st.session_state.use_secrets else 1
    )
    
    if api_source == "Enter manually":
        api_key_input = st.text_input(
            "OpenRouter API Key",
            type="password",
            placeholder="sk-or-v1-...",
            help="Get your API key from https://openrouter.ai/keys"
        )
        
        if api_key_input:
            if validate_api_key(api_key_input):
                if st.button("✅ Connect"):
                    with st.spinner("Testing API key..."):
                        if test_api_key(api_key_input):
                            st.session_state.api_key = api_key_input
                            st.session_state.api_key_valid = True
                            st.success("✅ Connected successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid API key. Please check and try again.")
            else:
                st.error("Invalid API key format. Key should start with 'sk-or-v1-'")
    
    else:
        st.info("📁 Using API key from secrets.toml file")
        if st.button("🔑 Load from secrets"):
            try:
                # This would load from secrets in production
                # For now, show a message
                st.warning("Please configure your secrets.toml file with OPENROUTER_API_KEY")
            except:
                st.error("No API key found in secrets.toml")
    
    st.markdown("---")
    st.markdown("[🔗 Get an OpenRouter API key](https://openrouter.ai/keys)")
    
    # AI Persona Selection
    st.markdown("### AI Persona")
    selected_persona = st.selectbox(
        "Choose AI Persona",
        ["Customer Support Agent"],
        index=0
    )

# Show welcome message if API key is not connected
if not st.session_state.api_key_valid:
    st.markdown("""
    <div class="welcome-box">
        <h2>👋 Welcome to Customer Support Agent</h2>
        <p>Please configure your API key above to start receiving professional customer support assistance.</p>
        <br>
        <p>✨ <strong>Features:</strong> 24/7 availability, professional responses, troubleshooting guides, and empathetic support.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Display welcome message
    st.markdown(f"""
    <div class="persona-badge">
        🎧 Active Persona: Customer Support Agent
    </div>
    """, unsafe_allow_html=True)
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <strong>👤 You</strong><br>
                {message["content"]}
                <div class="timer">🕐 {message.get("timestamp", "")}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="assistant-message">
                <strong>🎧 Customer Support Agent</strong><br>
                {message["content"]}
                <div class="timer">🕐 {message.get("timestamp", "")}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # If no messages, show welcome
    if len(st.session_state.messages) == 0:
        st.markdown(f"""
        <div class="assistant-message">
            <strong>🎧 Customer Support Agent</strong><br>
            {PERSONAS["customer_support"]["welcome"]}
        </div>
        """, unsafe_allow_html=True)
        # Add welcome to messages
        st.session_state.messages.append({
            "role": "assistant",
            "content": PERSONAS["customer_support"]["welcome"],
            "timestamp": datetime.now().strftime("%I:%M %p")
        })
    
    # Chat input
    st.markdown("---")
    user_input = st.text_input(
        "Type your message here...",
        placeholder="E.g., I'm facing problems with my internet connection",
        key="user_input",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([4, 1, 4])
    with col2:
        if st.button("📤 Send", use_container_width=True):
            if user_input:
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
                
                # Get response
                response, error = send_message(user_input, st.session_state.api_key)
                
                if response:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now().strftime("%I:%M %p")
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"⚠️ {error}. Please try again or check your connection.",
                        "timestamp": datetime.now().strftime("%I:%M %p")
                    })
                
                st.rerun()

# Delivery Possibility Section (as shown in the image)
st.markdown("""
<div class="delivery-section">
    <strong>📦 DELIVERY POSSIBILITY</strong><br>
    <small>Customer Support Agent • Available 24/7 • Average response time: &lt; 30 seconds</small>
</div>
""", unsafe_allow_html=True)

# Creative Winter Footer (matching the image)
st.markdown("""
<div class="creative-footer">
    <strong>Creative Winter</strong><br>
    <small>Professional Customer Support Solutions | Powered by DeepSeek AI</small>
</div>
""", unsafe_allow_html=True)

# Add a timer effect in sidebar for visual appeal
with st.sidebar:
    st.markdown("### 📊 Session Info")
    st.metric("Messages Exchanged", len(st.session_state.messages) // 2)
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    ### 💡 Quick Tips
    
    **Best practices for faster support:**
    1. Be specific about your issue
    2. Mention what you've already tried
    3. Include error messages if any
    4. Specify device/model if relevant
    
    ### 🕐 Support Hours
    24/7 Automated Support
    Human escalation available upon request
    """)
