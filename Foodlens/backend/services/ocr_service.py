"""
Enhanced OCR Service for food product nutrition analysis
Specialized in detecting and extracting structured nutrition tables from images
Optimized for Turkish food product labels with European Nutri-Score calculation
"""

import os
import cv2
import numpy as np
import re
import logging
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor
import asyncio
from PIL import Image, ImageEnhance, ImageFilter
from collections import defaultdict
import math

# Set environment variable to use PyTorch backend for DocTR
os.environ['USE_TORCH'] = '1'

# Optional imports for OCR libraries
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logging.warning("EasyOCR not available. Install with: pip install easyocr")

# Doctr imports
try:
    from doctr.io import DocumentFile
    from doctr.models import ocr_predictor
    DOCTR_AVAILABLE = True
except ImportError:
    DOCTR_AVAILABLE = False
    logging.warning("Doctr not available. Install with: pip install python-doctr")

# Pytesseract for advanced table detection
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    logging.warning("Pytesseract not available. Install with: pip install pytesseract")

# Advanced image processing
try:
    from skimage import restoration, filters, morphology
    from skimage.transform import rotate
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False
    logging.warning("Scikit-image not available. Install for advanced image processing")

class EnhancedOCRService:
    def __init__(self):
        """Initialize Enhanced OCR service with specialized nutrition table detection"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize EasyOCR readers if available
        self.easyocr_readers = {}
        if EASYOCR_AVAILABLE:
            try:
                # Turkish and English readers with optimized settings
                self.easyocr_readers = {
                    'tr': easyocr.Reader(['tr', 'en'], gpu=False, 
                                       model_storage_directory='./models/easyocr'),
                    'en': easyocr.Reader(['en', 'tr'], gpu=False,
                                       model_storage_directory='./models/easyocr')
                }
                self.logger.info("EasyOCR readers initialized successfully")
            except Exception as e:
                self.logger.warning(f"Could not initialize EasyOCR: {e}")
                self.easyocr_readers = {}
        
        # Initialize Doctr if available
        if DOCTR_AVAILABLE:
            try:
                # Use a more accurate model for food labels
                self.doctr_model = ocr_predictor(det_arch='db_resnet50', 
                                               reco_arch='crnn_vgg16_bn', 
                                               pretrained=True)
                self.logger.info("Doctr model initialized successfully")
            except Exception as e:
                self.logger.warning(f"Could not initialize Doctr: {e}")
                self.doctr_model = None
        else:
            self.doctr_model = None
        
        # Enhanced nutrition table keywords (multilingual)
        self.nutrition_keywords = {
            'table_headers': [
                'nutrition', 'besin', 'nährwert', 'valeur nutritive', 'valor nutritivo',
                'nutritional', 'beslenme', 'nutrition facts', 'besin değerleri',
                'değerleri', 'facts', 'içerik', 'content', 'tablası', 'table',
                'bilgiler', 'information', 'analiz', 'analysis'
            ],
            'per_portion': [
                'per 100g', 'per 100ml', '100g başına', '100 g', '100 ml', '100gr',
                'porsiyon', 'portion', 'porción', 'serving', 'başına', 'per',
                'ortalama', 'average', 'yaklaşık', 'approximately'
            ],
            'nutrient_names': [
                'energy', 'enerji', 'calories', 'kalori', 'kkal', 'kcal', 'kj',
                'fat', 'yağ', 'total fat', 'toplam yağ', 'lipid', 'lipids',
                'carbohydrate', 'karbonhidrat', 'carbs', 'karbon', 'hidrat',
                'protein', 'protein', 'sugar', 'şeker', 'sugars', 'şekerler',
                'salt', 'tuz', 'sodium', 'sodyum', 'fiber', 'lif', 'fibre',
                'saturated', 'doymuş', 'trans', 'saturates', 'doymamış',
                'cholesterol', 'kolesterol', 'calcium', 'kalsiyum',
                'iron', 'demir', 'vitamin', 'mineral'
            ]
        }
        
        # Advanced image preprocessing parameters
        self.preprocessing_params = {
            'resize_threshold': 2048,  # Increased for better small text detection
            'min_resize': 800,  # Minimum size to maintain detail
            'contrast_methods': ['adaptive', 'clahe', 'standard', 'gamma'],
            'denoise_strength': 5,
            'threshold_methods': ['adaptive', 'otsu', 'triangle'],
            'rotation_correction': True,
            'deskew_threshold': 0.5,
            'morphological_operations': True,
            'sharpen_kernel': np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        }
    
    def preprocess_image_for_ocr(self, image_path: str) -> List[np.ndarray]:
        """
        Advanced preprocessing pipeline for optimal OCR performance
        Returns multiple processed versions of the image for best results
        """
        try:
            # Read image
            original = cv2.imread(image_path)
            if original is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Convert to RGB
            rgb_image = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
            
            # Resize if too large (optimize for OCR)
            height, width = rgb_image.shape[:2]
            if max(width, height) > self.preprocessing_params['resize_threshold']:
                scale = self.preprocessing_params['resize_threshold'] / max(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                rgb_image = cv2.resize(rgb_image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Create grayscale
            gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
            
            # Auto-rotate if needed (find major text orientation)
            if self.preprocessing_params['rotation_correction']:
                try:
                    # Use Hough transform to find lines for table alignment
                    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
                    lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
                    
                    if lines is not None:
                        angles = []
                        for line in lines:
                            rho, theta = line[0]
                            # Convert to degrees and normalize to -90 to 90
                            angle = (theta * 180 / np.pi) % 180
                            if angle > 90:
                                angle -= 180
                            angles.append(angle)
                        
                        # Find most common angle using histogram
                        hist, bins = np.histogram(angles, bins=36, range=(-90, 90))
                        dominant_angle = bins[np.argmax(hist)]
                        
                        # Only rotate if angle is significant
                        if abs(dominant_angle) > self.preprocessing_params['deskew_threshold']:
                            center = (gray.shape[1] // 2, gray.shape[0] // 2)
                            rotation_matrix = cv2.getRotationMatrix2D(center, dominant_angle, 1.0)
                            gray = cv2.warpAffine(gray, rotation_matrix, (gray.shape[1], gray.shape[0]), 
                                                flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                            rgb_image = cv2.warpAffine(rgb_image, rotation_matrix, (rgb_image.shape[1], rgb_image.shape[0]), 
                                                    flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                except Exception as e:
                    self.logger.warning(f"Rotation correction failed: {e}")
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray, None, self.preprocessing_params['denoise_strength'], 7, 21)
            
            processed_images = [rgb_image]  # Always include original
            
            # Generate multiple processing variants for best results
            
            # 1. Adaptive thresholding
            if 'adaptive' in self.preprocessing_params['threshold_methods']:
                adaptive_threshold = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                                          cv2.THRESH_BINARY, 11, 2)
                processed_images.append(cv2.cvtColor(adaptive_threshold, cv2.COLOR_GRAY2RGB))
            
            # 2. OTSU thresholding
            if 'otsu' in self.preprocessing_params['threshold_methods']:
                _, otsu_threshold = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                processed_images.append(cv2.cvtColor(otsu_threshold, cv2.COLOR_GRAY2RGB))
            
            # 3. CLAHE (Contrast Limited Adaptive Histogram Equalization)
            if 'clahe' in self.preprocessing_params['contrast_methods']:
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                clahe_img = clahe.apply(gray)
                processed_images.append(cv2.cvtColor(clahe_img, cv2.COLOR_GRAY2RGB))
            
            # 4. Standard contrast enhancement
            if 'standard' in self.preprocessing_params['contrast_methods']:
                alpha = 1.5  # Contrast control
                beta = 10    # Brightness control
                contrast_img = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
                processed_images.append(cv2.cvtColor(contrast_img, cv2.COLOR_GRAY2RGB))
            
            return processed_images
            
        except Exception as e:
            self.logger.error(f"Error preprocessing image: {e}")
            # Return original image as fallback
            return [cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)]
    
    def detect_nutrition_table(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect and extract nutrition table region from image
        Returns the cropped table region or None if not found
        """
        try:
            # Convert to grayscale for processing
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
            
            # Find table-like structures (using edge detection and contour analysis)
            # Step 1: Edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Step 2: Dilate to connect broken lines
            kernel = np.ones((3, 3), np.uint8)
            dilated = cv2.dilate(edges, kernel, iterations=2)
            
            # Step 3: Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Find potential table-like rectangular contours
            potential_tables = []
            for contour in contours:
                # Check if contour is rectangular-ish
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                
                # Check if it's a rectangle or close to it (4-6 sides)
                if 4 <= len(approx) <= 6:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / float(h)
                    area = w * h
                    
                    # Tables typically have aspect ratio between 0.5 and 3, and significant area
                    if 0.5 <= aspect_ratio <= 3.0 and area > 10000 and area < 0.8 * gray.shape[0] * gray.shape[1]:
                        potential_tables.append((x, y, w, h, area))
            
            # Sort by area (largest first) as tables are usually large
            potential_tables.sort(key=lambda x: x[4], reverse=True)
            
            # Get the top candidates
            top_candidates = potential_tables[:3]
            
            # Score the candidates based on how likely they are to contain a nutrition table
            # by checking for specific text patterns inside
            best_candidate = None
            highest_score = -1
            
            # OCR only once for efficiency
            if PYTESSERACT_AVAILABLE and top_candidates:
                for x, y, w, h, area in top_candidates:
                    # Extract the region
                    roi = image[y:y+h, x:x+w]
                    
                    # Use pytesseract for quick text recognition
                    try:
                        text = pytesseract.image_to_string(roi).lower()
                        
                        # Score based on presence of nutrition keywords
                        score = 0
                        for keyword_type, keywords in self.nutrition_keywords.items():
                            for keyword in keywords:
                                if keyword.lower() in text:
                                    # Give more weight to table headers
                                    if keyword_type == 'table_headers':
                                        score += 3
                                    else:
                                        score += 1
                        
                        # Check if region contains numbers (nutrition tables always have numbers)
                        if re.search(r'\d', text):
                            score += 2
                        
                        # Check if region contains multiple lines (tables usually have many)
                        if len(text.split('\n')) > 3:
                            score += 2
                            
                        # Update best candidate if this one scores higher
                        if score > highest_score:
                            highest_score = score
                            best_candidate = (x, y, w, h)
                    except Exception as e:
                        self.logger.warning(f"Error processing table candidate with pytesseract: {e}")
            
            # If we found a good candidate with nutrition keywords, return the cropped region
            if best_candidate and highest_score >= 3:
                x, y, w, h = best_candidate
                # Add some padding around the table
                padding = 20
                x_start = max(0, x - padding)
                y_start = max(0, y - padding)
                x_end = min(image.shape[1], x + w + padding)
                y_end = min(image.shape[0], y + h + padding)
                return image[y_start:y_end, x_start:x_end]
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting nutrition table: {e}")
            return None
    
    def extract_text_easyocr(self, image: np.ndarray, language: str = 'tr') -> List[Dict]:
        """
        Extract text using EasyOCR with enhanced detection for nutrition information
        """
        if not EASYOCR_AVAILABLE or not self.easyocr_readers:
            return []
            
        try:
            reader = self.easyocr_readers.get(language, self.easyocr_readers.get('tr'))
            if not reader:
                return []
            
            # Extract text with bounding boxes and confidence scores
            # Use paragraph=False for nutrition tables to better preserve structure
            results = reader.readtext(image, detail=1, paragraph=False)
            
            extracted_texts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # Lower threshold for nutrition tables
                    # Store text with position info for table structure analysis
                    x_min = min([point[0] for point in bbox])
                    y_min = min([point[1] for point in bbox])
                    x_max = max([point[0] for point in bbox])
                    y_max = max([point[1] for point in bbox])
                    
                    extracted_texts.append({
                        'text': text.strip(),
                        'confidence': confidence,
                        'bbox': bbox,
                        'position': {
                            'x_min': x_min,
                            'y_min': y_min,
                            'x_max': x_max,
                            'y_max': y_max,
                            'center_x': (x_min + x_max) / 2,
                            'center_y': (y_min + y_max) / 2
                        },
                        'method': 'easyocr'
                    })
            
            return extracted_texts
            
        except Exception as e:
            self.logger.error(f"EasyOCR extraction failed: {e}")
            return []
    
    def extract_text_doctr(self, image_path: str) -> List[Dict]:
        """
        Extract text using Doctr with position information
        """
        if not DOCTR_AVAILABLE or not self.doctr_model:
            return []
        
        try:
            # Load document
            doc = DocumentFile.from_images(image_path)
            
            # Run OCR
            result = self.doctr_model(doc)
            
            extracted_texts = []
            for page in result.pages:
                page_height = page.dimensions[1]
                page_width = page.dimensions[0]
                
                for block in page.blocks:
                    for line in block.lines:
                        for word in line.words:
                            if word.confidence > 0.3:  # Lower threshold for nutrition tables
                                # Convert relative coordinates to absolute
                                x_min = word.geometry[0][0] * page_width
                                y_min = word.geometry[0][1] * page_height
                                x_max = word.geometry[1][0] * page_width
                                y_max = word.geometry[1][1] * page_height
                                
                                extracted_texts.append({
                                    'text': word.value,
                                    'confidence': word.confidence,
                                    'bbox': [[x_min, y_min], [x_max, y_min], 
                                            [x_max, y_max], [x_min, y_max]],
                                    'position': {
                                        'x_min': x_min,
                                        'y_min': y_min,
                                        'x_max': x_max,
                                        'y_max': y_max,
                                        'center_x': (x_min + x_max) / 2,
                                        'center_y': (y_min + y_max) / 2
                                    },
                                    'method': 'doctr'
                                })
            
            return extracted_texts
            
        except Exception as e:
            self.logger.error(f"Doctr extraction failed: {e}")
            return []
    
    def identify_table_structure(self, texts: List[Dict]) -> Dict:
        """
        Analyze position data to identify table structure (columns and rows)
        Returns a structured representation of the table
        """
        if not texts:
            return {'rows': [], 'columns': [], 'cells': {}}
        
        try:
            # Step 1: Identify potential rows based on y-coordinate clustering
            y_centers = [text['position']['center_y'] for text in texts]
            
            # Simple clustering of y-coordinates to identify rows (within 15px tolerance)
            tolerance = 15
            y_clusters = []
            current_cluster = [y_centers[0]]
            current_avg = y_centers[0]
            
            for y in y_centers[1:]:
                if abs(y - current_avg) <= tolerance:
                    current_cluster.append(y)
                    current_avg = sum(current_cluster) / len(current_cluster)
                else:
                    y_clusters.append(current_avg)
                    current_cluster = [y]
                    current_avg = y
            
            if current_cluster:
                y_clusters.append(current_avg)
            
            # Sort clusters by y-coordinate (top to bottom)
            y_clusters.sort()
            
            # Step 2: Identify potential columns based on x-coordinate clustering
            x_centers = [text['position']['center_x'] for text in texts]
            
            # Simple clustering of x-coordinates to identify columns (within 30px tolerance)
            tolerance = 30
            x_clusters = []
            current_cluster = [x_centers[0]]
            current_avg = x_centers[0]
            
            for x in x_centers[1:]:
                if abs(x - current_avg) <= tolerance:
                    current_cluster.append(x)
                    current_avg = sum(current_cluster) / len(current_cluster)
                else:
                    x_clusters.append(current_avg)
                    current_cluster = [x]
                    current_avg = x
            
            if current_cluster:
                x_clusters.append(current_avg)
            
            # Sort clusters by x-coordinate (left to right)
            x_clusters.sort()
            
            # Step 3: Assign texts to cells in the table grid
            cells = {}
            for text in texts:
                # Find closest row
                y_idx = min(range(len(y_clusters)), 
                           key=lambda i: abs(text['position']['center_y'] - y_clusters[i]))
                
                # Find closest column
                x_idx = min(range(len(x_clusters)), 
                           key=lambda i: abs(text['position']['center_x'] - x_clusters[i]))
                
                cell_key = f"{y_idx}_{x_idx}"
                if cell_key not in cells:
                    cells[cell_key] = []
                
                cells[cell_key].append(text)
            
            # Sort each cell's texts by confidence
            for cell_key in cells:
                cells[cell_key].sort(key=lambda text: text['confidence'], reverse=True)
            
            return {
                'rows': y_clusters,
                'columns': x_clusters,
                'cells': cells
            }
            
        except Exception as e:
            self.logger.error(f"Error identifying table structure: {e}")
            return {'rows': [], 'columns': [], 'cells': {}}
    
    def extract_nutrition_from_table(self, table_structure: Dict) -> Dict:
        """
        Extract nutritional information from the identified table structure
        """
        nutrition_values = {
            'energy_kj': None,
            'energy_kcal': None,
            'fat': None,
            'saturated_fat': None,
            'carbohydrates': None,
            'sugars': None,
            'fiber': None,
            'proteins': None,
            'salt': None,
            'sodium': None
        }
        
        # Nutrition keyword patterns (multilingual)
        patterns = {
            'energy_kj': [r'enerji.*kj', r'energy.*kj'],
            'energy_kcal': [r'enerji.*kcal', r'energy.*kcal', r'kalori', r'calories'],
            'fat': [r'yağ', r'fat'],
            'saturated_fat': [r'doymuş.*yağ', r'saturated.*fat'],
            'carbohydrates': [r'karbonhidrat', r'carbohydrate'],
            'sugars': [r'şeker', r'sugar'],
            'fiber': [r'lif', r'fiber', r'fibre'],
            'proteins': [r'protein', r'protein'],
            'salt': [r'tuz', r'salt'],
            'sodium': [r'sodyum', r'sodium']
        }
        
        # For each cell in the table
        for cell_key, texts in table_structure['cells'].items():
            row_idx, col_idx = map(int, cell_key.split('_'))
            
            # Check each text in the cell
            for text in texts:
                text_lower = text['text'].lower()
                
                # Try to identify the nutrient type
                nutrient_found = False
                for nutrient, pattern_list in patterns.items():
                    if any(re.search(pattern, text_lower) for pattern in pattern_list):
                        nutrient_found = True
                        
                        # Look for a value in adjacent cells (same row, different columns)
                        for value_col_idx in range(len(table_structure['columns'])):
                            if value_col_idx == col_idx:
                                continue
                                
                            value_cell_key = f"{row_idx}_{value_col_idx}"
                            if value_cell_key in table_structure['cells']:
                                for value_text in table_structure['cells'][value_cell_key]:
                                    value_match = re.search(r'(\d+(?:[.,]\d+)?)', value_text['text'])
                                    if value_match:
                                        value = float(value_match.group(0).replace(',', '.'))
                                        nutrition_values[nutrient] = value
                                        break
                        
                        # If no value found in adjacent cells, check if there's a value in the same cell
                        if nutrition_values[nutrient] is None:
                            value_match = re.search(r'(\d+(?:[.,]\d+)?)', text['text'])
                            if value_match:
                                value = float(value_match.group(0).replace(',', '.'))
                                nutrition_values[nutrient] = value
                                
                        break
                
                # If we found a nutrient in this text, move to next text
                if nutrient_found:
                    break
        
        # Clean up the nutrition values
        for key in nutrition_values:
            if nutrition_values[key] is None:
                nutrition_values[key] = 0.0
        
        return nutrition_values
    
    def clean_and_combine_text(self, ocr_results: List[Dict]) -> str:
        """
        Clean and combine OCR results into a single text string
        """
        if not ocr_results:
            return ""
        
        # Sort by confidence
        sorted_results = sorted(ocr_results, key=lambda x: x['confidence'], reverse=True)
        
        # Deduplicate and combine
        seen_texts = set()
        clean_texts = []
        
        for result in sorted_results:
            # Clean text
            text = self.clean_text(result['text'])
            
            # Skip if too short or already seen
            if len(text) <= 1 or text.lower() in seen_texts:
                continue
                
            clean_texts.append(text)
            seen_texts.add(text.lower())
        
        return ' '.join(clean_texts)
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text
        """
        # Remove special characters but keep Turkish characters
        text = re.sub(r'[^\w\s\-\.\,\%\(\)çÇğĞıİöÖşŞüÜ]', '', text)
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing spaces
        text = text.strip()
        
        return text
    
    def extract_ingredients_from_text(self, text: str) -> List[str]:
        """
        Extract ingredient list from OCR text
        """
        # Common ingredient indicators in Turkish and English
        ingredient_patterns = [
            r'İçindekiler[:\s]+(.*?)(?=\n|$)',
            r'Ingredients[:\s]+(.*?)(?=\n|$)',
            r'Malzemeler[:\s]+(.*?)(?=\n|$)',
            r'INGREDIENTS[:\s]+(.*?)(?=\n|$)',
            r'İÇİNDEKİLER[:\s]+(.*?)(?=\n|$)'
        ]
        
        ingredients = []
        
        for pattern in ingredient_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Split by common separators
                ingredient_list = re.split(r'[,;]\s*', match.strip())
                ingredients.extend([ing.strip() for ing in ingredient_list if ing.strip()])
        
        return ingredients
    
    async def process_image_async(self, image_path: str, language: str = 'tr') -> Dict:
        """
        Async process image with enhanced nutrition table detection
        """
        try:
            # Step 1: Advanced preprocessing
            processed_images = self.preprocess_image_for_ocr(image_path)
            
            # Step 2: Detect nutrition table in each processed image
            table_regions = []
            for processed_img in processed_images:
                table_region = self.detect_nutrition_table(processed_img)
                if table_region is not None:
                    table_regions.append(table_region)
            
            # Step 3: Extract text from both table regions and full images in parallel
            all_results = []
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                
                # Process full images first
                for processed_img in processed_images:
                    futures.append(executor.submit(
                        self.extract_text_easyocr, processed_img, language
                    ))
                
                # Process detected table regions (if any)
                for table_region in table_regions:
                    futures.append(executor.submit(
                        self.extract_text_easyocr, table_region, language
                    ))
                
                # Add doctr results
                futures.append(executor.submit(
                    self.extract_text_doctr, image_path
                ))
                
                # Get all results
                for future in futures:
                    result = future.result()
                    if result:
                        all_results.extend(result)
            
            # Step 4: Identify table structure in the results
            table_structure = self.identify_table_structure(all_results)
            
            # Step 5: Extract nutrition information from the table
            nutrition_values = self.extract_nutrition_from_table(table_structure)
            
            # Combine all text for ingredient extraction
            combined_text = self.clean_and_combine_text(all_results)
            
            # Extract ingredients
            ingredients = self.extract_ingredients_from_text(combined_text)
            
            # Calculate confidence based on how many nutrition values we found
            num_values_found = sum(1 for val in nutrition_values.values() if val > 0)
            confidence_score = min(0.95, num_values_found / len(nutrition_values) * 0.8 + 0.2)
            
            return {
                'success': True,
                'text': combined_text,
                'ingredients': ingredients,
                'nutrition_values': nutrition_values,
                'confidence': confidence_score,
                'table_structure': {
                    'rows': len(table_structure['rows']),
                    'columns': len(table_structure['columns']),
                    'cells': len(table_structure['cells'])
                },
                'language': language
            }
            
        except Exception as e:
            self.logger.error(f"Error processing image {image_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'ingredients': [],
                'nutrition_values': {},
                'confidence': 0.0,
                'language': language
            }
    
    def process_image(self, image_path: str, language: str = 'tr') -> Dict:
        """
        Synchronous wrapper for enhanced image processing
        """
        try:
            return asyncio.run(self.process_image_async(image_path, language))
        except Exception as e:
            self.logger.error(f"Enhanced OCR processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'ingredients': [],
                'nutrition_values': {},
                'confidence': 0.0,
                'language': language
            }


# Singleton instance
enhanced_ocr_service = EnhancedOCRService()
