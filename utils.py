from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time, re, os
from dotenv import load_dotenv
from ocacaptcha import oca_solve_captcha

load_dotenv()


def init_browser():
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    
    # Only run headless if DEBUG is not set
    if not os.getenv('DEBUG'):
        chrome_options.add_argument("--headless=new")
    
    browser = webdriver.Chrome(options=chrome_options)

    wait = WebDriverWait(browser, 20)

    return browser, wait


def login_tiktok(browser, wait, username, password):
    browser.get('https://www.tiktok.com/login/phone-or-email/email')
    
    actions = ActionChains(browser, duration=550)

    
    wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
    time.sleep(3)
    password_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="new-password"]')))
    time.sleep(3)
    password_field.send_keys(password)
    time.sleep(3)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[class*='StyledButton']"))).click()
    time.sleep(3)
    #if we found a div with the property "type=error" click again the button
    if wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[type='error']"))):
        error("Not logged in")

    user_api_key = os.getenv('CAPTCHA_API_KEY')
    print(user_api_key)
    number_captcha_attempts = 10
    action_type = 'tiktokcircle'
    oca_solve_captcha(browser, actions, user_api_key, action_type, number_captcha_attempts)
    time.sleep(300000)
    


def get_all_friends(browser, wait):
    browser.get('https://www.tiktok.com/messages?lang=vi')

    all_user = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='PInfoNickname']")))

    target_friend = os.getenv('TIKTOK_FRIEND_USERNAME')
    print(f"Target friend: {target_friend}")
    print("\nAll available friends:")

    for user in all_user:
        user.click()
        time.sleep(2)
        profile_element = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='StyledLink']")))[0]
        href = profile_element.get_attribute("href")
        username = re.search(r"/@(.+)", href).group(1)
        
        status = "✓ TARGET" if username == target_friend else ""
        print(f"  - {username} {status}")

    browser.quit()


def auto_send_message(browser, wait):
    browser.get('https://www.tiktok.com/messages?lang=vi')

    
    my_friends = [os.getenv('TIKTOK_FRIEND_USERNAME')]

    all_user = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='PInfoNickname']")))

    for user in all_user:
        user.click()
        time.sleep(2)
        profile_element = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='StyledLink']")))[0]
        href = profile_element.get_attribute("href")
        username = re.search(r"/@(.+)", href).group(1)

        if username not in my_friends:
            continue

        try: 
            print("Sending message to", username)
            message_input = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "public-DraftStyleDefault-block")))
            message_input.click()
            message_input.send_keys(os.getenv('MESSAGE'))
            message_input.send_keys(Keys.RETURN)

        except:
            print("Can't get user name")

