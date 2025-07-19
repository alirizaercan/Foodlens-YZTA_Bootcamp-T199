"""
Product Controller for FoodLens Application
Product search, retrieval, and management endpoints.
"""

from flask import Blueprint, request, jsonify

# Create blueprint
product_bp = Blueprint('product', __name__, url_prefix='/api/products')

@product_bp.route('/', methods=['GET'])
def search_products():
    """Search products by name or barcode."""
    return jsonify({"message": "Product search endpoint - under development"})

@product_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get product details by ID."""
    return jsonify({"message": f"Get product {product_id} - under development"})

@product_bp.route('/barcode/<barcode>', methods=['GET'])
def get_product_by_barcode(barcode):
    """Get product by barcode."""
    return jsonify({"message": f"Get product by barcode {barcode} - under development"})
