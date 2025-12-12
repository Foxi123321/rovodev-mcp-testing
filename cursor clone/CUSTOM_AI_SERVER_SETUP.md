# Custom AI Server Setup Guide

This guide explains how to connect your own AI server to the Cursor Clone application.

## Quick Start

1. **Open Settings** - Click the "Settings" button in the bottom-right corner of the editor
2. **Enter Server URL** - Set your AI server URL (e.g., `http://localhost:5000`)
3. **Test Connection** - Click "Test Connection" to verify it works
4. **Save Settings** - Your settings are automatically saved to browser localStorage

## Your AI Server Requirements

Your AI server must implement the following HTTP endpoints:

### 1. Health Check Endpoint

**GET /health**

Verify your server is running and healthy.

```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "model": "gpt-4"
}
```

### 2. Chat Endpoint

**POST /chat**

Send a message and get a response.

**Request:**
```json
{
  "message": "How do I optimize this code?",
  "context": "Optional code context",
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 2048
}
```

**Response:**
```json
{
  "content": "Here's how to optimize your code...",
  "model": "gpt-4",
  "tokens_used": 150
}
```

### 3. Code Completion Endpoint (Optional)

**POST /complete**

Get code completion suggestions.

**Request:**
```json
{
  "code": "function hello() {",
  "language": "typescript",
  "context": "Optional context"
}
```

**Response:**
```json
{
  "content": "console.log('Hello, World!');",
  "model": "gpt-4",
  "tokens_used": 50
}
```

### 4. Code Explanation Endpoint (Optional)

**POST /explain**

Explain code.

**Request:**
```json
{
  "code": "const arr = [1, 2, 3].map(x => x * 2);",
  "language": "typescript"
}
```

**Response:**
```json
{
  "content": "This code creates an array of doubled numbers...",
  "model": "gpt-4",
  "tokens_used": 75
}
```

### 5. Refactoring Endpoint (Optional)

**POST /refactor**

Get refactoring suggestions.

**Request:**
```json
{
  "code": "for (let i = 0; i < arr.length; i++) { ... }",
  "language": "typescript",
  "suggestions": "Make it more functional"
}
```

**Response:**
```json
{
  "content": "Here's a more functional approach: arr.forEach(...)",
  "model": "gpt-4",
  "tokens_used": 100
}
```

## Example Implementations

### Python Flask Server

```python
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)
openai.api_key = "your-api-key"

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "model": "gpt-4"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message")
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful coding assistant."},
            {"role": "user", "content": message}
        ]
    )
    
    return jsonify({
        "content": response.choices[0].message.content,
        "model": "gpt-4",
        "tokens_used": response.usage.total_tokens
    })

if __name__ == "__main__":
    app.run(port=5000)
```

### Node.js Express Server

```typescript
import express from "express";
import OpenAI from "openai";

const app = express();
app.use(express.json());

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

app.get("/health", (req, res) => {
  res.json({ status: "healthy", model: "gpt-4" });
});

app.post("/chat", async (req, res) => {
  try {
    const { message } = req.body;

    const response = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        { role: "system", content: "You are a helpful coding assistant." },
        { role: "user", content: message },
      ],
    });

    res.json({
      content: response.choices[0].message.content,
      model: "gpt-4",
      tokens_used: response.usage?.total_tokens || 0,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(5000, () => {
  console.log("AI Server running on port 5000");
});
```

### Using Ollama (Local LLM)

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
OLLAMA_URL = "http://localhost:11434"

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "model": "mistral"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message")
    
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": "mistral",
            "prompt": message,
            "stream": False
        }
    )
    
    return jsonify({
        "content": response.json()["response"],
        "model": "mistral",
        "tokens_used": 0
    })

if __name__ == "__main__":
    app.run(port=5000)
```

### Using Anthropic Claude

```python
from flask import Flask, request, jsonify
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic(api_key="your-api-key")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "model": "claude-3-opus"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message")
    
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": message}
        ]
    )
    
    return jsonify({
        "content": response.content[0].text,
        "model": "claude-3-opus",
        "tokens_used": response.usage.output_tokens
    })

if __name__ == "__main__":
    app.run(port=5000)
```

## Configuration Options

In the Settings panel, you can configure:

| Setting | Description | Default |
|---------|-------------|---------|
| **Server URL** | Your AI server endpoint | `http://localhost:5000` |
| **API Key** | Optional authentication token | Empty |
| **Model** | Model name to use | `gpt-4` |
| **Temperature** | Response creativity (0.0-2.0) | `0.7` |
| **Max Tokens** | Maximum response length | `2048` |

## Environment Variables

You can also set environment variables for your server:

```bash
# Server Configuration
AI_SERVER_URL=http://localhost:5000
AI_SERVER_API_KEY=your-api-key
AI_MODEL=gpt-4
AI_SERVER_TIMEOUT=30
```

## Testing Your Server

### Test Health Endpoint

```bash
curl http://localhost:5000/health
```

### Test Chat Endpoint

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "model": "gpt-4"
  }'
```

### With Authentication

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "message": "Hello, how are you?",
    "model": "gpt-4"
  }'
```

## Troubleshooting

### "Failed to connect to AI server"

1. Verify your server is running
2. Check the server URL is correct
3. Ensure there are no firewall issues
4. Check server logs for errors

### "Invalid JSON response"

1. Ensure your server returns valid JSON
2. Check the response format matches the expected schema
3. Verify Content-Type header is `application/json`

### "Timeout waiting for response"

1. Increase the timeout in settings
2. Check if your AI model is slow
3. Monitor server performance
4. Consider using a faster model

## Production Deployment

For production use:

1. **Use HTTPS** - Always use secure connections
2. **Add Authentication** - Use API keys or OAuth
3. **Rate Limiting** - Prevent abuse with rate limits
4. **Caching** - Cache common responses
5. **Monitoring** - Track API usage and errors
6. **Load Balancing** - Distribute requests across servers

## Support

If you need help setting up your AI server:

1. Check the sample implementations above
2. Review your server logs
3. Test endpoints with curl
4. Verify the response format matches the schema
5. Check browser console for error messages

## Next Steps

Once your server is set up:

1. Open the Cursor Clone application
2. Click "Settings" in the bottom-right corner
3. Enter your server URL
4. Click "Test Connection"
5. Start chatting with your AI!
