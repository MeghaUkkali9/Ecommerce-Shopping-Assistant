import csv
import time
import re
import os
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class DataScrapper:
    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

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

    def get_top_reviews(self, driver, product_url, count=2):
        driver.get(product_url)
        time.sleep(4)

        for i in range(10):
            driver.execute_script(f"window.scrollTo(0, {i*800});")
            time.sleep(1.5)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//section"))
            )
        except:
            pass

        soup = BeautifulSoup(driver.page_source, "html.parser")

        review_blocks = soup.select("section.css-1v6g5ho")

        reviews = []
        seen = set()

        if len(review_blocks) > 1:
            review_blocks = review_blocks[1:]

        for block in review_blocks:
            try:
                title = block.find("div")
                para = block.find("p")

                title_text = title.get_text(strip=True) if title else ""
                para_text = para.get_text(strip=True) if para else ""

                para_text = para_text.replace("...Read More", "").strip()
                
                full_review = f"{title_text} - {para_text}"
                full_review = full_review.replace('"', '').strip()
                full_review = self.__clean_review(full_review)
                
                if full_review and full_review not in seen:
                    reviews.append(full_review)
                    seen.add(full_review)

                if len(reviews) >= count:
                    break

            except:
                continue

        return " || ".join(reviews) if reviews else "No reviews found"


    def __clean_review(self, text):
        # remove emojis only (keep punctuation)
        text = re.sub(
            r"[\U00010000-\U0010ffff]", 
            "", 
            text
        )
        # normalize spaces
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # -----------------------------
    # MAIN SCRAPER
    # -----------------------------
    def scrape_flipkart_products(self, query, max_products=1, review_count=2):
        driver = self._init_driver()

        search_url = f"https://www.nykaa.com/search/result/?q={query.replace(' ', '%20')}"
        driver.get(search_url)
        time.sleep(4)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        products = []

        items = soup.select("div.productWrapper")[:max_products]

        for item in items:
            try:
                # TITLE
                title = item.select_one("h2.css-xrzmfa").get_text(strip=True)

                # PRICE
                price = item.select_one("span.css-111z9ua").get_text(strip=True)

                # RATING + REVIEWS
                rating_div = item.select_one("div[aria-label]")

                if rating_div:
                    label = rating_div["aria-label"]

                    rating_match = re.search(r"(\d+\.?\d*) out of 5", label)
                    review_match = re.search(r"(\d+(?:,\d+)*) reviews", label)

                    rating = rating_match.group(1) if rating_match else "N/A"
                    total_reviews = review_match.group(1) if review_match else "N/A"
                else:
                    rating = "N/A"
                    total_reviews = "N/A"
                    
                link_tag = item.select_one("a")
                href = link_tag["href"] if link_tag else ""

                product_link = "https://www.nykaa.com" + href

                match = re.search(r"productId=(\d+)", href)
                product_id = match.group(1) if match else "N/A"
                
                top_reviews = self.get_top_reviews(driver, product_link, count=review_count)

                products.append([product_id, title, rating, total_reviews, price, top_reviews])

            except Exception as e:
                print("Error:", e)
                continue

        driver.quit()
        return products
    
    def save_to_csv(self, data, filename="product_reviews.csv"):
        """Save the scraped product reviews to a CSV file."""
        if os.path.isabs(filename):
            path = filename
        elif os.path.dirname(filename):  # filename includes subfolder like 'data/product_reviews.csv'
            path = filename
            os.makedirs(os.path.dirname(path), exist_ok=True)
        else:
            # plain filename like 'output.csv'
            path = os.path.join(self.output_dir, filename)

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["product_id", "product_title", "rating", "total_reviews", "price", "top_reviews"])
            writer.writerows(data)
        