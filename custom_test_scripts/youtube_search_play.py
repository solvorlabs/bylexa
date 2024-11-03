from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import argparse
import sys

def search_and_play_youtube(query, duration=10, headless=False):
    """
    Search and play a YouTube video.
    
    Args:
        query (str): Search query for YouTube
        duration (int): How long to play the video in seconds
        headless (bool): Whether to run browser in headless mode
    """
    # Initialize Chrome options
    chrome_options = webdriver.ChromeOptions()
    if headless:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
    
    # Add additional arguments to prevent common errors
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-notifications')
    
    try:
        # Initialize the WebDriver with options
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)  # Set a standard window size
        
        # Navigate to YouTube
        print(f"Searching YouTube for: {query}")
        driver.get("https://www.youtube.com")
        
        # Wait for and find the search bar
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "search_query"))
        )
        
        # Perform the search
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        
        # Wait for and click the first video
        print("Waiting for search results...")
        first_video = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.ID, "video-title"))
        )[0]  # Get the second video (index 1) as it's often more reliable
        
        print("Playing video...")
        first_video.click()
        
        # Let the video play for specified duration
        print(f"Video will play for {duration} seconds")
        time.sleep(int(duration))
        
        return "Video played successfully"
        
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return f"Error: {str(e)}"
    finally:
        # Close the browser
        driver.quit()

def main():
    parser = argparse.ArgumentParser(description='Play YouTube videos from search query')
    parser.add_argument('--query', type=str, help='Search query for YouTube video', required=True)
    parser.add_argument('--duration', type=int, default=10, help='Duration to play video in seconds')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    
    # Parse command line arguments or parameter string
    if len(sys.argv) > 1:
        args = parser.parse_args()
    else:
        # Handle parameters passed as key=value pairs
        params = {}
        for arg in sys.argv[1:]:
            if '=' in arg:
                key, value = arg.split('=', 1)
                params[key.lstrip('-')] = value
        
        # Create a namespace object with the parameters
        class Args:
            pass
        args = Args()
        args.query = params.get('query', '')
        args.duration = int(params.get('duration', 10))
        args.headless = params.get('headless', 'false').lower() == 'true'
    
    if not args.query:
        print("Error: Query parameter is required", file=sys.stderr)
        return "Error: Query parameter is required"
    
    return search_and_play_youtube(args.query, args.duration, args.headless)

if __name__ == "__main__":
    main()