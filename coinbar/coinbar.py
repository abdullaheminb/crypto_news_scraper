import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import time

# URL of the webpage to scrape

def get_body_details_from_link(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the element with class 'event'
        event_content = soup.find(class_='event')

        # Exclude elements with classes 'changes-info' and 'tools'
        if event_content:
            for excluded_class in ['changes-info', 'tools']:
                for tag in event_content.find_all(class_=excluded_class):
                    tag.decompose()

            # Remove empty lines
            content_lines = event_content.text.strip().split('\n')
            cleaned_content = '\n'.join(line for line in content_lines if line.strip())
            return cleaned_content
        else:
            print("Event content not found")
            cleaned_content = ''
            return cleaned_content
    else:
        print("Failed to retrieve the webpage")
        cleaned_content = ''
        return cleaned_content

def get_date(day):
    date_raw = day.find('div', class_='day').text
    cleaned_date = ' '.join(date_raw.strip().split())
    cleaned_date = cleaned_date.rstrip(' UTC')
    date = datetime.strptime(cleaned_date, "%B %d, %Y").date()
    return date
    
def parse_page_and_print_csv(page_number):
    url = f'https://coindar.org/en/search?page={page_number}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    days = soup.find_all('div', class_='block-day')
    for day in days:
        date = get_date(day)
        events = day.find_all('div', class_='event')
       
        for event in events:
            #Get Protocol Name
            protocol_name = event.find('div', class_='coin').find('a').text

            #Get Coin Ticker
            ticker = event.find('div', class_='coin').find('span').text

            #Get Event title. Since event title have some styling around it we strip from decoration.
            event_title_raw = event.find('div', class_='caption').find('h3').find('a').text
            event_title = ' '.join(event_title_raw.strip().split())

            #Get event Tag
            event_tag = event.find('a', class_='category').text

            #Get event info
            event_info = get_body_details_from_link(f"https://coindar.org{event.find('div', class_='caption').find('h3').find('a').get('href')}")
            with open('events.csv', 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([date, protocol_name, ticker, event_title, event_tag, event_info])

def main():
    with open('events.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Protocol Name', 'Protocol Ticker', 'Event Body Title', 'Tag', 'Event Body'])
    for page_num in range(15):    
        parse_page_and_print_csv(page_num+1)
        print(f'Page {page_num} is parsed')

main()