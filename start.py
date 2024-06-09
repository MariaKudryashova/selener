from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm
import m3u8
import config
import requests

FIELD_EMAIL = "xpath", "//input[@class='form-control form-field-email']"
FIELD_PWD = "xpath", "//input[@class='form-control form-field-password']"
FIELD_BUTTON = "xpath", "//button[@id='xdget375631_1']"

options = webdriver.FirefoxOptions()
options.add_argument("--window-size=1920, 1080")
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, timeout=15, poll_frequency=1)

driver.get(config.URL_SITE)
dict_href = {}

def init():   
    EL_EMAIL = driver.find_element(*FIELD_EMAIL)
    EL_PWD = driver.find_element(*FIELD_PWD)
    EL_BUTTON = driver.find_element(*FIELD_BUTTON)

    EL_EMAIL.clear()
    EL_EMAIL.send_keys(config.EMAIL)

    EL_PWD.clear()
    EL_PWD.send_keys(config.PWD)

    button = driver.find_element(*FIELD_BUTTON)
    button.click()

    training_row = driver.find_element(By.XPATH, "//tr[@class='training-row has-children' and @data-training-id='748918518']")
    link = training_row.find_element(By.TAG_NAME, 'a')    
    href = link.get_attribute('href')
    driver.get(href)

    # Ждем загрузки элементов li
    lesson_items = WebDriverWait(driver, config.TIME_SLEEP).until(
            EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'user-state-reached')]"))
        )
    
    # Перебираем все элементы li и выводим ссылки
    for i, item in enumerate(lesson_items):
        link = item.find_element(By.TAG_NAME, 'a')
        href = link.get_attribute('href')
        dict_href[i] = href
        print(f"{i}: {href}")

def load_video(key):
    
    print(f"Загрузка видео №{key+1}")
    print(dict_href[key])
    driver.get(dict_href[key])

    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        driver.switch_to.frame(iframes[0])
    
    try:        
        JS_get_network_requests = """
        var callback = arguments[arguments.length - 1];
        var requests = [];
        var resources = window.performance.getEntries();
        for (var i = 0; i < resources.length; i++) {
            if (resources[i].name.includes('master.m3u8')) {
                requests.push(resources[i].name);
            }
        }
        callback(requests);
        """
        network_requests = driver.execute_async_script(JS_get_network_requests)
        print(network_requests)
        
        url = network_requests[0]

        r = requests.get(url) 
        print("--> Формируем плейлист")
        m3u8_master = m3u8.loads(r.text) 
        playlist_url = m3u8_master.data["playlists"][0]['uri'] 
        r = requests.get(playlist_url)    
        playlist = m3u8.loads(r.text) 

        r = requests.get(playlist.data['segments'][0]['uri']) 

        print("--> Прогружаем сегменты")
        file_name = f"video_{key+1}.ts"
        with open(file_name, 'wb') as f:
            # go through each segment and write it to the file
            for segment in tqdm(playlist.data['segments']): 
                url = segment['uri']
                r = requests.get(url)            
                f.write(r.content)

        print(f"Видео №{key+1} сохранено")
                
    except Exception as e:
        print(f"Произошла ошибка: {e}")


init()

for key in dict_href.keys():
    if key == 16:
        load_video(key)

driver.switch_to.default_content()
