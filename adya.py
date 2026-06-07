import streamlit as st
import requests
import json
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="AI Persona Assistant - DeepSeek",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: white;
        padding: 1rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #4caf50;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .config-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        border: 1px solid #e0e0e0;
    }
    .welcome-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    .footer {
        background-color: #1a1a2e;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        margin-top: 2rem;
    }
    .persona-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    .delivery-section {
        background-color: #fff3e0;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
        border-left: 4px solid #ff9800;
    }
</style>
""", unsafe_allow_html=True)

# ==================== PERSONA DEFINITIONS ====================

PERSONAS = {
    "reel_creator": {
        "name": "🎬 Content Creator - Reel Specialist",
        "dropdown_name": "🎬 Reel Creator - Viral Content Expert",
        "icon": "🎬",
        "emoji": "📱",
        "description": "Expert in creating viral reel content, trends, hooks, and engagement strategies",
        "temperature": 0.8,
        "system_prompt": """You are a professional Content Creator specializing in Reels and Short-form video content.

**Your Expertise:**
- Viral reel concepts and trending challenges
- Hook strategies for first 3 seconds
- Caption writing for maximum engagement
- Hashtag research and strategy
- Transition and editing ideas
- Platform-specific advice (Instagram, TikTok, YouTube Shorts)
- Sound and music selection
- Engagement optimization

**Response Guidelines:**
1. Always provide specific, actionable advice (not generic tips)
2. Include real examples of successful reels
3. Break down complex concepts into simple steps
4. Suggest specific trending audio and hashtags
5. Be enthusiastic and creative
6. Ask clarifying questions about niche, platform, goals
7. Format with emojis for better readability

**Never say "try again" - instead provide specific alternatives and improvements.**"""
    },
    "content_writer": {
        "name": "✍️ Content Writer",
        "dropdown_name": "✍️ Content Writer - SEO & Copywriting",
        "icon": "✍️",
        "emoji": "📝",
        "description": "Expert in writing, editing, SEO, and content strategy for all formats",
        "temperature": 0.7,
        "system_prompt": """You are a professional Content Writer and Editor.

**Your Expertise:**
- Blog post writing and structuring
- SEO optimization techniques (keywords, meta descriptions, headers)
- Copywriting for marketing and sales
- Email newsletters and sequences
- Social media captions
- Proofreading and editing
- Tone adaptation (formal, casual, humorous, professional)
- Storytelling techniques
- Headline writing (click-worthy titles)

**Response Guidelines:**
1. Provide clear, well-structured writing advice
2. Offer specific examples and templates
3. Explain the reasoning behind suggestions
4. Adapt tone based on target audience
5. Include SEO tips when relevant
6. Use proper formatting with headings and bullet points

**Never say "try again" - instead provide rewritten examples and specific improvements.**"""
    },
    "customer_support": {
        "name": "🎧 Customer Support Agent",
        "dropdown_name": "🎧 Customer Support - Problem Solver",
        "icon": "🎧",
        "emoji": "💬",
        "description": "Professional support that provides actual solutions, not generic responses",
        "temperature": 0.4,  # Lower for consistent, accurate support
        "system_prompt": """You are a professional Customer Support Agent who provides ACTUAL SOLUTIONS, not generic "try again" advice.

**Your Core Principle: NEVER say "try again" or "check your connection" without providing SPECIFIC, ACTIONABLE solutions.**

**Your Expertise:**
- Technical troubleshooting with step-by-step solutions
- Product feature explanations
- Account management (password reset, login issues)
- Billing and refund processes
- Shipping and delivery tracking
- Complaint resolution
- Service outage handling

**Response Format - ALWAYS follow this structure:**

1. **ACKNOWLEDGE** the issue with empathy
2. **DIAGNOSE** - Ask 1-2 specific clarifying questions
3. **SOLUTION** - Provide numbered, step-by-step instructions:
   - Step 1: [specific action]
   - Step 2: [specific action]
   - Step 3: [specific action]
