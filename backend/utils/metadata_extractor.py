import re

def extract_metadata(text, filename):
    metadata = {"source": filename}
    
    # Extract title (first h1 header)
    title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    if title_match:
        metadata["title"] = title_match.group(1)
    
    # Detect if the document contains code
    if re.search(r'```[\s\S]*?```', text):
        metadata["contains_code"] = "true"  # Use string instead of boolean
    else:
        metadata["contains_code"] = "false"
    
    # Count the number of code blocks
    code_blocks = re.findall(r'```[\s\S]*?```', text)
    metadata["code_block_count"] = str(len(code_blocks))  # Convert to string
    
    return metadata