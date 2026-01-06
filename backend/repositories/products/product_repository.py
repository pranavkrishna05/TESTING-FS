from typing import Optional, List
from backend.models.product import Product

class ProductRepository:

    def __init__(self, db):
        self.db = db

    def add_product(self, product: Product) -> Product:
        query = """
        INSERT INTO products (name, price, description, category, is_deleted, created_at, updated_at)
        VALUES (:name, :price, :description, :category, :is_deleted, :created_at, :updated_at)
        RETURNING id;
        """
        cursor = self.db.cursor()
        cursor.execute(query, product.dict())
        product.id = cursor.fetchone()[0]
        self.db.commit()
        return product

    def get_product_by_name(self, name: str) -> Optional<Product]:
        query = "SELECT * FROM products WHERE name = :name AND is_deleted = FALSE;"
        cursor = self.db.cursor()
        cursor.execute(query, {"name": name})
        row = cursor.fetchone()
        if row:
            return Product(id=row[0], name=row[1], price=row[2], description=row[3], category=row[4], is_deleted=row[5], created_at=row[6], updated_at=row[7])
        return None

    def update_product(self, product: Product) -> None:
        query = """
        UPDATE products SET name = :name, price = :price, description = :description, category = :category, is_deleted = :is_deleted, updated_at = :updated_at
        WHERE id = :id;
        """
        cursor = self.db.cursor()
        cursor.execute(query, product.dict())
        self.db.commit()

    def get_product_by_id(self, product_id: int) -> Optional<Product]:
        query = "SELECT * FROM products WHERE id = :id AND is_deleted = FALSE;"
        cursor = self.db.cursor()
        cursor.execute(query, {"id": product_id})
        row = cursor.fetchone()
        if row:
            return Product(id=row[0], name=row[1], price=row[2], description=row[3], category=row[4], is_deleted=row[5], created_at=row[6], updated_at=row[7])
        return None

    def delete_product(self, product_id: int) -> bool:
        query = "UPDATE products SET is_deleted = TRUE WHERE id = :id;"
        cursor = self.db.cursor()
        cursor.execute(query, {"id": product_id})
        self.db.commit()
        return cursor.rowcount > 0

    def get_all_products(self) -> List[Product]:
        query = "SELECT * FROM products WHERE is_deleted = FALSE;"
        cursor = self.db.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [Product(id=row[0], name=row[1], price=row[2], description=row[3], category=row[4], is_deleted=row[5], created_at=row[6], updated_at=row[7]) for row in rows]

    def search_products(self, term: str, limit: int, offset: int) -> List[Product]:
        query = """
        SELECT * FROM products
        WHERE (name LIKE :term OR description LIKE :term OR category LIKE :term) AND is_deleted = FALSE
        LIMIT :limit OFFSET :offset;
        """
        cursor = self.db.cursor()
        cursor.execute(query, {"term": f"%{term}%", "limit": limit, "offset": offset})
        rows = cursor.fetchall()
        return [Product(id=row[0], name=row[1], price=row[2], description=row[3], category=row[4], is_deleted=row[5], created_at=row[6], updated_at=row[7]) for row in rows]