import time
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
import pickle
import os
from selenium.common.exceptions import NoSuchElementException, WebDriverException, StaleElementReferenceException, ElementClickInterceptedException, TimeoutException
import asyncio

# ===================== Configuration Load =====================
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    IV = config['ivasms']
    TE = config['telegram']
    SC = config['scraper']
    print("\033[96m[INFO]\033[0m 🛠️ Config loaded successfully!")
except Exception as e:
    print(f"\033[91m[ERROR]\033[0m ❌ Failed to load config: {e}")
    exit(1)

# ===================== Telegram Bot Setup =====================
try:
    bot = Bot(token=TE['bot_token'])
    print("\033[96m[INFO]\033[0m 🤖 Telegram bot initialized!")
except Exception as e:
    print(f"\033[91m[ERROR]\033[0m ❌ Failed to initialize Telegram bot: {e}")
    exit(1)

# ===================== Customizable Telegram Message Template =====================
TELEGRAM_MSG_TEMPLATE = (
    "#️⃣ <b>ZBot OTP</b>\n\n"
    "🌐 <b>Country :</b> {range}\n"
    "🆔 <b>Platform :</b> {platform}\n"
    "☎️ <b>Number :</b> <a href='https://z-number.web.app'>{number}</a>\n\n"
    "🔐 <b>Code :</b> <b><code>{code}</code></b> <b> ⬅ Click here</b>\n"
    " <blockquote style='border-left: 4px solid #ccc; padding-left: 10px;'><code>💬{message}</code></blockquote>\n"
    "<b>Number site</b> - <a href=\"https://z-number.web.app\">ZNumbers</a>"
)

# ===================== Deduplication Set =====================
sent_otps = set()  # একবার যেটা পাঠানো হয়েছে, সেটা এখানে থাকবে
sent_numbers = set()

COOKIES_FILE = 'ivasms_cookies.pkl'

# ===================== Country Flag Helper =====================
def get_country_flag(country_name):
    country_flags = {
        'IVORY COAST': '🇨🇮',
        'MALI': '🇲🇱',
        'NIGERIA': '🇳🇬',
        'GHANA': '🇬🇭',
        'SENEGAL': '🇸🇳',
        'BURKINA FASO': '🇧🇫',
        'TOGO': '🇹🇬',
        'BENIN': '🇧🇯',
        'GUINEA': '🇬🇳',
        'CAMEROON': '🇨🇲',
        'GABON': '🇬🇦',
        'CONGO': '🇨🇬',
        'DRC': '🇨🇩',
        'SIERRA LEONE': '🇸🇱',
        'LIBERIA': '🇱🇷',
        'GAMBIA': '🇬🇲',
        'MAURITANIA': '🇲🇷',
        'CHAD': '🇹🇩',
        'CENTRAL AFRICAN REPUBLIC': '🇨🇫',
        'SOUTH SUDAN': '🇸🇸',
        'SUDAN': '🇸🇩',
        'EGYPT': '🇪🇬',
        'MOROCCO': '🇲🇦',
        'ALGERIA': '🇩🇿',
        'TUNISIA': '🇹🇳',
        'ETHIOPIA': '🇪🇹',
        'KENYA': '🇰🇪',
        'TANZANIA': '🇹🇿',
        'UGANDA': '🇺🇬',
        'RWANDA': '🇷🇼',
        'BURUNDI': '🇧🇮',
        'SOMALIA': '🇸🇴',
        'MOZAMBIQUE': '🇲🇿',
        'ANGOLA': '🇦🇴',
        'ZAMBIA': '🇿🇲',
        'ZIMBABWE': '🇿🇼',
        'BOTSWANA': '🇧🇼',
        'NAMIBIA': '🇳🇦',
        'SOUTH AFRICA': '🇿🇦',
        'LESOTHO': '🇱🇸',
        'ESWATINI': '🇸🇿',
        'MALAWI': '🇲🇼',
        'MADAGASCAR': '🇲🇬',
        'MAURITIUS': '🇲🇺',
        'SEYCHELLES': '🇸🇨',
        'COMOROS': '🇰🇲',
        'SAO TOME AND PRINCIPE': '🇸🇹',
        # Add more as needed
    }
    for key in country_flags:
        if country_name.upper().startswith(key):
            return country_flags[key]
    return ''

