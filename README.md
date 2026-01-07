# LangGraph Chatbot with Streamlit

A conversational AI chatbot built with LangGraph and Streamlit that supports multiple tools including web search, calculator, and stock price lookup.

## Features

- 🤖 **AI Chatbot**: Powered by OpenAI's GPT models
- 🔍 **Web Search**: DuckDuckGo search integration
- 🧮 **Calculator**: Basic arithmetic operations
- 📈 **Stock Prices**: Real-time stock price lookup via Alpha Vantage
- 💬 **Multi-threaded Conversations**: Separate conversation threads with persistent history
- 💾 **SQLite Persistence**: Conversations are saved in a local database

## Local Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Get your OpenAI API key from: https://platform.openai.com/api-keys

### 3. Run the Application

```bash
streamlit run frontend.py
```

The app will open in your browser at `http://localhost:8501`

## Deployment to Streamlit Community Cloud

### Step 1: Push to GitHub

1. Initialize a git repository (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Create a new repository on GitHub (don't initialize with README)

3. Push your code:
   ```bash
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Streamlit Cloud

1. Go to [Streamlit Community Cloud](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository and branch
5. Set the main file path to: `frontend.py`
6. Click "Deploy"

### Step 3: Add Secrets

1. In your Streamlit Cloud app dashboard, click "Settings" (⚙️)
2. Go to "Secrets" tab
3. Add your OpenAI API key:

```toml
OPENAI_API_KEY = "your_openai_api_key_here"
```

4. Click "Save" - your app will automatically redeploy

## Project Structure

```
.
├── frontend.py          # Streamlit UI and chat interface
├── backend.py           # LangGraph chatbot logic and tools
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (local only, not in git)
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## How It Works

### Backend (`backend.py`)
- Defines a LangGraph state machine with chat and tool nodes
- Implements three tools: DuckDuckGo search, calculator, and stock price lookup
- Uses SQLite for conversation persistence
- Routes between LLM responses and tool calls automatically

### Frontend (`frontend.py`)
- Streamlit-based chat interface
- Manages multiple conversation threads
- Streams AI responses in real-time
- Shows tool usage status when tools are invoked

## Usage

1. **Start a new chat**: Click "New Chat" in the sidebar
2. **Switch conversations**: Click on any previous chat in the sidebar
3. **Ask questions**: The chatbot can:
   - Answer general questions
   - Search the web for recent information
   - Perform calculations
   - Look up stock prices

## Example Queries

- "What's the weather like today?" (uses web search)
- "Calculate 25 * 17" (uses calculator)
- "What's the stock price of AAPL?" (uses stock tool)
- "Tell me about LangGraph" (general conversation)

## Notes

- The database file (`chatbot.db`) is created automatically
- Each conversation thread has a unique ID
- Chat titles are generated from the first user message
- Tool usage is indicated with a status indicator in the UI

## Troubleshooting

- **API Key Error**: Make sure your `OPENAI_API_KEY` is set correctly in `.env` (local) or Streamlit secrets (cloud)
- **Import Errors**: Ensure all dependencies are installed: `pip install -r requirements.txt`
- **Database Issues**: Delete `chatbot.db` to reset all conversations

## License

This project is for educational purposes.

