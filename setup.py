import os
from pathlib import Path

def create_project_structure():
    # Define base directory
    base_dir = Path("konsum_tracker")
    
    # Define all directories to create
    directories = [
        base_dir,
        base_dir / "config",
        base_dir / "scrapers",
        base_dir / "database",
        base_dir / "utils",
        base_dir / "cli"
    ]
    
    # Create directories
    for directory in directories:
        directory.mkdir(exist_ok=True)
        # Create __init__.py in each directory
        (directory / "__init__.py").touch()
    
    # Create additional files
    (base_dir.parent / "requirements.txt").touch()
    (base_dir.parent / "README.md").touch()
    (base_dir.parent / ".env").touch()
    
    # Create empty config files
    (base_dir / "config" / "settings.py").touch()
    (base_dir / "config" / "categories.json").touch()
    
    print("Project structure created successfully!")

if __name__ == "__main__":
    create_project_structure()