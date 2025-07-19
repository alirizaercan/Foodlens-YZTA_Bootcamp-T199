# FoodLens API Endpoints Documentation

## 🔗 Base URL
```
Development: http://localhost:5000
Production: https://api.foodlens.com
```

## 🔐 Authentication
All protected endpoints require Bearer token in the Authorization header:
```
Authorization: Bearer <your_token_here>
```

---

## 🔑 Authentication Endpoints

### Register User
- **POST** `/api/auth/register`
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "full_name": "John Doe"
  }
  ```
- **Response:** User data with auth token

### Login User
- **POST** `/api/auth/login`
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response:** User data with auth token

### Logout User
- **POST** `/api/auth/logout`
- **Headers:** Authorization required
- **Response:** Success message

### Refresh Token
- **POST** `/api/auth/refresh`
- **Headers:** Authorization required
- **Response:** New auth token

### Change Password
- **POST** `/api/auth/change-password`
- **Headers:** Authorization required
- **Body:**
  ```json
  {
    "current_password": "old_password",
    "new_password": "new_password"
  }
  ```

### Verify Token
- **GET** `/api/auth/verify`
- **Headers:** Authorization required
- **Response:** Token validity status

---

## 👤 User Management Endpoints

### Get User Profile
- **GET** `/api/users/profile`
- **Headers:** Authorization required
- **Response:** User profile data

### Update User Profile
- **PUT** `/api/users/profile`
- **Headers:** Authorization required
- **Body:** Profile data to update

### Setup User Profile (Initial)
- **POST** `/api/users/profile/setup`
- **Headers:** Authorization required
- **Body:**
  ```json
  {
    "height": 175,
    "weight": 70,
    "age": 25,
    "gender": "male",
    "activity_level": "moderately_active",
    "allergen_ids": ["gluten", "lactose"],
    "kvkk_approval": true
  }
  ```

### Get User Allergens
- **GET** `/api/users/allergens`
- **Headers:** Authorization required

### Add User Allergen
- **POST** `/api/users/allergens`
- **Headers:** Authorization required
- **Body:**
  ```json
  {
    "allergen_id": "gluten"
  }
  ```

### Remove User Allergen
- **DELETE** `/api/users/allergens/<allergen_id>`
- **Headers:** Authorization required

### Get Available Allergens
- **GET** `/api/users/allergens/available`
- **Headers:** Authorization required

### Get Nutrition Goals
- **GET** `/api/users/nutrition-goals`
- **Headers:** Authorization required

### Create Nutrition Goal
- **POST** `/api/users/nutrition-goals`
- **Headers:** Authorization required
- **Body:**
  ```json
  {
    "goal_type": "weight_loss",
    "target_calories": 2000,
    "target_protein": 150,
    "target_carbs": 200,
    "target_fat": 65,
    "target_weight": 65,
    "target_date": "2024-12-31"
  }
  ```

### Update Nutrition Goal
- **PUT** `/api/users/nutrition-goals/<goal_id>`
- **Headers:** Authorization required

### Delete Nutrition Goal
- **DELETE** `/api/users/nutrition-goals/<goal_id>`
- **Headers:** Authorization required

### Get User Dashboard
- **GET** `/api/users/dashboard`
- **Headers:** Authorization required
- **Response:** Dashboard statistics and progress

---

## 🔍 Product Analysis Endpoints

### Analyze Product Image
- **POST** `/api/analysis/analyze`
- **Headers:** Authorization required
- **Body:** FormData with image file
- **Form Fields:**
  - `image`: Image file
  - `language`: Language code (tr/en)
  - `product_name`: Optional product name
  - `brand`: Optional brand name

### Advanced Nutrition Analysis
- **POST** `/api/nutrition-analysis/analyze`
- **Headers:** Authorization required
- **Body:** FormData with image file
- **Response:** Detailed nutrition analysis

### Debug OCR (Development)
- **POST** `/api/nutrition-analysis/debug-ocr`
- **Headers:** Authorization required
- **Body:** FormData with image file
- **Response:** OCR debug information

---

## 🛒 Product Endpoints

### Search Products
- **GET** `/api/products/search`
- **Query Parameters:**
  - `q`: Search query
  - `limit`: Number of results (default: 10)
  - `category`: Product category filter
  - `brand`: Brand filter

### Get Product by Barcode
- **GET** `/api/products/barcode/<barcode>`
- **Headers:** Authorization required

### Get Product by ID
- **GET** `/api/products/<product_id>`
- **Headers:** Authorization required

### Save Product Analysis
- **POST** `/api/products/save-analysis`
- **Headers:** Authorization required
- **Body:** Product analysis data

### Get Analysis History
- **GET** `/api/products/history`
- **Headers:** Authorization required
- **Query Parameters:**
  - `page`: Page number (default: 1)
  - `limit`: Items per page (default: 20)
  - `sort_by`: Sort field (date, rating, name)
  - `order`: Sort order (asc, desc)

### Get Product Categories
- **GET** `/api/products/categories`
- **Headers:** Authorization required

### Report Product Issue
- **POST** `/api/products/<product_id>/report`
- **Headers:** Authorization required
- **Body:**
  ```json
  {
    "issue_type": "incorrect_nutrition",
    "description": "Calorie information is wrong"
  }
  ```

---

## 💡 Recommendation Endpoints

### Get Personalized Recommendations
- **GET** `/api/recommendations/personalized`
- **Headers:** Authorization required
- **Query Parameters:**
  - `meal_type`: Meal type (breakfast, lunch, dinner, snack)
  - `max_calories`: Maximum calories
  - `exclude_allergens`: Comma-separated allergen IDs
  - `preferred_cuisine`: Preferred cuisine type
  - `limit`: Number of recommendations

### Get Product-Based Recommendations
- **GET** `/api/recommendations/product/<product_id>`
- **Headers:** Authorization required
- **Query Parameters:**
  - `type`: Recommendation type (alternatives, complements, meals)
  - `limit`: Number of recommendations

### Get Meal Plan Recommendations
- **POST** `/api/recommendations/meal-plan`
- **Headers:** Authorization required
- **Body:**
  ```json
  {
    "days": 7,
    "target_calories": 2000,
    "meal_types": ["breakfast", "lunch", "dinner"],
    "macro_targets": {
      "protein": 150,
      "carbs": 200,
      "fat": 65
    }
  }
  ```

### Get Healthy Alternatives
- **POST** `/api/recommendations/alternatives/<product_id>`
- **Headers:** Authorization required
- **Body:**
  ```json
  {
    "lower_calories": true,
    "lower_sugar": true,
    "higher_protein": false,
    "limit": 5
  }
  ```

### Get Recipe Recommendations
- **POST** `/api/recommendations/recipes`
- **Headers:** Authorization required
- **Body:**
  ```json
  {
    "ingredients": ["chicken", "rice", "vegetables"],
    "cuisine": "turkish",
    "max_prep_time": 30,
    "difficulty": "easy",
    "servings": 4
  }
  ```

### Get Shopping List Recommendations
- **POST** `/api/recommendations/shopping-list`
- **Headers:** Authorization required
- **Body:**
  ```json
  {
    "goals": ["weight_loss"],
    "budget": 100,
    "store": "migros",
    "exclude_categories": ["alcohol"]
  }
  ```

### Save Recommendation Feedback
- **POST** `/api/recommendations/<recommendation_id>/feedback`
- **Headers:** Authorization required
- **Body:**
  ```json
  {
    "rating": 5,
    "helpful": true,
    "comment": "Great recommendation!"
  }
  ```

### Get Recommendation History
- **GET** `/api/recommendations/history`
- **Headers:** Authorization required
- **Query Parameters:**
  - `page`: Page number
  - `limit`: Items per page
  - `type`: Recommendation type filter

---

## 📊 Analytics Endpoints

### Track User Activity
- **POST** `/api/analytics/track`
- **Headers:** Authorization required
- **Body:**
  ```json
  {
    "event_type": "product_scan",
    "page": "scanner",
    "properties": {
      "scan_type": "barcode",
      "success": true
    }
  }
  ```

### Get User Analytics
- **GET** `/api/analytics/user`
- **Headers:** Authorization required
- **Query Parameters:**
  - `period`: Time period (day, week, month, year)
  - `start_date`: Start date (YYYY-MM-DD)
  - `end_date`: End date (YYYY-MM-DD)

### Get Nutrition Progress
- **GET** `/api/analytics/nutrition-progress`
- **Headers:** Authorization required
- **Query Parameters:**
  - `days`: Number of days to analyze (default: 30)

### Get Scanning Statistics
- **GET** `/api/analytics/scanning-stats`
- **Headers:** Authorization required

### Track Product Scan
- **POST** `/api/analytics/track-scan`
- **Headers:** Authorization required
- **Body:**
  ```json
  {
    "product_id": "123",
    "scan_type": "barcode",
    "successful": true,
    "processing_time": 1200
  }
  ```

### Get Goal Progress
- **GET** `/api/analytics/goal-progress/<goal_id>`
- **Headers:** Authorization required

---

## 🔧 Utility Endpoints

### Health Check
- **GET** `/api/health`
- **Response:** API health status

### Get Application Statistics
- **GET** `/api/stats`
- **Response:** General app statistics

### Contact Support
- **POST** `/api/contact`
- **Body:**
  ```json
  {
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Technical Issue",
    "message": "Having trouble with product scanning"
  }
  ```

### Server Status
- **GET** `/api/status`
- **Response:** Detailed server status

---

## 📝 Response Format

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    // Additional error details
  }
}
```

## 🔒 Error Codes

- **401** - Unauthorized (Invalid or missing token)
- **403** - Forbidden (Access denied)
- **404** - Not Found (Resource not found)
- **422** - Validation Error (Invalid input data)
- **429** - Rate Limited (Too many requests)
- **500** - Internal Server Error

## 📱 Frontend Integration

All services are available in the frontend through the services directory:

```javascript
import { authService, userService, productService } from '../services';

// Example usage
const login = async (email, password) => {
  try {
    const response = await authService.login(email, password);
    console.log('Login successful:', response);
  } catch (error) {
    console.error('Login failed:', error);
  }
};
```