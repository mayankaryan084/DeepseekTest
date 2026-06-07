import streamlit as st
import requests
import json
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="AI Persona Assistant - DeepSeek",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for navigation bar and styling
st.markdown("""
<style>
    /* Navigation Bar Styling */
    .navbar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white;
    }
    
    .navbar-brand {
        font-size: 1.5rem;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .navbar-menu {
        display: flex;
        gap: 1rem;
    }
    
    .nav-item {
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        background: rgba(255, 255, 255, 0.1);
    }
    
    .nav-item:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
    }
    
    .nav-item-active {
        background: white;
        color: #667eea;
        font-weight: bold;
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
    
    /* Configuration section */
    .config-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        border: 1px solid #e0e0e0;
    }
    
    /* Persona badge */
    .persona-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        font-size: 0.875rem;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    
    /* Welcome box */
    .welcome-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Footer */
    .footer {
        background-color: #1a1a2e;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        margin-top: 2rem;
    }
    
    /* Timer */
    .timer {
        font-family: monospace;
        font-size: 0.75rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    /* Persona info card */
    .persona-info {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Persona definitions with detailed prompts
PERSONAS = {
    "content_creator": {
        "name": "Content Creator - Reel Specialist",
        "short_name": "🎬 Reel Creator",
        "icon": "🎬",
        "emoji": "📱",
        "color": "#FF6B6B",
        "badge_color": "#ffebee",
        "text_color": "#c62828",
        "description": "Expert in creating viral reel content, trends, and engagement strategies",
        "welcome": "Hey creator! 🎬 I'm your Reel Specialist. Ready to make some viral content? Ask me about trending sounds, hook strategies, or editing tips!",
        "placeholder": "E.g., 'What are trending reel concepts for fitness?' or 'How to write better hooks for cooking reels?'",
        "system_prompt": """You are a professional Content Creator specializing in Reels and Short-form video content. Your expertise includes:
- Viral reel concepts and trends
- Hook strategies for first 3 seconds
- Caption writing for maximum engagement
- Hashtag strategies
- Transition and editing ideas
- Platform-specific advice (Instagram, TikTok, YouTube Shorts)
- Sound and music selection
- Engagement optimization

When responding:
1. Always provide specific, actionable advice
2. Include examples of successful reels
3. Break down complex concepts into simple steps
4. Suggest trending audio and hashtags when relevant
5. Be enthusiastic and creative in your responses
6. Ask clarifying questions when needed
7. Format with emojis for better readability"""
    },
    "content_writer": {
        "name": "Content Writer",
        "short_name": "✍️ Writer",
        "icon": "✍️",
        "emoji": "📝",
        "color": "#4ECDC4",
        "badge_color": "#e0f2f1",
        "text_color": "#00695c",
        "description": "Expert in writing, editing, and content strategy for all formats",
        "welcome": "Welcome to your Writing Assistant! ✍️ Need help with blog posts, SEO, copywriting, or editing? I've got you covered!",
        "placeholder": "E.g., 'Write a blog outline about AI' or 'Improve this headline: [your text]'",
        "system_prompt": """You are a professional Content Writer and Editor. Your expertise includes:
- Blog post writing and structuring
- SEO optimization techniques
- Copywriting for marketing
- Email newsletters
- Social media captions
- Proofreading and editing
- Tone adaptation (formal, casual, humorous, professional)
- Storytelling techniques
- Headline writing

When responding:
1. Provide clear, well-structured writing advice
2. Offer specific examples and templates
3. Explain the reasoning behind your suggestions
4. Adapt tone based on the target audience
5. Include SEO tips when relevant
6. Use proper formatting with headings and bullet points"""
    },
    "customer_support": {
        "name": "Customer Support Agent",
        "short_name": "🎧 Support",
        "icon": "🎧",
        "emoji": "💬",
        "color": "#45B7D1",
        "badge_color": "#e1f5fe",
        "text_color": "#0277bd",
        "description": "Professional customer support for product, service, and technical inquiries",
        "welcome": "Hello! I'm your Customer Support Agent. 🎧 How can I assist you today? I'm here to help with any issues or questions!",
        "placeholder": "E.g., 'I'm facing internet connection problems' or 'How do I request a refund?'",
        "system_prompt": """You are a professional Customer Support Agent. Your expertise includes:
- Troubleshooting technical issues
- Explaining product features and policies
- Handling complaints professionally
- Providing step-by-step solutions
- Escalation procedures
- Empathetic communication
- FAQ responses
- Return and refund processes
- Account management guidance

When responding:
1. Be polite, patient, and empathetic
2. Provide clear, step-by-step instructions
3. Acknowledge the customer's frustration when applicable
4. Offer alternative solutions when possible
5. Use professional but friendly language
6. Ask clarifying questions to better understand issues
7. Confirm when issues are resolved"""
    }
}

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False
if 'current_persona' not in st.session_state:
    st.session_state.current_persona = "customer_support"
if 'use_secrets' not in st.session_state:
    st.session_state.use_secrets = False

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

def send_message(message, api_key, persona_key):
    """Send message to OpenRouter API with selected persona"""
    
    persona = PERSONAS[persona_key]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ai-persona-assistant.streamlit.app",
        "X-Title": f"AI Persona - {persona['name']}"
    }
    
    # Build messages with system prompt
    messages = [
        {
            "role": "system",
            "content": persona["system_prompt"]
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
        with st.spinner(f"{persona['icon']} {persona['name']} is thinking..."):
            response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            return assistant_message, None
        else:
            return None, f"API Error: {response.status_code}"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

def switch_persona(persona_key):
    """Switch to a different persona and clear conversation"""
    if st.session_state.current_persona != persona_key:
        st.session_state.current_persona = persona_key
        st.session_state.messages = []
        return True
    return False

# ==================== NAVIGATION BAR ====================

# Navigation Bar
st.markdown(f"""
<div class="navbar">
    <div class="navbar-brand">
        <span>🤖</span>
        <span>AI Persona Assistant</span>
    </div>
    <div class="navbar-menu">
        <div class="nav-item {'nav-item-active' if st.session_state.current_persona == 'content_creator' else ''}" onclick="alert('Click the button in sidebar')">
            🎬 Reel Creator
        </div>
        <div class="nav-item {'nav-item-active' if st.session_state.current_persona == 'content_writer' else ''}" onclick="alert('Click the button in sidebar')">
            ✍️ Writer
        </div>
        <div class="nav-item {'nav-item-active' if st.session_state.current_persona == 'customer_support' else ''}" onclick="alert('Click the button in sidebar')">
            🎧 Support
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar for navigation and controls
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    st.markdown("---")
    
    # Persona selection in sidebar
    st.markdown("#### 🎭 Select AI Persona")
    
    for persona_key, persona in PERSONAS.items():
        is_active = st.session_state.current_persona == persona_key
        button_style = "primary" if is_active else "secondary"
        
        if st.button(
            f"{persona['icon']} {persona['name']}",
            key=f"nav_{persona_key}",
            use_container_width=True,
            type=button_style
        ):
            if switch_persona(persona_key):
                st.rerun()
    
    st.markdown("---")
    
    # API Configuration Section
    st.markdown("### 🔑 API Configuration")
    
    if not st.session_state.api_key_valid:
        api_source = st.radio(
            "API Key Source",
            ["Enter manually", "Use from secrets.toml"],
            index=0
        )
        
        if api_source == "Enter manually":
            api_key_input = st.text_input(
                "OpenRouter API Key",
                type="password",
                placeholder="sk-or-v1-...",
                help="Get your key from openrouter.ai/keys"
            )
            
            if api_key_input and validate_api_key(api_key_input):
                if st.button("✅ Connect", use_container_width=True):
                    with st.spinner("Testing..."):
                        if test_api_key(api_key_input):
                            st.session_state.api_key = api_key_input
                            st.session_state.api_key_valid = True
                            st.success("Connected!")
                            st.rerun()
                        else:
                            st.error("Invalid key")
        else:
            st.info("Using secrets.toml")
            if st.button("Load from secrets"):
                st.warning("Configure secrets.toml with OPENROUTER_API_KEY")
    else:
        st.success("✅ API Key Connected")
        if st.button("🔄 Change API Key", use_container_width=True):
            st.session_state.api_key = None
            st.session_state.api_key_valid = False
            st.session_state.messages = []
            st.rerun()
    
    st.markdown("---")
    st.markdown("[🔗 Get API Key](https://openrouter.ai/keys)")
    
    # Session controls
    if st.session_state.api_key_valid:
        st.markdown("---")
        st.markdown("### 🛠️ Controls")
        
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        # Stats
        st.markdown("---")
        st.markdown("### 📊 Stats")
        st.metric("Messages", len(st.session_state.messages))
        st.metric("Active Persona", PERSONAS[st.session_state.current_persona]["short_name"])

# Main content area
current_persona = PERSONAS[st.session_state.current_persona]

if not st.session_state.api_key_valid:
    # Welcome screen
    st.markdown(f"""
    <div class="welcome-box">
        <h2>👋 Welcome to AI Persona Assistant!</h2>
        <p>Choose from specialized AI personas and get expert assistance</p>
        <br>
        <h3>🎭 Available Personas:</h3>
        <table style="width: 100%; text-align: left; margin-top: 1rem;">
            <tr>
                <td>🎬 <strong>Content Creator - Reel Specialist</strong></td>
                <td>Viral content, trends, hooks, editing tips</td>
            </tr>
            <tr>
                <td>✍️ <strong>Content Writer</strong></td>
                <td>Blogs, SEO, copywriting, editing</td>
            </tr>
            <tr>
                <td>🎧 <strong>Customer Support Agent</strong></td>
                <td>Troubleshooting, policies, professional responses</td>
            </tr>
        </table>
        <br>
        <p>✨ <strong>Get started:</strong> Configure your API key in the sidebar!</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Show current persona info
    st.markdown(f"""
    <div class="persona-info">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 3rem;">{current_persona['icon']}</div>
            <div>
                <h2 style="margin: 0;">{current_persona['name']}</h2>
                <p style="margin: 0; color: #666;">{current_persona['description']}</p>
            </div>
        </div>
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
                <strong>{current_persona['icon']} {current_persona['name']}</strong><br>
                {message["content"]}
                <div class="timer">🕐 {message.get("timestamp", "")}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Show welcome message if no messages
    if len(st.session_state.messages) == 0:
        st.markdown(f"""
        <div class="assistant-message">
            <strong>{current_persona['icon']} {current_persona['name']}</strong><br>
            {current_persona['welcome']}
        </div>
        """, unsafe_allow_html=True)
        st.session_state.messages.append({
            "role": "assistant",
            "content": current_persona['welcome'],
            "timestamp": datetime.now().strftime("%I:%M %p")
        })
    
    # Chat input
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        user_input = st.text_area(
            "💬 Type your message",
            placeholder=current_persona['placeholder'],
            key="user_input",
            label_visibility="collapsed",
            height=100
        )
        
        col_send, col_clear = st.columns(2)
        with col_send:
            if st.button("📤 Send Message", use_container_width=True, type="primary"):
                if user_input:
                    # Add user message
                    st.session_state.messages.append({
                        "role": "user",
                        "content": user_input,
                        "timestamp": datetime.now().strftime("%I:%M %p")
                    })
                    
                    # Get response
                    response, error = send_message(
                        user_input, 
                        st.session_state.api_key,
                        st.session_state.current_persona
                    )
                    
                    if response:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "timestamp": datetime.now().strftime("%I:%M %p")
                        })
                    else:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"⚠️ {error}. Please try again.",
                            "timestamp": datetime.now().strftime("%I:%M %p")
                        })
                    
                    st.rerun()
        
        with col_clear:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

# Footer
st.markdown(f"""
<div class="footer">
    <strong>🎭 AI Persona Assistant</strong><br>
    <small>Powered by DeepSeek AI | OpenRouter API</small><br>
    <small>🎬 Reel Creator | ✍️ Content Writer | 🎧 Customer Support</small>
</div>
""", unsafe_allow_html=True)

# Delivery possibility section (like in your image)
st.markdown("""
<div style="background-color: #fff3e0; padding: 0.75rem; border-radius: 0.5rem; margin-top: 1rem; border-left: 4px solid #ff9800;">
    <strong>📦 DELIVERY POSSIBILITY</strong><br>
    <small>All personas active • 24/7 availability • Average response: &lt; 30 seconds</small>
</div>
""", unsafe_allow_html=True)
