from backend.repositories.cart.cart_repository import CartRepository
from backend.models.cart.cart import Cart, CartItem
from backend import db

class CartService:
    @staticmethod
    def save_cart(user_id: int, session_id: str) -> None:
        temp_cart = CartRepository.find_by_session(session_id)
        if temp_cart:
            saved_cart = CartRepository.find_or_create_by_user(user_id)
            for item in temp_cart.items:
                existing_item = CartRepository.find_item(saved_cart, item.product_id)
                if existing_item:
                    existing_item.quantity += item.quantity
                else:
                    new_item = CartItem(cart_id=saved_cart.id, product_id=item.product_id, quantity=item.quantity)
                    CartRepository.save_item(new_item)
            db.session.delete(temp_cart)
            db.session.commit()