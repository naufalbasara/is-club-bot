from bs4 import BeautifulSoup
import random
import requests
import time

async def get_image(user_input):
        """
        Scraping the website om IMGUR using beautifulsoup to get random image according to certain user input   
        """
        time.sleep(2)
        try:
            data = requests.get(f'https://imgur.com/search?q={user_input}', headers={
                    'User-Agent': 'Chrome/115.0.0.0',
                }).content
            soup = BeautifulSoup(data, 'html.parser')
            images = soup.find_all(class_='post')
            img = images[random.randint(0, len(images)-1)].find('img')

        except:
            return False
        
        return 'https:' + img['src']