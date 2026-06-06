import streamlit as st
import requests
import json
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="DeepSeek AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .api-key-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        color: white;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stButton button {
        width: 100%;
    }
    .model-selector {
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_count' not in st.session_state:
    st.session_state.conversation_count = 0
if 'total_tokens' not in st.session_state:
    st.session_state.total_tokens = 0
if 'current_model' not in st.session_state:
    st.session_state.current_model = "openrouter/free"
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False

# API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Available models
AVAILABLE_MODELS = {
    "openrouter/free": {
        "name": "🆓 OpenRouter Free (Auto-router)",
        "description": "Automatically routes to best free model",
        "context": "Variable",
        "free": True
    },
    "deepseek/deepseek-v4-flash:free": {
        "name": "⚡ DeepSeek V4 Flash",
        "description": "Fast responses, 1M context window",
        "context": "1M tokens",
        "free": True
    },
    "deepseek/deepseek-v3.2": {
        "name": "🧠 DeepSeek V3.2",
        "description": "Strong reasoning, 1M+ context",
        "context": "1M+ tokens",
        "free": False
    },
    "meta-llama/llama-3.3-70b-instruct:free": {
        "name": "🦙 Llama 3.3 70B",
        "description": "Excellent all-rounder",
        "context": "128K tokens",
        "free": True
    },
    "google/gemini-2.0-flash-lite-preview-02-05:free": {
        "name": "✨ Gemini 2.0 Flash Lite",
        "description": "Fast, good for quick answers",
        "context": "1M tokens",
        "free": True
    },
    "qwen/qwen3-next-80b-a3b-instruct:free": {
        "name": "🐉 Qwen 3 Next 80B",
        "description": "Strong technical & coding",
        "context": "128K tokens",
        "free": True
    },
    "microsoft/phi-4-mini-instruct:free": {
        "name": "🔬 Microsoft Phi-4 Mini",
        "description": "Lightweight but capable",
        "context": "128K tokens",
        "free": True
    }
}

def validate_api_key(api_key):
    """Validate OpenRouter API key format"""
    if not api_key:
        return False
    # OpenRouter API keys start with 'sk-or-v1-'
    pattern = r'^sk-or-v1-[a-zA-Z0-9]+$'
    return bool(re.match(pattern, api_key))

def test_api_key(api_key):
    """Test if API key works by making a simple request"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    data = {
        "model": "openrouter/free",
        "messages": [{"role": "user", "content": "Say 'API key works!'"}],
        "max_tokens": 20
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=10)
        return response.status_code == 200
    except:
        return False

def send_message(message, model, api_key, temperature=0.7, max_tokens=1000):
    """Send message to OpenRouter API"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://deepseek-chat-app.streamlit.app",
        "X-Title": "DeepSeek Streamlit App"
    }
    
    # Prepare messages (including history)
    messages = []
    for msg in st.session_state.messages:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        with st.spinner("🤔 Thinking..."):
            response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            
            # Estimate token usage (rough estimate)
            approx_tokens = len(message.split()) + len(assistant_message.split())
            st.session_state.total_tokens += approx_tokens
            
            return assistant_message, None
        else:
            error_msg = f"API Error: {response.status_code}\n```\n{response.text}\n```"
            return None, error_msg
            
    except requests.exceptions.Timeout:
        return None, "⏰ Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return None, "🔌 Connection failed. Check your internet."
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

# ==================== MAIN UI ====================

