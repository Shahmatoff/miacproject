from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import psycopg2
import time

# Настройка драйвера Selenium
service = Service(executable_path='C:/Users/Shahmatovid/chromedriver-win64/chromedriver.exe')
driver = webdriver.Chrome(service=service)

# Функция для входа в систему
def login(driver, username, password):
    driver.get('http://10.31.6.59/inst/')
    time.sleep(5)  # Ждем 5 секунд для полной загрузки страницы
    
    try:
        # Используем CSS-селекторы для полей ввода
        username_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#d3ctrl251723113103683 > div > input[type=text]')))
        password_field = driver.find_element(By.CSS_SELECTOR, '#d3ctrl341723113103683 > div > input[type=password]')
        login_button = driver.find_element(By.CSS_SELECTOR, '#d3ctrl401723113103683 > div')

        # Вводим данные для авторизации
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()
    except Exception as e:
        print(f"Ошибка при авторизации: {e}")
        driver.quit()

# Функция для выбора больницы
def select_hospital(driver, hospital_name):
    hospital_select = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.NAME, 'hospital')))
    hospital_select.click()
    
    hospital_option = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f'//option[contains(text(), "{hospital_name}")]')))
    hospital_option.click()
    
    confirm_button = driver.find_element(By.XPATH, '//input[@value="Выбор"]')
    confirm_button.click()

# Функция для парсинга данных с таблицы
def parse_data(driver, hospital_name):
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class': 'class_name'})  # Замените 'class_name' на реальный класс таблицы

    if table:
        rows = table.find_all('tr')
        for row in rows[1:]:
            cols = row.find_all('td')
            doctor_name = cols[0].text.strip()
            position = cols[1].text.strip()
            schedule_time = cols[2].text.strip()
            office = cols[3].text.strip()
            
            # Сохранение данных в PostgreSQL
            conn = psycopg2.connect(database="mydatabase", user="myuser", password="mypassword", host="localhost", port="5432")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO medical_workers (hospital_name, doctor_name, position, schedule_time, office) VALUES (%s, %s, %s, %s, %s)", 
                           (hospital_name, doctor_name, position, schedule_time, office))
            conn.commit()

        cursor.close()
        conn.close()

# Функция для выхода из системы
def logout(driver):
    logout_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@value="Выход"]')))
    logout_button.click()

# Список больниц для парсинга
hospitals = [
    "Центр семейной медицины",
    "Фельдшерско-акушерский пункт",
    # добавьте остальные больницы сюда
]

# Основной цикл по больницам
try:
    for hospital in hospitals:
        login(driver, 'SHD_MIAC', 'Wow7503woW')
        select_hospital(driver, hospital)
        parse_data(driver, hospital)
        logout(driver)
except Exception as e:
    print(f"Произошла ошибка: {e}")
    print(driver.page_source)  # Вывод содержимого страницы для отладки
finally:
    driver.quit()