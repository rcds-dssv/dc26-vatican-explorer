"""Shopping cart built with TDD."""


class ShoppingCart:
    """A simple shopping cart."""

    def __init__(self):
        self.items = {}
        self._discount = 0

    def add_item(self, name, price, quantity=1):
        """Add an item to the cart."""
        if name in self.items:
            self.items[name]['quantity'] += quantity
        else:
            self.items[name] = {'price': price, 'quantity': quantity}

    def remove_item(self, name):
        """Remove an item from the cart."""
        if name in self.items:
            del self.items[name]

    def apply_discount(self, percentage):
        """Apply a percentage discount."""
        self._discount = percentage / 100

    def total(self):
        """Calculate total cost after discount."""
        subtotal = sum(item['price'] * item['quantity']
                      for item in self.items.values())
        return subtotal * (1 - self._discount)
