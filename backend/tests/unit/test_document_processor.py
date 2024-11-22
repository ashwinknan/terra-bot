import pytest
from app.core.document_processor import DocumentProcessor, DocType
from pathlib import Path

def test_extract_document_type(tmp_path):
    processor = DocumentProcessor(str(tmp_path))
    
    # Test valid document type
    content = "## Type\nruleset\n# Test"
    assert processor._extract_document_type(content) == DocType.RULESET
    
    # Test invalid document type defaults to FUNCTIONS
    content = "## Type\ninvalid\n# Test"
    assert processor._extract_document_type(content) == DocType.FUNCTIONS

def test_document_processing(tmp_path):
    processor = DocumentProcessor(str(tmp_path))
    
    # Create test document
    doc_content = """# Test Document
## Type
functions
## Content
Test content with code:
```python
def test():
    pass
```
"""
    doc_path = tmp_path / "test.md"
    doc_path.write_text(doc_content)
    
    # Test document loading
    documents = processor.load_documents()
    assert len(documents) > 0
    assert documents[0].metadata["doc_type"] == "functions"
    assert documents[0].metadata["has_code"] is True

def test_empty_document_handling(tmp_path):
    processor = DocumentProcessor(str(tmp_path))
    
    # Create empty document
    doc_path = tmp_path / "empty.md"
    doc_path.write_text("")
    
    # Should handle empty documents gracefully
    documents = processor.load_documents()
    assert len(documents) == 0