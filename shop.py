import json


class Shop:
    def __init__(self, filepath):
        self.filepath = filepath
        self.items = self.load_items()

    def load_items(self):
        try:
            with open(self.filepath, 'r') as file:
                items = json.load(file)
        except FileNotFoundError:
            items = {}
        return items

    def save_items(self):
        with open(self.filepath, 'w') as file:
            json.dump(self.items, file, indent=4)

    def add_item(self, item_name, price, quantity):
        if item_name not in self.items:
            self.items[item_name] = {'price': price, 'quantity': quantity}
        else:
            self.items[item_name]['quantity'] += quantity
        self.save_items()

    def remove_item(self, item_name, quantity):
        if item_name in self.items and self.items[item_name]['quantity'] >= quantity:
            self.items[item_name]['quantity'] -= quantity
            if self.items[item_name]['quantity'] <= 0:
                del self.items[item_name]
            self.save_items()
            return True
        return False

    def get_item_price(self, item_name):
        return self.items.get(item_name, {}).get('price', 0)

    def get_item_quantity(self, item_name):
        return self.items.get(item_name, {}).get('quantity', 0)

    def list_items(self):
        return self.items
        
    def get_item(self, item_name):
        return self.items.get(item_name)

    def get_item_info(self, item_name):
        return self.items.get(item_name)
