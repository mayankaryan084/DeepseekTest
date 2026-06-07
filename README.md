# DeepseekTest

A Streamlit-based AI chat assistant powered by OpenRouter API with support for multiple models including DeepSeek.

## Overview

This project provides a user-friendly interface for interacting with various AI models through the OpenRouter API. It includes comprehensive conversation tracking, execution statistics, and detailed run metrics.

## Features

### 💬 Chat Interface
- **Multiple AI Models**: Choose from 7+ different models including:
  - DeepSeek V4 Flash (Fast, 1M context window)
  - DeepSeek V3.2 (Strong reasoning, paid)
  - Llama 3.3 70B (Excellent all-rounder)
  - Gemini 2.0 Flash Lite (Fast responses)
  - Qwen 3 Next 80B (Technical & coding)
  - Microsoft Phi-4 Mini (Lightweight)
  - OpenRouter Auto-router (Free tier)

- **Conversation Memory**: The AI remembers your entire conversation for contextual responses
- **Adjustable Parameters**:
  - Temperature (Creativity): 0.0 - 1.0
  - Max Response Length: 100 - 4000 tokens

### 📊 Run Details & Execution Statistics

The application now includes comprehensive tracking of execution metrics:

#### Session-Level Statistics
- **Session Duration**: Total time elapsed since session start
- **API Calls**: Total number of API requests made
- **Average Response Time**: Mean response time across all requests
- **Total Messages**: Combined count of user and assistant messages
- **Total Tokens**: Estimated token usage throughout the session

#### Per-Request Metrics
- **Timestamp**: When each request was made (YYYY-MM-DD HH:MM:SS)
- **Model Used**: Which AI model was selected for the request
- **Input Length**: Character count of user message
- **Output Length**: Character count of assistant response
- **Response Time**: Individual request latency in seconds
- **Status**: Success/Error indicators

#### Request History Tracking
- **Successful Requests**: Count of successful API calls
- **Failed Requests**: Count of failed attempts
- **Slowest Request**: Identification of longest response time
- **Request Details Table**: Last 10 requests with full metrics

### 🔒 Privacy & Security
- Your API key is stored only in your browser session
- No data is saved to disk or logs
- Secure password input for API key

### 💾 Export Functionality
Export your conversation with:
- Full message history
- Complete run history with all metrics
- Session statistics
- File format: JSON

## Getting Started

### Prerequisites
- Python 3.8+
- Streamlit
- requests library
- OpenRouter API key (get it at https://openrouter.ai/keys)

### Installation

```bash
# Clone the repository
git clone https://github.com/mayankaryan084/DeepseekTest.git
cd DeepseekTest

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run adya.py
```

The app will open in your browser at `http://localhost:8501`

### Setup Instructions

1. Go to https://openrouter.ai/keys
2. Sign up or log in to your account
3. Create a new API key
4. Copy the key (starts with `sk-or-v1-`)
5. Paste it in the sidebar of the Streamlit app
6. Click "Save & Test" to validate the key

## Project Structure

```
DeepseekTest/
├── adya.py              # Main Streamlit application
├── README.md            # Project documentation
└── requirements.txt     # Python dependencies
```

## Usage Tips

### Monitoring Performance
- Use the "Run Details" tab to monitor:
  - Response times for each request
  - Success/failure rates
  - Session duration
  - Token usage estimation

### Optimizing Responses
- Adjust temperature lower (0.0-0.3) for focused, deterministic responses
- Set temperature higher (0.7-1.0) for creative, varied outputs
- Reduce max tokens for faster responses
- Increase max tokens for more detailed answers

### Exporting Conversations
- Click "Export Conversation" to download:
  - All messages in JSON format
  - Complete execution history
  - Session statistics
  - Useful for analysis or record-keeping

## API Configuration

- **Base URL**: https://openrouter.ai/api/v1/chat/completions
- **Authentication**: Bearer token (your API key)
- **Timeout**: 30 seconds per request
- **Test Timeout**: 10 seconds for key validation

## Statistics Metrics Explained

### Response Time (seconds)
- Measures the latency of each API call
- Includes network time + API processing time
- Helps identify slow requests or network issues

### Token Estimation
- Rough estimate based on word count
- Actual token usage may vary by model
- Used for tracking resource consumption

### Success Rate
- Tracks both successful responses and errors
- Helps diagnose connectivity or authentication issues
- Can be used to optimize API key management

## Troubleshooting

### API Key Issues
- Ensure key starts with `sk-or-v1-`
- Check that key is active at https://openrouter.ai/keys
- Try clicking "Save & Test" again

### Slow Responses
- Check your internet connection
- Monitor average response time in Run Details
- Consider using a faster model (Flash versions)
- Reduce max tokens

### Connection Errors
- Verify internet connectivity
- Check if OpenRouter API is accessible
- Ensure API key hasn't expired
- Try clearing conversation and restarting

## Contributing

Feel free to add your contributions and improvements to this project:
- Report issues
- Suggest new features
- Submit pull requests
- Improve documentation

## License

Add your license information here.

## Author

Created by mayankaryan084

## Support

For issues with the application, check:
1. OpenRouter API status: https://openrouter.ai
2. API key validity: https://openrouter.ai/keys
3. Internet connectivity
4. Streamlit documentation: https://docs.streamlit.io
