from typing import Optional, Dict
from PIL import Image
from io import BytesIO
import base64

class ImageService:
    """Service class for image processing"""
    
    @staticmethod
    def validate_image(image_bytes: bytes) -> bool:
        """
        Validate if the bytes represent a valid image
        
        Args:
            image_bytes: Image file as bytes
        
        Returns:
            True if valid image, False otherwise
        """
        try:
            Image.open(BytesIO(image_bytes))
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_image_info(image_bytes: bytes) -> Dict[str, any]:
        """
        Get image information
        
        Args:
            image_bytes: Image file as bytes
        
        Returns:
            Dictionary with image information
        """
        try:
            img = Image.open(BytesIO(image_bytes))
            return {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height
            }
        except Exception as e:
            raise ValueError(f"Could not process image: {str(e)}")
    
    @staticmethod
    def image_to_base64(image_bytes: bytes) -> str:
        """
        Convert image bytes to base64 string for API transmission
        
        Args:
            image_bytes: Image file as bytes
        
        Returns:
            Base64 encoded string
        """
        return base64.b64encode(image_bytes).decode('utf-8')
    
    @staticmethod
    def base64_to_image(base64_string: str) -> bytes:
        """
        Convert base64 string to image bytes
        
        Args:
            base64_string: Base64 encoded image string
        
        Returns:
            Image as bytes
        """
        return base64.b64decode(base64_string)

