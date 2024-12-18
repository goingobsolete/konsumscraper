from pathlib import Path
import json
from typing import List, Set, Dict
import os

class CategorySelector:
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / 'config'
        self.categories_file = self.config_dir / 'categories.json'
        self.preferences_file = self.config_dir / 'category_preferences.json'
        self.categories = self._load_categories()
        self.selected_categories = self._load_preferences()

    def _load_categories(self) -> List[str]:
        """Load available categories from JSON file"""
        if not self.categories_file.exists():
            raise FileNotFoundError("Categories file not found. Run category scraper first.")
            
        with open(self.categories_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Filter out "Alle Produkte" by itself
            return [cat for cat in data.get('categories', []) 
                   if cat != "Alle Produkte" and len(cat.split(' > ')) > 1]

    def _load_preferences(self) -> Set[str]:
        """Load previously selected categories"""
        if not self.preferences_file.exists():
            return set()
            
        with open(self.preferences_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data.get('selected_categories', []))

    def select_categories(self) -> None:
        """Interactive category selection"""
        print("\nCategory Selection")
        print("-----------------")
        
        # Get real main categories (second level)
        main_categories = {cat.split(' > ')[1] for cat in self.categories}
        
        print("\nAvailable main categories:")
        for i, cat in enumerate(sorted(main_categories), 1):
            print(f"{i}. {cat}")
            
        while True:
            choice = input("\nEnter category numbers (comma-separated) or 'done' to finish: ")
            
            if choice.lower() == 'done':
                break
                
            try:
                selected_indices = [int(x.strip()) for x in choice.split(',')]
                selected_mains = [sorted(main_categories)[i-1] for i in selected_indices]
                
                for main_cat in selected_mains:
                    # Add all subcategories for selected main category
                    for category in self.categories:
                        if category.split(' > ')[1] == main_cat:
                            self.selected_categories.add(category)
                            
                print("\nSelected categories and their subcategories:")
                for cat in sorted(self.selected_categories):
                    print(f"- {cat}")
                    
            except (ValueError, IndexError) as e:
                print(f"Invalid input: {e}")
                continue

        self.save_preferences()
        print(f"\nSaved {len(self.selected_categories)} categories to preferences.")

    def get_selected_categories(self) -> Set[str]:
        """Return currently selected categories"""
        return self.selected_categories

def main():
    """Test category selection"""
    selector = CategorySelector()
    selector.select_categories()

if __name__ == "__main__":
    main()