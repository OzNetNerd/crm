#!/usr/bin/env python3
"""
Docstring validation script for ADR-013 compliance.

This script validates that all Python functions and classes have proper
Google-style docstrings according to the documentation standards.
"""

import ast
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Set


class DocstringValidator:
    """Validates Python docstrings for ADR-013 compliance."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_file(self, file_path: Path) -> bool:
        """
        Validate docstrings in a Python file.
        
        Args:
            file_path: Path to the Python file to validate.
            
        Returns:
            True if all docstrings are valid, False otherwise.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content, str(file_path))
            self._check_node(tree, file_path)
            
        except SyntaxError as e:
            self.errors.append(f"{file_path}:{e.lineno}: Syntax error - {e.msg}")
            return False
        except Exception as e:
            self.errors.append(f"{file_path}: Error parsing file - {e}")
            return False
            
        return len(self.errors) == 0
    
    def _check_node(self, node: ast.AST, file_path: Path, parent_name: str = ""):
        """Recursively check AST nodes for docstring compliance."""
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self._check_function_docstring(node, file_path, parent_name)
        elif isinstance(node, ast.ClassDef):
            self._check_class_docstring(node, file_path)
            parent_name = node.name
            
        # Recursively check child nodes
        for child in ast.iter_child_nodes(node):
            self._check_node(child, file_path, parent_name)
    
    def _check_function_docstring(self, node: ast.FunctionDef, file_path: Path, parent_name: str):
        """Check if a function has a proper docstring."""
        # Skip private methods and special methods
        if node.name.startswith('_') and not node.name.startswith('__'):
            return
            
        # Skip test functions
        if node.name.startswith('test_'):
            return
            
        docstring = ast.get_docstring(node)
        function_name = f"{parent_name}.{node.name}" if parent_name else node.name
        
        if not docstring:
            self.errors.append(
                f"{file_path}:{node.lineno}: Function '{function_name}' missing docstring"
            )
            return
            
        # Check for basic Google-style structure
        if not self._is_google_style_docstring(docstring):
            self.warnings.append(
                f"{file_path}:{node.lineno}: Function '{function_name}' docstring "
                "should follow Google style (Args:, Returns:, Raises: sections)"
            )
    
    def _check_class_docstring(self, node: ast.ClassDef, file_path: Path):
        """Check if a class has a proper docstring."""
        # Skip private classes
        if node.name.startswith('_'):
            return
            
        docstring = ast.get_docstring(node)
        
        if not docstring:
            self.errors.append(
                f"{file_path}:{node.lineno}: Class '{node.name}' missing docstring"
            )
            return
            
        # Check for basic structure
        if len(docstring.strip()) < 10:
            self.warnings.append(
                f"{file_path}:{node.lineno}: Class '{node.name}' docstring "
                "should be more descriptive"
            )
    
    def _is_google_style_docstring(self, docstring: str) -> bool:
        """Check if docstring follows Google style format."""
        # Basic check for Google-style sections
        lines = docstring.split('\n')
        has_description = len([line for line in lines if line.strip()]) > 0
        
        # More detailed validation could be added here
        return has_description


def main():
    """Main entry point for docstring validation."""
    parser = argparse.ArgumentParser(
        description="Validate Python docstrings for ADR-013 compliance"
    )
    parser.add_argument(
        'files', 
        nargs='*', 
        help='Python files to validate'
    )
    parser.add_argument(
        '--directory', 
        type=Path, 
        help='Directory to validate recursively'
    )
    parser.add_argument(
        '--strict', 
        action='store_true', 
        help='Treat warnings as errors'
    )
    
    args = parser.parse_args()
    
    validator = DocstringValidator()
    
    # Collect files to validate
    files_to_check: Set[Path] = set()
    
    if args.files:
        files_to_check.update(Path(f) for f in args.files)
    
    if args.directory:
        files_to_check.update(args.directory.rglob('*.py'))
    
    if not files_to_check:
        # Default: check app directory
        app_dir = Path('app')
        if app_dir.exists():
            files_to_check.update(app_dir.rglob('*.py'))
    
    # Validate files
    success = True
    for file_path in sorted(files_to_check):
        if not file_path.exists():
            continue
            
        # Skip __init__.py files and migrations
        if file_path.name == '__init__.py' or 'migrations' in str(file_path):
            continue
            
        file_success = validator.validate_file(file_path)
        if not file_success:
            success = False
    
    # Report results
    if validator.errors:
        print("❌ Docstring validation errors:")
        for error in validator.errors:
            print(f"  {error}")
        success = False
    
    if validator.warnings:
        print("⚠️  Docstring validation warnings:")
        for warning in validator.warnings:
            print(f"  {warning}")
        if args.strict:
            success = False
    
    if success:
        print("✅ All docstrings are valid!")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()