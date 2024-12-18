def analyze_categories(categories):
    """Analyze category structure to find depth and any direct products"""
    depths = {}
    direct_categories = []
    
    for category in categories:
        parts = category.split(' > ')
        depth = len(parts)
        depths[category] = depth
        
        # Check for categories directly under 'Alle Produkte'
        if depth == 1 or (depth == 2 and parts[0] == "Alle Produkte"):
            direct_categories.append(category)
    
    print("\nCategory Analysis:")
    print(f"Total categories: {len(categories)}")
    print(f"\nCategories with minimal depth (potentially direct products):")
    for cat in sorted(direct_categories):
        print(f"- {cat}")
    
    print("\nDepth distribution:")
    depth_counts = {}
    for depth in depths.values():
        depth_counts[depth] = depth_counts.get(depth, 0) + 1
    for depth, count in sorted(depth_counts.items()):
        print(f"Depth {depth}: {count} categories")

# Test the analyzer
if __name__ == "__main__":
    from pathlib import Path
    import json
    
    config_dir = Path(__file__).parent.parent / 'config'
    categories_file = config_dir / 'categories.json'
    
    with open(categories_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        analyze_categories(data['categories'])