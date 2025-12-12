# Cursor Clone - AI Integration Guide

This guide explains how to set up and connect your own AI server to the Cursor Clone application.

## Architecture Overview

The Cursor Clone consists of three main components:

1. **Frontend (React)** - Code editor UI with Monaco Editor
2. **Backend (Node.js/Express)** - tRPC API server
3. **AI Server (Python/Your Choice)** - Custom AI implementation

```
┌─────────────────┐
│  Frontend       │
│  (React)        │
└────────┬────────┘
         │ HTTP/tRPC
┌────────▼────────┐
│  Backend        │
│  (Node.js)      │
└────────┬────────┘
         │ HTTP
┌────────▼────────┐
│  AI Server      │
│  (Python/etc)   │
└─────────────────┘
```

## Quick Start

### 1. Start the Sample AI Server (for testing)

The project includes a sample Python AI server for demonstration:

```bash
# Install Flask
pip install flask

# Run the sample AI server
python3 server/sample_ai_server.py
```

The server will start on `http://localhost:5000`

### 2. Configure the Backend

Set the AI server URL in your environment:

```bash
# In your .env file or environment variables
AI_SERVER_URL=http://localhost:5000
AI_SERVER_API_KEY=your-optional-api-key
AI_MODEL=gpt-4
```

### 3. Start the Cursor Clone

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev
```

Visit `http://localhost:3000` in your browser.

## Using Your Own AI Server

### Option 1: Python-Based AI Server

The `server/ai_wrapper.py` module provides a Python interface for communicating with your AI server.

#### Example: OpenAI Integration

```python
#!/usr/bin/env python3
import os
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

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

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(port=5000)
```

#### Example: Local LLM (Ollama)

```python
#!/usr/bin/env python3
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434"

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

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(port=5000)
```

#### Example: Anthropic Claude

```python
#!/usr/bin/env python3
import os
from flask import Flask, request, jsonify
import anthropic

app = Flask(__name__)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

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

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(port=5000)
```

### Option 2: Node.js/Express AI Server

If you prefer to keep everything in Node.js:

```typescript
// ai-server.ts
import express from "express";
import { invokeLLM } from "./llm-helper"; // Your LLM integration

const app = express();
app.use(express.json());

app.post("/chat", async (req, res) => {
  try {
    const { message, context } = req.body;
    
    const response = await invokeLLM({
      messages: [
        { role: "system", content: "You are a helpful coding assistant." },
        { role: "user", content: message }
      ]
    });
    
    res.json({
      content: response.choices[0].message.content,
      model: "gpt-4",
      tokens_used: response.usage.total_tokens
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get("/health", (req, res) => {
  res.json({ status: "healthy" });
});

app.listen(5000, () => {
  console.log("AI Server running on port 5000");
});
```

### Option 3: Direct Integration (No Separate Server)

If you want to integrate AI directly into the backend without a separate server, modify the tRPC router:

```typescript
// server/routers/ai.ts
import { invokeLLM } from "./_core/llm";

export const aiRouter = router({
  chat: publicProcedure.input(chatSchema).mutation(async ({ input }) => {
    try {
      const response = await invokeLLM({
        messages: [
          { role: "system", content: "You are a helpful coding assistant." },
          { role: "user", content: input.message }
        ]
      });
      
      return {
        success: true,
        response: response.choices[0].message.content,
        model: "gpt-4"
      };
    } catch (error) {
      return {
        success: false,
        response: `Error: ${error.message}`,
        model: "unknown"
      };
    }
  })
});
```

## API Endpoints

Your AI server should implement these endpoints:

### POST /chat
Send a message to the AI.

**Request:**
```json
{
  "message": "How do I optimize this code?",
  "context": "Optional context about the code",
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

### POST /complete
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

### POST /explain
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

### POST /refactor
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

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model": "gpt-4"
}
```

## Frontend Usage

The frontend communicates with the AI through the tRPC API:

```typescript
// In React components
const { mutate: sendMessage } = trpc.ai.chat.useMutation();

sendMessage(
  { message: "How do I optimize this code?" },
  {
    onSuccess: (response) => {
      console.log("AI Response:", response.response);
    }
  }
);
```

## Keyboard Shortcuts

- **Ctrl+L** (or Cmd+L on Mac) - Open AI chat with selected code
- **Ctrl+K** - Open command palette
- **Shift+Enter** - New line in chat input
- **Enter** - Send message

## Environment Variables

Configure these in your `.env` file:

```bash
# AI Server Configuration
AI_SERVER_URL=http://localhost:5000
AI_SERVER_API_KEY=your-api-key-here
AI_MODEL=gpt-4

# Optional: Python wrapper settings
AI_SERVER_TIMEOUT=30
```

## Troubleshooting

### "AI server is not reachable"

1. Check if your AI server is running: `curl http://localhost:5000/health`
2. Verify the `AI_SERVER_URL` environment variable is correct
3. Check firewall settings
4. Look at server logs for errors

### "Invalid JSON response from AI server"

1. Ensure your server returns valid JSON
2. Check the response format matches the expected schema
3. Look at network requests in browser DevTools

### "Timeout waiting for AI server"

1. Increase `AI_SERVER_TIMEOUT` environment variable
2. Check if your AI model is slow
3. Monitor server performance

## Production Deployment

For production deployment:

1. **Use a proper AI provider** - OpenAI, Anthropic, or self-hosted LLM
2. **Add authentication** - Use API keys for your AI server
3. **Implement rate limiting** - Prevent abuse
4. **Add monitoring** - Track API usage and errors
5. **Use HTTPS** - Encrypt all communication
6. **Cache responses** - Reduce API calls
7. **Add error handling** - Graceful degradation

Example production setup:

```bash
# Production environment variables
AI_SERVER_URL=https://your-ai-server.com
AI_SERVER_API_KEY=sk-your-secret-key
AI_MODEL=gpt-4-turbo
AI_SERVER_TIMEOUT=60

# Enable rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

## Support

For issues or questions:

1. Check the sample AI server implementation
2. Review the tRPC router code
3. Test your AI server with curl
4. Check browser console for errors
5. Review server logs

## Next Steps

1. Choose your AI provider (OpenAI, Claude, local LLM, etc.)
2. Implement the AI server with the required endpoints
3. Set the `AI_SERVER_URL` environment variable
4. Test the integration in the Cursor Clone UI
5. Customize the AI prompts and behavior as needed
