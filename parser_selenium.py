from time import time, sleep
from tqdm.auto import tqdm
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import re
import os


from fake_useragent import UserAgent

options = Options()
options.add_argument(f'user-agent={UserAgent().random}')
options.add_argument('--disable-web-security')
options.add_argument('--ignore-certificate-errors-spki-list')

SCROLL_PAUSE = 1.5
MAX_SCROLL = 1 
current_scroll = 0

base_url = 'https://www.sothebys.com/en/results?from=01.01.2025&to=30.11.2025&f0=1735678800000-1764450000000&f2=00000164-609b-d1db-a5e6-e9ff01230000&f2=00000164-609b-d1db-a5e6-e9ff08ab0000&q='

main_dict = {}

def dismiss_cookie_and_overlays(browser: webdriver.Chrome, wait: WebDriverWait) -> None:
    """Try to close cookie banner and common overlays if present."""
    possible_selectors = [
        # Cookie banners
        '[id*="cookie"] button',
        '[class*="cookie"] button',
        'div.cookie a[class*="accept"]',
        'div[class*="cookie"] [class*="accept"]',
        'button[aria-label*="cookie"]',
        'button[onclick*="cookie"]',
        # Close/consent buttons
        'button[aria-label*="закрыть"]',
        'button[aria-label*="close"]',
        'button[title*="закрыть"]',
        'button[title*="close"]',
        'button[class*="close"]',
    ]
    possible_xpaths = [
        "//button[contains(translate(., 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'принять')]",
        "//button[contains(translate(., 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'соглаш')]",
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]",
        "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]",
        "//button[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]",
        "//button[contains(translate(@aria-label, 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'закрыть')]",
    ]
    try:
        try:
            current_cookie_bunner = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#onetrust-banner-sdk')))
            current_cookie_button = current_cookie_bunner.find_element(By.ID, 'onetrust-accept-btn-handler')
            current_cookie_button.click()
        except TimeoutException as error:
            print(f'Кнопка для куки-банера не нашлась')
        # Try CSS selectors
        for selector in possible_selectors:
            elements = browser.find_elements(By.CSS_SELECTOR, selector)
            for el in elements:
                try:
                    if el.is_displayed():
                        browser.execute_script('arguments[0].scrollIntoView({block: "center"});', el)
                        sleep(0.2)
                        browser.execute_script('arguments[0].click();', el)
                        sleep(0.3)
                except Exception:
                    continue
        # Try XPaths
        for xpath in possible_xpaths:
            elements = browser.find_elements(By.XPATH, xpath)
            for el in elements:
                try:
                    if el.is_displayed():
                        browser.execute_script('arguments[0].scrollIntoView({block: "center"});', el)
                        sleep(0.2)
                        browser.execute_script('arguments[0].click();', el)
                        sleep(0.3)
                except Exception:
                    continue
    except Exception:
        pass
    
auctions_href = []
auctions_href_seen = set()
    
with webdriver.Chrome(options=options) as browser:
    browser.set_page_load_timeout(10)
    wait = WebDriverWait(browser, timeout=10)
    print(1)
    try:
        browser.get(url=base_url)
        sleep(1.5)
        print('успешная загрузка')
    except Exception as error:
        print(f'Слишком долгая загрузка страницы по адресу {base_url}')
        actions = ActionChains(browser)
        actions.send_keys(Keys.ESCAPE).perform()
        sleep(1)
    dismiss_cookie_and_overlays(browser, wait)
    
    
    last_height = browser.execute_script('return document.body.scrollHeight') 
    
    while current_scroll < MAX_SCROLL:
        current_auctions_href = [elem.get_attribute('href').strip() for elem in wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.AuctionActionLink-link'))) if elem.get_attribute('href') not in auctions_href_seen]   
        # if len(current_auctions_href) != 0:
        for href in current_auctions_href:
            auctions_href_seen.add(href)
            
        auctions_href.extend(current_auctions_href)
        # print(current_auctions_href)
        # break
        browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        
        try:
            wait.until(lambda browser: browser.execute_script('return document.body.scrollHeight') > last_height)
            last_height = browser.execute_script('return document.body.scrollHeight')
        
            current_scroll += 1
            sleep(SCROLL_PAUSE)
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'body')))
        except TimeoutException as error:
            print(f'Не смогли совершить иттерацию скроллинга, ошибка {error}')
    input('готов закончить')
print(auctions_href)
print(len(auctions_href))
print(len(set(auctions_href)))

# a = ['https://www.sothebys.com/en/buy/auction/2025/modern-discoveries-l25005', 'https://www.sothebys.com/en/buy/auction/2025/modernites-pf2516']
# auctions_href = ['https://www.sothebys.com/en/buy/auction/2025/modern-contemporary-evening-auction-2?locale=en&lotFilter=AllLots', 'https://www.sothebys.com/en/buy/auction/2025/modernites-pf2516']

