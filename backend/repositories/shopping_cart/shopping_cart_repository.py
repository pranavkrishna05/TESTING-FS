from typing import Optional, List
from backend.models.shopping_cart import ShoppingCart

class ShoppingCartRepository:

    def __init__(self, db):
        self.db = db

    def add_item(self, cart_item: ShoppingCart) -> ShoppingCart:
        query = """
        INSERT INTO shopping_cart (user_id, session_id, product_id, quantity, added_at)
        VALUES (:user_id, :session_id, :product_id, :quantity, :added_at)
        RETURNING id;
        """
        cursor = self.db.cursor()
        cursor.execute(query, cart_item.dict())
        cart_item.id = cursor.fetchone()[0]
        self.db.commit()
        return cart_item

    def get_items_by_user_id(self, user_id: int) -> List[ShoppingCart]:
        query = "SELECT * FROM shopping_cart WHERE user_id = :user_id;"
        cursor = self.db.cursor()
        cursor.execute(query, {"user_id": user_id})
        rows = cursor.fetchall()
        return [ShoppingCart(id=row[0], user_id=row[1], session_id=row[2], product_id=row[3], quantity=row[4], added_at=row[5]) for row in rows]

    def get_items_by_session_id(self, session_id: str) -> List[ShoppingCart]:
        query = "SELECT * FROM shopping_cart WHERE session_id = :session_id;"
        cursor = self.db.cursor()
        cursor.execute(query, {"session_id": session_id})
        rows = cursor.fetchall()
        return [ShoppingCart(id=row[0], user_id=row[1], session_id=row[2], product_id=row[3], quantity=row[4], added_at=row[5]) for row in rows]

    def update_item_quantity(self, cart_item_id: int, quantity: int) -> bool:
        query = "UPDATE shopping_cart SET quantity = :quantity WHERE id = :id;"
        cursor = self.db.cursor()
        cursor.execute(query, {"quantity": quantity, "id": cart_item_id})
        self.db.commit()
        return cursor.rowcount > 0

    def remove_item(self, cart_item_id: int) -> bool:
        query = "DELETE FROM shopping_cart WHERE id = :id;"
        cursor = self.db.cursor()
        cursor.execute(query, {"id": cart_item_id})
        self.db.commit()
        return cursor.rowcount > 0