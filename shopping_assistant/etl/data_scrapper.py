import csv, time, re, os
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class DataScrapper:
    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def get_top_reviews(self, product_url, num_reviews=2):
        """
        Scrape the top N reviews from the given product URL.
         - Use Selenium to load the product page and navigate to the reviews section
         - Extract the review text, rating, and any other relevant metadata
         - Handle pagination if there are more reviews than can be displayed on one page
         - Return a list of reviews with their associated metadata for further processing
         - Ensure that the scraping process is robust and can handle potential changes in the website's structure
         - Implement error handling to manage issues such as network errors, missing elements, or unexpected page layouts
         - Use undetected_chromedriver to avoid being blocked by anti-scraping measures
         - Include appropriate delays between requests to mimic human browsing behavior and reduce the risk of being blocked
         - The function should be flexible enough to allow for adjustments in the number of reviews to scrape and the specific product URL
         - Consider implementing logging to track the scraping process and any issues that arise
         - Ensure that the scraped data is stored in a structured format (e.g., list of dictionaries) for easy integration into the data ingestion pipeline
         - The function should be designed to be reusable for different products and adaptable to changes in the website's structure over time
         - Include comments and documentation within the code to explain the scraping logic and any assumptions made about the website's structure
         - The function should be tested to ensure it works correctly and can handle various edge cases, such as products with no reviews, products with a large number of reviews, and products with reviews that contain special characters or formatting
         - Consider implementing a mechanism to detect and handle CAPTCHAs or other anti-scraping measures that may be encountered during the scraping process
         - The function should be designed to be efficient and minimize the number of requests made to the website while still retrieving the desired number of reviews
         - Ensure that the scraping process complies with the website's terms of service and any applicable laws regarding web scraping and data privacy
         - The function should be modular and allow for easy integration into a larger data pipeline, such as being called from a main function or being used as part of a class that manages the entire scraping and data ingestion process
         - Consider implementing a caching mechanism to store previously scraped reviews for products, which can help reduce the number of requests made to
        """
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        driver = uc.Chrome(options=options, use_subprocess=True)
        
        if not product_url.startswith("http"):
            raise ValueError("Invalid product URL. Please provide a valid URL starting with http or https.")        
        
        try:
            driver.get(product_url)
            time.sleep(5)  # Wait for the page to load
            
            try:
                driver.find_element(By.XPATH, "//button[contains(text(),'X')]").click()  # Click on the reviews section
                time.sleep(3)  # Wait for the reviews section to load
            except Exception as e:
                print("Error oocurred while closing popup", e)
                
            for _ in range(3): # Scroll down a few times to load more reviews
                ActionChains(driver).send_keys(Keys.END).perform()
                time.sleep(2)
                
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            review_blocks = soup.select("div._27M-vq, div.col.EPCmJX, div._6K-7Co")
            seen = set()
            reviews = []
            
            for block in review_blocks:
                review_text = block.get_text(separator=" ", strip=True)
                
                if review_text and review_text not in seen:
                    reviews.append(review_text)
                    seen.add(review_text)
                
                if len(reviews) >= num_reviews:
                    break
                
        except Exception as e:  
            print("Error loading product page:", e)
            driver.quit()
            reviews = []
        
        driver.quit()
        return " || ".join(reviews) if reviews else "No reviews found"
    
    def scrape_flipkart_product(self,  query, max_products=5, num_reviews=2):
        """
        Scrape product details and reviews from Flipkart based on a search query.
         - Search for the query on Flipkart
         - For the top N products, extract product name, price, rating, and reviews
         - Store the extracted data in a structured format (e.g., list of dictionaries)
         - Save the data to a CSV file for later use in the data ingestion pipeline
        """
        options = uc.ChromeOptions()
        driver = uc.Chrome(options=options,use_subprocess=True)
        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(4)

        try:
            driver.find_element(By.XPATH, "//button[contains(text(), '✕')]").click()
        except Exception as e:
            print(f"Error occurred while closing popup: {e}")

        time.sleep(2)
        products = []

        items = driver.find_elements(By.CSS_SELECTOR, "div[data-id]")[:max_products]
        for item in items:
            try:
                title = item.find_element(By.CSS_SELECTOR, "div.KzDlHZ").text.strip()
                price = item.find_element(By.CSS_SELECTOR, "div.Nx9bqj").text.strip()
                rating = item.find_element(By.CSS_SELECTOR, "div.XQDdHH").text.strip()
                reviews_text = item.find_element(By.CSS_SELECTOR, "span.Wphh3N").text.strip()
                match = re.search(r"\d+(,\d+)?(?=\s+Reviews)", reviews_text)
                total_reviews = match.group(0) if match else "N/A"

                link_el = item.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
                href = link_el.get_attribute("href")
                product_link = href if href.startswith("http") else "https://www.flipkart.com" + href
                match = re.findall(r"/p/(itm[0-9A-Za-z]+)", href)
                product_id = match[0] if match else "N/A"
            except Exception as e:
                print(f"Error occurred while processing item: {e}")
                continue

            top_reviews = self.get_top_reviews(product_link, num_reviews=num_reviews) if "flipkart.com" in product_link else "Invalid product URL"
            products.append([product_id, title, rating, total_reviews, price, top_reviews])

        driver.quit()
        return products
    
    def save_to_csv(self, data, filename="product_reviews.csv"):
        """
        Save the scraped product data to a CSV file.
         - The CSV file should have columns for product name, price, rating, and reviews
         - Each row should represent a single product and its associated reviews
         - The filename should be configurable, and the file should be saved in a designated output directory   
        """
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
        