for auction_url in tqdm(auctions_href):
    max_attempt_response = 3
    print(f'\nОбработка аукциона {auction_url}')
    for i in range(max_attempt_response):
        try:
            auction_headers = {'user-agent': UserAgent().random}
            auction_response = requests.get(url=auction_url, headers=auction_headers, timeout=(5, 5))
            auction_response.raise_for_status()
            auction_response.encoding = 'utf-8'
            if auction_response.ok:
                pass
            else:
                print(f'Ошибка запроса к странице аукциона по ссылке {auction_url}')
        
        except requests.exceptions.RequestException as error:
            print(f'При запросе к {auction_url} на {i} попытке возникла ошибка {error}')
        
        
    auction_soup = BeautifulSoup(auction_response.text, 'html.parser')
    
    try:
        auction_name = auction_soup.select_one('#__next > div > div:nth-child(3) > div > div.css-1nr62r8 > div.css-ifm2o5 > div > h1.headline-module_headline32Regular__pMgbY.css-e4ejw').text.strip()
    
    except Exception as error:
        print(f'Не смогли распарсить аукцион по ссылке {auction_url}')
        continue
    if auction_name is None:
        continue
    
    try:
        alternative_way_to_find = False
        auction_images = auction_soup.find('div', id="lot-list").find_all('div', class_='css-1up9enl')
        if len(auction_images) == 0:
            auction_images = auction_soup.find('div', id="lot-list").find_all('div', class_='css-10q0hxm')
            if len(auction_images) != 0:
                alternative_way_to_find = True
        print(len(auction_images))
        # print(auction_images)
    except Exception as error:
        print(f'При обработке аукциона {auction_url} произошла ошибка {error}')
        continue
    
    if len(auction_images) == 0:
        print(f'Не найдено ни одной картины в аукционе по ссылке {auction_url}')
        sleep(2)
        continue
    
    auction_name = re.sub(r'[^\w\s\-\.]', '_', auction_name)
    SAVE_DIR = f"data/{auction_name}"
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    # main_data.append({auction_name: {}})
    
    main_dict[auction_name] = []
    
    for image_tag in tqdm(auction_images):
        # print(image_tag)
        image_url = image_tag.find('div', class_='css-1f38y8e').find('img').get('src') if not alternative_way_to_find else image_tag.find('div', class_='css-14h6clq').find('img').get('src')
        if image_url is None:
            continue
        else:
            image_url = image_url.replace('extra_small', 'small', 1)
        print(image_url)
        
        if alternative_way_to_find is False:
            file_name = f'{image_tag.find('div', class_='css-1u3rssc').find('p').text.strip()}'
        else:
            file_name = image_tag.find('div', class_='css-14h6clq').find('img').get('alt').strip()
            
        # if alternative_way_to_find is False:
        #     estimate_price = image_tag.find('span', class_='css-17b8gen').find('p', class_='paragraph-module_paragraph14Regular__Zfr98 css-1ud9h99').text.strip()
            
        # else:
        #     estimate_price = image_tag.find('span', class_='css-17b8gen').find('p', class_='paragraph-module_paragraph14Regular__Zfr98 css-1ud9h99').text.strip()
            
        main_dict[auction_name].append({file_name: image_url})
        break
        
        # try:
        #     image_auction_response = requests.get(url=image_auction_url, headers=auction_headers, timeout=(3, 3))
        #     image_auction_response.encoding = 'utf-8'
        #     image_auction_response.raise_for_status()
        #     if auction_response.ok:
        #         pass
        #     else:
        #         print(f'Ошибка запроса к картине по ссылке {image_auction_url}')
        # except requests.exceptions.RequestException as error:
        #     print(f'При запросе к {image_auction_url} возникла ошибка {error}, {image_auction_response.reason}')
        # image_auction_soup = BeautifulSoup(image_auction_response.text, 'html.parser')
        # try:
        #     lot_title = image_auction_soup.find('h1', attrs={'data-testid': 'lotTitle'}).text.strip()
            
        # except Exception as error:
        #     print(f'Ошибка на этапе получения названия изображения аукциона {image_auction_url}')
        #     lot_title = None
        
        # try:
        #     estimate_price = image_auction_soup.find('div', id='placebidtombstone').find('p', class_='paragraph-module_paragraph14Regular__Zfr98 css-137o4wl').text.strip()
        # except Exception as error:
        #     estimate_price = None
        # try:
        #     image_url = image_auction_soup.find('li', class_='slide selected previous').find('img').get('src')
        # except Exception as error:
        #     print(f'Ошибка на этапе получения ссылки изображения аукциона {image_auction_url}')
            
        # image_dict = {'Название': lot_title, 'Прогнозная цена': estimate_price, 'Ссылка на изображение': image_url}
        # main_dict[auction_name][lot_title] = image_dict

with open(r'D:\python_main\training_env\art_analytics\data\image.json', 'w', encoding='utf-8') as writer_file:
    json.dump(main_dict, fp=writer_file, indent=4, ensure_ascii=False)
print(main_dict)