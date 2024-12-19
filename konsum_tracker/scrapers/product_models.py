from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class NutrientValue:
    """Data class for a nutrient value with its unit"""
    value: Optional[float] = None
    unit: Optional[str] = None

@dataclass
class NutritionInfo:
    """Data class for nutrition information with separate value and unit storage"""
    serving_size: Optional[str] = None
    energy_kcal: Optional[NutrientValue] = None
    energy_kj: Optional[NutrientValue] = None
    fat_total: Optional[NutrientValue] = None
    fat_saturated: Optional[NutrientValue] = None
    carbohydrates_total: Optional[NutrientValue] = None
    carbohydrates_sugar: Optional[NutrientValue] = None
    protein: Optional[NutrientValue] = None
    salt: Optional[NutrientValue] = None
    fiber: Optional[NutrientValue] = None
    raw_values: Dict[str, str] = field(default_factory=dict)

@dataclass
class Product:
    """Data class to store product information"""
    id: str
    url: str
    name: str
    price: float
    unit_price: Optional[float]
    unit: str
    category_path: str
    description: Optional[str]
    ingredients: Optional[str]
    nutrition: NutritionInfo
    allergens: List[str]
    scrape_date: datetime

def serialize_product(product: Product) -> dict:
    """Helper function to serialize a Product into a dictionary format"""
    return {
        'id': product.id,
        'url': product.url,
        'name': product.name,
        'price': product.price,
        'unit_price': product.unit_price,
        'unit': product.unit,
        'category_path': product.category_path,
        'description': product.description,
        'ingredients': product.ingredients,
        'nutrition': {
            'serving_size': product.nutrition.serving_size,
            'energy_kcal': {
                'value': product.nutrition.energy_kcal.value if product.nutrition.energy_kcal else None,
                'unit': product.nutrition.energy_kcal.unit if product.nutrition.energy_kcal else None
            },
            'energy_kj': {
                'value': product.nutrition.energy_kj.value if product.nutrition.energy_kj else None,
                'unit': product.nutrition.energy_kj.unit if product.nutrition.energy_kj else None
            },
            'fat_total': {
                'value': product.nutrition.fat_total.value if product.nutrition.fat_total else None,
                'unit': product.nutrition.fat_total.unit if product.nutrition.fat_total else None
            },
            'fat_saturated': {
                'value': product.nutrition.fat_saturated.value if product.nutrition.fat_saturated else None,
                'unit': product.nutrition.fat_saturated.unit if product.nutrition.fat_saturated else None
            },
            'carbohydrates_total': {
                'value': product.nutrition.carbohydrates_total.value if product.nutrition.carbohydrates_total else None,
                'unit': product.nutrition.carbohydrates_total.unit if product.nutrition.carbohydrates_total else None
            },
            'carbohydrates_sugar': {
                'value': product.nutrition.carbohydrates_sugar.value if product.nutrition.carbohydrates_sugar else None,
                'unit': product.nutrition.carbohydrates_sugar.unit if product.nutrition.carbohydrates_sugar else None
            },
            'protein': {
                'value': product.nutrition.protein.value if product.nutrition.protein else None,
                'unit': product.nutrition.protein.unit if product.nutrition.protein else None
            },
            'salt': {
                'value': product.nutrition.salt.value if product.nutrition.salt else None,
                'unit': product.nutrition.salt.unit if product.nutrition.salt else None
            },
            'fiber': {
                'value': product.nutrition.fiber.value if product.nutrition.fiber else None,
                'unit': product.nutrition.fiber.unit if product.nutrition.fiber else None
            },
            'raw_values': product.nutrition.raw_values
        },
        'allergens': product.allergens,
        'scrape_date': product.scrape_date.isoformat()
    }
