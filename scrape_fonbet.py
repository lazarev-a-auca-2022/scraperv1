############
# 4.9.2025 #
############
import os
import json
from seleniumbase import Driver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
os.makedirs("outputs", exist_ok=True)
os.makedirs("logs", exist_ok=True)
def log(message):
    with open("logs/scrape_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

log("Starting scraper")
driver = Driver(uc=True)

try:
    driver.get("https://fonbet.kz/sports")
    log("Navigated to fonbet.kz/sports")
    if driver.is_element_present('iframe[title="Widget containing a Cloudflare security challenge"]'):
        log("Cloudflare CAPTCHA detected")
        print("CAPTCHA detected. Please solve it manually within 120 seconds.")
    else:
        log("No CAPTCHA detected")

    log("Waiting for betting odds to load")
    driver.wait_for_element_present(
        '//div[contains(@class, "factor-value--")]',  
        timeout=180
    )
    log("Odds detected, page likely loaded")

    time.sleep(20)
    log("Waited 20 seconds for dynamic content")

    log("Scrolling to load all events")
    body = driver.find_element(By.TAG_NAME, "body")
    for _ in range(5):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(2)
    log("Finished scrolling")

    driver.save_screenshot("outputs/screenshot.png")
    log("Screenshot saved to outputs/screenshot.png")
    with open("outputs/page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.get_page_source())
    log("Page source saved to outputs/page_source.html")

    event_rows = driver.find_elements(
        By.XPATH,
        '//div[.//span[contains(text(), "—")] and .//div[contains(@class, "factor-value--")]]'
    )
    log(f"Found {len(event_rows)} event rows")

    betting_data = []
    processed_events = set()

    for event in event_rows:
        try:
            teams = event.find_elements(By.XPATH, './/span[contains(text(), "—")]')
            if len(teams) >= 1:
                team_text = teams[0].text.strip()
                if "—" in team_text:
                    team1, team2 = team_text.split("—", 1)
                    team1 = team1.strip()
                    team2 = team2.strip()
                else:
                    log(f"Skipping event: cannot split team names ('{team_text}')")
                    continue
            else:
                log(f"Skipping event: no team names found")
                continue

            odds = event.find_elements(By.XPATH, './/div[contains(@class, "factor-value--")]')
            if len(odds) >= 3:
                try:
                    odd1 = odds[0].find_element(By.XPATH, './/div[contains(@class, "value--OUKql")]').text.strip()
                    oddX = odds[1].find_element(By.XPATH, './/div[contains(@class, "value--OUKql")]').text.strip()
                    odd2 = odds[2].find_element(By.XPATH, './/div[contains(@class, "value--OUKql")]').text.strip()
                except:
                    odd1 = odds[0].find_element(By.XPATH, './/div[contains(@class, "value--")]').text.strip()
                    oddX = odds[1].find_element(By.XPATH, './/div[contains(@class, "value--")]').text.strip()
                    odd2 = odds[2].find_element(By.XPATH, './/div[contains(@class, "value--")]').text.strip()
            else:
                log(f"Skipping event: insufficient odds ({len(odds)} found)")
                continue

            # store data
            event_key = f"{team1}-{team2}"
            if event_key in processed_events:
                log(f"Skipping duplicate event: {event_key}")
                continue
            processed_events.add(event_key)

            betting_data.append({
                "team1": team1,
                "team2": team2,
                "odd1": odd1,
                "oddX": oddX,
                "odd2": odd2
            })
            log(f"Successfully extracted event: {team1} vs {team2}")
        except Exception as e:
            log(f"Error extracting event data: {str(e)}")
            continue

    log(f"Extracted {len(betting_data)} betting events")

    # write to JSON file
    with open("outputs/betting_data.json", "w", encoding="utf-8") as f:
        json.dump(betting_data, f, ensure_ascii=False, indent=4)
    log("Betting data saved to outputs/betting_data.json")

except Exception as e:
    log(f"Scraper failed: {str(e)}")
    driver.save_screenshot("outputs/error_screenshot.png")
    log("Error screenshot saved to outputs/error_screenshot.png")
    if "timeout" in str(e).lower():
        log("Timeout exceeded. Betting data might not have loaded.")
    raise

finally:
    driver.quit()
    log("Browser closed")