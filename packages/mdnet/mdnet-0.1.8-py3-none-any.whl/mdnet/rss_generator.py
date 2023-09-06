import os
import time
import json
import uuid
import pytz
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
from pathlib import Path

# Constants
GUID_STORAGE_FILE = 'resources/guids.json'

def get_stored_data():
    """Load stored GUIDs and timestamps from the JSON file."""
    try:
        with open(GUID_STORAGE_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    """Save the updated data to the JSON file."""
    # Ensure directory exists
    GUID_STORAGE_PATH = Path(GUID_STORAGE_FILE)
    GUID_STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(GUID_STORAGE_PATH, 'w') as file:
        json.dump(data, file, indent=4)

def generate_or_retrieve_guid(post, data):
    """Generate a new GUID for a post or retrieve a stored one."""
    if post['file'] in data:
        return data[post['file']].get('guid', str(uuid.uuid4()))  # Default to new UUID if not found
    new_guid = str(uuid.uuid4())
    data[post['file']] = {"guid": new_guid, "timestamp": None}  # Initialize with None
    return new_guid

def get_last_modified_time(filepath, preferred_timezone):
    """Return the last modification time of a file."""
    naive_datetime = datetime.utcfromtimestamp(os.path.getmtime(filepath))
    return naive_datetime.replace(tzinfo=timezone.utc).astimezone(preferred_timezone)

def generate_xml(config, posts):
    try:
        fg = FeedGenerator()
        fg.title(config['site_title'])
        fg.link(href=config['site_url'], rel='alternate')
        if 'site_description' in config:
            fg.description(config['site_description'])
        
        data = get_stored_data()
        
        # Get the preferred timezone from the config or default to UTC
        preferred_timezone_str = config.get('timezone', 'UTC')
        preferred_timezone = pytz.timezone(preferred_timezone_str)
        
        for post in posts:
            entry = fg.add_entry()
            entry.title(post['title'])
            entry.link(href=config['site_url'] + f"posts/{post['file']}")
            entry.guid(generate_or_retrieve_guid(post, data))
            entry.pubDate(post['date'].strftime('%a, %d %b %Y %H:%M:%S +0000'))
            entry.description(post['tldr'])
            
            # Check if the post content has been updated
            posts_dir = Path(config['output_dir']) / 'posts'
            last_mod_time = get_last_modified_time(posts_dir / post['file'], preferred_timezone)
            
            stored_timestamp_str = data[post['file']].get('timestamp')
            
            stored_time = datetime.fromisoformat(stored_timestamp_str) if stored_timestamp_str else None
            
            # Update the timestamp in the data
            data[post['file']]['timestamp'] = last_mod_time.strftime('%Y-%m-%dT%H:%M:%S')

        save_data(data) # Save the updated data
        fg.rss_file('public/resources/rss.xml', pretty=True)  # Save the XML to the public resources directory
    except Exception as e:
        print(f"Failed to generate RSS XML: {e}")