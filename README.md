📌 DESKRIPSI
---------------
Script otomatisasi ini digunakan untuk menjalankan aksi otomatis pada platform X (sebelumnya Twitter), seperti:
- Auto Follow
- Auto Retweet
- Auto Komen
- Auto Quote
- Pemrosesan cookies

Script ini memanfaatkan Selenium WebDriver untuk mengendalikan browser dan login menggunakan cookies dari beberapa akun.

📁 STRUKTUR FILE YANG DIPERLUKAN
----------------------------------
Pastikan file berikut tersedia dalam direktori yang sama:
1. cookies.txt             → berisi cookies mentah dari browser (multi akun)
2. cookies.json            → file hasil proses cookies.txt
3. komentartwitter.txt     → isi komentar untuk fitur Auto Komen (satu komentar per akun, pisahkan dengan enter 2x)
4. quote.txt               → isi teks quote (satu quote per akun, pisahkan dengan enter 2x)

🧾 INSTALASI DEPENDENSI
--------------------------
Sebelum menjalankan script, install semua dependensi Python berikut:

pip install selenium pyfiglet colorama webdriver-manager

📦 LIBRARY YANG DIGUNAKAN
--------------------------
- selenium
- pyfiglet
- colorama
- json, os, time, re, random, glob, traceback (built-in)
- webdriver-manager

💻 CARA MENJALANKAN SCRIPT
----------------------------
1. Jalankan script dengan perintah:
python namascriptkamu.py

2. Pilih menu yang tersedia:
   [0] Proses & Simpan Cookies dari cookies.txt ke cookies.json  
   [1] Jalankan Auto Follow  
   [2] Jalankan Auto Retweet  
   [3] Jalankan Auto Komen  
   [4] Jalankan Auto Quote  
   [5] Keluar dari program  

📂 FORMAT COOKIES.TXT
-------------------------
- Masukkan cookies dari ekstensi berikut : https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm.
- Letakkan cookies beberapa akun secara berurutan di satu file dengan pemisah antar akun:
  [ {cookie1}, {cookie2}, ... ]
  [ {cookie1}, {cookie2}, ... ]

🗂 FORMAT FILE KOMENTAR & QUOTE
----------------------------------
- komentartwitter.txt → setiap komentar dipisah dengan dua baris kosong
- quote.txt → setiap baris quote dipisah dengan dua baris kosong

🛠 FITUR YANG TERSEDIA
-------------------------
✅ Login otomatis menggunakan cookies  
✅ Auto Follow akun target  
✅ Auto Retweet postingan tertentu  
✅ Auto Komentar ke tweet dengan komentar per akun  
✅ Auto Quote postingan dengan teks yang berbeda per akun  
✅ Support banyak akun  

🧩 CATATAN TAMBAHAN
-------------------------
- Script menggunakan mode headless, jadi Chrome akan berjalan di background.
- Jeda antar aksi dan akun bisa diatur manual di bagian:
  JEDA_ANTAR_AKSI_DETIK = (5, 10)
  JEDA_ANTAR_AKUN_DETIK = (20, 30)
- Jika cookies salah atau kadaluarsa, login akan gagal dan akun dilewati.

-------------------------
Gunakan script ini dengan bijak dan tanggung jawab.Jangan gunakan secara berlebihan yang dapat menyebabkan akun terkena limit, restrict, atau banned.Beristirahatlah di antara sesi agar aman dari deteksi sistem. Selalu cek hasil dengan kepala dingin dan tidak tergesa-gesa.Script ini adalah alat bantu, bukan alat curang.
