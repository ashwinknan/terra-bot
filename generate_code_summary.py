import os
from pathlib import Path
from typing import List, Set

def create_directory_tree(path: Path, prefix: str = "", is_last: bool = True) -> List[str]:
    """
    Creates a visual directory tree structure, showing but not traversing specific folders.
    """
    tree_lines = []
    
    # Skip .git folder completely
    if path.name == ".git":
        return tree_lines
    
    # Add current directory/file
    tree_lines.append(prefix + ("└── " if is_last else "├── ") + path.name)
    
    # If it's a directory, process its contents
    if path.is_dir():
        # Get all items in the directory
        items = list(path.iterdir())
        # Filter out items to ignore
        items = [item for item in items if item.name != "Codebase_Summary.md" and 
                item.name != "__pycache__" and
                item.name != ".git"]
        items = sorted(items, key=lambda x: (not x.is_dir(), x.name))
        
        # Process each item
        for i, item in enumerate(items):
            is_last_item = i == len(items) - 1
            new_prefix = prefix + ("    " if is_last else "│   ")
            
            # Don't traverse into specific folders, but show them in tree
            if item.name not in ["venv", "node_modules", "build"]:
                tree_lines.extend(create_directory_tree(item, new_prefix, is_last_item))
            else:
                tree_lines.append(new_prefix + ("└── " if is_last_item else "├── ") + item.name)
    
    return tree_lines

def get_file_type_marker(file_extension: str) -> str:
    """
    Returns the appropriate markdown code block marker based on file extension.
    """
    extension_mapping = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'jsx',
        '.ts': 'typescript',
        '.tsx': 'tsx',
        '.css': 'css',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.html': 'html'
    }
    return extension_mapping.get(file_extension.lower(), 'plaintext')

def should_include_file(file_path: Path, context: str) -> bool:
    """
    Determines whether a file should be included in the summary based on context.
    """
    extension = file_path.suffix.lower()
    
    # Skip files in .git directory and build folder
    if any(excluded in str(file_path) for excluded in [".git", "/build/"]):
        return False
        
    if context == "root":
        return extension in ['.py', '.js', '.jsx', '.ts', '.tsx', '.yaml', '.yml']
    elif context == "backend":
        return extension == '.py'
    elif context == "frontend":
        return extension in ['.js', '.jsx', '.ts', '.tsx', '.css']
    return False

def scan_codebase(
    root_dir: str = ".",
    output_filename: str = "Codebase_Summary.md"
) -> None:
    """
    Creates a comprehensive codebase overview based on specified requirements.
    """
    # Convert the input and output paths to absolute paths
    root_path = Path(root_dir).resolve()
    output_file = root_path / output_filename
    
    # Check for frontend and backend directories
    frontend_path = root_path / "frontend"
    backend_path = root_path / "backend"
    
    # Generate directory tree
    tree_lines = create_directory_tree(root_path)
    
    # Lists to store file information
    root_contents = []
    frontend_contents = []
    backend_contents = []
    file_count = {}
    
    def process_directory(directory: Path, contents_list: List[str], context: str):
        for current_path, dirs, files in os.walk(directory):
            # Skip specific directories
            if any(excluded in current_path for excluded in ["venv", "node_modules", ".git", "/build/"]):
                continue
                
            current_path = Path(current_path)
            
            # Sort files to ensure consistent output
            for file in sorted(files):
                file_path = current_path / file
                
                if not should_include_file(file_path, context):
                    continue
                    
                file_extension = file_path.suffix.lower()
                
                # Update statistics
                file_count[file_extension] = file_count.get(file_extension, 0) + 1
                
                try:
                    # Get relative path from root directory
                    relative_path = file_path.relative_to(root_path)
                    
                    # Read file contents
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Get the appropriate code block marker
                    code_marker = get_file_type_marker(file_extension)
                    
                    contents_list.append(f"# File: {relative_path}\n```{code_marker}\n{content}\n```\n")
                except Exception as e:
                    contents_list.append(f"# File: {relative_path}\nError reading file: {str(e)}\n")
    
    # Process root directory files
    process_directory(root_path, root_contents, "root")
    
    # Process frontend and backend directories
    if frontend_path.exists():
        process_directory(frontend_path, frontend_contents, "frontend")
    if backend_path.exists():
        process_directory(backend_path, backend_contents, "backend")
    
    # Write everything to the summary file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Project Codebase Documentation\n\n")
            
            # Write directory structure
            f.write("## Complete Directory Structure\n")
            f.write("```\n")
            f.write('\n'.join(tree_lines))
            f.write("\n```\n\n")
            
            # Write file statistics
            f.write("## File Statistics\n")
            for ext, count in sorted(file_count.items()):
                f.write(f"- {ext}: {count} files\n")
            f.write("\n")
            
            # Write root directory contents
            if root_contents:
                f.write("## Root Directory Files\n\n")
                f.write('\n'.join(root_contents))
                f.write("\n")
            
            # Write frontend contents
            if frontend_contents:
                f.write("## Frontend Code Contents\n\n")
                f.write('\n'.join(frontend_contents))
                f.write("\n")
            
            # Write backend contents
            if backend_contents:
                f.write("## Backend Code Contents\n\n")
                f.write('\n'.join(backend_contents))
            
        print(f"Successfully created {output_filename} at {output_file}")
        # Print total number of files processed
        total_files = sum(file_count.values())
        print(f"Found and processed {total_files} files:")
        for ext, count in sorted(file_count.items()):
            print(f"  {ext}: {count} files")
    except Exception as e:
        print(f"Error writing {output_filename}: {str(e)}")

if __name__ == "__main__":
    scan_codebase(
        output_filename="Codebase_Summary.md"
    )