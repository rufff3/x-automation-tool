import time
import random
import os
import re
import json
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import glob

TARGET_POST_URL_FOR_COMMENT = "https://x.com/NAMAPENGGUNA/status/NOMOR_STATUS_POSTINGAN" # Ganti dengan URL target untuk Menu 3 (Auto Komen), bisa dikosongkan.
JEDA_ANTAR_AKSI_DETIK = (5, 10) # Jeda waktu acak antar setiap aksi (follow, repost, komen) dalam satuan DETIK.
JEDA_ANTAR_AKUN_DETIK = (20, 30) # Jeda waktu acak antar setiap akun dalam satuan DETIK.

def get_chrome_options(headless=True):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if headless:
        options.add_argument("--headless=new"); options.add_argument("--window-size=1920,1080"); options.add_argument("--log-level=3")
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"]); options.add_experimental_option('useAutomationExtension', False)
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
            print("⚠️  Peringatan: File 'cookies.txt' kosong.")
            return []
        json_string = re.sub(r']\s*\[', '],[', content)
        json_string = f"[{json_string}]"

        try:
            cookies_list = json.loads(json_string)
            if isinstance(cookies_list, list) and all(isinstance(i, list) for i in cookies_list):
                return cookies_list
            else:
                print("🛑 Error: Struktur JSON setelah diproses tidak valid. Seharusnya list dari list.")
                return None
        except json.JSONDecodeError as e:
            print(f"🛑 Error: Gagal mem-parsing konten 'cookies.txt' sebagai JSON. Error: {e}")
            print("   Pastikan format di cookies.txt adalah blok-blok JSON array yang dipisahkan baris baru.")
            return None

    except FileNotFoundError:
        print("🛑 Error: File 'cookies.txt' tidak ditemukan.")
        return None
    except Exception as e:
        print(f"🛑 Error tidak terduga saat memuat cookies: {e}")
        traceback.print_exc()
        return None

def load_cookies_from_json():
    try:
        with open('cookies.json', 'r', encoding='utf-8') as f: return json.load(f)
    except FileNotFoundError: print("🛑 Error: File 'cookies.json' tidak ditemukan. Jalankan Menu 0 terlebih dahulu."); return None
    except json.JSONDecodeError: print("🛑 Error: Format 'cookies.json' rusak. Coba jalankan ulang Menu 0."); return None

def login_and_verify(driver, account_cookies):
    driver.get("https://x.com")
    time.sleep(2)
    prepared_cookies = clean_and_prepare_cookies_for_selenium(account_cookies)
    for cookie in prepared_cookies: driver.add_cookie(cookie)
    driver.refresh()
    time.sleep(5)
    return not ("login" in driver.current_url or "flow" in driver.current_url)

def menu_0_proses_cookies():
    print("\n--- [MENU 0] Periksa & Simpan Format Cookies ---")
    raw_cookies_list = load_cookies_from_multiline_txt()
    if not raw_cookies_list:
        print("\nTidak ada data cookies yang valid untuk diproses."); return
    try:
        with open('cookies.json', 'w', encoding='utf-8') as f: json.dump(raw_cookies_list, f, indent=2)
        print(f"\n✅ Berhasil! {len(raw_cookies_list)} akun telah disimpan ke 'cookies.json'.")
    except Exception as e:
        print(f"\n🛑 Gagal menyimpan file 'cookies.json'. Error: {e}")

def menu_1_auto_follow():
    print("\n--- [MENU 1] Memulai Auto Follow ---")
    target_input = input("Masukkan link profil target (pisahkan dengan koma): ")
    if not target_input.strip(): return
    targets = [urlparse(url.strip()).path.strip('/') for url in target_input.split(',') if urlparse(url.strip()).path.strip('/')]
    cookies_list = load_cookies_from_json()
    if not cookies_list: return
    for index, account_cookies in enumerate(cookies_list):
        print(f"\n---> Memulai Proses untuk Akun #{index + 1}...")
        driver = None
        try:
            driver = webdriver.Chrome(options=get_chrome_options(headless=True))
            wait = WebDriverWait(driver, 20)
            if not login_and_verify(driver, account_cookies):
                print(f"🛑 Gagal login. Melewati."); continue
            print(f"✅ Login berhasil.")
            for user in targets:
                driver.get(f"https://x.com/{user}")
                try:
                    follow_button_xpath = "//button[descendant::span[text()='Follow' or text()='Ikuti']]"
                    wait.until(EC.element_to_be_clickable((By.XPATH, follow_button_xpath))).click()
                    print(f"   ✅ Berhasil follow @{user}.")
                    time.sleep(random.uniform(JEDA_ANTAR_AKSI_DETIK[0], JEDA_ANTAR_AKSI_DETIK[1]))
                except Exception:
                    print(f"   - Gagal follow @{user} (sudah difollow/dilindungi).")
        except Exception: traceback.print_exc()
        finally:
            if driver: driver.quit()
        if index < len(cookies_list) - 1:
            jeda = random.uniform(JEDA_ANTAR_AKUN_DETIK[0], JEDA_ANTAR_AKUN_DETIK[1])
            print(f"\n--- Jeda selama {jeda:.1f} detik...")
            time.sleep(jeda)
    print("\n--- Auto Follow Selesai ---")