4. **ALTERNATIVE** - If step 1 doesn't work, provide Plan B
5. **PREVENTION** - How to avoid this issue in the future

**Example of GOOD response:**
"🔧 **Internet Connection Fix**
1. Open Command Prompt as Admin
2. Type: `ipconfig /release` then Enter
3. Type: `ipconfig /renew` then Enter
4. Type: `ipconfig /flushdns` then Enter
5. Restart your browser

If this doesn't work, try:
- Use Ethernet cable instead of WiFi
- Contact your ISP at [number] with error code: [code]

**For future:** Update network drivers from [manufacturer website]"

**Example of BAD response (DO NOT USE):**
"Please try again later or check your connection" ← NEVER use this.

**Remember:** Every response must contain a SPECIFIC, ACTIONABLE solution. If you don't know, say "I need more information" and ask specific questions."""
    }
}

# API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_persona' not in st.session_state:
    st.session_state.current_persona = "customer_support"

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
        "max_tokens": 5
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=10)
        return response.status_code == 200
    except:
        return False

def send_message(message, api_key, persona_key, chat_history):
    """Send message with selected persona - guaranteed to provide solutions"""
    
    persona = PERSONAS[persona_key]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ai-persona-assistant.streamlit.app",
        "X-Title": f"AI Persona - {persona['name']}"
    }
    
    # Build messages with system prompt
    messages = [
        {"role": "system", "content": persona["system_prompt"]}
    ]
    
    # Add last 15 messages for context
    for msg in chat_history[-15:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": message})
    
    data = {
        "model": "openrouter/free",
        "messages": messages,
        "temperature": persona["temperature"],
        "max_tokens": 1000,
        "top_p": 0.9
    }
    
    try:
        with st.spinner(f"{persona['icon']} {persona['name']} is responding..."):
            response = requests.post(API_URL, headers=headers, json=data, timeout=35)
        
        if response.status_code == 200:
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            return assistant_message, None
            
        elif response.status_code == 401:
            return None, "❌ **Authentication Failed**\n\nYour API key is invalid. Please go to [OpenRouter Keys](https://openrouter.ai/keys) and create a new key."
            
        elif response.status_code == 429:
            return None, "⏳ **Rate Limit Exceeded**\n\nThe API is busy. Please wait 30 seconds and try again."
            
        elif response.status_code == 402:
            return None, "💰 **Insufficient Credits**\n\nPlease add credits at [openrouter.ai/credits](https://openrouter.ai/credits)"
            
        else:
            return None, f"⚠️ **Error {response.status_code}**\n\n```\n{response.text[:300]}\n```"
            
    except requests.exceptions.Timeout:
        return None, "⏰ **Request Timeout**\n\nPlease try again with a shorter message."
    except Exception as e:
        return None, f"❌ **Error:** {str(e)}"

# ==================== MAIN UI ====================

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 2rem; text-align: center; color: white;">
    <h1>🤖 AI Persona Assistant</h1>
    <p>Powered by DeepSeek | Choose your specialized AI expert</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎭 Select AI Persona")
    st.markdown("---")
    
    # Dropdown for persona selection
    persona_options = list(PERSONAS.keys())
    persona_labels = [PERSONAS[p]["dropdown_name"] for p in persona_options]
    
    selected_persona_key = st.selectbox(
        "Choose your AI assistant:",
        options=persona_options,
        format_func=lambda x: PERSONAS[x]["dropdown_name"],
        index=persona_options.index(st.session_state.current_persona)
    )
    
    # Update persona if changed
    if selected_persona_key != st.session_state.current_persona:
        st.session_state.current_persona = selected_persona_key
        st.session_state.messages = []
        st.rerun()
    
    # Show current persona info
    current = PERSONAS[st.session_state.current_persona]
    st.markdown(f"""
    <div class="persona-card">
        <h2>{current['icon']}</h2>
        <h4>{current['name']}</h4>
        <p style="font-size: 0.85rem;">{current['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # API Configuration
    st.markdown("### 🔑 API Configuration")
    
    if not st.session_state.api_key_valid:
        api_key_input = st.text_input(
            "OpenRouter API Key",
            type="password",
            placeholder="sk-or-v1-...",
            help="Get your key from openrouter.ai/keys"
        )
        
        if st.button("✅ Connect", use_container_width=True):
            if not api_key_input:
                st.error("Please enter an API key")
            elif not validate_api_key(api_key_input):
                st.error("❌ Invalid format. Key must start with 'sk-or-v1-'")
            else:
                with st.spinner("Testing API key..."):
                    if test_api_key(api_key_input):
                        st.session_state.api_key = api_key_input
                        st.session_state.api_key_valid = True
                        st.success("✅ Connected!")
                        st.rerun()
                    else:
                        st.error("❌ API key test failed")
        
        st.markdown("[🔗 Get API Key](https://openrouter.ai/keys)")
    else:
        st.success("✅ API Key Connected")
        if st.button("🔄 Change API Key", use_container_width=True):
            st.session_state.api_key = None
            st.session_state.api_key_valid = False
            st.session_state.messages = []
            st.rerun()
    
    st.markdown("---")
    
    if st.session_state.api_key_valid:
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.metric("💬 Messages", len(st.session_state.messages))

# Main content area
if not st.session_state.api_key_valid:
    st.markdown("""
    <div class="welcome-box">
        <h2>👋 Welcome to AI Persona Assistant!</h2>
        <p>Enter your OpenRouter API key in the sidebar to start chatting with specialized AI experts.</p>
        <br>
        <h3>🎭 Available Personas:</h3>
        <table style="width: 100%; text-align: left; margin: 1rem 0;">
            <tr><td>🎬</td><td><strong>Reel Creator</strong></td><td>Viral content, trends, hooks, editing tips</td></tr>
            <tr><td>✍️</td><td><strong>Content Writer</strong></td><td>Blogs, SEO, copywriting, editing</td></tr>
            <tr><td>🎧</td><td><strong>Customer Support</strong></td><td>Actual solutions, step-by-step fixes, no generic advice</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
else:
    # Chat interface
    current = PERSONAS[st.session_state.current_persona]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            st.caption(f"🕐 {message.get('timestamp', '')}")
    
    # Welcome message if no history
    if len(st.session_state.messages) == 0:
        welcome_messages = {
            "reel_creator": "Hey creator! 🎬 Ready to make some viral content? Ask me about trending sounds, hook strategies, or editing tips!",
            "content_writer": "Welcome to your Writing Assistant! ✍️ Need help with blog posts, SEO, or copywriting? I've got you covered!",
            "customer_support": "Hello! I'm your Customer Support Agent. 🎧 I provide **actual solutions**, not generic advice. Describe your issue and I'll give you step-by-step fixes!"
        }
        with st.chat_message("assistant"):
            st.markdown(welcome_messages[st.session_state.current_persona])
            st.caption(f"{current['icon']} {current['name']}")
        st.session_state.messages.append({
            "role": "assistant",
            "content": welcome_messages[st.session_state.current_persona],
            "timestamp": datetime.now().strftime("%I:%M %p")
        })
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().strftime("%I:%M %p")
        })
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response
        response, error = send_message(
            prompt,
            st.session_state.api_key,
            st.session_state.current_persona,
            st.session_state.messages[:-1]
        )
        
        with st.chat_message("assistant"):
            if response:
                st.markdown(response)
                st.caption(f"{current['icon']} {current['name']}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
            else:
                st.error(error)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"⚠️ {error}",
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })

# Footer
st.markdown("""
<div class="delivery-section">
    <strong>📦 DELIVERY POSSIBILITY</strong><br>
    <small>All personas active • 24/7 availability • Customer Support provides ACTUAL solutions</small>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    <strong>🤖 AI Persona Assistant</strong><br>
    <small>Powered by DeepSeek | OpenRouter API</small>
</div>
""", unsafe_allow_html=True)
