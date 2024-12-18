from pathlib import Path
import json
from typing import List, Set, Dict

class CategorySelector:
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / 'config'
        self.categories_file = self.config_dir / 'categories.json'
        self.preferences_file = self.config_dir / 'category_preferences.json'
        self.categories = self._load_categories()
        self.selected_categories = self._load_preferences()

    def _load_categories(self) -> List[str]:
        """Load categories, excluding the root 'Alle Produkte'"""
        if not self.categories_file.exists():
            raise FileNotFoundError("Categories file not found. Run category scraper first.")
            
        with open(self.categories_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Filter out single "Alle Produkte" and keep rest
            return [cat for cat in data.get('categories', []) 
                    if cat != "Alle Produkte" and cat.startswith("Alle Produkte > ")]

    def _load_preferences(self) -> Set[str]:
        """Load selected categories from preferences file"""
        if self.preferences_file.exists():
            with open(self.preferences_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('selected_categories', []))
        return set()

    def get_main_departments(self) -> List[str]:
        """Get just the main departments (depth 2 categories)"""
        departments = set()
        for cat in self.categories:
            parts = cat.split(' > ')
            if len(parts) == 2:  # Alle Produkte > Department
                departments.add(parts[1])
        return sorted(list(departments))

    def get_subcategories(self, department: str) -> List[str]:
        """Get subcategories for a department"""
        subcats = []
        for cat in self.categories:
            parts = cat.split(' > ')
            if len(parts) > 2 and parts[1] == department:
                subcats.append(' > '.join(parts[2:]))
        return sorted(subcats)

    def select_categories(self) -> None:
        """Interactive category selection with drill-down option"""
        print("\nMain Departments:")
        departments = self.get_main_departments()
        for i, dept in enumerate(departments, 1):
            print(f"{i}. {dept}")

        while True:
            choice = input("\nEnter department numbers to see subcategories (comma-separated) or 'done' to finish: ")
            
            if choice.lower() == 'done':
                break
                
            try:
                selected_indices = [int(x.strip()) for x in choice.split(',')]
                for idx in selected_indices:
                    if 1 <= idx <= len(departments):
                        department = departments[idx-1]
                        print(f"\nSubcategories for {department}:")
                        subcats = self.get_subcategories(department)
                        
                        print("0. Select entire department")
                        for i, subcat in enumerate(subcats, 1):
                            print(f"{i}. {subcat}")
                            
                        subcat_choice = input("\nEnter subcategory numbers or 0 for entire department: ")
                        if subcat_choice.strip() == "0":
                            # Add all categories for this department
                            self.selected_categories.update(
                                cat for cat in self.categories 
                                if cat.split(' > ')[1] == department
                            )
                        else:
                            try:
                                sub_indices = [int(x.strip()) for x in subcat_choice.split(',')]
                                for sub_idx in sub_indices:
                                    if 1 <= sub_idx <= len(subcats):
                                        selected_subcat = subcats[sub_idx-1]
                                        # Find and add the full category path
                                        matching_cats = [
                                            cat for cat in self.categories 
                                            if cat.split(' > ')[1] == department 
                                            and ' > '.join(cat.split(' > ')[2:]) == selected_subcat
                                        ]
                                        self.selected_categories.update(matching_cats)
                            except ValueError:
                                print("Invalid subcategory selection")
                                continue
                            
                print("\nCurrently selected categories:")
                for cat in sorted(self.selected_categories):
                    print(f"- {cat}")
                    
            except ValueError:
                print("Invalid input")
                continue

        self.save_preferences()
        print(f"\nSaved {len(self.selected_categories)} categories to preferences")

    def save_preferences(self) -> None:
        """Save selected categories to preferences file"""
        data = {
            'selected_categories': list(sorted(self.selected_categories))
        }
        with open(self.preferences_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

def main():
    selector = CategorySelector()
    selector.select_categories()

if __name__ == "__main__":
    main()
