import os
import uuid
from PIL import Image
import pytesseract
from fastapi import UploadFile
from app.config import settings
from app.core.exceptions import ImageProcessingError
import logging

logger = logging.getLogger(__name__)

class ImageService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def validate_image(self, file: UploadFile) -> bool:
        """Validate uploaded image file"""
        # Check file size
        contents = await file.read()
        if len(contents) > settings.MAX_UPLOAD_SIZE:
            raise ImageProcessingError("File size exceeds maximum allowed")
        
        # Check file type
        if file.content_type not in settings.allowed_image_types_list:
            raise ImageProcessingError(f"File type {file.content_type} not allowed")
        
        # Reset file pointer
        await file.seek(0)
        return True
    
    async def save_image(self, file: UploadFile) -> str:
        """Save uploaded image temporarily"""
        try:
            # Generate unique filename
            file_extension = file.filename.split(".")[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # Save file
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
            
            logger.info(f"Image saved: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            raise ImageProcessingError("Failed to save image")
    
    def preprocess_image(self, image_path: str) -> Image.Image:
        """Preprocess image for better OCR results"""
        try:
            img = Image.open(image_path)
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large
            max_size = (2000, 2000)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            return img
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise ImageProcessingError("Failed to preprocess image")
    
    def extract_text_ocr(self, image_path: str) -> str:
        """Extract text from image using Tesseract OCR"""
        try:
            img = self.preprocess_image(image_path)
            
            # Configure Tesseract
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(img, config=custom_config)
            
            logger.info(f"OCR extracted text length: {len(text)}")
            return text.strip()
        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            raise ImageProcessingError("Failed to extract text from image")
    
    async def extract_text_vision_llm(self, image_path: str, llm_service) -> str:
        """Extract text using LLM vision capabilities (GPT-4 Vision)"""
        # This will be implemented if using vision LLM instead of OCR
        # For Phase 1, we'll use OCR primarily
        pass
    
    def parse_ingredients(self, text: str) -> list[str]:
        """Parse ingredient list from extracted text"""
        try:
            # Simple parsing logic
            # Look for common patterns: "Ingredients:", comma-separated lists
            
            lines = text.split('\n')
            ingredient_section = []
            found_ingredients = False
            
            for line in lines:
                line_lower = line.lower()
                
                # Detect ingredient section start
                if 'ingredient' in line_lower:
                    found_ingredients = True
                    # Check if ingredients are on same line
                    if ':' in line:
                        ingredient_section.append(line.split(':', 1)[1])
                    continue
                
                # Collect ingredient lines
                if found_ingredients and line.strip():
                    ingredient_section.append(line)
                
                # Stop at other sections
                if found_ingredients and any(keyword in line_lower for keyword in ['nutrition', 'allergen', 'warning']):
                    break
            
            # Join and split by common delimiters
            ingredient_text = ' '.join(ingredient_section)
            ingredients = [ing.strip() for ing in ingredient_text.split(',')]
            ingredients = [ing for ing in ingredients if ing and len(ing) > 2]
            
            logger.info(f"Parsed {len(ingredients)} ingredients")
            return ingredients
        except Exception as e:
            logger.error(f"Error parsing ingredients: {str(e)}")
            return []
    
    def cleanup_image(self, image_path: str):
        """Delete temporary image file"""
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
                logger.info(f"Cleaned up image: {image_path}")
        except Exception as e:
            logger.error(f"Error cleaning up image: {str(e)}")
    
    async def process_image(self, file: UploadFile) -> dict:
        """Main method to process uploaded image"""
        image_path = None
        try:
            # Validate image
            await self.validate_image(file)
            
            # Save image
            image_path = await self.save_image(file)
            
            # Extract text
            extracted_text = self.extract_text_ocr(image_path)
            
            # Parse ingredients
            ingredients = self.parse_ingredients(extracted_text)
            
            return {
                "success": True,
                "extracted_text": extracted_text,
                "ingredients": ingredients,
                "ingredient_count": len(ingredients)
            }
        except ImageProcessingError as e:
            raise e
        except Exception as e:
            logger.error(f"Unexpected error in image processing: {str(e)}")
            raise ImageProcessingError("Unexpected error during image processing")
        finally:
            # Cleanup
            if image_path:
                self.cleanup_image(image_path)

# Singleton instance
image_service = ImageService()