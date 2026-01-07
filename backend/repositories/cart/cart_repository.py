from backend.models.cart.cart import Cart, CartItem
from backend import db

class CartRepository:
    @staticmethod
    def find_by_user(user_id: int) -> Cart:
        return Cart.query.filter_by(user_id=user_id).first()

    @staticmethod
    def find_by_session(session_id: str) -> Cart:
        return Cart.query.filter_by(session_id=session_id).first()

    @staticmethod
    def find_or_create_by_user(user_id: int) -> Cart:
        cart = CartRepository.find_by_user(user_id)
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.commit()
        return cart

    @staticmethod
    def find_or_create_by_session(session_id: str) -> Cart:
        cart = CartRepository.find_by_session(session_id)
        if not cart:
            cart = Cart(session_id=session_id)
            db.session.add(cart)
            db.session.commit()
        return cart

    @staticmethod
    def find_item(cart: Cart, product_id: int) -> CartItem:
        return CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()

    @staticmethod
    def save_item(cart_item: CartItem) -> None:
        db.session.add(cart_item)
        db.session.commit()