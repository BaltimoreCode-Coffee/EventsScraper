import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import json
import re
from supabase import create_client, Client

class EventScraper:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(self.url, self.key)
     
      
    def scraper(self):
        try:
                response = requests.get('https://www.meetup.com/baltimore-code-and-coffee/events')
                response.raise_for_status()
                
        except requests.RequestException as e:
                print(f"Error fetching page: {e}")
                return None
        print(f"response: {response}")
        self.post_processor(response.text)


        
        with open(f'past_html.json') as f:
            html = json.load(f)["Row"]

        self.post_processor(html)


    def post_processor(self,html):
        if not html:
            return None
        
        soup = BeautifulSoup(f"{html}", 'html.parser')
        events = []


        event_elements = soup.find_all('div', 'rounded-md')
    
       
            
        for element in event_elements:
            #todo: add error handeling for .get()
            event = {
                    'title': element.find('span', class_='ds-font-title-3').text.strip() if element.find('span', class_='ds-font-title-3') else '',
                    'start_date': element.find('time').text.strip() if element.find('time') else '',
                    'location': element.find('span', class_='text-gray6').text.strip() if element.find('span', class_='text-gray6') else '',
                    'description': element.find('div',class_='utils_cardDescription__1Qr0x').text.strip() if element.find('p') else '',
                    'attendees':element.find('span', class_='hidden sm:inline').text.strip() if element.find('span', class_='hidden sm:inline') else '',
                    'hyper_link':element.find('a').get('href') if element.find('a').get('href') else '',
                    'image': element.find('img').get('src') if element.find('img').get('src') else '',
                }

            atendees = event['attendees'] 
            number_match = re.compile(rf'[0-9]*', flags=re.IGNORECASE).search(atendees) 
            if number_match:
                event['attendees'] = int(number_match[0])
            else:
                event['attendees'] = 0
            desc = event['description'].splitlines()
                
            short_desc = f"{' '.join(desc[0:2])}"
            if short_desc[-1] == '.':
                    short_desc = short_desc[:-1]
            event['description'] = f"{short_desc[:-1]}..."
                
   
            self.supabase.table('event').insert(event).execute()
   
        return events


    def db_store(self):
        pass

    def patch(self):
        """For patching Db records"""
        d = self.supabase.table('event').select("*").execute().data

        for i in d:
            if not i['location']:
                print(i['location'])



#Uncomment to run 
#EventScraper().scraper()

