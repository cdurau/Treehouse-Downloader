import sys
import os
import re
import time
import json
from pathlib import Path
from pathvalidate import sanitize_filename, sanitize_filepath
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup


class txt:
    purple = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    warning = '\033[93m'
    error = '\033[91m'
    normal = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'


class Timer:
    def __init__(self):
        self.start = time.time()
        self.end = None

    def total_time(self):
        hours, rem = divmod(time.time() - self.start, 3600)
        minutes, seconds = divmod(rem, 60)

        self.end = "Total Time: {:0>2} hours, {:0>2} minutes and {:05.2f} seconds".format(
            int(hours), int(minutes), seconds)


def sanitize_special_chars(words):
    words = sanitize_filename(words)

    words = words.replace("'", "")
    words = words.replace('/', '')

    return words


def get_settings():
    settings = {}

    with open('data/settings.json', 'r') as f:
        settings = json.load(f)

    return settings


def login(settings):
    login_url = 'https://teamtreehouse.com/signin'
    email = settings['email']
    password = settings['password']

    # Create Webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(
        executable_path=settings['webdriver'], options=options)

    # Load Login Page
    driver.get(login_url)

    # Login to Treehouse
    # email_input = driver.find_element_by_xpath('//*[@id="user_session_email"]')
    email_input = driver.find_element_by_id('user_session_email')
    email_input.send_keys(email)

    # password_input = driver.find_element_by_xpath(
    # '//*[@id="user_session_password"]')
    password_input = driver.find_element_by_id('user_session_password')
    password_input.send_keys(password)

    signin_button = driver.find_element_by_xpath(
        '/html/body/main/div/div/div/div/div/form/button')
    signin_button.click()

    return driver


def create_folder(path):
    sanitize_filepath(path)

    if not os.path.exists(path):
        os.makedirs(path)

    os.chdir(path)

    return os.getcwd()


def wait_driver(driver, id_class, element):
    wait = WebDriverWait(driver, 10)

    if (id_class == 'id'):
        element = wait.until(EC.presence_of_element_located((By.ID, element)))
    else:
        element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, element)))


def get_links():
    # TODO: Test Link Format - Else Skip
    download_links = []

    with open(Path('data/links.txt'), 'r') as d_links:
        for link in d_links:

            # Get Download URL
            url = link.strip()

            # Check if link is commented out
            if (not url.startswith('#')) and (not url.strip() == ''):
                download_links.append(link)

    if download_links:
        return download_links

    # If no links found
    else:
        print(txt.error + 'No download links found!' + txt.normal)
        sys.exit()


def transform_links(text):
    links = text.findAll('a')
    strong = text.findAll('strong')

    # Sanitize Text
    text = text.getText().strip()
    text = text.replace('<', '`<')
    text = text.replace('>', '>`')

    # Markup for bold text
    for st in strong:
        strong_text = st.getText()
        text = text.replace(strong_text, '**{}**'.format(strong_text))

    # Replace HTML Links with markup
    for link in links:
        title = link.getText()
        href = link['href']

        if href.startswith('/'):
            href = 'https://teamtreehouse.com' + href

        text = text.replace(title, '[{}]({})'.format(title, href))

    return text


def get_page_type(driver):
    page_type = ''

    soup = BeautifulSoup(driver.page_source, 'lxml')

    if (driver.current_url.rsplit('/', 1)[-1].startswith('practice')):
        page_type = 'practice'
    elif (soup.find('div', id='track-card')):
        page_type = 'track'
    elif (soup.find('div', id='syllabus-title')):
        page_type = 'course'
    elif (soup.find('div', id='workshop-title')):
        page_type = 'workshop'
    elif (soup.find('div', class_='instruction--content--title')):
        page_type = 'instruction'
    else:
        print(txt.error + 'Could not get page type for: ' +
              txt.normal + driver.current_url)
        sys.exit()

    return page_type


def get_download_type(driver):
    try:
        wait_driver(driver, 'class_name', 'stage-progress-item')
    except:
        wait_driver(driver, 'class_name', 'stage-progress-list')

    download_type = ''

    soup = BeautifulSoup(driver.page_source, 'lxml')

    # Course or Workshop
    if soup.find('div', class_='stage-progress-container'):
        progress_list = soup.find('ul', class_='stage-progress-list')
        current_item = progress_list.find('li', class_='current')
        download_type = ''

        if current_item:
            icon = current_item.find(
                'svg', class_='stage-progress-step-icon-step')

            if ('video-22-icon' in icon['class']):
                download_type = 'video'
            elif ('quiz-22-icon' in icon['class']):
                download_type = 'quiz'
            elif ('code-challenge-22-icon' in icon['class']):
                download_type = 'code-challenge'
            elif ('instruction-22-icon' in icon['class']):
                download_type = 'instruction'
        elif (soup.find('div', id='video-meta')):
            download_type = 'video'
        else:
            print(txt.warning + 'Couldn\'t get Download Type for: ' +
                  txt.normal + driver.current_url)
            sys.exit()

    return download_type


def get_step_meta(driver, href, step):
    step.url = 'https://teamtreehouse.com' + href
    driver.get(step.url)
    try:
        wait_driver(driver, 'class_name', 'stage-progress-item')
    except:
        wait_driver(driver, 'class_name', 'stage-progress-list')

    soup = BeautifulSoup(driver.page_source, 'lxml')

    # Step Type
    step.type = get_download_type(driver)

    # Step Title
    if (step.type == 'video'):
        title = soup.find('div', id='video-meta').find('h1').getText().strip()
        step.title = sanitize_special_chars(title)
        step.duration = soup.find(
            'span', id='video-duration').getText().strip()
    elif (step.type == 'instruction'):
        title = soup.find(
            'div', class_='instruction--content--title').find('h1').getText().strip()
        step.title = sanitize_special_chars(title)
    else:
        title = soup.find('li', class_='current').find(
            'span', class_='stage-progress-step-tooltip').getText().strip()
        step.title = sanitize_special_chars(title)

    return step


def get_topic(soup):
    actions = soup.find('ul', id=re.compile('.*-actions'))
    topic = actions.find('li', class_=re.compile('topic-.*'))
    topic = topic.getText().strip()

    return topic


def get_skill_level(soup):
    actions = soup.find('ul', id=re.compile('.*-actions'))
    skill_level = actions.find('li', id=re.compile('.*-skill-level'))
    skill_level = skill_level.getText().strip()

    return skill_level


def mk_symlink(src, target):
    src = Path(src)
    target = Path(target)

    if not target.exists():
        os.symlink(src, target)
