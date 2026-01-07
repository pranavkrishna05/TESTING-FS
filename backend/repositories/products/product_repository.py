from backend.models.products.product import Product
from backend import db
from sqlalchemy import or_

class ProductRepository:
    @staticmethod
    def find_by_name(name: str) -> Product:
        return Product.query.filter_by(name=name).first()

    @staticmethod
    def find_by_id(product_id: int) -> Product:
        return Product.query.get(product_id)

    @staticmethod
    def save(product: Product) -> None:
        db.session.add(product)
        db.session.commit()

    @staticmethod
    def delete(product: Product) -> None:
        db.session.delete(product)
        db.session.commit()

    @staticmethod
    def search(query: str, page: int, per_page: int):
        search_query = f"%{query}%"
        products = Product.query.filter(
            or_(
                Product.name.ilike(search_query),
                Product.description.ilike(search_query)
            )
        ).paginate(page, per_page, error_out=False)
        return products.items, products.total