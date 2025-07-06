"""
Enhanced Nutri-Score calculation service for food product analysis
Based on European algorithm with improved accuracy and robustness
"""

import logging
import re
import math
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class NutritionData:
    """Enhanced nutritional data structure with validation and unit conversion"""
    energy_kj: float = 0.0
    energy_kcal: float = 0.0
    fat: float = 0.0
    saturated_fat: float = 0.0
    carbohydrates: float = 0.0
    sugars: float = 0.0
    fiber: float = 0.0
    proteins: float = 0.0
    salt: float = 0.0
    sodium: float = 0.0
    fruits_vegetables_nuts: float = 0.0  # percentage
    
    def validate_and_convert(self):
        """Validate nutrition values and perform necessary conversions"""
        # Convert energy units if needed
        if self.energy_kj <= 0 and self.energy_kcal > 0:
            # Convert kcal to kJ
            self.energy_kj = self.energy_kcal * 4.184
        elif self.energy_kcal <= 0 and self.energy_kj > 0:
            # Convert kJ to kcal
            self.energy_kcal = self.energy_kj / 4.184
        
        # Convert salt to sodium and vice versa if one is missing
        if self.sodium <= 0 and self.salt > 0:
            # Salt to sodium (sodium is ~40% of salt)
            self.sodium = self.salt * 400  # Convert to mg
        elif self.salt <= 0 and self.sodium > 0:
            # Sodium to salt
            self.salt = self.sodium / 1000 * 2.5  # Convert mg to g and multiply by 2.5
        
        # Validate ranges and fix unrealistic values
        self._validate_range('energy_kcal', 0, 900)
        self._validate_range('fat', 0, 100)
        self._validate_range('saturated_fat', 0, self.fat)  # Can't be more than total fat
        self._validate_range('carbohydrates', 0, 100)
        self._validate_range('sugars', 0, self.carbohydrates)  # Can't be more than total carbs
        self._validate_range('fiber', 0, 50)
        self._validate_range('proteins', 0, 100)
        self._validate_range('salt', 0, 50)
        self._validate_range('fruits_vegetables_nuts', 0, 100)
        
        # Ensure macronutrient consistency (total should not exceed 100g per 100g)
        total_macros = self.fat + self.carbohydrates + self.proteins
        if total_macros > 100:
            # Scale down proportionally
            scale_factor = 100 / total_macros
            self.fat *= scale_factor
            self.carbohydrates *= scale_factor
            self.proteins *= scale_factor
            # Also scale down components
            self.saturated_fat *= scale_factor
            self.sugars *= scale_factor
    
    def _validate_range(self, attribute: str, min_value: float, max_value: float):
        """Validate a value is within expected range or set to 0"""
        value = getattr(self, attribute)
        if not isinstance(value, (int, float)) or math.isnan(value) or value < min_value:
            setattr(self, attribute, 0.0)
        elif value > max_value:
            setattr(self, attribute, float(max_value))

