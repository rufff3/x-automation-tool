import time
import random
import os
import re
import json
import traceback
import glob
from urllib.parse import urlparse, quote_plus, quote
import pyfiglet
from colorama import Fore, Style, init
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
init(autoreset=True)

# Palet Warna
HIJAU = Fore.GREEN
MERAH = Fore.RED
KUNING = Fore.YELLOW
BIRU = Fore.BLUE
MAGENTA = Fore.MAGENTA
CYAN = Fore.CYAN
TEBAL = Style.BRIGHT

JEDA_ANTAR_AKSI_DETIK = (5, 10) #ATUREN DEWE
JEDA_ANTAR_AKUN_DETIK = (20, 30) #ATUREN DEWE

def tampilkan_banner(teks, warna=MAGENTA, font="slant"):
    banner_text = pyfiglet.figlet_format(teks, font=font, width=100)
    print(warna + TEBAL + banner_text)

def get_chrome_options(headless=True):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--log-level=3")
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
    return options

def clean_and_prepare_cookies_for_selenium(raw_cookies):
    cleaned_cookies = []
    for cookie in raw_cookies:
        clean_cookie = {'name': cookie['name'], 'value': cookie['value']}
        if 'domain' in cookie: clean_cookie['domain'] = cookie.get('domain')
        if 'path' in cookie: clean_cookie['path'] = cookie.get('path')
        if 'expirationDate' in cookie: clean_cookie['expiry'] = int(cookie['expirationDate'])
        if 'secure' in cookie: clean_cookie['secure'] = cookie.get('secure')
        if 'httpOnly' in cookie: clean_cookie['httpOnly'] = cookie.get('httpOnly')
        if 'sameSite' in cookie and cookie['sameSite'] is not None:
            samesite_value = cookie['sameSite'].lower()
            if samesite_value == 'no_restriction': clean_cookie['sameSite'] = 'None'
            elif samesite_value in ['lax', 'strict']: clean_cookie['sameSite'] = samesite_value.capitalize()
        cleaned_cookies.append(clean_cookie)
    return cleaned_cookies

def load_cookies_from_multiline_txt():
    try:
        with open('cookies.txt', 'r', encoding='utf-8') as f:
            content = f.read().strip()
        if not content:
            print(f"{KUNING}⚠️  Peringatan: File 'cookies.txt' kosong.")
            return []
        json_string = re.sub(r']\s*\[', '],[', content)
        json_string = f"[{json_string}]"
        cookies_list = json.loads(json_string)
        if isinstance(cookies_list, list) and all(isinstance(i, list) for i in cookies_list):
            return cookies_list
        else:
            print(f"{MERAH}🛑 Error: Struktur JSON tidak valid.")
            return None
    except FileNotFoundError:
        print(f"{MERAH}🛑 Error: File 'cookies.txt' tidak ditemukan.")
    except json.JSONDecodeError as e:
        print(f"{MERAH}🛑 Error parsing 'cookies.txt': {e}")
    except Exception as e:
        print(f"{MERAH}🛑 Error tidak terduga: {e}")
        traceback.print_exc()
    return None

def load_cookies_from_json():
    try:
        with open('cookies.json', 'r', encoding='utf-8') as f: return json.load(f)
    except FileNotFoundError: print(f"{MERAH}🛑 Error: File 'cookies.json' tidak ditemukan. Jalankan Menu 0."); return None
    except json.JSONDecodeError: print(f"{MERAH}🛑 Error: Format 'cookies.json' rusak. Jalankan ulang Menu 0."); return None

def login_and_verify(driver, account_cookies):
    driver.get("https://x.com")
    time.sleep(2)
    prepared_cookies = clean_and_prepare_cookies_for_selenium(account_cookies)
    for cookie in prepared_cookies: driver.add_cookie(cookie)
    driver.refresh()
    time.sleep(5)
    return "login" not in driver.current_url and "flow" not in driver.current_url