# ===================== Main Scraper Class =====================
class IVASmsReceivedScraper:
    def __init__(self, headless=True):
        print("\033[96m[INFO]\033[0m 🚀 Initializing Chrome driver...")
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument(f"--user-agent={SC['user_agent']}")
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(10)
            self.driver.set_window_size(1920, 1080)
            print("\033[92m[SUCCESS]\033[0m 🟢 Chrome driver ready! (1920x1080)")
        except Exception as e:
            print(f"\033[91m[ERROR]\033[0m ❌ Failed to start Chrome driver: {e}")
            exit(1)

    def login(self):
        print("\033[96m[INFO]\033[0m 🔐 Logging in to IVASMS...")
        try:
            self.driver.get(IV['login_url'])
            time.sleep(2)
            self.driver.find_element(By.ID, 'card-email').send_keys(IV['email'])
            self.driver.find_element(By.ID, 'card-password').send_keys(IV['password'])
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
            time.sleep(3)
            if "dashboard" in self.driver.current_url or "portal" in self.driver.current_url:
                print("\033[92m[SUCCESS]\033[0m 🟢 Login successful!")
            else:
                print("\033[91m[ERROR]\033[0m ❌ Login may have failed. Please check credentials.")
        except Exception as e:
            print(f"\033[91m[ERROR]\033[0m ❌ Login failed: {e}")
            raise

    def goto_received_page(self):
        self.driver.get('https://www.ivasms.com/portal/sms/received')
        print("\033[96m[INFO]\033[0m 🌐 Navigated to /portal/sms/received page.")
        time.sleep(2)
        try:
            next_btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Next")]'))
            )
            next_btn.click()
            print("\033[92m[SUCCESS]\033[0m 👉 'Next' popup closed.")
            time.sleep(1)
        except Exception:
            print("\033[93m[WARN]\033[0m ⚠️ No 'Next' popup found or already closed.")
        try:
            done_btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Done")]'))
            )
            done_btn.click()
            print("\033[92m[SUCCESS]\033[0m 👉 'Done' popup closed.")
            time.sleep(1)
        except Exception:
            print("\033[93m[WARN]\033[0m ⚠️ No 'Done' popup found or already closed.")
        try:
            get_sms_btn = self.driver.find_element(By.XPATH, '/html/body/div/div[1]/div[2]/div[3]/div[1]/div/div/div[3]/button')
            get_sms_btn.click()
            print("\033[92m[SUCCESS]\033[0m 📩 'Get SMS' button clicked.")
            time.sleep(2)
        except Exception as e:
            print(f"\033[91m[ERROR]\033[0m ❌ Could not click 'Get SMS' button: {e}")
            raise

    def reload_received_page(self):
        """
        Reloads the /portal/sms/received page and clicks the 'Get SMS' button, but does NOT handle popups.
        """
        self.driver.refresh()
        print("\033[96m[INFO]\033[0m 🔄 Page reloaded (no popup handling). Waiting for page to load...")
        time.sleep(5)
        try:
            get_sms_btn = self.driver.find_element(By.XPATH, '/html/body/div/div[1]/div[2]/div[3]/div[1]/div/div/div[3]/button')
            get_sms_btn.click()
            print("\033[92m[SUCCESS]\033[0m 📩 'Get SMS' button clicked after reload.")
            time.sleep(2)
        except Exception as e:
            print(f"\033[91m[ERROR]\033[0m ❌ Could not click 'Get SMS' button after reload: {e}")
            raise

    def scroll_to_load_all_numbers(self, numbers_container):
        last_height = self.driver.execute_script("return arguments[0].scrollHeight", numbers_container)
        while True:
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", numbers_container)
            time.sleep(1.2)  # Wait for AJAX to load more numbers
            new_height = self.driver.execute_script("return arguments[0].scrollHeight", numbers_container)
            if new_height == last_height:
                break
            last_height = new_height

    def scrape_all_otps(self):
        print("\033[96m[INFO]\033[0m 📨 Scraping all OTPs...")
        otps = []
        try:
            range_container = self.driver.find_element(By.ID, 'ResultCDR')
            range_blocks = range_container.find_elements(By.CSS_SELECTOR, 'div.card.card-body.mb-1.pointer')
            print(f"[INFO] Found {len(range_blocks)} ranges.")
            for r_idx, range_block in enumerate(range_blocks):
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView();", range_block)
                    range_block.click()
                    time.sleep(2)  # Wait for numbers to load
                    range_name_full = range_block.text.split('\n')[0].strip()
                    range_name = re.sub(r'\s*\d+$', '', range_name_full).strip()
                    print(f"[STEP] Range: {range_name}")

                    # Find the ContentNumbers div just after this range_block (and now visible)
                    try:
                        number_block = range_block.find_element(By.XPATH, "following-sibling::div[contains(@class, 'ContentNumbers') and contains(@class, 'open')]")
                    except Exception as e:
                        print(f"[WARN] Could not find open ContentNumbers for range {range_name}: {e}")
                        continue

                    # SCROLL to load all numbers!
                    self.scroll_to_load_all_numbers(number_block)

                    number_cards = number_block.find_elements(By.CSS_SELECTOR, 'div.card.card-body.border-bottom.bg-100.p-2.rounded-0')
                    print(f"[INFO] Found {len(number_cards)} number cards in this range block")
                    for card_idx, card in enumerate(number_cards):
                        try:
                            row = card.find_element(By.CSS_SELECTOR, 'div.row.g-2')
                            num_div = row.find_element(By.CSS_SELECTOR, 'div.col-sm-4.border-bottom')
                            phone = num_div.text.strip()
                            if not phone or not phone.isdigit():
                                continue
                            unique_number_key = f"{range_name}_{phone}"
                            if unique_number_key in sent_numbers:
                                print(f"[SKIP] Number {phone} in range {range_name} already sent. Skipping.")
                                continue
                            content_sms_divs = card.find_elements(By.CSS_SELECTOR, 'div.ContentSMS.border-top')
                            if not content_sms_divs:
                                print(f"[WARN] No ContentSMS div found for number {phone}")
                                continue
                            content_sms_div = content_sms_divs[0]
                            m = re.search(r'open_(\d+)_(\d+)', content_sms_div.get_attribute('class'))
                            if not m:
                                print(f"[WARN] Could not extract idNumber for number {phone}")
                                continue
                            idNumber = m.group(2)
                            print(f"[STEP] Clicking number: {phone} (idNumber: {idNumber})")
                            self.driver.execute_script("arguments[0].scrollIntoView();", num_div)
                            found = False
                            for attempt in range(3):
                                try:
                                    num_div.click()
                                    # Wait for ContentSMS div to be open and message text to be present
                                    def sms_content_loaded(driver):
                                        class_attr = content_sms_div.get_attribute('class')
                                        if 'open' not in class_attr or not content_sms_div.is_displayed():
                                            return False
                                        try:
                                            msg_elem = content_sms_div.find_element(By.CSS_SELECTOR, 'div.col-9.col-sm-6.text-center.text-sm-start > p')
                                            return msg_elem.text.strip() != ''
                                        except Exception:
                                            return False
                                    WebDriverWait(self.driver, 15).until(sms_content_loaded)
                                    found = True
                                    break
                                except Exception:
                                    print(f"[WARN] Message content not loaded for number {phone} on attempt {attempt+1}, retrying...")
                                    time.sleep(1)
                                    continue
                            if not found:
                                print(f"[ERROR] Skipping number {phone} after 3 attempts (message not loaded)")
                                continue
                            # Now scrape details from content_sms_div as before
                            try:
                                msg_text = ''
                                platform = ''
                                try:
                                    msg_text = content_sms_div.find_element(By.CSS_SELECTOR, 'div.col-9.col-sm-6.text-center.text-sm-start > p').text.strip()
                                except:
                                    msg_text = ''
                                try:
                                    platform_cell = content_sms_div.find_element(By.CSS_SELECTOR, 'div.col-sm-4.border-bottom')
                                    platform = platform_cell.text.strip()
                                except:
                                    platform = ''
                                code_match = re.search(r'(\d{4,8})', msg_text)
                                code = code_match.group(1) if code_match else ''
                                msg_hash = str(hash(msg_text))
                                unique_id = f"{range_name}_{phone}_{code}_{msg_hash}"
                                print(f"[INFO] Range: {range_name}, Number: {phone}, Platform: {platform}, Code: {code}, Message: {msg_text}")
                                if not code or not platform or not msg_text:
                                    continue
                                if unique_id in sent_otps:
                                    continue
                                sent_otps.add(unique_id)
                                otps.append({
                                    'range': range_name,
                                    'platform': platform,
                                    'code': code,
                                    'message': msg_text,
                                    'number': phone
                                })
                                print(f"[SUCCESS] OTP found:\nRange: {range_name},\nPlatform: {platform},\nNumber: {phone},\nCode: {code},\nMessage: {msg_text}\n")
                                sent_numbers.add(unique_number_key)
                            except Exception as e:
                                print(f"[WARN] Error extracting message for number {phone}: {e}")
                                continue
                        except Exception as e:
                            print(f"[WARN] Error extracting number card {card_idx}: {e}")
                            continue
                except Exception as e:
                    print(f"[WARN] Error extracting range block {r_idx}: {e}")
                    continue
        except Exception as e:
            print(f"\033[91m[ERROR]\033[0m ❌ Error scraping OTPs: {e}")
        print(f"\033[96m[INFO]\033[0m 🟢 Total OTPs scraped: {len(otps)}")
        return otps

    def close(self):
        if self.driver:
            self.driver.quit()
            print("\033[96m[INFO]\033[0m 👋 Chrome driver closed.")

