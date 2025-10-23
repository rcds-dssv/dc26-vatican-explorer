"""Tests for shopping cart."""
from shopping_cart import ShoppingCart


def test_empty_cart():
    cart = ShoppingCart()
    assert len(cart.items) == 0
    assert cart.total() == 0


def test_add_single_item():
    cart = ShoppingCart()
    cart.add_item("apple", 1.0)
    assert len(cart.items) == 1
    assert cart.total() == 1.0


def test_add_multiple_items():
    cart = ShoppingCart()
    cart.add_item("apple", 1.0)
    cart.add_item("banana", 0.5)
    assert len(cart.items) == 2
    assert cart.total() == 1.5


def test_add_with_quantity():
    cart = ShoppingCart()
    cart.add_item("apple", 1.0, quantity=3)
    assert cart.total() == 3.0


def test_remove_item():
    cart = ShoppingCart()
    cart.add_item("apple", 1.0)
    cart.add_item("banana", 0.5)
    cart.remove_item("apple")
    assert len(cart.items) == 1
    assert cart.total() == 0.5


def test_apply_discount():
    cart = ShoppingCart()
    cart.add_item("apple", 10.0)
    cart.apply_discount(10)  # 10% off
    assert cart.total() == 9.0
