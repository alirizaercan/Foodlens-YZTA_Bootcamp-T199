# FoodLens Backend API Documentation

## 🚀 Genel Bakış

FoodLens uygulaması için kapsamlı backend API sistemi. PostgreSQL veritabanı, Flask framework ve modern security özellikleri ile geliştirilmiştir.

## 📋 Özellikler

### ✅ Tamamlanan Backend Bileşenleri

#### 🔐 Authentication & Authorization
- **JWT Token Authentication**
- **User Registration & Login**
- **Password Hashing (bcrypt)**
- **Token Refresh & Validation**
- **KVKK Compliance**

#### 👤 User Management
- **User Profile Management**
- **Health Information Tracking**
- **BMI Auto-calculation**
- **Daily Calorie Goal Setting**
- **Activity Level Tracking**

#### 🌟 Allergen Management
- **Pre-populated Allergen Database**
- **User-specific Allergen Tracking**
- **Severity Level Management**
- **Allergen Association Management**

#### 🎯 Nutrition Goals
- **Goal Setting & Tracking**
- **Progress Calculation**
- **Multiple Goal Types Support**
- **Timeline Management**

#### 🔒 Security & Validation
- **Input Sanitization**
- **SQL Injection Prevention**
- **XSS Protection**
- **Data Validation**
- **Rate Limiting Ready**

#### 🧪 Testing Framework
- **Automated Unit Tests**
- **Integration Tests**
- **Database Tests**
- **API Endpoint Tests**
- **Performance Tests**

## 🗄️ Database Schema

### Core Tables
```sql
users                 -- User authentication data
user_profiles         -- Detailed health information
allergens            -- Common allergen definitions
user_allergens       -- User-allergen associations
nutrition_goals      -- User nutrition goals
products             -- Food product information
analyses             -- Analysis results
recommendations      -- AI recommendations
```

## 🛠️ API Endpoints

### 🔐 Authentication (`/api/auth`)
```
POST   /register       - User registration
POST   /login          - User login
POST   /logout         - User logout
POST   /refresh        - Token refresh
POST   /change-password - Password change
GET    /verify         - Token verification
```

### 👤 User Management (`/api/users`)
```
GET    /profile                    - Get user profile
PUT    /profile                    - Update user profile
POST   /profile/setup             - Setup profile (onboarding)
GET    /allergens                 - Get user allergens
POST   /allergens                 - Add allergen
DELETE /allergens/{id}            - Remove allergen
GET    /allergens/available       - Get all available allergens
GET    /nutrition-goals           - Get nutrition goals
POST   /nutrition-goals           - Create nutrition goal
PUT    /nutrition-goals/{id}      - Update nutrition goal
DELETE /nutrition-goals/{id}      - Delete nutrition goal
GET    /dashboard                 - Get dashboard data
```

### 🔍 Analysis (`/api/analysis`)
```
POST   /analyze        - Analyze food image
POST   /upload         - Upload image
```

### 📦 Products (`/api/products`)
```
GET    /               - Get products
GET    /{id}          - Get specific product
GET    /search        - Search products
POST   /              - Create product
```

### 📊 Analyses (`/api/analyses`)
```
GET    /               - Get user analyses
GET    /{id}          - Get specific analysis
DELETE /{id}          - Delete analysis
```

### 💡 Recommendations (`/api/recommendations`)
```
GET    /               - Get recommendations
PUT    /{id}/read     - Mark as read
DELETE /{id}          - Delete recommendation
```

## 🔧 Installation & Setup

### 1. Backend Setup
```bash
cd Foodlens/backend

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Edit .env with your database credentials

# Database setup
python -c "
from utils.database import Database
db = Database()
session = db.connect()
print('Database connected successfully!')
"

# Run SQL schema
psql -U your_username -d your_database -f database/create_tables.sql

# Start server
python app.py
```

### 2. Frontend Setup
```bash
cd Foodlens/frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 3. Environment Variables
```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/foodlens_db

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# API Configuration
FLASK_ENV=development
API_URL=http://localhost:5000/api
```

## 🧪 Testing

### Run All Tests
```bash
cd backend
pytest tests/ -v
```

### Test Categories
```bash
# Database tests
pytest tests/test_automated.py::TestDatabase -v

