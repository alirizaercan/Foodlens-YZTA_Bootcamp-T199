# OCR Setup and Configuration

This document provides detailed instructions for setting up and configuring the OCR (Optical Character Recognition) system used in the FoodLens application.

## Overview

The FoodLens OCR system is designed to extract nutrition information from food product labels. It uses a combination of technologies including EasyOCR, DocTR, and custom preprocessing techniques to achieve high accuracy in text extraction from nutrition tables.

## Requirements

- Python 3.9 or higher
- CUDA-compatible GPU (optional but recommended for better performance)
- At least 4GB RAM (8GB or more recommended)
- 2GB free disk space for model storage

## Installation

1. Install the required Python packages:

```bash
pip install -r requirements.txt
```

2. Download language models (if not automatically downloaded):

```bash
# For EasyOCR
python -c "import easyocr; reader = easyocr.Reader(['en', 'tr'])"

# For DocTR
python -c "from doctr.models import ocr_predictor; model = ocr_predictor(pretrained=True)"
```

## Configuration

The OCR system can be configured via environment variables or by editing the `config.py` file:

```python
# OCR configuration
OCR_CONFIG = {
    'GPU_ENABLED': True,  # Set to False if CUDA is not available
    'LANGUAGES': ['tr', 'en'],  # Primary and fallback languages
    'CONFIDENCE_THRESHOLD': 0.3,  # Minimum confidence level for text detection
    'MAX_IMAGE_SIZE': 1920,  # Maximum image dimension for processing
    'TABLE_DETECTION_ENABLED': True,  # Enable specialized nutrition table detection
    'PREPROCESSING_LEVELS': 'all'  # Options: 'minimal', 'standard', 'all'
}
```

## OCR Pipeline

The OCR process follows these steps:

1. **Image Preprocessing**: Enhance image quality (contrast adjustment, noise reduction, etc.)
2. **Nutrition Table Detection**: Locate and extract the nutrition facts table
3. **Text Extraction**: Apply OCR on both the full image and the detected table regions
4. **Table Structure Analysis**: Identify rows and columns in the nutrition table
5. **Data Extraction**: Extract nutrition values using position data and pattern matching
6. **Result Validation**: Validate extracted values against expected ranges and formats

## Improving OCR Accuracy

For best results:

- Ensure good lighting conditions when taking photos
- Avoid shadows and glare on the product label
- Keep the camera steady and close enough to the label
- Ensure the nutrition table is completely visible and not distorted
- Focus the camera properly before taking the photo

## Troubleshooting

Common issues and solutions:

1. **Poor text recognition**: Try adjusting the image brightness and contrast before upload
2. **Missing nutrition values**: Ensure the entire nutrition table is visible in the image
3. **Incorrect values**: Check for glare or shadows on the nutrition label
4. **Language detection issues**: Manually specify the language if auto-detection fails

## API Integration

The OCR system is accessible through the following API endpoint:

```
POST /api/analysis/analyze
Content-Type: multipart/form-data

Parameters:
- image: The product label image file
- language: Language code (tr or en, default: tr)
```

Response format:

```json
{
  "success": true,
  "file_url": "/static/uploads/image.jpg",
  "nutri_score": {
    "grade": "A",
    "score": -2,
    "color": "#038141",
    "nutrition_data": {
      "energy_kj": 543,
      "energy_kcal": 217,
      "fat": 12,
      "saturated_fat": 5.8,
      "carbohydrates": 23,
      "sugars": 15,
      "fiber": 1,
      "proteins": 2.6,
      "salt": 0.1
    }
  },
  "nutrition": {
    "energy_kj": 543,
    "energy_kcal": 217,
    "fat": 12,
    "saturated_fat": 5.8,
    "carbohydrates": 23,
    "sugars": 15,
    "fiber": 1,
    "proteins": 2.6,
    "salt": 0.1
  },
  "data_quality": {
    "completeness": 100,
    "confidence": 95,
    "manual_review_needed": false,
    "missing_nutrients": []
  }
}
```

## Debug Mode

For debugging OCR issues, use the debug endpoint:

```
POST /api/analysis/debug-ocr
```

This returns detailed information about the OCR process, including:
- Raw extracted text
- Detected table structure
- Confidence scores for each detected text element
- Processing time

## Performance Considerations

- OCR processing can take 5-15 seconds depending on the image complexity
- GPU acceleration can improve processing speed by 3-5x
- Consider implementing a queueing system for high-traffic deployments
