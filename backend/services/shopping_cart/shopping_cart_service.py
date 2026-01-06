from backend.repositories.shopping_cart.shopping_cart_repository import ShoppingCartRepository
from backend.models.shopping_cart import ShoppingCart
from typing import Optional, List

class ShoppingCartService:
    def __init__(self, shopping_cart_repository: ShoppingCartRepository):
        self.shopping_cart_repository = shopping_cart_repository

    def add_item_to_cart(self, user_id: Optional[int], session_id: Optional[str], product_id: int, quantity: int) -> ShoppingCart:
        cart_item = ShoppingCart(user_id=user_id, session_id=session_id, product_id=product_id, quantity=quantity)
        return self.shopping_cart_repository.add_item(cart_item)

    def get_cart_items(self, user_id: Optional[int] = None, session_id: Optional[str] = None) -> List[ShoppingCart]:
        if user_id is not None:
            return self.shopping_cart_repository.get_items_by_user_id(user_id)
        if session_id is not None:
            return self.shopping_cart_repository.get_items_by_session_id(session_id)
        return []

    def remove_item_from_cart(self, cart_item_id: int) -> bool:
        return self.shopping_cart_repository.remove_item(cart_item_id)