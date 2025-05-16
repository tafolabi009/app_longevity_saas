import requests
import pandas as pd
import numpy as np
import time
import os
import json
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app_data_collection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create directories
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

# App Store API constants
APP_STORE_API = "https://itunes.apple.com/lookup"
APP_STORE_SEARCH_API = "https://itunes.apple.com/search"
APP_STORE_CATEGORIES = {
    "6000": "Business",
    "6001": "Weather",
    "6002": "Utilities",
    "6003": "Travel",
    "6004": "Sports",
    "6005": "Social Networking",
    "6006": "Reference",
    "6007": "Productivity",
    "6008": "Photo & Video",
    "6009": "News",
    "6010": "Navigation",
    "6011": "Music",
    "6012": "Lifestyle",
    "6013": "Health & Fitness",
    "6014": "Games",
    "6015": "Finance",
    "6016": "Entertainment",
    "6017": "Education",
    "6018": "Books",
    "6020": "Medical",
    "6021": "Magazines & Newspapers",
    "6023": "Food & Drink",
    "6024": "Shopping"
}

# Play Store scraping constants
PLAY_STORE_URL = "https://play.google.com/store/apps/details"
PLAY_STORE_TOP_URL = "https://play.google.com/store/apps/top"
PLAY_STORE_CATEGORY_URL = "https://play.google.com/store/apps/category/"