# ===================== Telegram Message Sender =====================
async def send_otp_to_telegram(otp):
    try:
        clean_message = otp['message'].replace('<', '&lt;').replace('>', '&gt;')
        flag = get_country_flag(otp['range'])
        country_with_flag = f"{flag} {otp['range']}" if flag else otp['range']
        message = TELEGRAM_MSG_TEMPLATE.format(
            range=country_with_flag,
            platform=otp['platform'],
            number=otp['number'],
            code=otp['code'],
            message=clean_message
        )
        
        # Create inline keyboard with Main Channel button
        keyboard = [
            [InlineKeyboardButton("Main Channel", url="https://t.me/+UumXK3D0Cf4xOTVl")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await bot.send_message(
            chat_id=TE['chat_id'], 
            text=message, 
            parse_mode='HTML', 
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )
        print(f"\033[92m[SUCCESS]\033[0m ✉️ OTP sent to Telegram: {otp['code']} [{otp['platform']}] | {otp['number']}")
    except Exception as e:
        print(f"\033[91m[ERROR]\033[0m ❌ Failed to send OTP to Telegram: {e}")

def save_cookies(driver, path):
    with open(path, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)

def load_cookies(driver, path):
    with open(path, 'rb') as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            if isinstance(cookie.get('expiry', None), float):
                cookie['expiry'] = int(cookie['expiry'])
            try:
                driver.add_cookie(cookie)
            except WebDriverException:
                pass

def login_with_cookies_or_credentials(driver, email, password, login_url, cookies_file=COOKIES_FILE):
    driver.get(login_url)
    logged_in = False
    if os.path.exists(cookies_file):
        print("\033[96m[INFO]\033[0m 🍪 Loading cookies for auto-login...")
        driver.delete_all_cookies()
        load_cookies(driver, cookies_file)
        driver.refresh()
        try:
            driver.find_element(By.XPATH, "//a[contains(text(), 'Logout') or contains(text(), 'Profile')]")
            print("\033[92m[SUCCESS]\033[0m 🔓 Auto-login with cookies successful!")
            logged_in = True
        except NoSuchElementException:
            print("\033[93m[WARN]\033[0m ⚠️  Cookies expired or invalid. Logging in with credentials...")
    if not logged_in:
        try:
            email_input = driver.find_element(By.NAME, 'email')
            password_input = driver.find_element(By.NAME, 'password')
            email_input.clear()
            email_input.send_keys(email)
            password_input.clear()
            password_input.send_keys(password)
            password_input.submit()
            time.sleep(5)
            try:
                driver.find_element(By.XPATH, "//a[contains(text(), 'Logout') or contains(text(), 'Profile')]")
                print("\033[92m[SUCCESS]\033[0m 🔑 Login with credentials successful!")
                save_cookies(driver, cookies_file)
                print("\033[96m[INFO]\033[0m 🍪 Cookies saved for future auto-login.")
            except NoSuchElementException:
                print("\033[91m[ERROR]\033[0m ❌ Login failed!")
                raise Exception("Login failed!")
        except Exception as e:
            print(f"\033[91m[ERROR]\033[0m ❌ Login failed with credentials: {e}")
            raise

# ===================== Main Loop =====================
async def main():
    print("\033[96m[INFO]\033[0m 🚦 Starting main loop...")
    scraper = IVASmsReceivedScraper(headless=True)  # Use headless for speed use [False]
    while True:
        try:
            login_with_cookies_or_credentials(scraper.driver, IV['email'], IV['password'], IV['login_url'])
            scraper.goto_received_page()
            while True:
                otps = scraper.scrape_all_otps()  # Complete scraping first
                if otps:
                    print(f"[INFO] Found {len(otps)} new OTPs. Sending...")
                    for otp in otps:
                        await send_otp_to_telegram(otp)
                    print("[INFO] All OTPs sent. Waiting 3 seconds before reload...")
                    time.sleep(3)  # Wait 3 seconds after sending
                    scraper.reload_received_page()  # Then reload
                else:
                    print("[WAIT] 🟢 No new OTPs. Reloading page...")
                    scraper.reload_received_page()
        except Exception as e:
            print(f"[ERROR] Main loop error or session expired: {e}")
            print("[INFO] Attempting to re-login and resume...")
            try:
                scraper.close()
            except:
                pass
            scraper = IVASmsReceivedScraper(headless=True)
            continue

if __name__ == "__main__":
    asyncio.run(main())