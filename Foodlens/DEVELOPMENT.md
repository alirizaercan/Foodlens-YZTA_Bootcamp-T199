# FoodLens Development Setup

This document provides instructions for setting up the FoodLens development environment.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- PostgreSQL 12 or higher
- Git

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your actual configuration values.

6. Set up the database:
   ```bash
   python -c "from utils.database import init_db; init_db()"
   ```

7. Run the application:
   ```bash
   python app.py
   ```

## Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your actual configuration values.

4. Start the development server:
   ```bash
   npm start
   ```

## Database Setup

1. Install PostgreSQL and create a database:
   ```sql
   CREATE DATABASE foodlens_db;
   CREATE USER foodlens_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE foodlens_db TO foodlens_user;
   ```

2. Run database migrations:
   ```bash
   cd backend
   python -c "from utils.database import run_migrations; run_migrations()"
   ```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## API Documentation

Once the backend is running, visit `http://localhost:5000/api/docs` for interactive API documentation.

## Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure ports 3000 (frontend) and 5000 (backend) are available
2. **Database connection**: Verify PostgreSQL is running and credentials are correct
3. **Dependencies**: Run `pip install -r requirements.txt` and `npm install` to ensure all packages are installed

### Environment Variables

Make sure to set up all required environment variables in both `.env` files:

- Backend: Database URL, API keys for OCR and AI services
- Frontend: Backend API URL, feature flags

## Development Workflow

1. Create feature branches from `main`
2. Make changes and test locally
3. Create pull requests for review
4. Deploy to staging for final testing
5. Merge to main and deploy to production
