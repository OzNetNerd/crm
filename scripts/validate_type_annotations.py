#!/usr/bin/env python3
"""
Type annotation validation script for ADR-013 compliance.

This script validates that all Python functions have proper type annotations
according to the documentation standards.
"""

import ast
import sys
import argparse
from pathlib import Path
from typing import List, Set


class TypeAnnotationValidator:
    """Validates Python type annotations for ADR-013 compliance."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_file(self, file_path: Path) -> bool:
        """
        Validate type annotations in a Python file.
        
        Args:
            file_path: Path to the Python file to validate.
            
        Returns:
            True if all type annotations are valid, False otherwise.
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
        """Recursively check AST nodes for type annotation compliance."""
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self._check_function_annotations(node, file_path, parent_name)
        elif isinstance(node, ast.ClassDef):
            parent_name = node.name
            
        # Recursively check child nodes
        for child in ast.iter_child_nodes(node):
            self._check_node(child, file_path, parent_name)
    
    def _check_function_annotations(self, node: ast.FunctionDef, file_path: Path, parent_name: str):
        """Check if a function has proper type annotations."""
        # Skip private methods and special methods (except __init__)
        if node.name.startswith('_') and node.name != '__init__':
            return
            
        # Skip test functions
        if node.name.startswith('test_'):
            return
            
        function_name = f"{parent_name}.{node.name}" if parent_name else node.name
        
        # Check return type annotation
        if not node.returns and node.name != '__init__':
            self.warnings.append(
                f"{file_path}:{node.lineno}: Function '{function_name}' "
                "missing return type annotation"
            )
        
        # Check parameter type annotations
        missing_annotations = []
        for arg in node.args.args:
            # Skip 'self' and 'cls' parameters
            if arg.arg in ('self', 'cls'):
                continue
                
            if not arg.annotation:
                missing_annotations.append(arg.arg)
        
        if missing_annotations:
            self.warnings.append(
                f"{file_path}:{node.lineno}: Function '{function_name}' "
                f"missing type annotations for parameters: {', '.join(missing_annotations)}"
            )


def main():
    """Main entry point for type annotation validation."""
    parser = argparse.ArgumentParser(
        description="Validate Python type annotations for ADR-013 compliance"
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
    
    validator = TypeAnnotationValidator()
    
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
        print("❌ Type annotation validation errors:")
        for error in validator.errors:
            print(f"  {error}")
        success = False
    
    if validator.warnings:
        print("⚠️  Type annotation validation warnings:")
        for warning in validator.warnings:
            print(f"  {warning}")
        if args.strict:
            success = False
    
    if success:
        print("✅ All type annotations are valid!")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()