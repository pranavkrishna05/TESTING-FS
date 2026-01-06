from backend.repositories.shopping_cart.shopping_cart_repository import ShoppingCartRepository
from backend.models.shopping_cart import ShoppingCart
from backend.models.product import Product
from typing import Optional, List
from backend.repositories.products.product_repository import ProductRepository

class ShoppingCartService:
    def __init__(self, shopping_cart_repository: ShoppingCartRepository, product_repository: ProductRepository):
        self.shopping_cart_repository = shopping_cart_repository
        self.product_repository = product_repository

    def add_item_to_cart(self, user_id: Optional[int], session_id: Optional[str], product_id: int, quantity: int) -> ShoppingCart:
        cart_item = ShoppingCart(user_id=user_id, session_id=session_id, product_id=product_id, quantity=quantity)
        return self.shopping_cart_repository.add_item(cart_item)

    def get_cart_items(self, user_id: Optional[int] = None, session_id: Optional[str] = None) -> List[ShoppingCart]:
        if user_id is not None:
            return self.shopping_cart_repository.get_items_by_user_id(user_id)
        if session_id is not None:
            return self.shopping_cart_repository.get_items_by_session_id(session_id)
        return []

    def update_item_quantity(self, cart_item_id: int, quantity: int) -> bool:
        return self.shopping_cart_repository.update_item_quantity(cart_item_id, quantity)

    def remove_item_from_cart(self, cart_item_id: int) -> bool:
        return self.shopping_cart_repository.remove_item(cart_item_id)

    def get_total_price(self, user_id: Optional[int] = None, session_id: Optional[str] = None) -> float:
        cart_items = self.get_cart_items(user_id, session_id)
        total_price = 0.0
        for item in cart_items:
            product = self.product_repository.get_product_by_id(item.product_id)
            total_price += product.price * item.quantity
        return total_price