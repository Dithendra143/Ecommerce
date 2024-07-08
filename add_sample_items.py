from app import db, Item

# Sample items to add to the database
sample_items = [
    {
        'name': 'Item 1',
        'price': 10.99,
        'description': 'Description for Item 1',
        'image': 'item1.jpg',
        'gpio_pin': 17
    },
    {
        'name': 'Item 2',
        'price': 15.99,
        'description': 'Description for Item 2',
        'image': 'item2.jpg',
        'gpio_pin': 27
    },
    {
        'name': 'Item 3',
        'price': 20.99,
        'description': 'Description for Item 3',
        'image': 'item3.jpg',
        'gpio_pin': 22
    }
]

# Add sample items to the database
for item in sample_items:
    new_item = Item(name=item['name'], price=item['price'], description=item['description'], image=item['image'], gpio_pin=item['gpio_pin'])
    db.session.add(new_item)

db.session.commit()
print("Sample items added to the database.")