def fetch_app_store_data(app_id):
    """Fetch data for a specific iOS app"""
    try:
        params = {
            "id": app_id,
            "country": "us",
            "entity": "software"
        }
        response = requests.get(APP_STORE_API, params=params)
        data = response.json()
        
        if data["resultCount"] == 0:
            logger.warning(f"No data found for App Store app ID: {app_id}")
            return None
        
        app_data = data["results"][0]
        
        # Calculate days since release and last update
        release_date = datetime.strptime(app_data.get("releaseDate", "2020-01-01"), "%Y-%m-%dT%H:%M:%SZ")
        days_since_release = (datetime.now() - release_date).days
        
        if "currentVersionReleaseDate" in app_data:
            last_update = datetime.strptime(app_data["currentVersionReleaseDate"], "%Y-%m-%dT%H:%M:%SZ")
            days_since_last_update = (datetime.now() - last_update).days
        else:
            days_since_last_update = days_since_release
        
        # Calculate update frequency if multiple versions exist
        if "version" in app_data and days_since_release > 0:
            version_number = app_data["version"]
            try:
                major_version = int(version_number.split('.')[0])
                # Estimate updates based on major version and app age
                estimated_updates = major_version + 2
                update_frequency = max(1, days_since_release // estimated_updates)
            except:
                update_frequency = 90  # Default if can't parse version
        else:
            update_frequency = 90
        
        # Parse pricing info
        price = app_data.get("price", 0)
        has_in_app_purchases = "inAppPurchases" in app_data and app_data["inAppPurchases"] == True
        
        # Get ratings data
        rating = app_data.get("averageUserRating", 0)
        total_ratings = app_data.get("userRatingCount", 0)
        
        # Estimate user engagement based on ratings
        if total_ratings > 0:
            engagement_score = min(1.0, (total_ratings / 10000) * (rating / 5))
        else:
            engagement_score = 0.1
            
        # Estimate user sentiment from rating
        positive_sentiment_ratio = min(1.0, max(0.0, (rating - 1) / 4))
        
        # Extract keywords from description
        description = app_data.get("description", "")
        keywords = []
        
        # Create structured app data
        structured_data = {
            "app_id": app_id,
            "app_name": app_data.get("trackName", "Unknown"),
            "platform": "iOS",
            "category": app_data.get("primaryGenreName", "Unknown"),
            "rating": rating,
            "total_ratings": total_ratings,
            "price": price,
            "size_mb": app_data.get("fileSizeBytes", 0) / 1000000,
            "developer": app_data.get("artistName", "Unknown"),
            "has_in_app_purchases": has_in_app_purchases,
            "days_since_release": days_since_release,
            "days_since_last_update": days_since_last_update,
            "update_frequency": update_frequency,
            "content_rating": app_data.get("contentAdvisoryRating", "Unknown"),
            "languages": len(app_data.get("languageCodesISO2A", [])),
            "keywords": keywords,
            "description": description[:500],  # Truncated for storage
            "positive_sentiment_ratio": positive_sentiment_ratio,
            "engagement_score": engagement_score
        }
        
        return structured_data
    except Exception as e:
        logger.error(f"Error fetching App Store data for {app_id}: {str(e)}")
        return None

def fetch_play_store_data(package_id):
    """Fetch data for a specific Android app"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        params = {
            "id": package_id,
            "hl": "en",
            "gl": "US"
        }
        
        response = requests.get(PLAY_STORE_URL, params=params, headers=headers)
        
        if response.status_code != 200:
            logger.warning(f"Failed to fetch Play Store data for {package_id}: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract app name
        app_name = "Unknown"
        app_name_elem = soup.select_one("h1[itemprop='name']") or soup.select_one("h1")
        if app_name_elem:
            app_name = app_name_elem.text.strip()
        
        # Extract rating
        rating = 0
        rating_elem = soup.select_one("div[itemprop='starRating']") or soup.select_one("div[role='img'][aria-label*='rating']")
        if rating_elem:
            aria_label = rating_elem.get("aria-label", "")
            rating_match = re.search(r"([\d.]+) out of", aria_label)
            if rating_match:
                rating = float(rating_match.group(1))
        
        # Extract total ratings
        total_ratings_text = ""
        total_ratings = 0
        ratings_elem = soup.select_one("span[aria-label*='ratings']")
        if ratings_elem:
            total_ratings_text = ratings_elem.text.strip()
            # Parse numbers like "1,234,567", "1.2M", etc.
            total_ratings_text = total_ratings_text.replace(",", "")
            if "M" in total_ratings_text:
                total_ratings = float(total_ratings_text.replace("M", "")) * 1000000
            elif "K" in total_ratings_text:
                total_ratings = float(total_ratings_text.replace("K", "")) * 1000
            else:
                try:
                    total_ratings = float(total_ratings_text)
                except:
                    total_ratings = 0
        
        # Extract category
        category = "Unknown"
        category_elem = soup.select_one("a[itemprop='genre']")
        if category_elem:
            category = category_elem.text.strip()
        
        # Extract price
        price = 0
        price_elem = soup.select_one("meta[itemprop='price']")
        if price_elem:
            try:
                price = float(price_elem.get("content", "0"))
            except:
                price = 0
        
        # Extract size
        size_mb = 0
        size_elem = soup.select_one("div:contains('Size')")
        if size_elem:
            size_text = size_elem.text.strip()
            size_match = re.search(r"([\d.]+)\s*(MB|GB|KB)", size_text, re.IGNORECASE)
            if size_match:
                size_value = float(size_match.group(1))
                size_unit = size_match.group(2).upper()
                if size_unit == "KB":
                    size_mb = size_value / 1000
                elif size_unit == "GB":
                    size_mb = size_value * 1000
                else:  # MB
                    size_mb = size_value
        
        # Extract developer
        developer = "Unknown"
        dev_elem = soup.select_one("a[href*='/developer?id=']")
        if dev_elem:
            developer = dev_elem.text.strip()
        
        # Check for in-app purchases
        has_in_app_purchases = "in-app purchases" in response.text.lower()
        
        # Extract last update info
        updated_date = None
        days_since_last_update = 90  # Default
        update_text_elem = soup.select_one("div:contains('Updated')")
        if update_text_elem:
            update_text = update_text_elem.text.strip()
            date_match = re.search(r"Updated on (.*)", update_text)
            if date_match:
                try:
                    date_str = date_match.group(1).strip()
                    # Handle different date formats
                    try:
                        updated_date = datetime.strptime(date_str, "%B %d, %Y")
                    except:
                        try:
                            updated_date = datetime.strptime(date_str, "%d %B %Y")
                        except:
                            # If still can't parse, try month day format
                            current_year = datetime.now().year
                            try:
                                # Add current year to string
                                updated_date = datetime.strptime(f"{date_str}, {current_year}", "%B %d, %Y")
                            except:
                                updated_date = None
                    
                    if updated_date:
                        days_since_last_update = (datetime.now() - updated_date).days
                except Exception as date_err:
                    logger.warning(f"Could not parse update date: {str(date_err)}")
        
        # Extract content rating
        content_rating = "Unknown"
        content_elem = soup.select_one("div:contains('Content Rating')")
        if content_elem:
            content_text = content_elem.text.strip()
            rating_match = re.search(r"Content Rating\s*(.*)", content_text)
            if rating_match:
                content_rating = rating_match.group(1).strip()
        
        # Extract description for keyword analysis
        description = ""
        desc_elem = soup.select_one("div[itemprop='description']")
        if desc_elem:
            description = desc_elem.text.strip()
        
        # Estimate days since release
        days_since_release = 365  # Default to 1 year
        
        # Estimate update frequency
        if rating >= 4.0:
            update_frequency = 30  # Assume good apps update more frequently
        else:
            update_frequency = 90
        
        # Estimate engagement from ratings
        if total_ratings > 0:
            engagement_score = min(1.0, (total_ratings / 100000) * (rating / 5))
        else:
            engagement_score = 0.1
            
        # Estimate sentiment from rating
        positive_sentiment_ratio = min(1.0, max(0.0, (rating - 1) / 4))
        
        # Create structured app data
        structured_data = {
            "app_id": package_id,
            "app_name": app_name,
            "platform": "Android",
            "category": category,
            "rating": rating,
            "total_ratings": total_ratings,
            "price": price,
            "size_mb": size_mb,
            "developer": developer,
            "has_in_app_purchases": has_in_app_purchases,
            "days_since_release": days_since_release,
            "days_since_last_update": days_since_last_update,
            "update_frequency": update_frequency,
            "content_rating": content_rating,
            "languages": 1,  # Default, hard to extract from Play Store
            "keywords": [],
            "description": description[:500],  # Truncated for storage
            "positive_sentiment_ratio": positive_sentiment_ratio,
            "engagement_score": engagement_score
        }
        
        return structured_data
    except Exception as e:
        logger.error(f"Error fetching Play Store data for {package_id}: {str(e)}")
        return None

def search_app_store(query, limit=10):
    """Search for apps on the App Store"""
    try:
        params = {
            "term": query,
            "country": "us",
            "entity": "software",
            "limit": limit
        }
        response = requests.get(APP_STORE_SEARCH_API, params=params)
        data = response.json()
        
        if data["resultCount"] == 0:
            logger.warning(f"No results found for App Store search: {query}")
            return []
        
        app_ids = [app["trackId"] for app in data["results"]]
        return app_ids
    except Exception as e:
        logger.error(f"Error searching App Store for {query}: {str(e)}")
        return []

def get_top_play_store_packages(category=None, limit=50):
    """Get top app package IDs from Play Store"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        url = PLAY_STORE_TOP_URL
        if category:
            url = f"{PLAY_STORE_CATEGORY_URL}{category}/top"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            logger.warning(f"Failed to fetch top Play Store apps: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        app_links = soup.select("a[href*='/store/apps/details?id=']")
        
        package_ids = []
        for link in app_links:
            href = link.get("href", "")
            package_match = re.search(r"id=([^&]+)", href)
            if package_match:
                package_id = package_match.group(1)
                if package_id not in package_ids:
                    package_ids.append(package_id)
                    if len(package_ids) >= limit:
                        break
        
        return package_ids
    except Exception as e:
        logger.error(f"Error getting top Play Store apps: {str(e)}")
        return []

def calculate_feature_engineering(app_data):
    """Add calculated features to enhance predictive value"""
    
    # Skip if no app data
    if not app_data:
        return app_data
    
    try:
        # Calculate price tier (free, low, medium, high)
        price = app_data.get("price", 0)
        if price == 0:
            app_data["price_tier"] = "free"
        elif price <= 2.99:
            app_data["price_tier"] = "low"
        elif price <= 6.99:
            app_data["price_tier"] = "medium"
        else:
            app_data["price_tier"] = "high"
        
        # Calculate update recency score (1.0 = recent, 0.0 = old)
        days_since_update = app_data.get("days_since_last_update", 365)
        app_data["update_recency_score"] = max(0.0, min(1.0, 1.0 - (days_since_update / 365)))
        
        # Calculate app maturity score based on days since release
        days_since_release = app_data.get("days_since_release", 0)
        app_data["app_maturity_score"] = min(1.0, days_since_release / 730)  # Max at 2 years
        
        # Calculate a composite quality score
        rating = app_data.get("rating", 0)
        total_ratings = app_data.get("total_ratings", 0)
        positive_sentiment = app_data.get("positive_sentiment_ratio", 0.5)
        
        # Rating weight based on number of ratings
        rating_weight = min(1.0, total_ratings / 10000) if total_ratings > 0 else 0.1
        
        # Composite quality score (0.0 - 1.0)
        quality_score = (
            (rating / 5) * 0.6 + 
            positive_sentiment * 0.3 + 
            rating_weight * 0.1
        )
        app_data["quality_score"] = quality_score
        
        # Calculate maintenance score based on update frequency and recency
        update_frequency = app_data.get("update_frequency", 90)
        update_frequency_score = max(0.0, min(1.0, 1.0 - (update_frequency / 180)))
        
        maintenance_score = (
            app_data["update_recency_score"] * 0.7 + 
            update_frequency_score * 0.3
        )
        app_data["maintenance_score"] = maintenance_score
        
        # Calculate estimated revenue class based on price, ratings, and in-app purchases
        has_iap = app_data.get("has_in_app_purchases", False)
        
        revenue_score = (
            price * 0.3 + 
            (quality_score * total_ratings / 5000) * 0.4 + 
            (1.0 if has_iap else 0.0) * 0.3
        )
        
        if revenue_score < 0.2:
            app_data["revenue_class"] = "low"
        elif revenue_score < 0.5:
            app_data["revenue_class"] = "medium"
        else:
            app_data["revenue_class"] = "high"
        
        # Calculate longevity score (our target variable when training)
        # This is a combination of quality, maintenance, maturity and revenue potential
        longevity_score = (
            quality_score * 0.4 + 
            maintenance_score * 0.3 + 
            app_data["app_maturity_score"] * 0.2 + 
            revenue_score * 0.1
        )
        app_data["longevity"] = longevity_score
        
        return app_data
    except Exception as e:
        logger.error(f"Error calculating engineered features: {str(e)}")
        return app_data

def collect_app_data(categories=None, count_per_category=20, include_top_apps=True):
    """Collect app data across platforms and categories"""
    all_app_data = []
    
    # Use default categories if none provided
    if not categories:
        ios_categories = list(APP_STORE_CATEGORIES.keys())[:5]  # Use first 5 categories for demo
        android_categories = ["PRODUCTIVITY", "BUSINESS", "GAME", "SOCIAL", "TOOLS"]
    else:
        ios_categories = categories.get("ios", [])
        android_categories = categories.get("android", [])
    
    # Collect iOS app data
    for category_id in ios_categories:
        logger.info(f"Collecting data for iOS category: {APP_STORE_CATEGORIES.get(category_id, category_id)}")
        
        # Search for top apps in this category
        search_term = f"top {APP_STORE_CATEGORIES.get(category_id, '')}"
        app_ids = search_app_store(search_term, limit=count_per_category)
        
        for app_id in tqdm(app_ids, desc=f"iOS {APP_STORE_CATEGORIES.get(category_id, category_id)}"):
            time.sleep(1)  # Rate limiting
            app_data = fetch_app_store_data(app_id)
            if app_data:
                app_data = calculate_feature_engineering(app_data)
                all_app_data.append(app_data)
    
    # Collect Android app data
    for category in android_categories:
        logger.info(f"Collecting data for Android category: {category}")
        
        # Get top apps for this category
        package_ids = get_top_play_store_packages(category, limit=count_per_category)
        
        for package_id in tqdm(package_ids, desc=f"Android {category}"):
            time.sleep(1)  # Rate limiting
            app_data = fetch_play_store_data(package_id)
            if app_data:
                app_data = calculate_feature_engineering(app_data)
                all_app_data.append(app_data)
    
    # Include additional top apps
    if include_top_apps:
        logger.info("Collecting data for top apps")
        
        # Top iOS apps
        top_ios_ids = search_app_store("popular", limit=20)
        for app_id in tqdm(top_ios_ids, desc="Top iOS Apps"):
            time.sleep(1)  # Rate limiting
            app_data = fetch_app_store_data(app_id)
            if app_data:
                app_data = calculate_feature_engineering(app_data)
                all_app_data.append(app_data)
        
        # Top Android apps
        top_android_ids = get_top_play_store_packages(limit=20)
        for package_id in tqdm(top_android_ids, desc="Top Android Apps"):
            time.sleep(1)  # Rate limiting
            app_data = fetch_play_store_data(package_id)
            if app_data:
                app_data = calculate_feature_engineering(app_data)
                all_app_data.append(app_data)
    
    # Save the collected data
    df = pd.DataFrame(all_app_data)
    logger.info(f"Collected data for {len(df)} apps")
    
    # Save raw data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_csv(f"data/raw/app_data_{timestamp}.csv", index=False)
    
    # Also save as the final dataset
    df.to_csv("data/raw/app_data_final.csv", index=False)
    
    logger.info(f"Data saved to data/raw/app_data_final.csv")
    
    return df

def process_existing_data(input_file, output_file=None):
    """Process existing data to add engineered features"""
    try:
        df = pd.read_csv(input_file)
        logger.info(f"Processing existing data from {input_file}, {len(df)} records")
        
        processed_data = []
        for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing"):
            app_data = row.to_dict()
            processed_app = calculate_feature_engineering(app_data)
            processed_data.append(processed_app)
        
        result_df = pd.DataFrame(processed_data)
        
        if output_file:
            result_df.to_csv(output_file, index=False)
            logger.info(f"Processed data saved to {output_file}")
        
        return result_df
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Collect and process app data")
    parser.add_argument("--collect", action="store_true", help="Collect new app data")
    parser.add_argument("--process", type=str, help="Process existing data file")
    parser.add_argument("--output", type=str, help="Output file for processed data")
    parser.add_argument("--count", type=int, default=20, help="Number of apps per category")
    args = parser.parse_args()
    
    if args.collect:
        collect_app_data(count_per_category=args.count)
    
    if args.process:
        process_existing_data(args.process, args.output or "data/processed/app_data_processed.csv") 
