# FoodLens Project Structure

This document outlines the complete file structure for the FoodLens application.

## Project Overview

FoodLens is a web application that helps users analyze food products using OCR and AI technology. Users can upload images of product labels to get nutritional analysis, allergen information, and personalized recommendations.

## Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **OCR**: Tesseract/Google Cloud Vision
- **AI/ML**: OpenAI API, scikit-learn
- **Image Processing**: Pillow
- **Testing**: pytest
- **Deployment**: Docker

### Frontend
- **Framework**: React.js
- **Routing**: React Router
- **HTTP Client**: Axios
- **UI Library**: Material-UI
- **Image Upload**: react-dropzone
- **State Management**: Context API + hooks
- **Testing**: Jest, React Testing Library
- **Build Tool**: Create React App

### DevOps & Tools
- **Version Control**: Git
- **CI/CD**: GitHub Actions
- **Containerization**: Docker & Docker Compose
- **Code Quality**: ESLint, Prettier, Black

## Complete File Structure

```
Foodlens/
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── docker-compose.yml
├── DEVELOPMENT.md
├── backend/
│   ├── .env.example
│   ├── Dockerfile
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── controllers/
│   │   ├── auth_controller.py
│   │   ├── product_controller.py
│   │   ├── analysis_controller.py
│   │   ├── user_controller.py
│   │   └── recommendation_controller.py
│   ├── database/
│   │   ├── create_tables.sql
│   │   ├── seed_data.sql
│   │   └── migrations/
│   │       └── 001_initial_schema.sql
│   ├── middleware/
│   │   ├── auth_middleware.py
│   │   ├── cors_middleware.py
│   │   └── error_middleware.py
│   ├── models/
│   │   ├── user.py
│   │   ├── user_profile.py
│   │   ├── product.py
│   │   ├── analysis.py
│   │   ├── recommendation.py
│   │   ├── allergen.py
│   │   └── nutrition_goal.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── product_service.py
│   │   ├── analysis_service.py
│   │   └── recommendation_service.py
│   ├── static/
│   │   └── uploads/
│   │       └── .gitkeep
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_analysis.py
│   │   └── test_ocr.py
│   └── utils/
│       ├── database.py
│       ├── ocr_service.py
│       ├── ai_service.py
│       ├── nutrition_calculator.py
│       ├── external_apis.py
│       └── csv_loader.py
├── frontend/
│   ├── .env.example
│   ├── Dockerfile
│   ├── package.json
│   ├── package-lock.json
│   ├── public/
│   │   ├── index.html
│   │   └── manifest.json
│   └── src/
│       ├── App.js
│       ├── index.js
│       ├── components/
│       │   ├── Header.js
│       │   ├── Footer.js
│       │   ├── ImageUpload.js
│       │   ├── ProductAnalysis.js
│       │   ├── NutritionDisplay.js
│       │   ├── LoadingSpinner.js
│       │   ├── ErrorBoundary.js
│       │   └── ProtectedRoute.js
│       ├── config/
│       │   ├── constants.js
│       │   └── config.js
│       ├── context/
│       │   ├── AuthContext.js
│       │   └── AppContext.js
│       ├── hooks/
│       │   ├── useAuth.js
│       │   ├── useImageUpload.js
│       │   └── useApi.js
│       ├── pages/
│       │   ├── AuthenticationPage.js
│       │   ├── HomePage.js
│       │   ├── AnalysisResultsPage.js
│       │   ├── UserProfilePage.js
│       │   ├── ProductHistoryPage.js
│       │   ├── RecommendationsPage.js
│       │   └── ProductSearchPage.js
│       ├── services/
│       │   ├── api.js
│       │   ├── authService.js
│       │   ├── productService.js
│       │   └── userService.js
│       ├── styles/
│       │   ├── globals.css
│       │   └── performance.css
│       └── utils/
│           ├── imageUtils.js
│           ├── validation.js
│           ├── formatters.js
│           └── localStorage.js
└── data/
    ├── processed_data/
    └── raw_data/
```

## Key Features Supported

1. **User Authentication**: Registration, login, JWT tokens
2. **Image Upload & OCR**: Product label scanning and text extraction
3. **AI Analysis**: Nutritional analysis and health scoring
4. **User Profiles**: Dietary preferences, allergies, health goals
5. **Product History**: Track previously analyzed products
6. **Recommendations**: Personalized product suggestions
7. **Search & Compare**: Find and compare products
8. **Responsive Design**: Mobile-first UI design

## Development Workflow

1. **Setup**: Follow `DEVELOPMENT.md` for environment setup
2. **Development**: Use Docker Compose for local development
3. **Testing**: Run backend (`pytest`) and frontend (`npm test`) tests
4. **Deployment**: GitHub Actions handles CI/CD pipeline
5. **Monitoring**: Built-in error handling and logging

## Next Steps

1. Implement core functionality in all placeholder files
2. Set up external API integrations (OCR, AI services)
3. Configure production database and hosting
4. Add comprehensive test coverage
5. Implement security best practices
6. Set up monitoring and analytics

All files are currently structured with appropriate placeholders and documentation. The project is ready for development team to begin implementation.
