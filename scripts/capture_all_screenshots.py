import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def capture_dashboard_screenshots():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "screenshots")
    os.makedirs(output_dir, exist_ok=True)

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1200')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=options)
    driver.get("http://localhost:8501")
    time.sleep(8)

    pages = [
        ("Executive Overview", "01_executive_overview.png"),
        ("Customer 360", "02_customer_360.png"),
        ("Marketing Attribution", "03_marketing_attribution.png"),
        ("Paid Campaign Performance", "04_paid_campaign_performance.png")
    ]

    for page_name, filename in pages:
        print(f"Navigating to {page_name}...")
        try:
            # Find the radio button label matching page_name
            labels = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='stRadio'] label")
            target_label = None
            for lbl in labels:
                if page_name in lbl.text:
                    target_label = lbl
                    break
            
            if target_label:
                driver.execute_script("arguments[0].click();", target_label)
                time.sleep(6)  # Allow charts to render
            else:
                print(f"Warning: Label for '{page_name}' not found!")

            file_path = os.path.join(output_dir, filename)
            driver.save_screenshot(file_path)
            print(f"Captured: {filename} ({os.path.getsize(file_path):,} bytes)")

        except Exception as e:
            print(f"Error capturing {page_name}: {e}")

    driver.quit()
    print("All screenshots captured successfully!")

if __name__ == "__main__":
    capture_dashboard_screenshots()

