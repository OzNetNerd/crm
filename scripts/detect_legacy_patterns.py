#!/usr/bin/env python3
"""
Legacy pattern detection script for ADR-010 compliance.

This script scans the codebase for legacy patterns and implements
loud failure enforcement according to the zero-tolerance policy.
"""

import sys
import argparse
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import ast

# Add app to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.validation.template_validator import TemplateValidator
from app.utils.exceptions.legacy_exceptions import (
    LegacyCodeError,
    TemplateModernizationError,
    LegacySQLError,
    ConfigurationLegacyError
)


class LegacyPatternDetector:
    """Comprehensive legacy pattern detection and enforcement."""
    
    def __init__(self, project_root: str = "."):
        """
        Initialize legacy pattern detector.
        
        Args:
            project_root: Root directory of the project to scan
        """
        self.project_root = Path(project_root)
        self.template_validator = TemplateValidator()
        self.errors: List[LegacyCodeError] = []
        self.warnings: List[str] = []
        
    def detect_template_violations(self) -> List[TemplateModernizationError]:
        """
        Detect JavaScript embedded in templates.
        
        Returns:
            List of template modernization errors
        """
        return self.template_validator.validate_all_templates()
    
    def detect_raw_sql_patterns(self) -> List[LegacySQLError]:
        """
        Detect raw SQL usage in Python files.
        
        Returns:
            List of legacy SQL errors
        """
        errors = []
        python_files = list(self.project_root.rglob("*.py"))
        
        # Patterns that indicate raw SQL usage
        raw_sql_patterns = [
            (r'\.execute\s*\(\s*["\']SELECT.*?["\']', 'Use ORM query methods'),
            (r'\.execute\s*\(\s*["\']INSERT.*?["\']', 'Use ORM model.save() or session.add()'),
            (r'\.execute\s*\(\s*["\']UPDATE.*?["\']', 'Use ORM model.update() or instance modification'),
            (r'\.execute\s*\(\s*["\']DELETE.*?["\']', 'Use ORM model.delete() or session.delete()'),
            (r'text\s*\(\s*["\']SELECT.*?["\']', 'Use ORM query relationships'),
            (r'text\s*\(\s*["\']INSERT.*?["\']', 'Use ORM model creation'),
        ]
        
        for py_file in python_files:
            # Skip specific files that legitimately need raw SQL
            if any(skip in str(py_file) for skip in ['migrations', 'tools/database', 'seed_data']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern, suggestion in raw_sql_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
                    for match in matches:
                        query_snippet = match.group(0)[:100]
                        errors.append(LegacySQLError(
                            query=f"{py_file}:{query_snippet}",
                            suggested_orm_method=suggestion
                        ))
                        
            except (OSError, UnicodeDecodeError):
                continue
                
        return errors
    
    def detect_hardcoded_config(self) -> List[ConfigurationLegacyError]:
        """
        Detect hardcoded configuration values.
        
        Returns:
            List of configuration legacy errors
        """
        errors = []
        python_files = list(self.project_root.rglob("*.py"))
        
        # Patterns for hardcoded configuration
        config_patterns = [
            (r'SECRET_KEY\s*=\s*["\'][^"\']+["\']', 'SECRET_KEY'),
            (r'DEBUG\s*=\s*True', 'DEBUG'),
            (r'host\s*=\s*["\']localhost["\']', 'HOST'),
            (r'port\s*=\s*[0-9]+(?![.])', 'PORT'),
            (r'database\s*=\s*["\'][^"\']+["\']', 'DATABASE_URL'),
        ]
        
        for py_file in python_files:
            # Skip test files and tools
            if any(skip in str(py_file) for skip in ['test_', '_test', 'tools/', 'scripts/']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern, config_key in config_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Skip if it's already using environment variables
                        if 'os.environ' in match.group(0) or 'getenv' in match.group(0):
                            continue
                            
                        hardcoded_value = match.group(0)
                        errors.append(ConfigurationLegacyError(
                            config_key=config_key,
                            hardcoded_value=f"{py_file}: {hardcoded_value}"
                        ))
                        
            except (OSError, UnicodeDecodeError):
                continue
                
        return errors
    
    def detect_manual_form_definitions(self) -> List[str]:
        """
        Detect manual form class definitions instead of dynamic generation.
        
        Returns:
            List of warnings for manual form definitions
        """
        warnings = []
        form_files = list(self.project_root.rglob("**/forms/**/*.py"))
        
        for form_file in form_files:
            # Skip base forms and builders (these are allowed)
            if any(allowed in str(form_file) for allowed in ['base_forms.py', 'builders.py']):
                continue
                
            try:
                with open(form_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for manual form class definitions
                form_class_pattern = r'class\s+(\w+Form)\s*\(\s*FlaskForm\s*\):'
                matches = re.finditer(form_class_pattern, content)
                
                for match in matches:
                    form_class = match.group(1)
                    warnings.append(
                        f"Manual form definition in {form_file}: {form_class} "
                        f"- Consider using dynamic form builders (ADR-008)"
                    )
                    
            except (OSError, UnicodeDecodeError):
                continue
                
        return warnings
    
    def detect_duplicated_crud_logic(self) -> List[str]:
        """
        Detect duplicated CRUD logic in route handlers.
        
        Returns:
            List of warnings for duplicated route logic
        """
        warnings = []
        route_files = list(self.project_root.rglob("**/routes/**/*.py"))
        
        # Common CRUD patterns that might be duplicated
        crud_patterns = [
            r'\.get_or_404\(',
            r'request\.method\s*==\s*["\']POST["\']',
            r'form\.validate_on_submit\(\)',
            r'db\.session\.add\(',
            r'db\.session\.commit\(\)',
            r'flash\(',
            r'redirect\(url_for\(',
        ]
        
        pattern_counts = {}
        
        for route_file in route_files:
            try:
                with open(route_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in crud_patterns:
                    matches = len(re.findall(pattern, content))
                    if matches > 0:
                        key = f"{route_file.name}:{pattern}"
                        pattern_counts[key] = pattern_counts.get(key, 0) + matches
                        
            except (OSError, UnicodeDecodeError):
                continue
        
        # Identify files with high pattern repetition
        for key, count in pattern_counts.items():
            if count > 5:  # Threshold for potential duplication
                file_name, pattern = key.split(':', 1)
                warnings.append(
                    f"Potential CRUD duplication in {file_name}: {pattern} appears {count} times "
                    f"- Consider using base handlers (ADR-008)"
                )
                
        return warnings
    
    def run_full_scan(self) -> Dict[str, Any]:
        """
        Run comprehensive legacy pattern detection.
        
        Returns:
            Dictionary containing all detected violations and statistics
        """
        print("🔍 Running comprehensive legacy pattern detection...")
        
        # Detect template violations
        template_errors = self.detect_template_violations()
        
        # Detect SQL violations  
        sql_errors = self.detect_raw_sql_patterns()
        
        # Detect configuration violations
        config_errors = self.detect_hardcoded_config()
        
        # Detect potential issues (warnings)
        form_warnings = self.detect_manual_form_definitions()
        crud_warnings = self.detect_duplicated_crud_logic()
        
        all_errors = template_errors + sql_errors + config_errors
        all_warnings = form_warnings + crud_warnings
        
        return {
            "status": "violations_found" if all_errors else "compliant",
            "total_violations": len(all_errors),
            "total_warnings": len(all_warnings),
            "template_violations": len(template_errors),
            "sql_violations": len(sql_errors),
            "config_violations": len(config_errors),
            "errors": [str(error) for error in all_errors],
            "warnings": all_warnings,
            "compliance_percentage": self._calculate_compliance_percentage(all_errors, all_warnings)
        }
    
    def _calculate_compliance_percentage(self, errors: List, warnings: List) -> float:
        """Calculate overall compliance percentage."""
        total_issues = len(errors) + len(warnings)
        if total_issues == 0:
            return 100.0
            
        # Errors are weighted more heavily than warnings
        error_weight = 1.0
        warning_weight = 0.3
        
        total_weighted = len(errors) * error_weight + len(warnings) * warning_weight
        max_score = 100.0
        
        compliance = max(0, 100 - (total_weighted * 10))  # Each issue reduces score
        return round(compliance, 1)


def main():
    """Main entry point for legacy pattern detection."""
    parser = argparse.ArgumentParser(
        description="Detect and enforce legacy pattern elimination (ADR-010)"
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors (loud failure mode)'
    )
    parser.add_argument(
        '--directory',
        type=str,
        default='.',
        help='Directory to scan for legacy patterns'
    )
    parser.add_argument(
        '--fail-fast',
        action='store_true',
        help='Stop on first violation found'
    )
    
    args = parser.parse_args()
    
    detector = LegacyPatternDetector(args.directory)
    results = detector.run_full_scan()
    
    # Report results
    print(f"\n📊 Legacy Pattern Detection Results:")
    print(f"Status: {results['status'].upper()}")
    print(f"Compliance: {results['compliance_percentage']}%")
    print(f"Violations: {results['total_violations']}")
    print(f"Warnings: {results['total_warnings']}")
    
    if results['errors']:
        print("\n🔴 CRITICAL VIOLATIONS (Loud Failures):")
        for i, error in enumerate(results['errors'], 1):
            print(f"\n{i}. {error}")
            if args.fail_fast:
                print("\n💥 FAIL FAST: Stopping on first violation")
                sys.exit(1)
    
    if results['warnings']:
        print("\n⚠️  WARNINGS:")
        for i, warning in enumerate(results['warnings'], 1):
            print(f"{i}. {warning}")
    
    if results['status'] == 'compliant':
        print("\n✅ All legacy patterns eliminated! ADR-010 compliance achieved.")
        sys.exit(0)
    else:
        print(f"\n❌ {results['total_violations']} critical violations found.")
        print("🚨 LEGACY CODE ELIMINATION REQUIRED")
        
        if args.strict and results['warnings']:
            print("⚠️  Treating warnings as errors in strict mode")
            sys.exit(1)
        elif results['errors']:
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()