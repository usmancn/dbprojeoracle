import os
import time
import oracledb
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()


def get_data_count():
    try:
        # Oracle veritabanına bağlantı (.env dosyasından)
        conn = oracledb.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            dsn=f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_SERVICE_NAME')}"
        )

        cursor = conn.cursor()

        # Addresses tablosundan kayıt sayısını al
        cursor.execute(f"SELECT COUNT(*) FROM {os.getenv('DB_USER')}.ADDRESSES")
        count = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return count

    except Exception as e:
        print(f"DB hatası: {e}")
        return 0


# Selenium kurulumu
service = Service(os.getenv('CHROMEDRIVER_PATH'))
driver = webdriver.Chrome(service=service)
driver.maximize_window()
driver.implicitly_wait(int(os.getenv('IMPLICIT_WAIT')))

try:
    # Ana sayfaya git
    driver.get(os.getenv('SELENIUM_URL'))

    # Select kısmından projeyi seç
    project_selector = os.getenv('XPATH_PROJECT_SELECTOR')
    driver.find_element(By.XPATH, project_selector).click()

    # Proje seçimini xpath'e dinamik olarak ekle
    project_xpath = os.getenv('XPATH_PROJECT_OPTION').format(project_name=os.getenv('PROJECT_NAME'))
    driver.find_element(By.XPATH, project_xpath).click()

    # Case kısmına gel
    case_xpath = os.getenv('XPATH_CASE_BUTTON').format(case_name=os.getenv('CASE_NAME'))
    driver.find_element(By.XPATH, case_xpath).click()

    # Hedef veri sayısı ve buton xpath'leri
    target_data = int(os.getenv('TARGET_DATA_COUNT'))
    run_button_1_xpath = os.getenv('XPATH_RUN_BUTTON_1')
    run_button_2_xpath = os.getenv('XPATH_RUN_BUTTON_2')
    sleep_interval = int(os.getenv('SLEEP_INTERVAL'))
    error_wait_time = int(os.getenv('ERROR_WAIT_TIME'))

    current_run = 0

    print("Başlangıç veri sayısı kontrol ediliyor...")
    initial_count = get_data_count()
    print(f"{os.getenv('DB_USER')}.ADDRESSES tablosunda şuan {initial_count:,} kayıt var")

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
            driver.find_element(By.XPATH, run_button_1_xpath).click()
            current_run += 1
            print(f"Run {current_run} başlatıldı")

            # İkinci RUN butonuna bas
            driver.find_element(By.XPATH, run_button_2_xpath).click()
            print(f"Veri üretimi başlatıldı")

            # İşlem bitene kadar bekle
            while True:
                time.sleep(sleep_interval)
                run_button = driver.find_element(By.XPATH, run_button_1_xpath)
                if run_button.is_enabled():
                    print("İşlem tamamlandı!")
                    break

            # İşlem bittikten sonra DB'yi kontrol et
            new_count = get_data_count()
            added = new_count - current_count
            print(f"{added:,} yeni kayıt eklendi (Toplam: {new_count:,})")

        except Exception as e:
            print(f"Hata: {e}")
            print(f"{error_wait_time} saniye bekleyip devam")
            time.sleep(error_wait_time)
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