class EnhancedNutriScoreCalculator:
    def __init__(self):
        """Initialize Enhanced Nutri-Score calculator"""
        self.logger = logging.getLogger(__name__)
        
        # Nutri-Score grade mapping
        self.grade_mapping = {
            'A': {'min': -15, 'max': -1, 'color': '#038141'},
            'B': {'min': 0, 'max': 2, 'color': '#85BB2F'},
            'C': {'min': 3, 'max': 10, 'color': '#FECB00'},
            'D': {'min': 11, 'max': 18, 'color': '#EE8100'},
            'E': {'min': 19, 'max': 40, 'color': '#E63312'}
        }
        
        # Common food types for classification
        self.food_types = {
            'cheese': ['peynir', 'cheese', 'fromage', 'käse'],
            'beverage': ['içecek', 'beverage', 'drink', 'su', 'water', 'juice', 'meyve suyu'],
            'added_fat': ['yağ', 'oil', 'zeytinyağı', 'olive oil', 'margarin', 'tereyağı', 'butter'],
            'breakfast_cereal': ['müsli', 'cornflakes', 'cereal', 'kahvaltılık gevrek']
        }
        
        # Multilingual nutrition terms for better extraction
        self.nutrition_terms = {
            'energy': ['energy', 'enerji', 'calories', 'kalori', 'kcal', 'kj'],
            'fat': ['fat', 'yağ', 'fett', 'matière grasse'],
            'saturated_fat': ['saturated fat', 'doymuş yağ', 'gesättigte fettsäuren', 'acides gras saturés'],
            'carbohydrates': ['carbohydrate', 'karbonhidrat', 'kohlenhydrate', 'glucides'],
            'sugars': ['sugar', 'şeker', 'zucker', 'sucres'],
            'fiber': ['fiber', 'fibre', 'lif', 'ballaststoffe', 'fibres'],
            'proteins': ['protein', 'protein', 'eiweiß', 'protéines'],
            'salt': ['salt', 'tuz', 'salz', 'sel'],
            'sodium': ['sodium', 'sodyum', 'natrium', 'sodium']
        }
    
    def extract_nutrition_from_values(self, nutrition_values: Dict) -> NutritionData:
        """
        Convert OCR extracted nutrition values to NutritionData object
        with validation and unit conversion
        """
        nutrition = NutritionData()
        
        # Map nutrition_values to NutritionData
        for key, value in nutrition_values.items():
            if hasattr(nutrition, key) and isinstance(value, (int, float)):
                setattr(nutrition, key, float(value))
        
        # Validate and convert units
        nutrition.validate_and_convert()
        
        return nutrition
    
    def extract_nutrition_from_text(self, text: str) -> NutritionData:
        """
        Extract nutritional information from OCR text with improved patterns
        """
        nutrition = NutritionData()
        
        # Advanced patterns for extracting nutritional values (multilingual)
        patterns = {
            'energy_kj': [
                r'enerji[:\s]*(\d+(?:[.,]\d+)?)\s*kj',
                r'energy[:\s]*(\d+(?:[.,]\d+)?)\s*kj',
                r'kj[:\s]*(\d+(?:[.,]\d+)?)'
            ],
            'energy_kcal': [
                r'enerji[:\s]*(\d+(?:[.,]\d+)?)\s*k?cal',
                r'energy[:\s]*(\d+(?:[.,]\d+)?)\s*k?cal',
                r'kalori[:\s]*(\d+(?:[.,]\d+)?)',
                r'calories[:\s]*(\d+(?:[.,]\d+)?)',
                r'kcal[:\s]*(\d+(?:[.,]\d+)?)'
            ],
            'fat': [
                r'yağ[:\s]*(\d+(?:[.,]\d+)?)\s*g',
                r'fat[:\s]*(\d+(?:[.,]\d+)?)\s*g',
                r'total\s+fat[:\s]*(\d+(?:[.,]\d+)?)\s*g',
                r'toplam\s+yağ[:\s]*(\d+(?:[.,]\d+)?)\s*g'
            ],
            'saturated_fat': [
                r'doymuş\s+yağ[:\s]*(\d+(?:[.,]\d+)?)\s*g',
                r'saturated\s+fat[:\s]*(\d+(?:[.,]\d+)?)\s*g',
                r'doymuş[:\s]*(\d+(?:[.,]\d+)?)\s*g'
            ],
            'carbohydrates': [
                r'karbonhidrat[:\s]*(\d+(?:[.,]\d+)?)\s*g',
                r'carbohydrate[:\s]*(\d+(?:[.,]\d+)?)\s*g',
                r'karb[:\s]*(\d+(?:[.,]\d+)?)\s*g',
                r'carbs?[:\s]*(\d+(?:[.,]\d+)?)\s*g'
            ],
            'sugars': [
                r'şeker[:\s]*(\d+(?:[.,]\d+)?)\s*g',
                r'sugar[:\s]*(\d+(?:[.,]\d+)?)\s*g'
            ],
            'fiber': [
                r'lif[:\s]*(\d+(?:[.,]\d+)?)\s*g',
                r'fiber[:\s]*(\d+(?:[.,]\d+)?)\s*g',
                r'fibre[:\s]*(\d+(?:[.,]\d+)?)\s*g'
            ],
            'proteins': [
                r'protein[:\s]*(\d+(?:[.,]\d+)?)\s*g'
            ],
            'salt': [
                r'tuz[:\s]*(\d+(?:[.,]\d+)?)\s*g',
                r'salt[:\s]*(\d+(?:[.,]\d+)?)\s*g'
            ],
            'sodium': [
                r'sodyum[:\s]*(\d+(?:[.,]\d+)?)\s*mg',
                r'sodium[:\s]*(\d+(?:[.,]\d+)?)\s*mg'
            ]
        }
        
        text_lower = text.lower()
        
        # Look for patterns with "per 100g" context to ensure we're getting the right values
        per_100g_patterns = [
            r'100\s*g', r'100g', r'per\s*100\s*g', r'100\s*gr',
            r'100\s*gramı', r'100\s*gram', r'her\s*100\s*g', r'başına'
        ]
        
        # Try to find sections that refer to per 100g values
        per_100g_sections = []
        for pattern in per_100g_patterns:
            matches = list(re.finditer(pattern, text_lower))
            for match in matches:
                # Take text around the match (200 chars before and after)
                start = max(0, match.start() - 200)
                end = min(len(text_lower), match.end() + 200)
                per_100g_sections.append(text_lower[start:end])
        
        # If we found per 100g sections, prioritize searching in them
        search_texts = per_100g_sections if per_100g_sections else [text_lower]
        
        for nutrient, pattern_list in patterns.items():
            # First try to find in per 100g sections
            found = False
            for section in search_texts:
                for pattern in pattern_list:
                    matches = re.findall(pattern, section, re.IGNORECASE)
                    if matches:
                        try:
                            value = float(matches[0].replace(',', '.'))
                            # Apply sanity checks
                            if value >= 0 and not math.isnan(value):
                                setattr(nutrition, nutrient, value)
                                found = True
                                break
                        except (ValueError, IndexError):
                            continue
                if found:
                    break
            
            # If not found in per 100g sections, try the full text
            if not found and search_texts != [text_lower]:
                for pattern in pattern_list:
                    matches = re.findall(pattern, text_lower, re.IGNORECASE)
                    if matches:
                        try:
                            value = float(matches[0].replace(',', '.'))
                            # Apply sanity checks
                            if value >= 0 and not math.isnan(value):
                                setattr(nutrition, nutrient, value)
                                break
                        except (ValueError, IndexError):
                            continue
        
        # Validate and convert units
        nutrition.validate_and_convert()
        
        return nutrition
    
    def estimate_fruits_vegetables_nuts_percentage(self, ingredients: List[str]) -> float:
        """
        Estimate the percentage of fruits, vegetables, and nuts in ingredients
        with improved heuristics
        """
        if not ingredients:
            return 0.0
        
        # Expanded keywords for fruits, vegetables, and nuts (multilingual)
        fvn_keywords = {
            # Fruits in multiple languages
            'fruits': [
                'meyve', 'fruit', 'früchte', 'fruits', 'elma', 'apple', 'portakal', 'orange',
                'çilek', 'strawberry', 'kiraz', 'cherry', 'üzüm', 'grape', 'muz', 'banana',
                'karpuz', 'watermelon', 'kavun', 'melon', 'ananas', 'pineapple', 'armut', 'pear',
                'şeftali', 'peach', 'kayısı', 'apricot', 'erik', 'plum', 'kivi', 'kiwi', 'incir', 'fig',
                'hurma', 'date', 'nar', 'pomegranate', 'böğürtlen', 'blackberry', 'ahududu', 'raspberry',
                'yaban mersini', 'blueberry', 'dut', 'mulberry'
            ],
            # Vegetables in multiple languages
            'vegetables': [
                'sebze', 'vegetable', 'gemüse', 'légumes', 'domates', 'tomato', 'salatalık', 'cucumber',
                'havuç', 'carrot', 'soğan', 'onion', 'sarımsak', 'garlic', 'patates', 'potato',
                'patlıcan', 'eggplant', 'kabak', 'zucchini', 'biber', 'pepper', 'marul', 'lettuce',
                'ıspanak', 'spinach', 'lahana', 'cabbage', 'brokoli', 'broccoli', 'karnabahar', 'cauliflower',
                'pırasa', 'leek', 'kereviz', 'celery', 'turp', 'radish', 'bezelye', 'pea',
                'fasulye', 'bean', 'mısır', 'corn', 'mantar', 'mushroom', 'pancar', 'beet',
                'enginar', 'artichoke', 'kuşkonmaz', 'asparagus', 'bamya', 'okra'
            ],
            # Nuts in multiple languages
            'nuts': [
                'kuruyemiş', 'nuts', 'nüsse', 'noix', 'badem', 'almond', 'fındık', 'hazelnut',
                'ceviz', 'walnut', 'antep fıstığı', 'pistachio', 'kaju', 'cashew', 'yer fıstığı', 'peanut',
                'çam fıstığı', 'pine nut', 'macadamia', 'macadamia', 'brezilya cevizi', 'brazil nut',
                'pekan', 'pecan'
            ],
            # Legumes in multiple languages
            'legumes': [
                'baklagil', 'legume', 'hülsenfrüchte', 'légumineuses', 'mercimek', 'lentil',
                'nohut', 'chickpea', 'fasulye', 'bean', 'barbunya', 'kidney bean', 'börülce', 'black-eyed pea',
                'bakla', 'broad bean', 'soya', 'soy', 'bezelye', 'pea'
            ]
        }
        
        # Weight of each ingredient (assuming ingredients are listed in descending order by weight)
        max_weight = 100
        min_weight = 20
        weight_step = (max_weight - min_weight) / (len(ingredients) - 1) if len(ingredients) > 1 else 0
        
        total_fvn_weight = 0
        total_weight = 0
        
        for i, ingredient in enumerate(ingredients):
            # Estimate weight based on position (earlier ingredients have higher weight)
            weight = max_weight - (i * weight_step)
            total_weight += weight
            
            ingredient_lower = ingredient.lower()
            
            # Check if this ingredient is fruit, vegetable, nut, or legume
            is_fvn = False
            for category, keywords in fvn_keywords.items():
                if any(keyword in ingredient_lower for keyword in keywords):
                    is_fvn = True
                    break
            
            # Add to FVN weight if it's a fruit, vegetable, nut, or legume
            if is_fvn:
                total_fvn_weight += weight
        
        # Calculate percentage
        if total_weight > 0:
            percentage = (total_fvn_weight / total_weight) * 100
            return min(percentage, 100.0)  # Cap at 100%
        else:
            return 0.0
    
    def classify_food_type(self, ingredients: List[str], nutrition: NutritionData) -> str:
        """
        Classify the food type based on ingredients and nutrition
        Used for applying different Nutri-Score algorithms
        """
        # Check ingredients text for food type keywords
        ingredients_text = ' '.join(ingredients).lower()
        
        for food_type, keywords in self.food_types.items():
            if any(keyword in ingredients_text for keyword in keywords):
                return food_type
        
        # Use nutrition profile to guess food type if ingredients don't provide clear indication
        
        # Beverage detection: typically low in fat, protein, and fiber
        if nutrition.fat < 3 and nutrition.proteins < 4 and nutrition.fiber < 1:
            return 'beverage'
        
        # Added fat detection: extremely high fat content
        if nutrition.fat > 80:
            return 'added_fat'
        
        # Cheese detection: high protein, high fat
        if nutrition.proteins > 15 and nutrition.fat > 15:
            return 'cheese'
            
        # Default to general food
        return 'general_food'
    
    def calculate_nutri_score_points(self, nutrition: NutritionData, food_type: str = 'general_food') -> Dict:
        """
        Calculate Nutri-Score points based on European algorithm with food type adjustments
        """
        # Negative points (per 100g)
        negative_points = 0
        positive_points = 0
        
        # Energy points (kJ per 100g)
        energy_points = 0
        if nutrition.energy_kj <= 335:
            energy_points = 0
        elif nutrition.energy_kj <= 670:
            energy_points = 1
        elif nutrition.energy_kj <= 1005:
            energy_points = 2
        elif nutrition.energy_kj <= 1340:
            energy_points = 3
        elif nutrition.energy_kj <= 1675:
            energy_points = 4
        elif nutrition.energy_kj <= 2010:
            energy_points = 5
        elif nutrition.energy_kj <= 2345:
            energy_points = 6
        elif nutrition.energy_kj <= 2680:
            energy_points = 7
        elif nutrition.energy_kj <= 3015:
            energy_points = 8
        elif nutrition.energy_kj <= 3350:
            energy_points = 9
        else:
            energy_points = 10
        
        negative_points += energy_points
        
        # Saturated fat points (g per 100g)
        saturated_fat_points = 0
        if nutrition.saturated_fat <= 1:
            saturated_fat_points = 0
        elif nutrition.saturated_fat <= 2:
            saturated_fat_points = 1
        elif nutrition.saturated_fat <= 3:
            saturated_fat_points = 2
        elif nutrition.saturated_fat <= 4:
            saturated_fat_points = 3
        elif nutrition.saturated_fat <= 5:
            saturated_fat_points = 4
        elif nutrition.saturated_fat <= 6:
            saturated_fat_points = 5
        elif nutrition.saturated_fat <= 7:
            saturated_fat_points = 6
        elif nutrition.saturated_fat <= 8:
            saturated_fat_points = 7
        elif nutrition.saturated_fat <= 9:
            saturated_fat_points = 8
        elif nutrition.saturated_fat <= 10:
            saturated_fat_points = 9
        else:
            saturated_fat_points = 10
            
        negative_points += saturated_fat_points
        
        # Sugar points (g per 100g)
        sugar_points = 0
        if food_type == 'beverage':
            # Beverages use different sugar scale
            if nutrition.sugars <= 0:
                sugar_points = 0
            elif nutrition.sugars <= 1.5:
                sugar_points = 1
            elif nutrition.sugars <= 3:
                sugar_points = 2
            elif nutrition.sugars <= 4.5:
                sugar_points = 3
            elif nutrition.sugars <= 6:
                sugar_points = 4
            elif nutrition.sugars <= 7.5:
                sugar_points = 5
            elif nutrition.sugars <= 9:
                sugar_points = 6
            elif nutrition.sugars <= 10.5:
                sugar_points = 7
            elif nutrition.sugars <= 12:
                sugar_points = 8
            elif nutrition.sugars <= 13.5:
                sugar_points = 9
            else:
                sugar_points = 10
        else:
            # Standard sugar scale
            if nutrition.sugars <= 4.5:
                sugar_points = 0
            elif nutrition.sugars <= 9:
                sugar_points = 1
            elif nutrition.sugars <= 13.5:
                sugar_points = 2
            elif nutrition.sugars <= 18:
                sugar_points = 3
            elif nutrition.sugars <= 22.5:
                sugar_points = 4
            elif nutrition.sugars <= 27:
                sugar_points = 5
            elif nutrition.sugars <= 31:
                sugar_points = 6
            elif nutrition.sugars <= 36:
                sugar_points = 7
            elif nutrition.sugars <= 40:
                sugar_points = 8
            elif nutrition.sugars <= 45:
                sugar_points = 9
            else:
                sugar_points = 10
                
        negative_points += sugar_points
        
        # Sodium points (mg per 100g)
        sodium_points = 0
        if nutrition.sodium <= 90:
            sodium_points = 0
        elif nutrition.sodium <= 180:
            sodium_points = 1
        elif nutrition.sodium <= 270:
            sodium_points = 2
        elif nutrition.sodium <= 360:
            sodium_points = 3
        elif nutrition.sodium <= 450:
            sodium_points = 4
        elif nutrition.sodium <= 540:
            sodium_points = 5
        elif nutrition.sodium <= 630:
            sodium_points = 6
        elif nutrition.sodium <= 720:
            sodium_points = 7
        elif nutrition.sodium <= 810:
            sodium_points = 8
        elif nutrition.sodium <= 900:
            sodium_points = 9
        else:
            sodium_points = 10
            
        negative_points += sodium_points
        
        # Positive points
        
        # Fruits, vegetables, nuts points (% of total weight)
        fruits_vegetables_nuts_points = 0
        if food_type == 'beverage':
            # Beverages use different FVN scale
            if nutrition.fruits_vegetables_nuts <= 40:
                fruits_vegetables_nuts_points = 0
            elif nutrition.fruits_vegetables_nuts <= 60:
                fruits_vegetables_nuts_points = 2
            elif nutrition.fruits_vegetables_nuts <= 80:
                fruits_vegetables_nuts_points = 4
            else:
                fruits_vegetables_nuts_points = 10
        else:
            # Standard FVN scale
            if nutrition.fruits_vegetables_nuts <= 40:
                fruits_vegetables_nuts_points = 0
            elif nutrition.fruits_vegetables_nuts <= 60:
                fruits_vegetables_nuts_points = 1
            elif nutrition.fruits_vegetables_nuts <= 80:
                fruits_vegetables_nuts_points = 2
            else:
                fruits_vegetables_nuts_points = 5
                
        positive_points += fruits_vegetables_nuts_points
        
        # Fiber points (g per 100g)
        fiber_points = 0
        if nutrition.fiber <= 0.9:
            fiber_points = 0
        elif nutrition.fiber <= 1.9:
            fiber_points = 1
        elif nutrition.fiber <= 2.8:
            fiber_points = 2
        elif nutrition.fiber <= 3.7:
            fiber_points = 3
        elif nutrition.fiber <= 4.7:
            fiber_points = 4
        else:
            fiber_points = 5
            
        positive_points += fiber_points
        
        # Protein points (g per 100g)
        protein_points = 0
        if nutrition.proteins <= 1.6:
            protein_points = 0
        elif nutrition.proteins <= 3.2:
            protein_points = 1
        elif nutrition.proteins <= 4.8:
            protein_points = 2
        elif nutrition.proteins <= 6.4:
            protein_points = 3
        elif nutrition.proteins <= 8.0:
            protein_points = 4
        else:
            protein_points = 5
            
        positive_points += protein_points
        
        # Calculate final score according to food type
        final_score = 0
        
        # Special rules for cheese (high protein, calcium-rich foods)
        if food_type == 'cheese':
            final_score = energy_points + saturated_fat_points + sodium_points - protein_points
        # Special rules for added fats (oils, butter, etc.)
        elif food_type == 'added_fat':
            final_score = energy_points + saturated_fat_points + sugar_points + sodium_points - fruits_vegetables_nuts_points - fiber_points
        # For beverages and general foods
        else:
            # If negative points >= 11 and fruits/vegs/nuts is < 5, only subtract FVN, fiber, protein
            if negative_points >= 11 and fruits_vegetables_nuts_points < 5:
                final_score = negative_points - fruits_vegetables_nuts_points - fiber_points
            else:
                final_score = negative_points - positive_points
        
        return {
            'score': final_score,
            'negative_points': negative_points,
            'positive_points': positive_points,
            'energy_points': energy_points,
            'saturated_fat_points': saturated_fat_points,
            'sugar_points': sugar_points,
            'sodium_points': sodium_points,
            'fruits_vegetables_nuts_points': fruits_vegetables_nuts_points,
            'fiber_points': fiber_points,
            'protein_points': protein_points,
            'food_type': food_type
        }
    
    def calculate_nutri_score(self, nutrition: NutritionData, ingredients: List[str] = None) -> Dict:
        """
        Calculate final Nutri-Score grade with enhanced food type detection
        """
        # Ensure we have a valid NutritionData object
        if not isinstance(nutrition, NutritionData):
            nutrition = self.extract_nutrition_from_values(nutrition)
        
        # If no ingredients provided, assume empty list
        ingredients = ingredients or []
        
        # Estimate fruits/vegetables/nuts percentage if not provided
        if nutrition.fruits_vegetables_nuts <= 0:
            nutrition.fruits_vegetables_nuts = self.estimate_fruits_vegetables_nuts_percentage(ingredients)
        
        # Classify food type
        food_type = self.classify_food_type(ingredients, nutrition)
        
        # Calculate score
        score_results = self.calculate_nutri_score_points(nutrition, food_type)
        final_score = score_results['score']
        
        # Determine grade
        grade = 'E'  # Default worst grade
        for grade_key, grade_info in self.grade_mapping.items():
            if grade_info['min'] <= final_score <= grade_info['max']:
                grade = grade_key
                break
        
        return {
            'grade': grade,
            'score': final_score,
            'color': self.grade_mapping[grade]['color'],
            'nutrition_data': {
                'energy_kj': nutrition.energy_kj,
                'energy_kcal': nutrition.energy_kcal,
                'fat': nutrition.fat,
                'saturated_fat': nutrition.saturated_fat,
                'carbohydrates': nutrition.carbohydrates,
                'sugars': nutrition.sugars,
                'fiber': nutrition.fiber,
                'proteins': nutrition.proteins,
                'salt': nutrition.salt,
                'sodium': nutrition.sodium,
                'fruits_vegetables_nuts': nutrition.fruits_vegetables_nuts
            },
            'scoring_details': score_results
        }
    
    def analyze_product_from_ocr(self, ocr_result: Dict, ingredients: List[str] = None) -> Dict:
        """
        Analyze product from enhanced OCR results and return Nutri-Score
        """
        try:
            # Get nutrition values from OCR result if available
            if 'nutrition_values' in ocr_result and ocr_result['nutrition_values']:
                nutrition = self.extract_nutrition_from_values(ocr_result['nutrition_values'])
            else:
                # Fall back to text extraction if structured values not available
                nutrition = self.extract_nutrition_from_text(ocr_result.get('text', ''))
            
            # Get ingredients from OCR or use provided
            ingredients = ingredients or ocr_result.get('ingredients', [])
            
            # Calculate Nutri-Score
            nutri_score_result = self.calculate_nutri_score(nutrition, ingredients)
            
            # Data quality assessment
            data_quality = self.assess_data_quality(nutrition, ocr_result.get('confidence', 0))
            
            return {
                'success': True,
                'nutri_score': nutri_score_result,
                'extracted_nutrition': nutrition,
                'ingredients_analyzed': ingredients,
                'data_quality': data_quality,
                'ocr_confidence': ocr_result.get('confidence', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing product: {e}")
            return {
                'success': False,
                'error': str(e),
                'nutri_score': None
            }
    
    def assess_data_quality(self, nutrition: NutritionData, ocr_confidence: float) -> Dict:
        """
        Assess the quality and completeness of the extracted nutrition data
        """
        # Count how many essential nutrients have values
        essential_nutrients = [
            'energy_kcal', 'fat', 'saturated_fat', 'carbohydrates', 
            'sugars', 'proteins', 'salt'
        ]
        
        # Count nutrients with values
        present_nutrients = sum(1 for nutrient in essential_nutrients 
                               if getattr(nutrition, nutrient, 0) > 0)
        
        # Calculate completeness percentage
        completeness = (present_nutrients / len(essential_nutrients)) * 100
        
        # Calculate data confidence score
        # Combine OCR confidence with nutritional completeness
        confidence_score = (ocr_confidence * 0.6) + (completeness / 100 * 0.4)
        confidence_score = min(confidence_score, 1.0)  # Cap at 1.0
        
        # Determine if manual review is needed
        manual_review_needed = (confidence_score < 0.7) or (completeness < 70)
        
        return {
            'completeness': completeness,
            'confidence': confidence_score * 100,  # Convert to percentage
            'manual_review_needed': manual_review_needed,
            'missing_nutrients': [
                nutrient for nutrient in essential_nutrients
                if getattr(nutrition, nutrient, 0) <= 0
            ]
        }


# Singleton instance
enhanced_nutri_score_calculator = EnhancedNutriScoreCalculator()
