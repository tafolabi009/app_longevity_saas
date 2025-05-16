import os
import json
import pandas as pd
import numpy as np
import joblib
from typing import Dict, Any, List, Optional, Union
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import logging
from difflib import SequenceMatcher
import sys
from pathlib import Path

# Add parent directory to path to make imports work in different environments
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

try:
    from core.config import settings
    from services.model_manager import model_manager
except ImportError:
    try:
        from backend.core.config import settings
        from backend.services.model_manager import model_manager
    except ImportError:
        from app_longevity_saas.backend.core.config import settings
        from app_longevity_saas.backend.services.model_manager import model_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppLongevityPredictorService:
    """Service wrapper for the App Longevity ML model"""
    
    def __init__(self, model_name: str = None):
        self.model = None
        self.scaler = None
        self.preprocessor = None
        self.feature_importances = {}
        self.model_name = model_name if model_name else settings.DEFAULT_MODEL
        self.metadata = {}
        self.load_model(self.model_name)
    
    def load_model(self, model_name: str = None):
        """Load the ML model and related artifacts"""
        if model_name is None:
            model_name = settings.DEFAULT_MODEL
        
        self.model_name = model_name
            
        try:
            # Use the model manager to load the model
            model_data = model_manager.load_model(model_name)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.preprocessor = model_data.get('preprocessor')
            self.feature_importances = model_data['feature_importances']
            self.metadata = model_data.get('metadata', {})
            
            if self.model is None:
                logger.error(f"Failed to load model {model_name}")
                return False
            
            # If no model name is specified, use the base name of the file
            if '.' in model_name:
                self.model_name = os.path.splitext(model_name)[0]
            else:
                self.model_name = model_name
                
            logger.info(f"Successfully loaded model {model_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            return False
            
    async def predict_app_longevity(self, app_name: str, compare_competitors: bool = False) -> Dict[str, Any]:
        """
        Predict longevity for an app by name
        
        Args:
            app_name: Name of the app to analyze
            compare_competitors: Whether to compare with competitors
            
        Returns:
            Prediction results dictionary
        """
        try:
            # Check if model is loaded
            if self.model is None:
                logger.warning(f"Model not loaded. Attempting to load model: {self.model_name}")
                if not self.load_model():
                    # If we can't load the specified model, try to load any available model
                    available_models = model_manager.get_available_models()
                    if available_models:
                        alt_model = available_models[0]
                        logger.warning(f"Trying alternative model: {alt_model}")
                        if self.load_model(alt_model):
                            logger.info(f"Successfully loaded alternative model: {alt_model}")
                        else:
                            return {
                                "app_name": app_name,
                                "error": "No prediction model available"
                            }
                    else:
                        return {
                            "app_name": app_name,
                            "error": "No prediction model available"
                        }
            
            # Fetch app data from stores
            ios_data = await self._fetch_app_store_data(app_name)
            android_data = await self._fetch_play_store_data(app_name)
            
            # Determine which platform's data to use
            app_data = None
            platform = None
            app_store_id = None
            
            if ios_data and android_data:
                # Choose the platform with more features available
                ios_nulls = sum(1 for v in ios_data.values() if v is None)
                android_nulls = sum(1 for v in android_data.values() if v is None)
                
                if ios_nulls <= android_nulls:
                    app_data = ios_data
                    platform = "iOS"
                    app_store_id = ios_data.get("app_id")
                else:
                    app_data = android_data
                    platform = "Android"
                    app_store_id = android_data.get("app_id")
            elif ios_data:
                app_data = ios_data
                platform = "iOS"
                app_store_id = ios_data.get("app_id")
            elif android_data:
                app_data = android_data
                platform = "Android"
                app_store_id = android_data.get("app_id")
            
            if not app_data:
                return {
                    "app_name": app_name,
                    "error": "Could not find sufficient data for this app on either platform"
                }
            
            # Prepare data for prediction
            app_df = pd.DataFrame([app_data])
            
            # Remove columns not used in training
            exclude_cols = ['app_name', 'app_id', 'keywords', 'reviews']
            for col in exclude_cols:
                if col in app_df.columns:
                    app_df = app_df.drop(columns=[col])
            
            # Fill missing values
            app_df = app_df.fillna(0)
            
            # Use preprocessor if available, otherwise fall back to scaler
            if self.preprocessor:
                try:
                    # Ensure all expected columns are present
                    if hasattr(self.preprocessor, 'get_feature_names_out'):
                        expected_cols = self.preprocessor.get_feature_names_out()
                    elif hasattr(self.preprocessor, 'feature_names_in_'):
                        expected_cols = self.preprocessor.feature_names_in_
                    else:
                        expected_cols = None
                    
                    if expected_cols is not None:
                        for col in expected_cols:
                            if col not in app_df.columns:
                                app_df[col] = 0
                        app_df = app_df[expected_cols]
                    
                    # Apply preprocessing
                    app_df_processed = pd.DataFrame(
                        self.preprocessor.transform(app_df),
                        columns=expected_cols if expected_cols is not None else app_df.columns
                    )
                except Exception as e:
                    logger.warning(f"Error using preprocessor: {str(e)}. Falling back to scaler.")
                    app_df_processed = None
            else:
                app_df_processed = None
            
            # Scale features if no preprocessor or preprocessor failed
            if app_df_processed is None and self.scaler:
                try:
                    # Ensure all expected columns are present
                    if hasattr(self.scaler, 'get_feature_names_out'):
                        expected_cols = self.scaler.get_feature_names_out()
                    elif hasattr(self.scaler, 'feature_names_in_'):
                        expected_cols = self.scaler.feature_names_in_
                    else:
                        expected_cols = None
                    
                    if expected_cols is not None:
                        for col in expected_cols:
                            if col not in app_df.columns:
                                app_df[col] = 0
                        app_df = app_df[expected_cols]
                    
                    # Apply scaling
                    app_df_processed = pd.DataFrame(
                        self.scaler.transform(app_df),
                        columns=expected_cols if expected_cols is not None else app_df.columns
                    )
                except Exception as e:
                    logger.warning(f"Error using scaler: {str(e)}. Using unscaled data.")
                    app_df_processed = app_df
            elif app_df_processed is None:
                app_df_processed = app_df
            
            # Make prediction
            prediction = self.model.predict(app_df_processed)
            predicted_value = float(prediction[0])
            
            # Build results
            results = {
                "app_name": app_name,
                "platform": platform,
                "store_id": app_store_id,
                "predicted_longevity": predicted_value,
                "longevity_interpretation": self._interpret_longevity_score(predicted_value),
                "key_metrics": {
                    "rating": app_data.get("rating", "Unknown"),
                    "downloads": app_data.get("downloads", "Unknown"),
                    "price": app_data.get("price", "Unknown"),
                    "size_mb": app_data.get("size_mb", "Unknown"),
                    "days_since_last_update": app_data.get("days_since_last_update", "Unknown"),
                    "days_since_release": app_data.get("days_since_release", "Unknown"),
                    "positive_sentiment_ratio": app_data.get("positive_sentiment_ratio", "Unknown"),
                    "in_app_purchases": app_data.get("has_in_app_purchases", False),
                    "total_ratings": app_data.get("total_ratings", "Unknown"),
                },
                "date_analyzed": datetime.now().strftime("%Y-%m-%d"),
                "model_used": self.model_name
            }
            
            # Add contributing factors if available
            if self.feature_importances:
                # Identify top contributing factors
                contributing_factors = []
                
                # Use non-null features from the app data
                available_features = {k: v for k, v in app_data.items() 
                                    if k in self.feature_importances and v is not None}
                
                # Sort by feature importance
                sorted_features = sorted(available_features.items(), 
                                        key=lambda x: self.feature_importances.get(x[0], 0), 
                                        reverse=True)
                
                # Take top 5 contributors
                for feature, value in sorted_features[:5]:
                    impact = "positive" if self.feature_importances[feature] > 0 else "negative"
                    contributing_factors.append({
                        "feature": feature,
                        "value": value,
                        "importance": self.feature_importances[feature],
                        "impact": impact,
                        "description": self._get_feature_description(feature, value)
                    })
                
                results["contributing_factors"] = contributing_factors
            
            # Add recommendations
            results["recommendations"] = self._generate_recommendations(app_data)
            
            return results
        except Exception as e:
            logger.error(f"Error predicting app longevity: {str(e)}", exc_info=True)
            return {
                "app_name": app_name,
                "error": f"Error analyzing app: {str(e)}"
            }
    
    async def _fetch_app_store_data(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Fetch data for an iOS app from the App Store"""
        try:
            # Encode app name for URL
            encoded_app_name = requests.utils.quote(app_name)
            search_url = f"https://itunes.apple.com/search?term={encoded_app_name}&entity=software&limit=5"
            
            response = requests.get(search_url)
            search_data = response.json()
            
            if search_data['resultCount'] > 0:
                # Sort results by relevance (name similarity)
                def similarity(a, b):
                    return SequenceMatcher(None, a.lower(), b.lower()).ratio()
                
                # Find the most relevant app
                best_match = max(search_data['results'], 
                                key=lambda x: similarity(x.get('trackName', ''), app_name))
                
                app_id = str(best_match['trackId'])
                logger.info(f"Found iOS app: {best_match.get('trackName')} (ID: {app_id})")
                
                # Extract relevant data
                app_data = {
                    "app_id": app_id,
                    "app_name": best_match.get('trackName'),
                    "rating": best_match.get('averageUserRating'),
                    "total_ratings": best_match.get('userRatingCount'),
                    "price": best_match.get('price'),
                    "size_mb": best_match.get('fileSizeBytes', 0) / 1000000,
                    "category": best_match.get('primaryGenreName'),
                    "developer": best_match.get('artistName'),
                    "has_in_app_purchases": 'offers in-app purchases' in best_match.get('description', '').lower(),
                }
                
                # Calculate days since release if available
                if 'releaseDate' in best_match:
                    release_date = datetime.fromisoformat(best_match['releaseDate'].replace('Z', '+00:00'))
                    app_data["days_since_release"] = (datetime.now() - release_date).days
                
                # Calculate days since last update if available
                if 'currentVersionReleaseDate' in best_match:
                    update_date = datetime.fromisoformat(best_match['currentVersionReleaseDate'].replace('Z', '+00:00'))
                    app_data["days_since_last_update"] = (datetime.now() - update_date).days
                
                # Calculate feature engineering metrics
                app_data["positive_sentiment_ratio"] = 0.5 + (0.1 * min(5, app_data.get("rating", 2.5) - 2.5))
                
                return app_data
            else:
                logger.info(f"No iOS app found for '{app_name}'")
                return None
        except Exception as e:
            logger.error(f"Error fetching iOS app data: {str(e)}", exc_info=True)
            return None
    
    async def _fetch_play_store_data(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Fetch data for an Android app from the Play Store"""
        try:
            search_term = app_name.replace(' ', '+')
            search_url = f"https://play.google.com/store/search?q={search_term}&c=apps"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch Play Store search results: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            app_links = soup.select('a[href^="/store/apps/details?id="]')
            
            if not app_links:
                logger.info(f"No Android apps found for '{app_name}'")
                return None
            
            # Extract package ID from the first result
            href = app_links[0]['href']
            import re
            package_match = re.search(r'id=([^&]+)', href)
            if not package_match:
                logger.warning("Could not extract package ID from Play Store link")
                return None
            
            package_id = package_match.group(1)
            logger.info(f"Found Android app with package: {package_id}")
            
            # Now get the app details
            app_url = f"https://play.google.com/store/apps/details?id={package_id}"
            app_response = requests.get(app_url, headers=headers)
            
            if app_response.status_code != 200:
                logger.warning(f"Failed to fetch app details: {app_response.status_code}")
                return None
            
            app_soup = BeautifulSoup(app_response.text, 'html.parser')
            
            # Extract app data
            app_data = {
                "app_id": package_id,
                "app_name": app_name,  # Default to search term
                "category": "Unknown",
                "developer": "Unknown",
                "has_in_app_purchases": False,
                "rating": None,
                "total_ratings": None,
                "price": 0,  # Default to free
                "size_mb": None,
            }
            
            # Try to extract app name from title
            title_elem = app_soup.select_one('h1')
            if title_elem:
                app_data["app_name"] = title_elem.text.strip()
            
            # Try to extract rating
            rating_elem = app_soup.select_one('div[role="img"][aria-label*="rating"]')
            if rating_elem:
                aria_label = rating_elem.get('aria-label', '')
                rating_match = re.search(r'([\d.]+) out of', aria_label)
                if rating_match:
                    app_data["rating"] = float(rating_match.group(1))
            
            # Try to extract other info
            info_elements = app_soup.select('div.bARER')
            for elem in info_elements:
                text = elem.text.lower()
                if 'in-app purchases' in text:
                    app_data["has_in_app_purchases"] = True
                elif 'mb' in text or 'gb' in text:
                    size_match = re.search(r'([\d.]+)\s*(mb|gb)', text, re.IGNORECASE)
                    if size_match:
                        size = float(size_match.group(1))
                        if size_match.group(2).lower() == 'gb':
                            size *= 1000  # Convert GB to MB
                        app_data["size_mb"] = size
            
            # Calculate feature engineering metrics
            app_data["positive_sentiment_ratio"] = 0.5 + (0.1 * min(5, app_data.get("rating", 2.5) - 2.5))
            
            # Set approximate days since last update and release
            # Since this info is harder to extract reliably, use defaults based on rating
            if app_data["rating"] is not None:
                if app_data["rating"] > 4.0:
                    app_data["days_since_last_update"] = 30  # Assume recently updated for high-rated apps
                else:
                    app_data["days_since_last_update"] = 90  # Assume less frequently updated for lower-rated apps
                
                app_data["days_since_release"] = 365  # Default to 1 year
            
            return app_data
        except Exception as e:
            logger.error(f"Error fetching Play Store data: {str(e)}", exc_info=True)
            return None
    
    def _interpret_longevity_score(self, score: float) -> Dict[str, str]:
        """Provide interpretation of the longevity score"""
        if score >= 0.8:
            return {
                "category": "Excellent",
                "description": "This app shows strong indicators of long-term success and user retention.",
                "expected_lifespan": "5+ years",
                "success_probability": "Very High"
            }
        elif score >= 0.6:
            return {
                "category": "Good",
                "description": "This app has solid fundamentals and is likely to remain viable for years.",
                "expected_lifespan": "3-5 years",
                "success_probability": "High"
            }
        elif score >= 0.4:
            return {
                "category": "Average",
                "description": "This app has moderate longevity indicators, typical of the average app.",
                "expected_lifespan": "1-3 years",
                "success_probability": "Medium"
            }
        elif score >= 0.2:
            return {
                "category": "Below Average",
                "description": "This app shows some concerning metrics that may limit its lifespan.",
                "expected_lifespan": "6 months - 1 year",
                "success_probability": "Low"
            }
        else:
            return {
                "category": "Poor",
                "description": "This app shows significant risk factors that suggest a short lifespan.",
                "expected_lifespan": "Less than 6 months",
                "success_probability": "Very Low"
            }
    
    def _get_feature_description(self, feature: str, value: Any) -> str:
        """Get human-readable description of a feature's impact"""
        descriptions = {
            "rating": f"App rating of {value}/5",
            "days_since_last_update": f"Last updated {value} days ago",
            "days_since_release": f"Released {value} days ago" if value else "Release date unknown",
            "downloads": f"Approximately {value} downloads",
            "size_mb": f"App size of {value} MB",
            "number_of_reviews": f"{value} user reviews",
            "positive_sentiment_ratio": f"{value*100:.1f}% positive sentiment in reviews" if value else "Sentiment unknown",
            "update_frequency": f"Updated every {value} days on average" if value else "Update frequency unknown",
            "has_in_app_purchases": "Offers in-app purchases" if value else "No in-app purchases",
            "price": f"Priced at ${value}" if value else "Free app",
            "content_rating": f"Content rated for {value}",
            "total_ratings": f"{value} total ratings"
        }
        
        return descriptions.get(feature, f"{feature}: {value}")
    
    def _generate_recommendations(self, app_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate specific recommendations based on app data"""
        recommendations = []
        
        # Extract key metrics
        rating = app_data.get("rating")
        days_since_update = app_data.get("days_since_last_update")
        positive_sentiment = app_data.get("positive_sentiment_ratio")
        
        # Rating-based recommendations
        if rating is not None:
            if rating < 3.5:
                recommendations.append({
                    "area": "User Satisfaction",
                    "issue": "Low app rating",
                    "recommendation": "Address common complaints in reviews and consider a major update to improve user experience."
                })
            elif rating < 4.0:
                recommendations.append({
                    "area": "User Satisfaction",
                    "issue": "Average app rating",
                    "recommendation": "Focus on improving specific features mentioned in user reviews to increase ratings."
                })
        
        # Update frequency recommendations
        if days_since_update is not None and days_since_update > 90:
            recommendations.append({
                "area": "App Maintenance",
                "issue": "Infrequent updates",
                "recommendation": "Establish a regular update schedule to fix bugs and add new features."
            })
        
        # Sentiment-based recommendations
        if positive_sentiment is not None and positive_sentiment < 0.6:
            recommendations.append({
                "area": "User Sentiment",
                "issue": "Negative user sentiment",
                "recommendation": "Analyze user reviews to identify pain points and prioritize addressing them."
            })
        
        # Generic recommendations if we don't have enough data
        if len(recommendations) < 2:
            recommendations.append({
                "area": "User Engagement",
                "issue": "Potential engagement improvements",
                "recommendation": "Consider adding features that encourage daily app usage, such as notifications, rewards, or social elements."
            })
            
            recommendations.append({
                "area": "Monetization",
                "issue": "Revenue optimization",
                "recommendation": "Review your monetization strategy compared to competitors in your category."
            })
        
        return recommendations 