# Sidebar
with st.sidebar:
    st.title("🤖 DeepSeek Assistant")
    st.markdown("---")
    
    # API Key Input Section
    st.markdown("### 🔑 API Key Configuration")
    
    if not st.session_state.api_key_valid:
        st.markdown("""
        <div class="warning-message">
        ⚠️ Please enter your OpenRouter API key to start chatting
        </div>
        """, unsafe_allow_html=True)
        
        api_key_input = st.text_input(
            "OpenRouter API Key:",
            type="password",
            placeholder="sk-or-v1-...",
            help="Get your API key from https://openrouter.ai/keys"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Save & Test", use_container_width=True):
                if validate_api_key(api_key_input):
                    with st.spinner("Testing API key..."):
                        if test_api_key(api_key_input):
                            st.session_state.api_key = api_key_input
                            st.session_state.api_key_valid = True
                            st.success("✅ API key valid!")
                            st.rerun()
                        else:
                            st.error("❌ API key test failed. Check your key and try again.")
                else:
                    st.error("❌ Invalid API key format. Key should start with 'sk-or-v1-'")
        
        with col2:
            st.markdown(f"""
            <div style='font-size: 0.8rem; margin-top: 0.5rem;'>
            🔗 <a href='https://openrouter.ai/keys' target='_blank'>Get your key here</a>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.markdown("""
        <div class="success-message">
        ✅ API Key Connected
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Change API Key", use_container_width=True):
            st.session_state.api_key = None
            st.session_state.api_key_valid = False
            st.session_state.messages = []
            st.rerun()
    
    st.markdown("---")
    
    # Only show settings if API key is valid
    if st.session_state.api_key_valid:
        # Model Selection
        st.markdown("### 🎛️ Model Settings")
        
        selected_model_key = st.selectbox(
            "Choose AI Model:",
            options=list(AVAILABLE_MODELS.keys()),
            format_func=lambda x: AVAILABLE_MODELS[x]["name"],
            index=0
        )
        
        if selected_model_key != st.session_state.current_model:
            st.session_state.current_model = selected_model_key
            if st.session_state.messages:
                st.warning("⚠️ Model changed! Consider clearing conversation for best results.")
        
        # Show model details
        model_info = AVAILABLE_MODELS[selected_model_key]
        st.markdown(f"""
        <div class="model-selector">
            <small>
            📝 {model_info['description']}<br>
            📚 Context: {model_info['context']}<br>
            {'✅ Free' if model_info['free'] else '💰 Paid model'}
            </small>
        </div>
        """, unsafe_allow_html=True)
        
        # Temperature slider
        temperature = st.slider(
            "🎨 Creativity (Temperature):",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Lower = more focused, Higher = more creative"
        )
        
        # Max tokens
        max_tokens = st.number_input(
            "📝 Max Response Length:",
            min_value=100,
            max_value=4000,
            value=1000,
            step=100
        )
        
        st.markdown("---")
        
        # Stats
        st.markdown("### 📊 Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💬 Messages", len(st.session_state.messages) // 2)
        with col2:
            st.metric("🔤 Est. Tokens", st.session_state.total_tokens)
        
        st.markdown("---")
        
        # Actions
        st.markdown("### 🛠️ Actions")
        
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_count = 0
            st.rerun()
        
        if st.button("📤 Export Conversation", use_container_width=True):
            if st.session_state.messages:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_data = {
                    "timestamp": timestamp,
                    "model": st.session_state.current_model,
                    "messages": st.session_state.messages
                }
                st.download_button(
                    label="💾 Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"conversation_{timestamp}.json",
                    mime="application/json"
                )
            else:
                st.info("No conversation to export")
        
        # System info
        st.markdown("---")
        st.markdown("""
        <div style="font-size: 0.8rem; color: #666;">
        <b>ℹ️ About</b><br>
        Powered by OpenRouter API<br>
        Using DeepSeek & other LLMs<br>
        🔒 Your API key is stored only in session<br>
        and never saved to disk or logs
        </div>
        """, unsafe_allow_html=True)

# Main content area
st.title("💬 DeepSeek AI Chat Assistant")

if not st.session_state.api_key_valid:
    # Show welcome screen when no API key
    st.markdown("""
    <div class="api-key-container">
        <h2>👋 Welcome to DeepSeek AI Assistant!</h2>
        <p>To get started, please enter your OpenRouter API key in the sidebar.</p>
        <br>
        <h4>📝 How to get your API key:</h4>
        <ol>
            <li>Go to <a href="https://openrouter.ai/keys" style="color: white;" target="_blank">openrouter.ai/keys</a></li>
            <li>Sign up or log in to your account</li>
            <li>Create a new API key</li>
            <li>Copy the key (starts with <code>sk-or-v1-</code>)</li>
            <li>Paste it in the sidebar and click "Save & Test"</li>
        </ol>
        <br>
        <p>✨ <strong>It's free!</strong> Many models are available with free tiers.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show features
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🎨 **Multiple Models**\n\nChoose from 7+ different AI models including DeepSeek, Llama, Gemini, and more")
    with col2:
        st.info("💬 **Conversation Memory**\n\nThe AI remembers your entire conversation for contextual responses")
    with col3:
        st.info("🔒 **Privacy First**\n\nYour API key is only stored in your browser session and never saved")
    
else:
    # Show chat interface when API key is valid
    st.caption(f"Currently using: **{model_info['name']}** | {model_info['description']}")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "timestamp" in message:
                st.caption(f"🕐 {message['timestamp']}")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        response, error = send_message(
            prompt, 
            st.session_state.current_model, 
            st.session_state.api_key,
            temperature, 
            max_tokens
        )
        
        if response:
            # Add assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "model": st.session_state.current_model
            })
            
            # Display assistant message
            with st.chat_message("assistant"):
                st.markdown(response)
                st.caption(f"🤖 {model_info['name']}")
        else:
            # Display error
            with st.chat_message("assistant"):
                st.error(error)
            
            # Optionally add error to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ Error: {error}",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.8rem;'>"
    "Powered by OpenRouter API | DeepSeek Models | Built with Streamlit<br>"
    "🔒 Your API key is never stored - it exists only in your current browser session"
    "</div>",
    unsafe_allow_html=True
)