def menu_0_proses_cookies():
    os.system('cls' if os.name == 'nt' else 'clear')
    tampilkan_banner("Proses Cookies", warna=CYAN)
    raw_cookies_list = load_cookies_from_multiline_txt()
    if not raw_cookies_list:
        print(f"\n{KUNING}Tidak ada data cookies valid untuk diproses."); return
    try:
        with open('cookies.json', 'w', encoding='utf-8') as f: json.dump(raw_cookies_list, f, indent=2)
        print(f"\n{HIJAU}✅ Berhasil! {len(raw_cookies_list)} akun telah disimpan ke 'cookies.json'.")
    except Exception as e:
        print(f"\n{MERAH}🛑 Gagal menyimpan 'cookies.json'. Error: {e}")

def menu_1_auto_follow():
    os.system('cls' if os.name == 'nt' else 'clear')
    tampilkan_banner("Auto Follow", warna=HIJAU)
    target_input = input(f"{MAGENTA}Masukkan link profil target (pisahkan koma): ")
    if not target_input.strip(): return
    targets = [urlparse(url.strip()).path.strip('/') for url in target_input.split(',') if urlparse(url.strip()).path.strip('/')]
    cookies_list = load_cookies_from_json()
    if not cookies_list: return

    for index, account_cookies in enumerate(cookies_list):
        print(f"\n{TEBAL}{BIRU}---> Memproses Akun #{index + 1}...{Style.RESET_ALL}")
        driver = None
        try:
            driver = webdriver.Chrome(options=get_chrome_options(headless=True))
            if not login_and_verify(driver, account_cookies):
                print(f"{MERAH}🛑 Gagal login. Melewati."); continue
            print(f"{HIJAU}✅ Login berhasil.")
            for user in targets:
                driver.get(f"https://x.com/{user}")
                try:
                    follow_btn_xpath = "//button[descendant::span[text()='Follow' or text()='Ikuti']]"
                    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, follow_btn_xpath))).click()
                    print(f"   {HIJAU}✅ Berhasil follow @{user}.")
                    time.sleep(random.uniform(*JEDA_ANTAR_AKSI_DETIK))
                except Exception:
                    print(f"   {KUNING}- Gagal follow @{user} (mungkin sudah difollow).")
        except Exception: traceback.print_exc()
        finally:
            if driver: driver.quit()
        if index < len(cookies_list) - 1:
            jeda = random.uniform(*JEDA_ANTAR_AKUN_DETIK)
            print(f"\n{CYAN}--- Jeda selama {jeda:.1f} detik...{Style.RESET_ALL}")
            time.sleep(jeda)
    print(f"\n{TEBAL}{HIJAU}--- Auto Follow Selesai ---{Style.RESET_ALL}")

def menu_2_auto_retweet():
    os.system('cls' if os.name == 'nt' else 'clear')
    tampilkan_banner("Auto Retweet", warna=HIJAU)
    target_input = input(f"{MAGENTA}Masukkan link postingan (pisahkan dengan koma): ")
    if not target_input.strip(): return
    targets = [url.strip() for url in target_input.split(',')]
    cookies_list = load_cookies_from_json()
    if not cookies_list: return
    for index, account_cookies in enumerate(cookies_list):
        print(f"\n{TEBAL}{BIRU}---> Memproses Akun #{index + 1}...{Style.RESET_ALL}")
        driver = None
        try:
            driver = webdriver.Chrome(options=get_chrome_options(headless=True))
            wait = WebDriverWait(driver, 25)
            if not login_and_verify(driver, account_cookies):
                print(f"{MERAH}🛑 Gagal login. Melewati."); continue
            print(f"{HIJAU}✅ Login berhasil.")
            for url in targets:
                try:
                    tweet_id = url.split('?')[0].split('/')[-1]
                    if not tweet_id.isdigit(): continue
                    driver.get(f"https://x.com/intent/retweet?tweet_id={tweet_id}")
                    repost_button_xpath = "//button[@data-testid='confirmationSheetConfirm']"
                    wait.until(EC.element_to_be_clickable((By.XPATH, repost_button_xpath))).click()
                    print(f"   {HIJAU}✅ Berhasil repost: {url.split('?')[0]}")
                    time.sleep(random.uniform(*JEDA_ANTAR_AKSI_DETIK))
                except Exception:
                    print(f"   {KUNING}- Gagal repost {url} (mungkin sudah di-repost).")
        except Exception: traceback.print_exc()
        finally:
            if driver: driver.quit()
        if index < len(cookies_list) - 1:
            jeda = random.uniform(*JEDA_ANTAR_AKUN_DETIK)
            print(f"\n{CYAN}--- Jeda selama {jeda:.1f} detik...{Style.RESET_ALL}")
            time.sleep(jeda)
    print(f"\n{TEBAL}{HIJAU}--- Auto Retweet Selesai ---{Style.RESET_ALL}")

