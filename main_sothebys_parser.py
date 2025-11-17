from time import time, sleep
from tqdm.auto import tqdm
from random import randint
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import re
import os
from fake_useragent import UserAgent

options = Options()
options.add_argument(f'user-agent={UserAgent(os=["Windows", "Linux", "Ubuntu", "Chrome OS", "Mac OS X"], platforms=['desktop']).random}')
options.add_argument('--disable-web-security')
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument("--headless=new")


SCROLL_PAUSE = 1.5
MAX_SCROLL = 2
current_scroll = 0
main_dict = {}

base_url = 'https://www.sothebys.com/en/results?from=01.01.2025&to=30.11.2025&f0=1735678800000-1764450000000&f2=00000164-609b-d1db-a5e6-e9ff01230000&f2=00000164-609b-d1db-a5e6-e9ff08ab0000&q='

start = time()
max_iter = 10
current_itttter = 0

def dismiss_cookie_and_overlays(browser: webdriver.Chrome, wait: WebDriverWait) -> None:
    '''
    Try to close cookie banner and common overlays if present 
    '''
    possible_selectors = [
        '[id*="cookie"] button',
        '[class*="cookie"] button',
        'div.cookie a[class*="accept"]',
        'div[class*="cookie"] [class*="accept"]',
        'button[aria-label*="cookie"]',
        'button[onclick*="cookie"]',
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
            # print(f'Кнопка для куки-банера не нашлась')
            pass
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
auctions_title_massive = []
auctions_href_seen = set()
auctions_title_seen = set()
    
with webdriver.Chrome(options=options) as browser:
    browser.set_page_load_timeout(5)
    wait = WebDriverWait(browser, timeout=4)
    try:
        browser.get(url=base_url)
        sleep(1.5)
        print('Успешная загрузка браузера\n')
    except Exception as error:
        # print(f'Слишком долгая загрузка страницы по адресу {base_url}')
        actions = ActionChains(browser)
        actions.send_keys(Keys.ESCAPE).perform()
        sleep(1)
        print('Успешная загрузка браузера\n')
    dismiss_cookie_and_overlays(browser, wait)
    
    
    last_height = browser.execute_script('return document.body.scrollHeight') 
    
    while current_scroll < MAX_SCROLL:
        current_auctions_href_title = [(elem.find_element(By.CSS_SELECTOR, '.AuctionActionLink-link').get_attribute('href').strip(), elem.find_element(By.CSS_SELECTOR, '.Card-title').text.strip() + str(randint(-10, 10)), 
                                        elem.find_element(By.CSS_SELECTOR, '.Card-details').text.strip())
                                      for elem in wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.Card-info'))) if
                                      elem.find_element(By.CSS_SELECTOR, '.AuctionActionLink-link').get_attribute('href').strip()
                                      not in auctions_href_seen]
        for href, title, _ in current_auctions_href_title:
            auctions_href_seen.add(href)
            
        auctions_href.extend(current_auctions_href_title)
        browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        
        try:
            wait.until(lambda browser: browser.execute_script('return document.body.scrollHeight') > last_height)
            last_height = browser.execute_script('return document.body.scrollHeight')
        
            current_scroll += 1
            sleep(SCROLL_PAUSE)
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'body')))
        except TimeoutException as error:
            print(f'Не смогли совершить иттерацию скроллинга, ошибка {error}')
            
    total_auctions = len(auctions_href)
    current_auction = 1
    print(f'Всего будет обработано {len(auctions_href)} аукционов')
    
    for auction_href, auction_title, auction_additional_info in auctions_href:
        print('--------------------------------')
        current_itttter +=1
        if current_itttter >= max_iter:
            break        
        try:
            browser.get(url=auction_href)
        except TimeoutException as error:
            # print(f'Слишком долгая загрузка страницы по адресу {base_url}')
            actions = ActionChains(browser)
            actions.send_keys(Keys.ESCAPE).perform()
        print(f'Успешная загрузка страницы аукциона {auction_title}')
        sleep(1.5)
        dismiss_cookie_and_overlays(browser, wait)
        auction_additional_info = auction_additional_info.split('|')
        if len(auction_additional_info) == 2:
            auction_date, auction_city =  auction_additional_info
        
        elif len(auction_additional_info) == 3:
            auction_date, gmt_hours, auction_city = auction_additional_info
        auction_date = auction_date.strip()
        auction_city = auction_city.strip()
        # main_dict = {}
        main_dict[auction_title] = {'Auction_date':auction_date, 'auction_city': auction_city}
        
        try:
            auctions_images_list = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#lot-list')))
        except TimeoutException as error:
            print(f'Не удалось найти список картин по аукциону {auction_href}\n')
            continue
        auctions_images = [elem for elem in browser.find_elements(By.CSS_SELECTOR, '.css-1up9enl')]
        browser.implicitly_wait(2)
        if len(auctions_images) != 0:
            print(f'Успешно нашли список лотов аукциона, начинаем обработку')
            total = len(auctions_images)
            for auction_image_element_index in tqdm(range(len(auctions_images)), total=total, desc=f'Processing: {auction_title}'):
                try:
                    auctions_images = [elem for elem in  wait.until(EC.presence_of_all_elements_located(((By.CSS_SELECTOR, '.css-1up9enl'))))]
                    auction_image_element = auctions_images[auction_image_element_index]
                except (TimeoutException, IndexError, NoSuchElementException) as error:
                    print(f'Не успешная обработка {auction_image_element_index} лота аукциона {auction_title}')
                    continue
                
                try:
                    auction_image_element_url = auction_image_element.find_element(By.CSS_SELECTOR, '.css-1ivophs')
                    auction_image_element_url = auction_image_element_url.get_attribute('href').strip()
                except TimeoutException as error:
                    print(f'Не смолги получить ссылку на лот')
                    continue
                
                try:
                    lot_image_url = auction_image_element.find_element(By.CLASS_NAME, 'css-1f38y8e').find_element(By.TAG_NAME, 'img').get_attribute('src')
                except NoSuchElementException as error:
                    print(f'Не получили ссылку на изображение лота')
                    lot_image_url = None                    
                try:
                    auction_image_element = auction_image_element.find_element(By.CSS_SELECTOR, '.css-m0n40v')
                except NoSuchElementException as error:
                    continue
                browser.execute_script('arguments[0].scrollIntoView({block: "center"});', auction_image_element)
                actions = ActionChains(browser)
                actions.move_to_element(auction_image_element)
                actions.click(auction_image_element)
                actions.perform()
                sleep(1)
                    
                try:
                    image_estimate_price = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.paragraph-module_paragraph14Regular__Zfr98.css-137o4wl')))
                    image_estimate_price = image_estimate_price.text.strip()
                except TimeoutException as error:
                    print(f'Не смогли получить цену лота')
                    image_estimate_price = None
                    
                try:
                    image_title = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="placebidtombstone"]/div/div[2]/div[1]/div[1]/div')))
                    image_title = image_title.text.strip()
                except TimeoutException as error:
                    print(f'Не смогли получить название лота')
                    image_title = None
                
                image_info = {'lot_link': auction_image_element_url, 
                              'image_url': lot_image_url,
                              'estimate_price': image_estimate_price}
                
                main_dict[auction_title][image_title] = image_info
                sleep(1)
                browser.back()
                sleep(1)
        else:
            print(f'Не нашли список картин аукциона {auction_href}')
            continue
        
        # with open(fr'D:\python_main\training_env\art_analytics\data_selenium\{auction_title}.json', 'w', encoding='utf-8') as writer_file:
            # json.dump(main_dict, fp=writer_file, ensure_ascii=False, indent=4)
        print(f'Обработано {current_auction}/{total_auctions}')
        current_auction += 1
        print('--------------------------------\n')
             
    
with open(r'D:\python_main\training_env\art_analytics\data\images_selenium.json', 'w', encoding='utf-8') as writer_file:
    json.dump(main_dict, fp=writer_file, ensure_ascii=False, indent=4)

end = time()
print(f'Время работы {round(end - start, 2)}')