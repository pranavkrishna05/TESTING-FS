from backend.models.products.product import Product
from backend import db

class ProductRepository:
    @staticmethod
    def find_by_name(name: str) -> Product:
        return Product.query.filter_by(name=name).first()

    @staticmethod
    def save(product: Product) -> None:
        db.session.add(product)
        db.session.commit()