import os
from pathlib import Path
from typing import List

def create_directory_tree(path: Path, prefix: str = "", is_last: bool = True) -> List[str]:
    """
    Creates a visual directory tree structure, ignoring venv_new folder.
    """
    tree_lines = []
    
    # Skip venv_new folder completely
    if path.name == "venv":
        return tree_lines
    
    # Add current directory/file
    tree_lines.append(prefix + ("└── " if is_last else "├── ") + path.name)
    
    # If it's a directory, process its contents
    if path.is_dir():
        # Get all items in the directory
        items = list(path.iterdir())
        # Filter out venv_new and other items to ignore
        items = [item for item in items if item.name != "venv_new" and 
                item.name != "LLM_Summary.md" and 
                item.name != "__pycache__"]
        items = sorted(items, key=lambda x: (not x.is_dir(), x.name))
        
        # Process each item
        for i, item in enumerate(items):
            is_last_item = i == len(items) - 1
            new_prefix = prefix + ("    " if is_last else "│   ")
            tree_lines.extend(create_directory_tree(item, new_prefix, is_last_item))
    
    return tree_lines

def scan_specific_directories(
    root_dir: str = "backend",
    output_filename: str = "LLM_Summary.md",
    target_folders: List[str] = None
) -> None:
    """
    Creates a directory overview (excluding venv_new) and scans specified folders for Python files.
    
    Args:
        root_dir (str): Root directory path (defaults to 'backend')
        output_filename (str): Name of the output file (defaults to 'LLM_Summary.md')
        target_folders (List[str]): List of specific folder paths to scan
    """
    # Convert the input and output paths to absolute paths
    root_path = Path(root_dir).resolve()
    output_file = root_path / output_filename
    
    # Generate directory tree
    tree_lines = create_directory_tree(root_path)
    
    # Convert target folders to Path objects
    target_folders = [root_path / folder for folder in target_folders]
    
    # List to store all file information
    file_contents = []
    
    # Scan each target folder
    for target_folder in target_folders:
        if not target_folder.exists():
            print(f"Warning: Folder {target_folder} not found")
            continue
            
        # Skip venv_new folder
        if "venv_new" in str(target_folder):
            continue
            
        # Walk through the target folder
        for current_path, dirs, files in os.walk(target_folder):
            current_path = Path(current_path)
            
            # Skip if we're in venv_new folder
            if "venv_new" in str(current_path):
                continue
                
            # Sort files to ensure consistent output
            for file in sorted(files):
                file_path = current_path / file
                
                # Skip the summary file if it exists
                if file_path.name == output_filename:
                    continue
                    
                # Only process Python files
                if file_path.suffix.lower() == '.py':
                    try:
                        # Get relative path from root directory
                        relative_path = file_path.relative_to(root_path)
                        
                        # Read Python file contents
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        file_contents.append(f"# File: {relative_path}\n```python\n{content}\n```\n")
                    except Exception as e:
                        file_contents.append(f"# File: {relative_path}\nError reading file: {str(e)}\n")
    
    # Write everything to the summary file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# RAG Chatbot Implementation Documentation\n\n")
            f.write("This document describes the code for a RAG chatbot and how the files are organized. "
                   "Below you'll find the complete source code and structure of the implementation.\n\n")
            
            # Write directory structure
            f.write("## Complete Directory Structure\n")
            f.write("```\n")
            f.write('\n'.join(tree_lines))
            f.write("\n```\n\n")
            
            # Write which folders were scanned
            f.write("## Scanned Folders:\n")
            for folder in target_folders:
                if "venv_new" not in str(folder):  # Only show non-venv folders
                    f.write(f"- {folder.relative_to(root_path)}\n")
            f.write("\n")
            
            f.write("## Code Contents\n\n")
            f.write('\n'.join(file_contents))
            
        print(f"Successfully created {output_filename} at {output_file}")
        # Print number of Python files found
        num_files = len(file_contents)
        print(f"Found and processed {num_files} Python files")
    except Exception as e:
        print(f"Error writing {output_filename}: {str(e)}")

if __name__ == "__main__":
    # Specify the folders you want to scan
    folders_to_scan = [
        "app",
        "data",
        "scripts",
        "tests"
    ]
    
    scan_specific_directories(
        target_folders=folders_to_scan
    )