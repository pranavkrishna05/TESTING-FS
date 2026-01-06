from backend.repositories.categories.category_repository import CategoryRepository
from backend.models.category import Category
from typing import Optional, List

class CategoryService:
    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    def add_category(self, name: str, parent_id: Optional[int] = None) -> Category:
        category = Category(name=name, parent_id=parent_id)
        return self.category_repository.add_category(category)

    def get_category_by_id(self, category_id: int) -> Optional<Category]:
        return self.category_repository.get_category_by_id(category_id)

    def get_all_categories(self) -> List<Category]:
        return self.category_repository.get_all_categories()

    def update_category(self, category_id: int, name: Optional[str], parent_id: Optional[int]) -> bool:
        category = self.category_repository.get_category_by_id(category_id)
        if not category:
            return False

        if name:
            category.name = name
        if parent_id is not None:
            category.parent_id = parent_id

        self.category_repository.update_category(category)
        return True