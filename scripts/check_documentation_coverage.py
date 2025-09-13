#!/usr/bin/env python3
"""
Documentation coverage analysis script for ADR-013 compliance.

This script analyzes the overall documentation coverage of the codebase
and provides detailed reporting on documentation quality.
"""

import ast
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass


@dataclass
class DocumentationStats:
    """Statistics for documentation coverage."""
    total_functions: int = 0
    documented_functions: int = 0
    total_classes: int = 0
    documented_classes: int = 0
    total_methods: int = 0
    documented_methods: int = 0
    
    @property
    def function_coverage(self) -> float:
        """Calculate function documentation coverage percentage."""
        if self.total_functions == 0:
            return 100.0
        return (self.documented_functions / self.total_functions) * 100
    
    @property
    def class_coverage(self) -> float:
        """Calculate class documentation coverage percentage."""
        if self.total_classes == 0:
            return 100.0
        return (self.documented_classes / self.total_classes) * 100
    
    @property
    def method_coverage(self) -> float:
        """Calculate method documentation coverage percentage."""
        if self.total_methods == 0:
            return 100.0
        return (self.documented_methods / self.total_methods) * 100
    
    @property
    def overall_coverage(self) -> float:
        """Calculate overall documentation coverage percentage."""
        total_items = self.total_functions + self.total_classes + self.total_methods
        documented_items = self.documented_functions + self.documented_classes + self.documented_methods
        
        if total_items == 0:
            return 100.0
        return (documented_items / total_items) * 100


