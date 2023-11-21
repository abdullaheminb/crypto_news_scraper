from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import time

# URL to scrape
url = 'https://coinmarketcap.com/events/'

def press_readmore_and_scrape(url, time_to_press):
    # Path to your WebDriver executable
    driver_path = '/Users/abdullahbayraklilar/Desktop/chromedriver/chromedriver'

    # Create a Service object with the path to the Chrome driver
    service = Service(driver_path)

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(service=service)

    # Go to the URL
    driver.get(url)

    # Pause for a moment to allow the page to load
    time.sleep(4)

    try:
        # Accept cookies.
        accept_cookies_button = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
        accept_cookies_button.click()
        time.sleep(2)

        for i in range(time_to_press):
            # Find the "Read More" button and click it
            read_more_button = driver.find_element(By.CLASS_NAME, 'sc-5bfb714f-6')
            ActionChains(driver).move_to_element(read_more_button).perform()
            read_more_button.click()

            # Wait for the page to load more content
            time.sleep(2)

    except NoSuchElementException:
        pass

    # Get the page source after interactions
    page_source = driver.page_source

    # Close the driver
    driver.quit()

    return page_source

def parse_and_save_data(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # [Your existing logic to parse the HTML and write to CSV]
    # Ensure you modify this part to work with the new HTML structure if needed
    counter = 0

    #Find each day
    days = soup.find_all('div', class_='sc-4d1833d9-0')
    
    #Add a title
    with open('events.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write header
            writer.writerow(['Date', 'Event Name', 'Event Body Title', 'Event Body Expalanation', 'Tag', 'Link'])
    
    #Loop through the days list
    for day in days:
        with open('events.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            #Get events list.
            events = day.find_all('div', class_='sc-6f6d1dae-0')

            #Since CMC list first 2 days as today and tomorrow on the title and give the actual date in subtitle, i need to get subtitle for the first 2 days. Thereafter we get title.
            if counter > 1:
                date_raw = day.find_all('p', class_='dBsgIu')[0].text
                date_string = date_raw.split(' UTC')[0]
            else:
                date_raw = day.find_all('p', class_='ihZPK')[0].text
                date_string = date_raw.split(', ')[1].split(' UTC')[0]
            counter += 1

            #we get date as string. We update it and turn it into a datetime type and remove time by using '.date()' function.
            event_date = datetime.strptime(date_string, '%d %B %Y').date()

            #Now we iterate through every event in that particular day.
            for event in events:
                event_name = event.find_all('span', class_='sc-4984dd93-0')[0].text
                event_body_title = event.find_all('p', class_='sc-4984dd93-0')[0].text
                event_body_text = event.find_all('p', class_='ihZPK')[0].text
                event_tag = event.find_all('button', class_='sc-2861d03b-0')[0].text
                
                #There is 2 'a' link with that class. First directs to cmc page of related coin second directs to related link of the news. We get the 'href' tagged link from second one.
                event_link = event.find_all('a', class_='cmc-link')[1].get('href')

                #Write to CSV
                writer.writerow([event_date, event_name, event_body_title, event_body_text, event_tag, event_link])

# Main execution
html_after_clicks = press_readmore_and_scrape(url, 3)
parse_and_save_data(html_after_clicks)

