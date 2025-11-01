import requests
from time import sleep
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
from tqdm import tqdm
import csv
import os

base_url_to_parse = 'https://www.sothebys.com/en/results?from=&to=&f2=00000164-609b-d1db-a5e6-e9ff01230000&f2=00000164-609b-d1db-a5e6-e9ff08ab0000&q='
base_fake_user_agent = {'user-agent': UserAgent().random}
max_checked_auctions = 1
current_cheked = 0
try:
    base_response = requests.get(url=base_url_to_parse, timeout=(3, 3), headers=base_fake_user_agent)
    base_response.raise_for_status()
    base_response.encoding = 'utf-8'
    if base_response.ok:
        print(f'Запрос выполнен успешно: {base_response.status_code}')
    else:
        print(f'Ошибка запроса к первоначальной странице с аукционами по ссылке {base_url_to_parse}')
        
except requests.exceptions.RequestException as error:
    print(f'При запросе к {base_url_to_parse} возникла ошибка {error}, {base_response.reason}')
    
base_soup = BeautifulSoup(base_response.text, 'html.parser')
massive_of_auctions_to_pasrse = base_soup.find_all('li', class_='SearchModule-results-item')
massive_of_urls_to_parse = []
for auction_tag in massive_of_auctions_to_pasrse:
    card_media = auction_tag.find('div', class_='Card-media')
    auction_url = card_media.find('a', href=True).get('href')
    massive_of_urls_to_parse.append(auction_url)
    
# print(massive_of_urls_to_parse)

for auction_url in tqdm(massive_of_urls_to_parse):
    print(f'\nОбработка аукциона {auction_url}')
    if current_cheked < max_checked_auctions: # для дебагга, адли после того как фулл напишешь иначе гг будет
        current_cheked += 1
    else:
        break
    try:
        auction_headers = {'user-agent': UserAgent().random}
        auction_response = requests.get(url=auction_url, timeout=(3, 3), headers=auction_headers)
        auction_response.raise_for_status()
        auction_response.encoding = 'utf-8'
        if auction_response.ok:
            pass
        else:
            print(f'Ошибка запроса к странице аукциона по ссылке {base_url_to_parse}')
            
    except requests.exceptions.RequestException as error:
        print(f'При запросе к {base_url_to_parse} возникла ошибка {error}, {base_response.reason}')
    
    auction_soup = BeautifulSoup(auction_response.text, 'html.parser')
    
    try:
        auction_name = auction_soup.find('h1', class_='headline-module_headline28Regular__CWxFH css-16yerai').text.strip()
    except:
        auction_name = auction_url.split('/')[-1]
    auction_images = auction_soup.find('div', id="lot-list").find_all('div', class_='css-1up9enl')
    # SAVE_DIR = fr'D:\python_main\training_env\art_analytics\data\{auction_name}'
    SAVE_DIR = f"data/{auction_name}"
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    for image_tag in auction_images:
        image_url = image_tag.find('div', class_='css-1f38y8e').find('img').get('src')
        try:
            image_download_response = requests.get(url=image_url, headers=auction_headers, timeout=5)
            if image_download_response.status_code != 200:
                continue
                
            file_name = f'image_test.jpg'
            file_path = os.path.join(SAVE_DIR, file_name)
            
            with open(file_path, 'wb') as writer_file:
                writer_file.write(image_download_response.content)
                
            sleep(1)
            
        except Exception as error:
            print(f'На этапе загрузки картинки произошла ошибка {error}')
            break
    sleep(2)
    

# print(len(massive_of_auctions_to_pasrse))
# print(base_response.text)