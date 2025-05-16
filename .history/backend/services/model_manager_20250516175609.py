import os
import json
import logging
from typing import Dict, List, Optional
import joblib
import importlib.util

from app_longevity_saas.backend.core.config import settings

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Service for managing prediction models.
    Handles model discovery, loading, and management.
    """
    
    def __init__(self):
        self.models = {}
        self.default_model_name = settings.DEFAULT_MODEL
        self.model_path = settings.MODEL_PATH
        self.discover_models()
    
    def discover_models(self) -> Dict[str, Dict]:
        """
        Scan the model directory and discover available models
        """
        model_info = {}
        
        try:
            # Ensure model directory exists
            os.makedirs(os.path.join(os.path.dirname(__file__), "..", self.model_path), exist_ok=True)
            
            # List files in the model directory
            model_files = [f for f in os.listdir(os.path.join(os.path.dirname(__file__), "..", self.model_path)) 
                          if f.endswith(('.joblib', '.pkl', '.h5', '.keras'))]
            
            for model_file in model_files:
                if model_file.endswith(('.joblib', '.pkl', '.h5', '.keras')) and not model_file == "scaler.joblib" and not model_file.startswith(("preprocessor")):
                    model_name = os.path.splitext(model_file)[0]
                    
                    # Check for metadata file
                    metadata_file = os.path.join(os.path.dirname(__file__), "..", self.model_path, f"{model_name}_metadata.json")
                    alt_metadata_file = os.path.join(os.path.dirname(__file__), "..", self.model_path, "model_metadata.json")
                    
                    metadata = {}
                    if os.path.exists(metadata_file):
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                    elif os.path.exists(alt_metadata_file):
                        with open(alt_metadata_file, 'r') as f:
                            metadata = json.load(f)
                    
                    model_info[model_name] = {
                        'file_name': model_file,
                        'metadata': metadata,
                        'type': model_name.split('_')[0] if '_' in model_name else model_name,
                        'full_path': os.path.join(self.model_path, model_file)
                    }
            
            self.models = model_info
            logger.info(f"Discovered {len(model_info)} models: {list(model_info.keys())}")
            
            return model_info
        except Exception as e:
            logger.error(f"Error discovering models: {str(e)}")
            return {}
    
    def load_model(self, model_name: Optional[str] = None) -> Dict:
        """
        Load a specific model by name
        
        Args:
            model_name: Name of the model to load, or None to use default
            
        Returns:
            Dictionary with model, scaler, and feature_importances
        """
        if model_name is None:
            model_name = self.default_model_name
            # If default model name includes extension, strip it
            if '.' in model_name:
                model_name = os.path.splitext(model_name)[0]
        
        # If model wasn't discovered, try to discover it
        if model_name not in self.models:
            self.discover_models()
        
        # If still not found, use whatever is available
        if model_name not in self.models and self.models:
            model_name = list(self.models.keys())[0]
            logger.warning(f"Requested model {model_name} not found, using {model_name} instead")
        
        # If no models available, return empty
        if not self.models:
            logger.error("No models available")
            return {'model': None, 'scaler': None, 'feature_importances': {}}
        
        try:
            model_info = self.models[model_name]
            model_path = os.path.join(os.path.dirname(__file__), "..", model_info['full_path'])
            
            # Load model based on file extension
            if model_path.endswith(('.joblib', '.pkl')):
                model = joblib.load(model_path)
            elif model_path.endswith(('.h5', '.keras')):
                # Late import to avoid requiring tensorflow when not needed
                try:
                    from tensorflow.keras.models import load_model
                    model = load_model(model_path)
                except ImportError:
                    logger.error("Tensorflow not installed, cannot load Keras model")
                    return {'model': None, 'scaler': None, 'feature_importances': {}}
            else:
                logger.error(f"Unsupported model format: {model_path}")
                return {'model': None, 'scaler': None, 'feature_importances': {}}
            
            # Load scaler if exists
            scaler = None
            scaler_path = os.path.join(os.path.dirname(__file__), "..", self.model_path, "scaler.joblib")
            if os.path.exists(scaler_path):
                scaler = joblib.load(scaler_path)
            
            # Load preprocessor if exists
            preprocessor = None
            preprocessor_path = os.path.join(os.path.dirname(__file__), "..", self.model_path, "preprocessor.pkl")
            if os.path.exists(preprocessor_path):
                preprocessor = joblib.load(preprocessor_path)
            
            # Load feature importances if exists
            feature_importances = {}
            feature_importances_path = os.path.join(
                os.path.dirname(__file__), "..", 
                self.model_path, 
                f"{model_info['type']}_feature_importance.json"
            )
            
            if os.path.exists(feature_importances_path):
                with open(feature_importances_path, 'r') as f:
                    feature_importances = json.load(f)
            
            logger.info(f"Successfully loaded model {model_name}")
            
            return {
                'model': model,
                'scaler': scaler,
                'preprocessor': preprocessor,
                'feature_importances': feature_importances,
                'metadata': model_info.get('metadata', {})
            }
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")
            return {'model': None, 'scaler': None, 'feature_importances': {}}
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available model names
        """
        return list(self.models.keys())
    
    def get_model_info(self, model_name: Optional[str] = None) -> Dict:
        """
        Get information about a specific model
        """
        if model_name is None:
            model_name = self.default_model_name
        
        # If model name includes extension, strip it
        if '.' in model_name:
            model_name = os.path.splitext(model_name)[0]
        
        if model_name in self.models:
            return self.models[model_name]
        return {}

# Create a singleton instance
model_manager = ModelManager() 
