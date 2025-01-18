# Twitter Thread Extractor

A simple web application that allows you to extract text from Twitter/X threads. The application consists of a Flask backend and a clean HTML/JavaScript frontend.

## Features

- Extract text from Twitter/X threads by providing the thread URL
- View individual tweets or combined full text
- Clean and responsive user interface
- Copy full thread text with one click
- Rate limit handling and automatic retries
- No browser extension required

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Twitter API credentials (see below)

## Getting Twitter API Credentials

1. Go to the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Sign in with your Twitter account
3. Create a new project:
   - Click "Add Project"
   - Give it a name (e.g., "Thread Extractor")
   - Select "Development" as the environment
   - Click "Next"

4. Create a new app within the project:
   - Click "Add App"
   - Give it a name
   - Copy and save the following credentials:
     - API Key (Consumer Key)
     - API Key Secret (Consumer Secret)

5. Generate Bearer Token:
   - Go to "Keys and Tokens" tab
   - Under "Authentication Tokens", find "Bearer Token"
   - Click "Generate" if not already generated
   - Copy and save the Bearer Token

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd threadextractor
```

2. Create and activate a Python virtual environment:

On Linux/macOS:
```bash
# Create the virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

On Windows:
```bash
# Create the virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your Twitter API credentials
nano .env  # or use any text editor
```

Fill in your Twitter API credentials in the `.env` file:
```
TWITTER_BEARER_TOKEN=your_bearer_token_here
API_KEY=your_api_key_here
API_SECRET_KEY=your_api_secret_key_here
```

## Quick Start

1. Make sure your virtual environment is activated (see Installation step 2)

2. Start the Flask backend:
```bash
python app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

4. Paste a Twitter/X thread URL into the input field and click "Extract Thread"

## How It Works

The application uses:
- Flask for the backend API
- Twitter's official API v2 for fetching tweets
- Tweepy for Twitter API integration
- Simple HTML/CSS/JavaScript for the frontend

## Project Structure

```
threadextractor/
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
├── app.py             # Flask backend
├── index.html         # Frontend interface
├── .env.example       # Example environment variables
└── .gitignore         # Git ignore rules
```

## Rate Limits

The application includes built-in rate limit handling:
- Automatic retries when rate limits are hit
- Exponential backoff for failed requests
- User-friendly error messages
- Minimum delay between requests

## Notes

- The application uses Twitter's official API v2
- Make sure to keep your API credentials secure
- Don't commit the `.env` file to version control
- For production use, consider implementing additional security measures

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 