from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import tweepy
import os
import logging
from dotenv import load_dotenv
import time
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Twitter API credentials
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
API_KEY = os.getenv('API_KEY')
API_SECRET_KEY = os.getenv('API_SECRET_KEY')

# Initialize Twitter client with retry handler
class RetryClient(tweepy.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_request_time = 0
        self.min_time_between_requests = 1.1  # Minimum seconds between requests

    def request(self, *args, **kwargs):
        # Ensure minimum time between requests
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_time_between_requests:
            sleep_time = self.min_time_between_requests - time_since_last_request
            logger.info(f"Rate limiting: Sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

        # Try the request with retries
        max_retries = 3
        retry_delay = 2
        for attempt in range(max_retries):
            try:
                self.last_request_time = time.time()
                response = super().request(*args, **kwargs)
                return response
            except tweepy.TooManyRequests as e:
                reset_time = int(e.response.headers.get('x-rate-limit-reset', 0))
                wait_time = max(reset_time - int(time.time()), 0) + 1
                
                if attempt < max_retries - 1:  # Don't sleep on last attempt
                    logger.warning(f"Rate limit hit. Waiting {wait_time} seconds. Attempt {attempt + 1}/{max_retries}")
                    time.sleep(min(wait_time, 15))  # Wait at most 15 seconds
                    continue
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Request failed. Retrying in {retry_delay} seconds. Attempt {attempt + 1}/{max_retries}")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                raise

# Initialize Twitter client with retry handler
client = RetryClient(
    bearer_token=TWITTER_BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    wait_on_rate_limit=True
)

def extract_tweet_id(url):
    """Extract tweet ID from URL."""
    try:
        return url.split('status/')[-1].split('?')[0]
    except Exception as e:
        logger.error(f"Error extracting tweet ID: {str(e)}")
        return None

def get_conversation_thread(tweet_id):
    """Get the full conversation thread for a tweet."""
    try:
        logger.info(f"Fetching conversation for tweet ID: {tweet_id}")
        
        # Get the main tweet with expanded content
        tweet = client.get_tweet(
            tweet_id, 
            tweet_fields=['conversation_id', 'author_id', 'created_at', 'text'],
            expansions=['attachments.media_keys', 'referenced_tweets.id'],
            media_fields=['url', 'alt_text']
        )
        
        if not tweet.data:
            logger.warning("Main tweet not found")
            return {
                'individual_tweets': ["Tweet not found. Please check the URL."],
                'full_text': "Tweet not found. Please check the URL."
            }

        conversation_id = tweet.data.conversation_id
        author_id = tweet.data.author_id
        
        logger.info(f"Found conversation ID: {conversation_id}, author ID: {author_id}")

        # Add small delay between requests
        time.sleep(1)

        # Get all tweets in the conversation by the same author
        tweets = client.search_recent_tweets(
            query=f"conversation_id:{conversation_id} from:{author_id}",
            tweet_fields=['created_at', 'text'],
            expansions=['attachments.media_keys', 'referenced_tweets.id'],
            media_fields=['url', 'alt_text'],
            max_results=100
        )

        if not tweets.data:
            # If no additional tweets found, just return the main tweet
            thread_text = [tweet.data.text]
            return {
                'individual_tweets': thread_text,
                'full_text': tweet.data.text
            }

        # Sort tweets by creation time
        thread_tweets = sorted(tweets.data, key=lambda x: x.created_at)
        
        # Extract text from tweets
        thread_text = []
        full_text_parts = []
        
        # Add the main tweet if it's not in the search results
        main_tweet_text = tweet.data.text
        if main_tweet_text:
            thread_text.append(main_tweet_text)
            full_text_parts.append(main_tweet_text)
            logger.info(f"Added main tweet: {main_tweet_text[:100]}...")

        # Add the rest of the thread
        for tweet in thread_tweets:
            if tweet.text and tweet.id != tweet_id:  # Avoid duplicating the main tweet
                cleaned_text = tweet.text.strip()
                thread_text.append(cleaned_text)
                full_text_parts.append(cleaned_text)
                logger.info(f"Added tweet: {cleaned_text[:100]}...")

        # Create the full text version with proper formatting
        full_text = "\n\n".join(full_text_parts)
        
        logger.info(f"Successfully extracted {len(thread_text)} tweets")
        return {
            'individual_tweets': thread_text,
            'full_text': full_text
        }

    except tweepy.TooManyRequests as e:
        logger.error("Rate limit exceeded. Please try again later.")
        error_msg = "Rate limit exceeded. Please try again in a few minutes."
        return {
            'individual_tweets': [error_msg],
            'full_text': error_msg
        }
    except Exception as e:
        logger.error(f"Error getting conversation thread: {str(e)}")
        error_msg = f"Error: {str(e)}"
        return {
            'individual_tweets': [error_msg],
            'full_text': error_msg
        }

def extract_thread(url):
    """Extract thread from Twitter URL."""
    try:
        logger.info(f"Starting thread extraction for URL: {url}")
        
        # Extract tweet ID from URL
        tweet_id = extract_tweet_id(url)
        if not tweet_id:
            error_msg = "Invalid Twitter URL. Please check the format."
            return {
                'individual_tweets': [error_msg],
                'full_text': error_msg
            }
            
        # Get the conversation thread
        return get_conversation_thread(tweet_id)
        
    except Exception as e:
        logger.error(f"Error during thread extraction: {str(e)}")
        error_msg = f"Error: {str(e)}"
        return {
            'individual_tweets': [error_msg],
            'full_text': error_msg
        }

@app.route('/')
def home():
    logger.info("Serving home page")
    return app.send_static_file('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    logger.info("Received extraction request")
    data = request.get_json()
    logger.debug(f"Request data: {data}")
    
    url = data.get('url')
    if not url:
        logger.warning("No URL provided in request")
        return jsonify({'error': 'URL is required'}), 400
    
    if not TWITTER_BEARER_TOKEN:
        logger.error("Twitter Bearer Token not found")
        error_msg = "Error: Twitter API credentials not configured. Please set TWITTER_BEARER_TOKEN environment variable."
        return jsonify({
            'individual_tweets': [error_msg],
            'full_text': error_msg
        }), 500
    
    logger.info(f"Processing URL: {url}")
    thread_content = extract_thread(url)
    
    return jsonify(thread_content)

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(debug=True) 