class DocumentationCoverageAnalyzer:
    """Analyzes documentation coverage across Python files."""
    
    def __init__(self):
        self.stats = DocumentationStats()
        self.file_stats: Dict[str, DocumentationStats] = {}
        self.undocumented_items: List[str] = []
        
    def analyze_file(self, file_path: Path) -> DocumentationStats:
        """
        Analyze documentation coverage for a single file.
        
        Args:
            file_path: Path to the Python file to analyze.
            
        Returns:
            DocumentationStats for the file.
        """
        file_stats = DocumentationStats()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content, str(file_path))
            self._analyze_node(tree, file_path, file_stats)
            
        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")
            return file_stats
        
        self.file_stats[str(file_path)] = file_stats
        
        # Update global stats
        self.stats.total_functions += file_stats.total_functions
        self.stats.documented_functions += file_stats.documented_functions
        self.stats.total_classes += file_stats.total_classes
        self.stats.documented_classes += file_stats.documented_classes
        self.stats.total_methods += file_stats.total_methods
        self.stats.documented_methods += file_stats.documented_methods
        
        return file_stats
    
    def _analyze_node(self, node: ast.AST, file_path: Path, file_stats: DocumentationStats, 
                     parent_name: str = "", in_class: bool = False):
        """Recursively analyze AST nodes for documentation."""
        if isinstance(node, ast.ClassDef):
            self._analyze_class(node, file_path, file_stats)
            # Analyze class methods
            for child in ast.iter_child_nodes(node):
                self._analyze_node(child, file_path, file_stats, node.name, True)
                
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if in_class:
                self._analyze_method(node, file_path, file_stats, parent_name)
            else:
                self._analyze_function(node, file_path, file_stats)
        else:
            # Continue traversing for nested structures
            for child in ast.iter_child_nodes(node):
                self._analyze_node(child, file_path, file_stats, parent_name, in_class)
    
    def _analyze_class(self, node: ast.ClassDef, file_path: Path, file_stats: DocumentationStats):
        """Analyze a class for documentation."""
        # Skip private classes
        if node.name.startswith('_'):
            return
            
        file_stats.total_classes += 1
        
        docstring = ast.get_docstring(node)
        if docstring:
            file_stats.documented_classes += 1
        else:
            self.undocumented_items.append(f"{file_path}:{node.lineno}: Class '{node.name}'")
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: Path, file_stats: DocumentationStats):
        """Analyze a function for documentation."""
        # Skip private functions and test functions
        if node.name.startswith('_') or node.name.startswith('test_'):
            return
            
        file_stats.total_functions += 1
        
        docstring = ast.get_docstring(node)
        if docstring:
            file_stats.documented_functions += 1
        else:
            self.undocumented_items.append(f"{file_path}:{node.lineno}: Function '{node.name}'")
    
    def _analyze_method(self, node: ast.FunctionDef, file_path: Path, 
                       file_stats: DocumentationStats, class_name: str):
        """Analyze a method for documentation."""
        # Skip private methods (but include __init__)
        if node.name.startswith('_') and node.name != '__init__':
            return
            
        file_stats.total_methods += 1
        
        docstring = ast.get_docstring(node)
        if docstring:
            file_stats.documented_methods += 1
        else:
            method_name = f"{class_name}.{node.name}"
            self.undocumented_items.append(f"{file_path}:{node.lineno}: Method '{method_name}'")
    
    def generate_report(self, min_coverage: float = 90.0) -> bool:
        """
        Generate a comprehensive documentation coverage report.
        
        Args:
            min_coverage: Minimum required coverage percentage.
            
        Returns:
            True if coverage meets minimum requirements, False otherwise.
        """
        print("📊 Documentation Coverage Report")
        print("=" * 50)
        
        # Overall statistics
        print(f"\n🎯 Overall Coverage: {self.stats.overall_coverage:.1f}%")
        print(f"   Functions: {self.stats.documented_functions}/{self.stats.total_functions} "
              f"({self.stats.function_coverage:.1f}%)")
        print(f"   Classes:   {self.stats.documented_classes}/{self.stats.total_classes} "
              f"({self.stats.class_coverage:.1f}%)")
        print(f"   Methods:   {self.stats.documented_methods}/{self.stats.total_methods} "
              f"({self.stats.method_coverage:.1f}%)")
        
        # File-by-file breakdown
        print(f"\n📁 File Coverage Breakdown:")
        for file_path, stats in sorted(self.file_stats.items()):
            if stats.overall_coverage < 100:
                status = "❌" if stats.overall_coverage < min_coverage else "⚠️"
                print(f"  {status} {file_path}: {stats.overall_coverage:.1f}%")
            else:
                print(f"  ✅ {file_path}: 100%")
        
        # Undocumented items
        if self.undocumented_items:
            print(f"\n📝 Undocumented Items ({len(self.undocumented_items)}):")
            for item in sorted(self.undocumented_items):
                print(f"  - {item}")
        
        # Coverage assessment
        meets_requirement = self.stats.overall_coverage >= min_coverage
        
        print(f"\n{'✅' if meets_requirement else '❌'} Coverage Status:")
        print(f"   Required: {min_coverage}%")
        print(f"   Actual:   {self.stats.overall_coverage:.1f}%")
        
        if not meets_requirement:
            gap = min_coverage - self.stats.overall_coverage
            print(f"   Gap:      {gap:.1f}%")
        
        return meets_requirement


def main():
    """Main entry point for documentation coverage analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze documentation coverage for ADR-013 compliance"
    )
    parser.add_argument(
        '--directory', 
        type=Path, 
        default=Path('app'),
        help='Directory to analyze recursively (default: app)'
    )
    parser.add_argument(
        '--min-coverage', 
        type=float, 
        default=90.0,
        help='Minimum required coverage percentage (default: 90.0)'
    )
    parser.add_argument(
        '--output-format', 
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    args = parser.parse_args()
    
    analyzer = DocumentationCoverageAnalyzer()
    
    # Collect and analyze Python files
    if not args.directory.exists():
        print(f"❌ Directory {args.directory} does not exist")
        sys.exit(1)
    
    python_files = list(args.directory.rglob('*.py'))
    
    # Filter out __init__.py and migration files
    python_files = [
        f for f in python_files 
        if f.name != '__init__.py' and 'migrations' not in str(f)
    ]
    
    if not python_files:
        print(f"❌ No Python files found in {args.directory}")
        sys.exit(1)
    
    print(f"🔍 Analyzing {len(python_files)} Python files...")
    
    for file_path in python_files:
        analyzer.analyze_file(file_path)
    
    # Generate report
    meets_requirement = analyzer.generate_report(args.min_coverage)
    
    sys.exit(0 if meets_requirement else 1)


if __name__ == "__main__":
    main()