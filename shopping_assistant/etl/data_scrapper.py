import csv
import time
import re
import os
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class DataScrapper:
    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    # -----------------------------
    # DRIVER SETUP
    # -----------------------------
    def _init_driver(self):
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")

        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
        )

        return uc.Chrome(options=options, use_subprocess=True)

    # -----------------------------
    # GET REVIEWS
    # -----------------------------
    def get_top_reviews(self, product_url, count=2):
        driver = self._init_driver()

        if not product_url.startswith("http"):
            try: driver.quit()
            except: pass
            return "No reviews found"

        try:
            driver.get(product_url)
            time.sleep(5)  # Wait for the page to load
            
            try:
                driver.find_element(By.XPATH, "//button[contains(text(), '✕')]").click()
                time.sleep(1)
            except:
                pass

            for _ in range(4):
                ActionChains(driver).send_keys(Keys.END).perform()
                time.sleep(1.5)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            review_blocks = soup.select("div._27M-vq, div.col.EPCmJX, div._6K-7Co")

            seen = set()
            reviews = []

            for block in review_blocks:
                text = block.get_text(" ", strip=True)
                if text and text not in seen:
                    reviews.append(text)
                    seen.add(text)
                if len(reviews) >= count:
                    break

        except Exception as e:
            print("Review error:", e)
            reviews = []

        try: driver.quit()
        except: pass

        return " || ".join(reviews) if reviews else "No reviews found"

    # -----------------------------
    # MAIN SCRAPER
    # -----------------------------
    def scrape_flipkart_products(self, query, max_products=1, review_count=2):
        driver = self._init_driver()

        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"

        try:
            driver.get(search_url)
        except Exception:
            print("Driver crashed, restarting...")
            driver = self._init_driver()
            driver.get(search_url)

        time.sleep(4)

        try:
            driver.find_element(By.XPATH, "//button[contains(text(), '✕')]").click()
        except:
            pass

        time.sleep(2)

        products = []

        items = driver.find_elements(By.CSS_SELECTOR, "div[data-id]")[:max_products]
        print("Products found:", len(items))

        for idx, item in enumerate(items):
            try:
                # ---------- TITLE ----------
                try:
                    title = item.find_element(By.CSS_SELECTOR, "div.RG5Slk").text.strip()
                except:
                    try:
                        title = item.find_element(By.CSS_SELECTOR, "a[title]").get_attribute("title")
                    except:
                        title = "N/A"

                # ---------- PRICE ----------
                try:
                    price = item.find_element(By.CSS_SELECTOR, "div.DeU9vF").text.strip()
                except:
                    try:
                        price = item.find_element(By.XPATH, ".//div[contains(text(),'₹')]").text
                    except:
                        price = "N/A"

                # ---------- RATING ----------
                try:
                    rating = item.find_element(By.CSS_SELECTOR, "div.MKiFS6").text.strip()
                except:
                    rating = "N/A"

                # ---------- REVIEW COUNT ----------
                try:
                    reviews_text = item.find_element(By.CSS_SELECTOR, "span.PvbNMB").text.strip()
                    match = re.search(r"(\d+[,\d]*)\s+Reviews", reviews_text)
                    total_reviews = match.group(1) if match else "N/A"
                except:
                    total_reviews = "N/A"

                # ---------- LINK ----------
                link_el = item.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
                href = link_el.get_attribute("href")

                product_link = (
                    href if href.startswith("http")
                    else "https://www.flipkart.com" + href
                )

                match = re.findall(r"/p/(itm[0-9A-Za-z]+)", href)
                product_id = match[0] if match else "N/A"

            except Exception as e:
                print(f"Error processing item {idx}:", e)
                continue

            time.sleep(1)

            top_reviews = self.get_top_reviews(product_link, count=review_count)

            products.append([
                product_id,
                title,
                rating,
                total_reviews,
                price,
                top_reviews
            ])

        try: driver.quit()
        except: pass

        return products

    # -----------------------------
    # SAVE CSV
    # -----------------------------
    def save_to_csv(self, data, filename="product_reviews.csv"):
        if os.path.isabs(filename) or "/" in filename:
            path = filename
        else:
            path = os.path.join(self.output_dir, filename)

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "product_id",
                "product_title",
                "rating",
                "total_reviews",
                "price",
                "top_reviews"
            ])
            writer.writerows(data)
            
            