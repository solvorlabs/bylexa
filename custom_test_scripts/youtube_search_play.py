from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def search_and_play_youtube(query):
    # Initialize the WebDriver (Make sure to use the path to your WebDriver if not in PATH)
    driver = webdriver.Chrome()  # Change to webdriver.Firefox() if using Firefox

    try:
        # Navigate to YouTube
        driver.get("https://www.youtube.com")
        
        # Wait for the page to load
        time.sleep(2)

        # Find the search bar and enter the query
        search_box = driver.find_element(By.NAME, "search_query")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        # Wait for the search results to load
        time.sleep(2)

        # Click on the first video link
        first_video = driver.find_elements(By.ID, "video-title")[0]
        first_video.click()

        # Optionally, you can keep the video playing for a specified time or indefinitely
        time.sleep(10)  # Let the video play for 10 seconds before closing

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the browser
        driver.quit()

# Example usage
search_and_play_youtube("lofi hip hop beats")