# API tests
pytest tests/test_automated.py::TestAPIEndpoints -v

# Validation tests
pytest tests/test_automated.py::TestValidators -v

# Performance tests
pytest tests/test_automated.py::TestPerformance -v

# Integration tests
pytest tests/test_automated.py::TestIntegration -v
```

## 📝 Usage Examples

### 1. User Registration
```javascript
const userData = {
  email: 'user@example.com',
  password: 'SecurePass123!',
  username: 'newuser',
  first_name: 'John',
  last_name: 'Doe'
};

const response = await authAPI.register(userData);
```

### 2. Profile Setup (Based on UI Mockup)
```javascript
const profileData = {
  height: 175.0,        // Length field from mockup
  weight: 70.0,         // Weight field from mockup
  age: 25,              // Age field from mockup
  gender: 'male',
  activity_level: 'moderate',
  kvkk_approval: true   // KVKK checkbox from mockup
};

const response = await userAPI.setupProfile(profileData);
```

### 3. Add Allergen
```javascript
const allergenData = {
  allergen_id: 1,       // From allergens dropdown
  severity: 'moderate',
  notes: 'Mild reaction'
};

const response = await userAPI.addAllergen(allergenData);
```

## 🔒 Security Features

### Data Validation
- **Email format validation**
- **Strong password requirements**
- **Input sanitization**
- **Length restrictions**
- **Type validation**

### Authentication Security
- **JWT tokens with expiration**
- **Password hashing with bcrypt**
- **Token refresh mechanism**
- **Session management**

### Database Security
- **Parameterized queries**
- **SQL injection prevention**
- **Foreign key constraints**
- **Data integrity checks**

## 📊 Form Validation (UI Mockup Based)

### Profile Setup Form
```javascript
// Validation rules based on mockup
const validationRules = {
  height: {
    required: true,
    min: 50,
    max: 300,
    label: 'Length (Height)'
  },
  weight: {
    required: true,
    min: 20,
    max: 500,
    label: 'Weight'
  },
  age: {
    required: true,
    min: 13,
    max: 120,
    label: 'Age'
  },
  allergies: {
    type: 'array',
    label: 'Allergies'
  },
  kvkk_approval: {
    required: true,
    type: 'boolean',
    label: 'I approve KVKK'
  }
};
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Scale services
docker-compose up --scale backend=3
```

### Manual Deployment
```bash
# Install production dependencies
pip install -r requirements.txt

# Set production environment
export FLASK_ENV=production

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📈 Performance

### Database Optimization
- **Indexed columns for fast queries**
- **Foreign key relationships**
- **Optimized query patterns**
- **Connection pooling ready**

### API Performance
- **Pagination support**
- **Efficient data serialization**
- **Caching headers**
- **Compression ready**

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check PostgreSQL service
   sudo systemctl status postgresql
   
   # Verify connection
   psql -U username -d foodlens_db -c "SELECT 1;"
   ```

2. **Token Validation Error**
   ```bash
   # Check JWT secret configuration
   echo $JWT_SECRET_KEY
   ```

3. **Import Errors**
   ```bash
   # Verify Python path
   export PYTHONPATH="${PYTHONPATH}:/path/to/backend"
   ```

## 📚 Dependencies

### Backend Dependencies
```
Flask==3.0.0
SQLAlchemy==2.0.23
psycopg2-binary==2.9.9
bcrypt==4.1.2
PyJWT==2.8.0
email-validator==2.1.0
bleach==6.1.0
pytest==7.4.3
```

### Frontend Dependencies
```
react==18.2.0
axios==1.6.0
react-hot-toast==2.4.1
react-router-dom==6.8.0
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Run test suite
5. Submit pull request

### Code Standards
- **PEP 8 for Python**
- **ESLint for JavaScript**
- **Type hints where applicable**
- **Comprehensive docstrings**

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 📞 Support

For support and questions:
- **Email**: support@foodlens.app
- **Documentation**: [API Docs](http://localhost:5000/api/health)
- **Issues**: GitHub Issues
