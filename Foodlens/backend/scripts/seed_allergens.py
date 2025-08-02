"""
Initial allergen data seeding script for FoodLens Application
This script populates the allergens table with common allergens.
"""

from utils.database import Database
from models.allergen import Allergen

def seed_allergens():
    """Seed the database with common allergens."""
    db = Database()
    session = db.connect()
    
    try:
        # Check if allergens already exist
        existing_count = session.query(Allergen).count()
        if existing_count > 0:
            print(f"Allergens already exist ({existing_count} records). Skipping seed.")
            return
        
        # Common allergens data
        allergens_data = [
            {
                'name': 'Gluten',
                'scientific_name': 'Gliadin and Glutenin proteins',
                'description': 'Protein found in wheat, barley, rye, and triticale',
                'category': 'Cereals',
                'severity_level': 'moderate',
                'common_sources': ['wheat', 'barley', 'rye', 'bread', 'pasta', 'beer'],
                'alternative_names': ['wheat protein', 'triticum', 'wheat gluten'],
                'is_major_allergen': True
            },
            {
                'name': 'Laktoz',
                'scientific_name': 'Lactose',
                'description': 'Sugar found in milk and dairy products',
                'category': 'Dairy',
                'severity_level': 'moderate',
                'common_sources': ['milk', 'cheese', 'yogurt', 'butter', 'ice cream'],
                'alternative_names': ['milk sugar', 'lactose'],
                'is_major_allergen': True
            },
            {
                'name': 'Yer fıstığı',
                'scientific_name': 'Arachis hypogaea',
                'description': 'Legume commonly known as peanut',
                'category': 'Nuts and Legumes',
                'severity_level': 'severe',
                'common_sources': ['peanuts', 'peanut butter', 'peanut oil', 'groundnuts'],
                'alternative_names': ['groundnut', 'arachis', 'monkey nut'],
                'is_major_allergen': True
            },
            {
                'name': 'Deniz ürünleri',
                'scientific_name': 'Marine seafood',
                'description': 'Fish, shellfish, and other marine animals',
                'category': 'Seafood',
                'severity_level': 'severe',
                'common_sources': ['fish', 'shrimp', 'crab', 'lobster', 'mussels', 'oysters'],
                'alternative_names': ['shellfish', 'crustaceans', 'mollusks'],
                'is_major_allergen': True
            },
            {
                'name': 'Yumurta',
                'scientific_name': 'Chicken egg proteins',
                'description': 'Proteins found in chicken eggs',
                'category': 'Eggs',
                'severity_level': 'moderate',
                'common_sources': ['eggs', 'mayonnaise', 'meringue', 'custard'],
                'alternative_names': ['ovalbumin', 'egg protein', 'albumin'],
                'is_major_allergen': True
            },
            {
                'name': 'Soya',
                'scientific_name': 'Glycine max',
                'description': 'Protein from soybeans',
                'category': 'Legumes',
                'severity_level': 'moderate',
                'common_sources': ['soybeans', 'soy sauce', 'tofu', 'tempeh', 'soy milk'],
                'alternative_names': ['soybean', 'glycine max', 'soy protein'],
                'is_major_allergen': True
            },
            {
                'name': 'Badem',
                'scientific_name': 'Prunus dulcis',
                'description': 'Tree nut allergen',
                'category': 'Tree Nuts',
                'severity_level': 'severe',
                'common_sources': ['almonds', 'almond milk', 'marzipan', 'almond oil'],
                'alternative_names': ['sweet almond', 'prunus dulcis'],
                'is_major_allergen': True
            },
            {
                'name': 'Ceviz',
                'scientific_name': 'Juglans regia',
                'description': 'Common walnut allergen',
                'category': 'Tree Nuts',
                'severity_level': 'severe',
                'common_sources': ['walnuts', 'walnut oil', 'walnut butter'],
                'alternative_names': ['english walnut', 'juglans'],
                'is_major_allergen': True
            },
            {
                'name': 'Fındık',
                'scientific_name': 'Corylus avellana',
                'description': 'Hazelnut tree nut allergen',
                'category': 'Tree Nuts',
                'severity_level': 'severe',
                'common_sources': ['hazelnuts', 'hazelnut oil', 'nutella'],
                'alternative_names': ['filbert', 'cobnut'],
                'is_major_allergen': True
            },
            {
                'name': 'Susam',
                'scientific_name': 'Sesamum indicum',
                'description': 'Sesame seed allergen',
                'category': 'Seeds',
                'severity_level': 'moderate',
                'common_sources': ['sesame seeds', 'tahini', 'sesame oil', 'halva'],
                'alternative_names': ['benne seed', 'gingelly'],
                'is_major_allergen': True
            },
            {
                'name': 'Kükürt dioksit',
                'scientific_name': 'Sulfur dioxide',
                'description': 'Sulfite preservative allergen',
                'category': 'Additives',
                'severity_level': 'mild',
                'common_sources': ['wine', 'dried fruits', 'processed foods'],
                'alternative_names': ['sulfites', 'E220', 'sulfur dioxide'],
                'is_major_allergen': False
            },
            {
                'name': 'Kereviz',
                'scientific_name': 'Apium graveolens',
                'description': 'Celery vegetable allergen',
                'category': 'Vegetables',
                'severity_level': 'mild',
                'common_sources': ['celery', 'celery seed', 'celery salt'],
                'alternative_names': ['celeriac', 'celery root'],
                'is_major_allergen': False
            },
            {
                'name': 'Hardal',
                'scientific_name': 'Brassica species',
                'description': 'Mustard seed allergen',
                'category': 'Seeds',
                'severity_level': 'mild',
                'common_sources': ['mustard seeds', 'mustard sauce', 'dijon mustard'],
                'alternative_names': ['mustard seed', 'brassica'],
                'is_major_allergen': False
            }
        ]
        
        # Create allergen records
        for allergen_data in allergens_data:
            allergen = Allergen(
                name=allergen_data['name'],
                scientific_name=allergen_data['scientific_name'],
                description=allergen_data['description'],
                category=allergen_data['category'],
                severity_level=allergen_data['severity_level'],
                common_sources=allergen_data['common_sources'],
                alternative_names=allergen_data['alternative_names'],
                is_major_allergen=allergen_data['is_major_allergen']
            )
            session.add(allergen)
            
        session.commit()
        print(f"Successfully seeded {len(allergens_data)} allergens!")
        
    except Exception as e:
        session.rollback()
        print(f"Error seeding allergens: {str(e)}")
        raise
    finally:
        db.close(session)

if __name__ == "__main__":
    seed_allergens()
