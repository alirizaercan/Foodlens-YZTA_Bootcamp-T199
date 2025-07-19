-- FoodLens Database Schema
-- PostgreSQL table creation script

-- This SQL script will create the following tables:
-- 1. users - User authentication and basic information
-- 2. user_profiles - Detailed user health and dietary information
-- 3. allergens - Common allergen definitions
-- 4. products - Food product information and nutritional data
-- 5. analyses - Product analysis results and AI insights
-- 6. recommendations - AI-powered recommendations and suggestions
-- 7. nutrition_goals - User nutrition goals and progress tracking
-- 8. user_allergens - User-specific allergen associations (junction table)

-- Tables will include appropriate indexes, foreign keys, and constraints
-- following PostgreSQL best practices for the FoodLens application

-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS user_allergens CASCADE;
DROP TABLE IF EXISTS nutrition_goals CASCADE;
DROP TABLE IF EXISTS recommendations CASCADE;
DROP TABLE IF EXISTS analyses CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS allergens CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users table - Basic authentication and user information
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- 2. Allergens table - Common allergen definitions
CREATE TABLE allergens (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    scientific_name VARCHAR(200),
    description TEXT,
    category VARCHAR(50),
    severity_level VARCHAR(20) DEFAULT 'moderate',
    common_sources TEXT[],
    alternative_names TEXT[],
    is_major_allergen BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. User profiles table - Detailed user health and dietary information
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    age INTEGER CHECK (age > 0 AND age < 150),
    gender VARCHAR(20),
    height DECIMAL(5,2) CHECK (height > 0), -- in cm
    weight DECIMAL(5,2) CHECK (weight > 0), -- in kg
    activity_level VARCHAR(20) DEFAULT 'moderate',
    dietary_preferences VARCHAR(50)[],
    health_conditions TEXT[],
    medications TEXT[],
    bmi DECIMAL(4,2),
    daily_calorie_goal INTEGER,
    kvkk_approval BOOLEAN DEFAULT FALSE,
    notification_preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. User allergens junction table - Many-to-many relationship
CREATE TABLE user_allergens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    allergen_id INTEGER NOT NULL REFERENCES allergens(id) ON DELETE CASCADE,
    severity VARCHAR(20) DEFAULT 'moderate',
    notes TEXT,
    diagnosed_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, allergen_id)
);

-- 5. Products table - Food product information
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    barcode VARCHAR(50) UNIQUE,
    category VARCHAR(100),
    nutritional_info JSONB,
    ingredients TEXT[],
    allergen_info TEXT[],
    serving_size VARCHAR(50),
    calories_per_serving INTEGER,
    image_url VARCHAR(500),
    product_url VARCHAR(500),
    country_of_origin VARCHAR(100),
    manufacturer VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Analyses table - Product analysis results
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    image_url VARCHAR(500),
    ocr_text TEXT,
    extracted_ingredients TEXT[],
    nutritional_analysis JSONB,
    allergen_warnings TEXT[],
    health_score INTEGER CHECK (health_score >= 0 AND health_score <= 100),
    ai_insights TEXT,
    analysis_status VARCHAR(20) DEFAULT 'pending',
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Recommendations table - AI-powered recommendations
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    analysis_id UUID REFERENCES analyses(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium',
    category VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    action_taken BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. Nutrition goals table - User nutrition tracking
CREATE TABLE nutrition_goals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    goal_type VARCHAR(50) NOT NULL,
    target_value DECIMAL(10,2),
    current_value DECIMAL(10,2) DEFAULT 0,
    unit VARCHAR(20),
    period VARCHAR(20) DEFAULT 'daily',
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_active ON users(is_active);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_age ON user_profiles(age);

CREATE INDEX idx_user_allergens_user_id ON user_allergens(user_id);
CREATE INDEX idx_user_allergens_allergen_id ON user_allergens(allergen_id);

CREATE INDEX idx_products_barcode ON products(barcode);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);

CREATE INDEX idx_analyses_user_id ON analyses(user_id);
CREATE INDEX idx_analyses_product_id ON analyses(product_id);
CREATE INDEX idx_analyses_status ON analyses(analysis_status);
CREATE INDEX idx_analyses_created_at ON analyses(created_at);

CREATE INDEX idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX idx_recommendations_type ON recommendations(recommendation_type);
CREATE INDEX idx_recommendations_is_read ON recommendations(is_read);

CREATE INDEX idx_nutrition_goals_user_id ON nutrition_goals(user_id);
CREATE INDEX idx_nutrition_goals_active ON nutrition_goals(is_active);
CREATE INDEX idx_nutrition_goals_type ON nutrition_goals(goal_type);

-- Create triggers for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_nutrition_goals_updated_at BEFORE UPDATE ON nutrition_goals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert common allergens
INSERT INTO allergens (name, scientific_name, description, category, is_major_allergen, common_sources) VALUES
('Gluten', 'Triticum aestivum proteins', 'Protein found in wheat, barley, rye', 'Protein', TRUE, ARRAY['Wheat', 'Barley', 'Rye', 'Bread', 'Pasta']),
('Milk', 'Bos taurus milk proteins', 'Dairy proteins including casein and whey', 'Protein', TRUE, ARRAY['Milk', 'Cheese', 'Butter', 'Yogurt', 'Cream']),
('Eggs', 'Gallus gallus egg proteins', 'Proteins found in chicken eggs', 'Protein', TRUE, ARRAY['Eggs', 'Mayonnaise', 'Baked goods', 'Pasta']),
('Peanuts', 'Arachis hypogaea', 'Legume allergen, not a tree nut', 'Legume', TRUE, ARRAY['Peanuts', 'Peanut butter', 'Peanut oil']),
('Tree Nuts', 'Various tree nut proteins', 'Nuts that grow on trees', 'Nuts', TRUE, ARRAY['Almonds', 'Walnuts', 'Cashews', 'Pistachios']),
('Soy', 'Glycine max proteins', 'Soybean proteins', 'Legume', TRUE, ARRAY['Soybeans', 'Soy sauce', 'Tofu', 'Tempeh']),
('Fish', 'Various fish proteins', 'Proteins from finned fish', 'Protein', TRUE, ARRAY['Salmon', 'Tuna', 'Cod', 'Fish sauce']),
('Shellfish', 'Crustacean and mollusk proteins', 'Proteins from shellfish', 'Protein', TRUE, ARRAY['Shrimp', 'Crab', 'Lobster', 'Oysters']),
('Sesame', 'Sesamum indicum proteins', 'Sesame seed proteins', 'Seeds', TRUE, ARRAY['Sesame seeds', 'Tahini', 'Sesame oil']);

-- Add comments to tables
COMMENT ON TABLE users IS 'User authentication and basic account information';
COMMENT ON TABLE user_profiles IS 'Detailed user health and dietary profile information';
COMMENT ON TABLE allergens IS 'Common allergen definitions and information';
COMMENT ON TABLE user_allergens IS 'User-specific allergen associations';
COMMENT ON TABLE products IS 'Food product information and nutritional data';
COMMENT ON TABLE analyses IS 'Product analysis results and AI insights';
COMMENT ON TABLE recommendations IS 'AI-powered recommendations for users';
COMMENT ON TABLE nutrition_goals IS 'User nutrition goals and progress tracking';
