from typing import Optional, List
from backend.models.category import Category

class CategoryRepository:

    def __init__(self, db):
        self.db = db

    def add_category(self, category: Category) -> Category:
        query = """
        INSERT INTO categories (name, parent_id, created_at, updated_at)
        VALUES (:name, :parent_id, :created_at, :updated_at)
        RETURNING id;
        """
        cursor = self.db.cursor()
        cursor.execute(query, category.dict())
        category.id = cursor.fetchone()[0]
        self.db.commit()
        return category

    def get_category_by_id(self, category_id: int) -> Optional<Category]:
        query = "SELECT * FROM categories WHERE id = :id;"
        cursor = self.db.cursor()
        cursor.execute(query, {"id": category_id})
        row = cursor.fetchone()
        if row:
            return Category(id=row[0], name=row[1], parent_id=row[2], created_at=row[3], updated_at=row[4])
        return None

    def get_all_categories(self) -> List[Category]:
        query = "SELECT * FROM categories;"
        cursor = self.db.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [Category(id=row[0], name=row[1], parent_id=row[2], created_at=row[3], updated_at=row[4]) for row in rows]

    def update_category(self, category: Category) -> None:
        query = """
        UPDATE categories SET name = :name, parent_id = :parent_id, updated_at = :updated_at
        WHERE id = :id;
        """
        cursor = self.db.cursor()
        cursor.execute(query, category.dict())
        self.db.commit()