import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import json

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode

# Initialize the Chrome driver
driver = webdriver.Chrome(options=chrome_options)

try:
    # Navigate to the URL
    url = 'https://snapshot.org/#/klimadao.eth/proposals'
    print(f"Navigating to {url}")
    driver.get(url)
    
    # Wait for the content to load
    print("Waiting for content to load...")
    wait = WebDriverWait(driver, 30)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='proposal/']")))
    
    # Function to check if KIP-1 is present
    def is_kip1_present():
        elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='proposal/']")
        for element in elements:
            text = element.text.strip()
            if 'KIP-1 ' in text or text == 'KIP-1':
                print("Found KIP-1!")
                return True
        return False
    
    # Scroll down until KIP-1 is found or no new content is loaded
    print("Scrolling to load all proposals...")
    scroll_pause_time = 2
    last_height = driver.execute_script("return document.body.scrollHeight")
    kip1_found = is_kip1_present()
    scroll_count = 0
    
    while not kip1_found:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait to load page
        time.sleep(scroll_pause_time)
        scroll_count += 1
        print(f"Scroll #{scroll_count} - Looking for KIP-1...")
        
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # Check if KIP-1 is now present
        kip1_found = is_kip1_present()
        
        # If heights are the same and KIP-1 is not found, it means we've reached the end
        if new_height == last_height and not kip1_found:
            print("Reached the end of content without finding KIP-1")
            break
            
        last_height = new_height
    
    # Now extract all the KIP proposals
    print("Extracting all KIP proposals...")
    proposals = []
    
    # Find all proposal elements
    proposal_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='proposal/']")
    
    kip_links = []
    for element in proposal_elements:
        text = element.text.strip()
        if text.startswith('KIP'):
            href = element.get_attribute('href')
            kip_links.append({'text': text, 'href': href})
            print(f"Found: {text} - {href}")
    
    # Now visit each proposal page and extract more details
    print("\nVisiting each proposal page to extract content and voting data...")
    
    detailed_proposals = []
    for i, proposal in enumerate(kip_links):
        try:
            print(f"\n[{i+1}/{len(kip_links)}] Processing: {proposal['text']}")
            
            # Visit proposal page
            driver.get(proposal['href'])
            time.sleep(3)  # Wait for page to load
            
            # Extract content from markdown body
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".markdown-body")))
            content_element = driver.find_element(By.CSS_SELECTOR, ".markdown-body.break-words.mb-4")
            content = content_element.text if content_element else ""
            
            # Look for votes - might be in various elements
            votes = 0
            try:
                votes_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'vote') or contains(text(), 'votes')]")
                for vote_elem in votes_elements:
                    vote_text = vote_elem.text
                    if 'vote' in vote_text.lower():
                        numbers = re.findall(r'\d+', vote_text)
                        if numbers:
                            votes = int(numbers[0])
                            break
            except Exception as e:
                print(f"Error extracting votes: {e}")
            
            # Extract voting options using the specific class pattern mentioned
            options = []
            try:
                # CSS selector for the specific class pattern identified
                option_selector = "div.flex.gap-2.border.rounded-lg.px-3.py-2\\.5.last\\:mb-0.text-skin-link.relative.overflow-hidden.items-center"
                option_elements = driver.find_elements(By.CSS_SELECTOR, option_selector)
                
                if option_elements:
                    for option_elem in option_elements:
                        option_text = option_elem.text.strip()
                        if option_text:
                            options.append(option_text)
                    print(f"Found {len(options)} options using specific class pattern")
                
                # If still no options found, try backup methods
                if not options:
                    # First backup method: look for elements with "option" class
                    option_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='option']")
                    for option_elem in option_elements:
                        option_text = option_elem.text.strip()
                        if option_text and option_text != "Results" and option_text not in options:
                            options.append(option_text)
                    
                    # Second backup method: look for divs containing "option" in their class
                    if not options:
                        option_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'option')]")
                        for option_elem in option_elements:
                            option_text = option_elem.text.strip()
                            if option_text and option_text != "Results" and option_text not in options:
                                options.append(option_text)
            except Exception as e:
                print(f"Error extracting options: {e}")
            
            # Add all data to our proposals list
            detailed_proposal = {
                'text': proposal['text'],
                'href': proposal['href'],
                'content': content,
                'votes': votes,
                'options': json.dumps(options)  # Convert list to string for DataFrame storage
            }
            detailed_proposals.append(detailed_proposal)
            
            print(f"Extracted: Content length: {len(content)}, Votes: {votes}, Options: {options}")
            
        except Exception as e:
            print(f"Error processing {proposal['text']}: {e}")
            detailed_proposals.append({
                'text': proposal['text'], 
                'href': proposal['href'],
                'content': "",
                'votes': 0,
                'options': "[]"
            })
        
        # Add delay to avoid overwhelming the server
        time.sleep(1)
    
    # Save to DataFrame
    df = pd.DataFrame(detailed_proposals)
    if not df.empty:
        # Sort the proposals to make sure they're in order (KIP-1, KIP-2, etc.)
        def extract_kip_number(text):
            match = re.search(r'KIP-(\d+)', text)
            if match:
                return int(match.group(1))
            return float('inf')  # For any non-matching items
        
        df['kip_num'] = df['text'].apply(extract_kip_number)
        df = df.sort_values('kip_num').drop('kip_num', axis=1)
        
        df.to_csv('kip_proposals_detailed.csv', index=False)
        print(f"\nSaved {len(df)} detailed KIP proposals to kip_proposals_detailed.csv")
        print(df[['text', 'votes']])
    else:
        print("No KIP proposals found.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()
    print("Browser closed.")