def menu_2_auto_retweet():
    print("\n--- [MENU 2] Memulai Auto Retweet ---")
    target_input = input("Masukkan link postingan (pisahkan dengan koma): ")
    if not target_input.strip(): return
    targets = [url.strip() for url in target_input.split(',')]
    cookies_list = load_cookies_from_json()
    if not cookies_list: return
    for index, account_cookies in enumerate(cookies_list):
        print(f"\n---> Memulai Proses untuk Akun #{index + 1}...")
        driver = None
        try:
            driver = webdriver.Chrome(options=get_chrome_options(headless=True))
            wait = WebDriverWait(driver, 25)
            if not login_and_verify(driver, account_cookies):
                print(f"🛑 Gagal login. Melewati."); continue
            print(f"✅ Login berhasil.")
            for url in targets:
                try:
                    tweet_id = url.split('?')[0].split('/')[-1]
                    if not tweet_id.isdigit(): continue
                    driver.get(f"https://x.com/intent/retweet?tweet_id={tweet_id}")
                    repost_button_xpath = "//button[@data-testid='confirmationSheetConfirm']"
                    print(f"   Mencari tombol konfirmasi untuk: {url}")
                    wait.until(EC.element_to_be_clickable((By.XPATH, repost_button_xpath))).click()
                    print(f"   ✅ Berhasil repost.")
                    time.sleep(random.uniform(JEDA_ANTAR_AKSI_DETIK[0], JEDA_ANTAR_AKSI_DETIK[1]))
                except Exception:
                    print(f"   - Gagal repost {url} (mungkin sudah di-repost).")
        except Exception: traceback.print_exc()
        finally:
            if driver: driver.quit()
        if index < len(cookies_list) - 1:
            jeda = random.uniform(JEDA_ANTAR_AKUN_DETIK[0], JEDA_ANTAR_AKUN_DETIK[1])
            print(f"\n--- Jeda selama {jeda:.1f} detik...")
            time.sleep(jeda)
    print("\n--- Auto Retweet Selesai ---")

def menu_3_auto_comment():
    """MENU 3: Melakukan auto-komen ke target link."""
    print("\n--- [MENU 3] Memulai Auto Komen ---")
    try:
        with open('komentartwitter.txt', 'r', encoding='utf-8') as f: comments = [b.strip() for b in re.split(r'\n\s*\n', f.read()) if b.strip()]
    except FileNotFoundError:
        print("🛑 Error: File 'komentartwitter.txt' tidak ditemukan."); return
    if not comments: print("🛑 File 'komentartwitter.txt' kosong."); return
        
    target_input = input("Masukkan link postingan untuk dikomentari (pisahkan dengan koma): ")
    if not target_input.strip(): return
    
    target_urls = [url.strip() for url in target_input.split(',')]
    cookies_list = load_cookies_from_json()
    if not cookies_list: return
    for url in target_urls:
        print(f"\n=== Memproses Target Postingan: {url} ===")
        for index, account_cookies in enumerate(cookies_list):
            if index >= len(comments):
                print("\nSemua komentar dari 'komentartwitter.txt' sudah digunakan.")
                break 
            
            comment_text = comments[index]
            print(f"\n---> Proses Akun #{index + 1} | Komen: '{comment_text[:50]}...'")
            driver = None
            try:
                driver = webdriver.Chrome(options=get_chrome_options(headless=True))
                wait = WebDriverWait(driver, 25)
                if not login_and_verify(driver, account_cookies):
                    print(f"🛑 Gagal login Akun #{index + 1}. Melewati."); continue
                
                print(f"✅ Login Akun #{index + 1} berhasil.")
                driver.get(url)
                comment_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='tweetTextarea_0']")))
                comment_box.send_keys(comment_text)
                reply_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='tweetButtonInline']")))
                reply_button.click()
                
                print("     ✅ Komentar berhasil dikirim!")
                time.sleep(random.uniform(JEDA_ANTAR_AKSI_DETIK[0], JEDA_ANTAR_AKSI_DETIK[1]))
            except Exception:
                print(f"     ❌ Gagal memproses untuk Akun #{index + 1}:")
                traceback.print_exc()
            finally:
                if driver: driver.quit()
            if index < len(cookies_list) - 1:
                jeda = random.uniform(JEDA_ANTAR_AKUN_DETIK[0], JEDA_ANTAR_AKUN_DETIK[1])
                print(f"\n--- Jeda selama {jeda:.1f} detik...")
                time.sleep(jeda)
                
    print("\n--- Auto Komen Selesai ---")

if __name__ == "__main__":
    while True:
        print("\n" + "="*15 + " TOOLS TWITTER " + "="*15)
        print("0. Periksa & Simpan Format Cookies")
        print("1. Jalankan Auto Follow")
        print("2. Jalankan Auto Retweet (Fixed)")
        print("3. Jalankan Auto Komen (Fixed)")
        print("4. Keluar")
        print("="*56)
        choice = input("Masukkan pilihan Anda (0-4): ")
        if choice == '0': menu_0_proses_cookies()
        elif choice == '1': menu_1_auto_follow()
        elif choice == '2': menu_2_auto_retweet()
        elif choice == '3': menu_3_auto_comment()
        elif choice == '4': print("Terima kasih."); break
        else: print("Pilihan tidak valid.")
        input("\nTekan Enter untuk kembali ke menu...")