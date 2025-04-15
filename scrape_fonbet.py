import os
import json
import time
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

os.makedirs("outputs", exist_ok=True)
os.makedirs("logs", exist_ok=True)

def log(message):
    with open("logs/scrape_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def parse_betting_data(text):
    """Parse betting data from raw text"""
    betting_data = []
    # Split into lines and look for team names and odds patterns
    lines = text.split('\n')
    current_event = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for team name patterns (Team1 vs Team2, Team1 - Team2, etc)
        for separator in [" vs ", " - ", " — ", "—"]:
            if separator in line:
                parts = line.split(separator)
                if len(parts) == 2:
                    team1 = parts[0].strip()
                    team2 = parts[1].strip()
                    # Basic validation
                    if len(team1) > 1 and len(team2) > 1:
                        # Check it's not UI text
                        if not any(x in line.lower() for x in ["login", "register", "menu", "sports", "live"]):
                            current_event = {
                                "team1": team1,
                                "team2": team2,
                                "odd1": None,
                                "oddX": None, 
                                "odd2": None
                            }
                            break
        
        # Look for odds (groups of 3 numbers like "1.55 3.40 6.70")
        if current_event and not current_event["odd1"]:
            parts = line.split()
            if len(parts) >= 3:
                odds = []
                for part in parts[:3]:
                    try:
                        odd = float(part.replace(",", "."))
                        if 1.01 <= odd <= 30.0:  # Reasonable odds range
                            odds.append(odd)
                    except ValueError:
                        continue
                
                if len(odds) == 3:
                    current_event["odd1"] = str(odds[0])
                    current_event["oddX"] = str(odds[1]) 
                    current_event["odd2"] = str(odds[2])
                    betting_data.append(current_event)
                    current_event = {}
    
    return betting_data

log("Starting scraper")
driver = Driver(uc=True)

try:
    driver.get("https://fonbet.kz/sports")
    log("Navigated to fonbet.kz/sports")

    if driver.is_element_present(By.CSS_SELECTOR, 'iframe[title="Widget containing a Cloudflare security challenge"]'):
        log("Cloudflare CAPTCHA detected")
        print("CAPTCHA detected. Please solve it manually within 120 seconds.")
        time.sleep(120)  # Wait for manual CAPTCHA solving
    else:
        log("No CAPTCHA detected")

    log("Waiting for betting odds to load")
    driver.wait_for_element_present(
        '//div[contains(@class, "factor-value--")]',
        timeout=180
    )
    log("Odds detected, page likely loaded")

    time.sleep(10)
    log("Waited 10 seconds for dynamic content")

    # More precise text extraction targeting betting events
    page_text = driver.execute_script("""
        function extractBettingData() {
            let data = [];
            
            // Find all event containers
            const events = document.querySelectorAll('div[class*="event-"], div[class*="sport-base-event"]');
            
            events.forEach(event => {
                let eventText = '';
                
                // Get team names
                const teamElements = event.querySelectorAll('div[class*="team"], div[class*="sport-event__name"], a[class*="sport-event__name"]');
                teamElements.forEach(team => {
                    eventText += team.textContent.trim() + '\\n';
                });
                
                // Get odds
                const oddElements = event.querySelectorAll('div[class*="factor-value"]');
                oddElements.forEach(odd => {
                    eventText += odd.textContent.trim() + '\\n';
                });
                
                if (eventText) {
                    data.push(eventText);
                }
            });
            
            return data.join('\\n');
        }
        return extractBettingData();
    """)

    log(f"Extracted betting data: {len(page_text)} characters")

    # Parse the extracted text with enhanced validation
    betting_data = []
    current_teams = None
    current_odds = []
    
    for line in page_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Try to match team names
        for separator in [" vs ", " - ", " — ", "—", " – "]:
            if separator in line:
                parts = line.split(separator)
                if len(parts) == 2:
                    # Clear previous incomplete event
                    if current_teams and len(current_odds) < 3:
                        current_teams = None
                        current_odds = []
                    
                    team1 = parts[0].strip()
                    team2 = parts[1].strip()
                    
                    # Basic validation of team names
                    if (len(team1) > 1 and len(team2) > 1 and
                        not any(x in line.lower() for x in ["login", "register", "menu", "live", "all", "sports"])):
                        current_teams = (team1, team2)
                        current_odds = []
                        break
        
        # Try to match odds
        if current_teams and len(current_odds) < 3:
            try:
                value = float(line.replace(",", "."))
                if 1.01 <= value <= 30.0:  # Reasonable odds range
                    current_odds.append(str(value))
                    
                    # If we have all odds, save the event
                    if len(current_odds) == 3:
                        betting_data.append({
                            "team1": current_teams[0],
                            "team2": current_teams[1],
                            "odd1": current_odds[0],
                            "oddX": current_odds[1],
                            "odd2": current_odds[2]
                        })
                        current_teams = None
                        current_odds = []
            except ValueError:
                pass
    
    log(f"Found {len(betting_data)} complete betting events")

    # Validate parsed data
    valid_events = []
    for event in betting_data:
        # Skip events with incomplete data
        if not all([event["team1"], event["team2"], event["odd1"], event["oddX"], event["odd2"]]):
            continue
            
        # Skip events with invalid team names
        if len(event["team1"]) < 2 or len(event["team2"]) < 2:
            continue
            
        # Skip events with suspicious odds
        try:
            odds = [float(event["odd1"]), float(event["oddX"]), float(event["odd2"])]
            if any(odd < 1.01 or odd > 30.0 for odd in odds):
                continue
        except ValueError:
            continue
            
        valid_events.append(event)
    
    betting_data = valid_events
    log(f"Found {len(betting_data)} valid betting events")

    # Save the parsed data
    with open("outputs/betting_data.json", "w", encoding="utf-8") as f:
        json.dump(betting_data, f, ensure_ascii=False, indent=4)
    log("Betting data saved to outputs/betting_data.json")

except Exception as e:
    log(f"Scraper failed: {str(e)}")
    driver.save_screenshot("outputs/error_screenshot.png")
    log("Error screenshot saved to outputs/error_screenshot.png")
    raise

finally:
    driver.quit()
    log("Browser closed")