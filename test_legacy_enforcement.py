#!/usr/bin/env python3
"""
Test Script for Legacy Code Enforcement
ADR-010: Legacy Code Elimination Strategy with Loud Failure Enforcement

Tests that legacy patterns trigger loud failures as expected.
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.legacy.enforcement import (
    LegacyPatternDetector, 
    LegacyCodeViolationError,
    LegacyCodeEnforcer,
    get_relationship_owners_legacy,
    get_account_team_legacy,
    get_stakeholders_legacy
)


def test_legacy_sql_methods():
    """Test that legacy SQL method triggers loud failure."""
    print("🧪 Testing legacy SQL method loud failure...")
    
    try:
        get_relationship_owners_legacy()
        print("❌ FAILED: Legacy method should have triggered loud failure!")
        return False
    except LegacyCodeViolationError as e:
        print("✅ SUCCESS: Legacy SQL method triggered loud failure")
        print(f"   Error: {str(e)[:100]}...")
        return True
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False


def test_itcss_architecture_detection():
    """Test that ITCSS architecture detection works."""
    print("🧪 Testing ITCSS architecture detection...")
    
    try:
        LegacyPatternDetector.detect_itcss_architecture_usage("app/static/css/01-settings/")
        print("❌ FAILED: ITCSS detection should have triggered loud failure!")
        return False
    except LegacyCodeViolationError as e:
        print("✅ SUCCESS: ITCSS architecture detection triggered loud failure")
        print(f"   Error: {str(e)[:100]}...")
        return True
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False


def test_javascript_template_detection():
    """Test that JavaScript in templates detection works.""" 
    print("🧪 Testing JavaScript in templates detection...")
    
    try:
        LegacyPatternDetector.detect_javascript_in_templates("test_template.html")
        print("❌ FAILED: JavaScript template detection should have triggered loud failure!")
        return False
    except LegacyCodeViolationError as e:
        print("✅ SUCCESS: JavaScript template detection triggered loud failure")
        print(f"   Error: {str(e)[:100]}...")
        return True
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False


def test_hardcoded_config_detection():
    """Test that hardcoded configuration detection works."""
    print("🧪 Testing hardcoded configuration detection...")
    
    try:
        LegacyPatternDetector.detect_hardcoded_configuration("DATABASE_URL", "sqlite:///hardcoded.db")
        print("❌ FAILED: Hardcoded config detection should have triggered loud failure!")
        return False
    except LegacyCodeViolationError as e:
        print("✅ SUCCESS: Hardcoded configuration detection triggered loud failure") 
        print(f"   Error: {str(e)[:100]}...")
        return True
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False


def test_manual_dict_construction_detection():
    """Test that manual dictionary construction detection works."""
    print("🧪 Testing manual dictionary construction detection...")
    
    try:
        LegacyPatternDetector.detect_manual_dictionary_construction("test_route")
        print("❌ FAILED: Manual dict construction detection should have triggered loud failure!")
        return False
    except LegacyCodeViolationError as e:
        print("✅ SUCCESS: Manual dictionary construction detection triggered loud failure")
        print(f"   Error: {str(e)[:100]}...")
        return True
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False


def test_non_restful_api_detection():
    """Test that non-RESTful API detection works."""
    print("🧪 Testing non-RESTful API detection...")
    
    try:
        LegacyPatternDetector.detect_non_restful_api_patterns("/api/notes/entity/company/123")
        print("❌ FAILED: Non-RESTful API detection should have triggered loud failure!")
        return False
    except LegacyCodeViolationError as e:
        print("✅ SUCCESS: Non-RESTful API detection triggered loud failure")
        print(f"   Error: {str(e)[:100]}...")
        return True
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False


def run_all_tests():
    """Run all legacy enforcement tests."""
    print("🚀 Starting ADR-010 Legacy Code Enforcement Tests")
    print("=" * 60)
    
    tests = [
        test_legacy_sql_methods,
        test_itcss_architecture_detection,
        test_javascript_template_detection,
        test_hardcoded_config_detection,
        test_manual_dict_construction_detection,
        test_non_restful_api_detection,
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ TEST FAILED with exception: {e}")
            print()
    
    print("=" * 60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! ADR-010 enforcement is working correctly.")
        print("✅ Legacy code patterns will trigger loud failures as expected.")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Legacy enforcement needs fixes.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)