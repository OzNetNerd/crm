#!/usr/bin/env python3
"""
Simple test script to verify task forms work correctly after DRY refactoring.
Tests form instantiation and field generation without requiring full web app.
"""
import sys
import os

# Add project root to Python path
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_form_imports():
    """Test that all form classes can be imported successfully"""
    try:
        from app.forms import TaskForm, QuickTaskForm, ChildTaskForm, MultiTaskForm
        print("✅ All form classes imported successfully")
        return True
    except Exception as e:
        print(f"❌ Form import failed: {e}")
        return False

def test_form_instantiation():
    """Test that forms can be instantiated without errors"""
    try:
        from services.crm.main import create_app
        app = create_app()
        
        with app.app_context():
            with app.test_request_context():
                from app.forms import TaskForm, QuickTaskForm, ChildTaskForm, MultiTaskForm
            
            # Test TaskForm
            task_form = TaskForm()
            print(f"✅ TaskForm instantiated with fields: {list(task_form._fields.keys())}")
            
            # Test QuickTaskForm  
            quick_form = QuickTaskForm()
            print(f"✅ QuickTaskForm instantiated with fields: {list(quick_form._fields.keys())}")
            
            # Test ChildTaskForm
            child_form = ChildTaskForm()
            print(f"✅ ChildTaskForm instantiated with fields: {list(child_form._fields.keys())}")
            
            # Test MultiTaskForm
            multi_form = MultiTaskForm()
            print(f"✅ MultiTaskForm instantiated with fields: {list(multi_form._fields.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ Form instantiation failed: {e}")
        return False

def test_field_choices():
    """Test that SelectField choices are properly generated from model metadata"""
    try:
        from services.crm.main import create_app
        app = create_app()
        
        with app.app_context():
            with app.test_request_context():
            from app.forms import TaskForm
            
            form = TaskForm()
            
            # Test priority field choices
            priority_choices = form.priority.choices
            print(f"✅ Priority choices: {priority_choices}")
            
            # Test status field choices  
            status_choices = form.status.choices
            print(f"✅ Status choices: {status_choices}")
            
            # Test next_step_type field choices
            next_step_choices = form.next_step_type.choices
            print(f"✅ Next step type choices: {next_step_choices}")
            
            # Verify choices aren't empty and contain expected values
            assert len(priority_choices) > 0, "Priority choices should not be empty"
            assert len(status_choices) > 0, "Status choices should not be empty"
            assert len(next_step_choices) > 0, "Next step choices should not be empty"
            
            # Look for expected values (case insensitive check)
            priority_values = [choice[0].lower() for choice in priority_choices if choice[0]]
            assert 'high' in priority_values or 'medium' in priority_values or 'low' in priority_values
            
            print("✅ All field choices validated successfully")
        
        return True
    except Exception as e:
        print(f"❌ Field choices test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing task forms after DRY refactoring...")
    print("=" * 50)
    
    tests = [
        test_form_imports,
        test_form_instantiation, 
        test_field_choices
    ]
    
    results = []
    for test in tests:
        print(f"\n🔍 Running {test.__name__}:")
        results.append(test())
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} tests passed! Forms refactoring successful.")
        return 0
    else:
        print(f"❌ {total - passed} of {total} tests failed.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)