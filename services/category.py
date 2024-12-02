from models.category import Category
from schemas.category import CategorySchema


class CategoryService():
    def __init__(self, db) -> None:
        self.db = db

    def get_categories(self):
        result = self.db.query(Category).all()
        return result

    def get_category(self, id):
        result = self.db.query(Category).filter(Category.id == id).first()
        return result

    def create_category(self, category: Category):
        new_category = Category(**category.dict())
        self.db.add(new_category)
        self.db.commit()
        return

    def update_category(self, id: int, category: Category):
        result = self.db.query(Category).filter(Category.id == id).first()
        result.name = category.name
        result.description = category.description
        self.db.commit()
        return

    def delete_category(self, id: int):
        self.db.query(Category).filter(Category.id == id).delete()
        self.db.commit()
        return