def menu_3_auto_comment():
    os.system('cls' if os.name == 'nt' else 'clear')
    tampilkan_banner("Auto Comment", warna=HIJAU)
    try:
        with open('komentartwitter.txt', 'r', encoding='utf-8') as f: comments = [b.strip() for b in re.split(r'\n\s*\n', f.read()) if b.strip()]
    except FileNotFoundError:
        print(f"{MERAH}🛑 Error: File 'komentartwitter.txt' tidak ditemukan."); return
    if not comments: print(f"{MERAH}🛑 File 'komentartwitter.txt' kosong."); return
    target_input = input(f"{MAGENTA}Masukkan link postingan untuk dikomentari (pisahkan koma): ")
    if not target_input.strip(): return
    target_urls = [url.strip() for url in target_input.split(',')]
    cookies_list = load_cookies_from_json()
    if not cookies_list: return
    for url in target_urls:
        print(f"\n{TEBAL}{BIRU}=== Memproses Target Postingan: {url} ==={Style.RESET_ALL}")
        for index, account_cookies in enumerate(cookies_list):
            if index >= len(comments):
                print(f"\n{KUNING}Semua komentar dari 'komentartwitter.txt' sudah digunakan.")
                break
            comment_text = comments[index]
            print(f"\n{TEBAL}{BIRU}---> Proses Akun #{index + 1} | Komen: '{comment_text[:50]}...'{Style.RESET_ALL}")
            driver = None
            try:
                driver = webdriver.Chrome(options=get_chrome_options(headless=True))
                wait = WebDriverWait(driver, 25)
                if not login_and_verify(driver, account_cookies):
                    print(f"{MERAH}🛑 Gagal login Akun #{index + 1}. Melewati."); continue
                print(f"{HIJAU}✅ Login Akun #{index + 1} berhasil.")
                driver.get(url)
                comment_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='tweetTextarea_0']")))
                comment_box.send_keys(comment_text)
                reply_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='tweetButtonInline']")))
                reply_button.click()
                print(f"     {HIJAU}✅ Komentar berhasil dikirim!")
                time.sleep(random.uniform(*JEDA_ANTAR_AKSI_DETIK))
            except Exception:
                print(f"     {MERAH}❌ Gagal memproses untuk Akun #{index + 1}:")
                traceback.print_exc()
            finally:
                if driver: driver.quit()
            if index < len(cookies_list) - 1:
                jeda = random.uniform(*JEDA_ANTAR_AKUN_DETIK)
                print(f"\n{CYAN}--- Jeda selama {jeda:.1f} detik...{Style.RESET_ALL}")
                time.sleep(jeda)
    print(f"\n{TEBAL}{HIJAU}--- Auto Komen Selesai ---{Style.RESET_ALL}")

