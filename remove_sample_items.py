from app import db, Item

# Names of the sample items to remove
sample_item_names = ['Item 1', 'Item 2', 'Item 3']

# Remove sample items from the database
for name in sample_item_names:
    item = Item.query.filter_by(name=name).first()
    if item:
        db.session.delete(item)

db.session.commit()
print("Sample items removed from the database.")
