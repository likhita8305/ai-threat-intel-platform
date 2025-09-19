import requests
import feedparser
import time

# The URL of the API endpoints
API_URL = "http://127.0.0.1:8000/threats/"
RSS_FEED_URL = "https://feeds.feedburner.com/TheHackersNews"

def get_existing_threat_titles():
    """Fetches all threat titles currently in the database."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        # Return a 'set' for very fast lookups
        return {item['title'] for item in data}
    except requests.exceptions.RequestException as e:
        print(f"Could not connect to the API to get existing titles: {e}")
        return set()

def ingest_threats():
    """
    Fetches threats, checks against existing ones, and only sends new threats 
    for AI analysis to save API quota.
    """
    print("--- Starting Smart Ingestion Process ---")
    
    # 1. Get all titles we already have in our database
    existing_titles = get_existing_threat_titles()
    print(f"Found {len(existing_titles)} existing threats in the database.")
    
    # 2. Fetch the latest articles from the RSS feed
    print(f"Fetching latest threats from {RSS_FEED_URL}...")
    feed = feedparser.parse(RSS_FEED_URL)
    
    new_threats_found = 0
    # 3. Loop through the latest 10 articles and process only the new ones
    for entry in feed.entries[:10]: # Check the latest 10 articles
        if entry.title not in existing_titles:
            new_threats_found += 1
            print(f"\n✨ New threat found: '{entry.title}'. Sending for AI analysis...")
            
            threat_data = {
                "title": entry.title,
                "type": "News Article",
                "severity": "Medium",
                "source": "The Hacker News",
                "description": entry.summary
            }
            
            try:
                response = requests.post(API_URL, json=threat_data)
                if response.status_code == 200:
                    print(f"  -> Successfully ingested and analyzed.")
                else:
                    print(f"  -> Error ingesting: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Could not connect to the API: {e}")
                break
            
            # Pause to respect the API's rate limit per minute
            print("--- Pausing for 2 seconds ---")
            time.sleep(2)
        else:
            # This is the "caching" part in action!
            print(f"-> Skipping already existing threat: '{entry.title}'")

    if new_threats_found == 0:
        print("\nNo new threats found to ingest.")

if __name__ == "__main__":
    ingest_threats()
    print("\nSmart Ingestion complete.")