def menu_4_auto_quote():
    os.system('cls' if os.name == 'nt' else 'clear')
    tampilkan_banner("Auto Quote", warna=HIJAU)
    try:
        with open('quote.txt', 'r', encoding='utf-8') as f:
            quotes = [q.strip() for q in re.split(r'\n\s*\n', f.read()) if q.strip()]
        if not quotes:
            print(f"{MERAH}🛑 Error: File 'quote.txt' kosong."); return
    except FileNotFoundError:
        print(f"{MERAH}🛑 Error: File 'quote.txt' tidak ditemukan."); return
    target_url = input(f"{MAGENTA}🔗 Masukkan link postingan X yang ingin di-quote: ").strip()
    if not target_url.startswith(("https://x.com/", "https://twitter.com/")):
        print(f"{KUNING}URL sepertinya tidak valid."); return
    cookies_list = load_cookies_from_json()
    if not cookies_list: return
    print(f"\n{HIJAU}👍 Siap memproses {len(cookies_list)} akun dengan {len(quotes)} quote.")
    for index, account_cookies in enumerate(cookies_list):
        if index >= len(quotes):
            print(f"\n{KUNING}⚠️ Semua quote dari file telah digunakan."); break
        quote_text = quotes[index]
        nomor_akun = index + 1
        print(f"\n{TEBAL}{BIRU}---> Proses Akun #{nomor_akun} | Quote: '{quote_text[:50]}...'{Style.RESET_ALL}")
        driver = None
        try:
            driver = webdriver.Chrome(options=get_chrome_options(headless=True))
            driver.get("https://x.com")
            prepared_cookies = clean_and_prepare_cookies_for_selenium(account_cookies)
            for cookie in prepared_cookies:
                driver.add_cookie(cookie)
            base_url = "https://x.com/intent/post"
            encoded_url = quote_plus(target_url)
            encoded_text = quote_plus(quote_text)
            link_final = f"{base_url}?url={encoded_url}&text={encoded_text}"
            print(f"{BIRU}... Akun #{nomor_akun}: Navigasi ke halaman post.")
            driver.get(link_final)

            tombol_post_xpath = "//button[@data-testid='tweetButton']"
            wait = WebDriverWait(driver, 20)
            tombol_post = wait.until(EC.element_to_be_clickable((By.XPATH, tombol_post_xpath)))
            tombol_post.click()
            time.sleep(5)
            print(f"{HIJAU}✅ Berhasil! Akun #{nomor_akun} telah memposting quote.")
        except Exception:
            print(f"{MERAH}❌ Gagal memproses Quote untuk Akun #{nomor_akun}:")
            traceback.print_exc()
        finally:
            if driver: driver.quit()
        if index < len(cookies_list) - 1:
            jeda = random.uniform(*JEDA_ANTAR_AKUN_DETIK)
            print(f"\n{CYAN}--- Jeda antar akun selama {jeda:.1f} detik...{Style.RESET_ALL}")
            time.sleep(jeda)
    print(f"\n{TEBAL}{HIJAU}--- Auto Quote Selesai ---{Style.RESET_ALL}")

if __name__ == "__main__":
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        tampilkan_banner("Twitter Tools", warna=MAGENTA)
        tampilkan_banner("By Ruff", warna=BIRU, font="small")

        print(f"{CYAN} {'[0]'} Proses & Simpan Cookies")
        print(f"{CYAN} {'[1]'} Jalankan Auto Follow")
        print(f"{CYAN} {'[2]'} Jalankan Auto Retweet")
        print(f"{CYAN} {'[3]'} Jalankan Auto Komen")
        print(f"{CYAN} {'[4]'} Jalankan Auto Quote")
        print(f"{KUNING} {'[5]'} Keluar")
        print(f"{TEBAL}{MAGENTA}" + "="*56)

        choice = input(f"{TEBAL}Pilih menu: {Style.RESET_ALL}")

        if choice == '0': menu_0_proses_cookies()
        elif choice == '1': menu_1_auto_follow()
        elif choice == '2': menu_2_auto_retweet()
        elif choice == '3': menu_3_auto_comment()
        elif choice == '4': menu_4_auto_quote()
        elif choice == '5':
            print(f"{KUNING}Terima kasih!")
            break
        else:
            print(f"{MERAH}Pilihan tidak valid.")

        input(f"\n{KUNING}Tekan Enter untuk kembali ke menu...")
