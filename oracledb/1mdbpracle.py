import time
import oracledb
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def get_data_count():
    try:
        # Oracle veritabanına bağlantı
        conn = oracledb.connect(
            user="C##ECOMMERCE",
            password="oracle123",
            dsn="172.29.112.1:1521/MYCDB"
        )

        cursor = conn.cursor()

        # C##ECOMMERCE.ADDRESSES tablosundan kayıt sayısını al
        cursor.execute("SELECT COUNT(*) FROM C##ECOMMERCE.ADDRESSES")
        count = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return count

    except Exception as e:
        print(f"DB hatası: {e}")
        return 0


# Selenium kurulumu
service = Service("./chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.maximize_window()
driver.implicitly_wait(30)

try:
    driver.get("http://172.29.112.1:80")

    # Select kısmından projeyi seç
    driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-selector')]").click()
    driver.find_element(By.XPATH, "//div[contains(text(),'oracleproje')]").click()

    # Case kısmına gel
    driver.find_element(By.XPATH, "//span[text()='DATA GENERATION CASE']").click()

    # Hedef: 1 milyon data
    target_data = 1000000
    current_run = 0

    print("Başlangıç veri sayısı kontrol ediliyor...")
    initial_count = get_data_count()
    print(f"C##ECOMMERCE.ADDRESSES tablosunda şuan {initial_count:,} kayıt var")

    while True:
        # Her döngüde DB'yi kontrol et
        current_count = get_data_count()

        # Hedef sayıya ulaştık mı?
        if current_count >= target_data:
            print(f"HEDEF ULAŞILDI! {current_count:,} kayıt var!")
            break

        remaining = target_data - current_count
        print(f"Şuan: {current_count:,} | Hedefe kalan: {remaining:,}")

        try:
            # İlk run butonuna bas
            driver.find_element(By.XPATH, "//tbody//tr[1]//button[3]").click()
            current_run += 1
            print(f"Run {current_run} başlatıldı")

            # İkinci RUN butonuna bas
            driver.find_element(By.XPATH, "//button[contains(., 'RUN')]").click()
            print(f"Veri üretimi başlatıldı")

            # İşlem bitene kadar bekle
            while True:
                time.sleep(2)
                run_button = driver.find_element(By.XPATH, "//tbody//tr[1]//button[3]")
                if run_button.is_enabled():
                    print("İşlem tamamlandı!")
                    break

            # İşlem bittikten sonra DB'yi kontrol et
            new_count = get_data_count()
            added = new_count - current_count
            print(f"{added:,} yeni kayıt eklendi (Toplam: {new_count:,})")

        except Exception as e:
            print(f"Hata: {e}")
            print("5 saniye bekleyip devam")
            time.sleep(5)
            continue

    # Final rapor
    final_count = get_data_count()
    total_added = final_count - initial_count
    print(f"\nBAŞARILI")
    print(f"Başlangıç: {initial_count:,}")
    print(f"Son durum: {final_count:,}")
    print(f"Eklenen: {total_added:,}")
    print(f"Toplam run: {current_run}")

except Exception as e:
    print(f"Genel hata: {e}")

finally:
    input("Enter'a basınca kapanacak")
    driver.quit()