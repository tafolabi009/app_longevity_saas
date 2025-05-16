import os
import json
import logging
from typing import Dict, List, Optional
import joblib
import importlib.util
import glob
import sys
from pathlib import Path

# Add parent directory to path to make imports work in different environments
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

try:
    from core.config import settings
except ImportError:
    try:
        from backend.core.config import settings
    except ImportError:
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
        self.model_paths = [settings.MODEL_PATH] + settings.ADDITIONAL_MODEL_PATHS
        self.model_extensions = settings.MODEL_FILE_EXTENSIONS
        self.discover_models()
    
    def discover_models(self) -> Dict[str, Dict]:
        """
        Scan the model directory and discover available models
        """
        model_info = {}
        
        try:
            # Search in all model paths
            for base_path in self.model_paths:
                # Ensure path is absolute or relative to the backend directory
                if not os.path.isabs(base_path):
                    base_path = os.path.join(os.path.dirname(__file__), "..", base_path)
                
                # Ensure model directory exists
                os.makedirs(base_path, exist_ok=True)
                
                # Search for model files with supported extensions
                for ext in self.model_extensions:
                    model_files = glob.glob(os.path.join(base_path, f"*{ext}"))
                    
                    for model_path in model_files:
                        model_file = os.path.basename(model_path)
                        
                        # Skip scaler and preprocessor files
                        if model_file == "scaler.joblib" or model_file.startswith("preprocessor"):
                            continue
                        
                        model_name = os.path.splitext(model_file)[0]
                        
                        # Check for metadata files
                        metadata_paths = [
                            os.path.join(base_path, f"{model_name}_metadata.json"),
                            os.path.join(base_path, "model_metadata.json")
                        ]
                        
                        metadata = {}
                        for metadata_path in metadata_paths:
                            if os.path.exists(metadata_path):
                                try:
                                    with open(metadata_path, 'r') as f:
                                        metadata = json.load(f)
                                    break
                                except Exception as e:
                                    logger.warning(f"Error reading metadata file {metadata_path}: {str(e)}")
                        
                        # Record the model
                        model_info[model_name] = {
                            'file_name': model_file,
                            'metadata': metadata,
                            'type': model_name.split('_')[0] if '_' in model_name else model_name,
                            'full_path': model_path,
                            'directory': base_path
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
            model_path = model_info['full_path']
            model_dir = model_info['directory']
            
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
            
            # Look for scaler in the same directory as the model
            scaler = None
            scaler_paths = [
                os.path.join(model_dir, "scaler.joblib"),
                os.path.join(model_dir, f"{model_name}_scaler.joblib")
            ]
            
            for scaler_path in scaler_paths:
                if os.path.exists(scaler_path):
                    try:
                        scaler = joblib.load(scaler_path)
                        break
                    except Exception as e:
                        logger.warning(f"Error loading scaler from {scaler_path}: {str(e)}")
            
            # Look for preprocessor in the same directory
            preprocessor = None
            preprocessor_paths = [
                os.path.join(model_dir, "preprocessor.pkl"),
                os.path.join(model_dir, f"{model_name}_preprocessor.pkl")
            ]
            
            for preprocessor_path in preprocessor_paths:
                if os.path.exists(preprocessor_path):
                    try:
                        preprocessor = joblib.load(preprocessor_path)
                        break
                    except Exception as e:
                        logger.warning(f"Error loading preprocessor from {preprocessor_path}: {str(e)}")
            
            # Look for feature importances
            feature_importances = {}
            feature_importances_paths = [
                os.path.join(model_dir, f"{model_info['type']}_feature_importance.json"),
                os.path.join(model_dir, f"{model_name}_feature_importance.json"),
                os.path.join(model_dir, "feature_importance.json")
            ]
            
            for fi_path in feature_importances_paths:
                if os.path.exists(fi_path):
                    try:
                        with open(fi_path, 'r') as f:
                            feature_importances = json.load(f)
                        break
                    except Exception as e:
                        logger.warning(f"Error loading feature importances from {fi_path}: {str(e)}")
            
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
