"""Test suite for refactored services following CLAUDE.MD principles."""
import pytest
from app.models import db
from app.main import create_app
from app.services import DisplayService, SearchService, SerializationService, MetadataService
from app.models.task import Task
from app.models.opportunity import Opportunity
from app.models.enums import TaskStatus, Priority, OpportunityStage
from app.utils.task_utils import can_task_start, get_completion_percentage
from app.utils.opportunity_utils import calculate_priority_by_value, get_stage_choices
from app.exceptions import ValidationError, NotFoundError


@pytest.fixture
def app():
    """Create app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()


class TestEnums:
    """Test enum replacements for magic strings."""

    def test_task_status_enum(self):
        """Verify TaskStatus enum values."""
        assert TaskStatus.TODO == "todo"
        assert TaskStatus.IN_PROGRESS == "in-progress"
        assert TaskStatus.COMPLETE == "complete"

    def test_priority_enum(self):
        """Verify Priority enum values."""
        assert Priority.HIGH == "high"
        assert Priority.MEDIUM == "medium"
        assert Priority.LOW == "low"

    def test_opportunity_stage_enum(self):
        """Verify OpportunityStage enum values."""
        assert OpportunityStage.PROSPECT == "prospect"
        assert OpportunityStage.QUALIFIED == "qualified"
        assert OpportunityStage.CLOSED_WON == "closed-won"


class TestUtils:
    """Test utility functions following single responsibility."""

    def test_calculate_priority_by_value(self):
        """Test priority calculation based on value."""
        assert calculate_priority_by_value(None) == "low"
        assert calculate_priority_by_value(5000) == "low"
        assert calculate_priority_by_value(10000) == "medium"
        assert calculate_priority_by_value(50000) == "high"
        assert calculate_priority_by_value(100000) == "high"

    def test_get_stage_choices(self):
        """Test stage choices are properly defined."""
        stages = get_stage_choices()
        assert "prospect" in stages
        assert "closed-won" in stages
        assert stages["prospect"]["label"] == "Prospect"

    def test_can_task_start(self, app):
        """Test task dependency logic."""
        with app.app_context():
            # Single task can always start
            single_task = Task(task_type="single")
            assert can_task_start(single_task) == True

            # Child task with parallel dependency can start
            child_task = Task(task_type="child", dependency_type="parallel")
            assert can_task_start(child_task) == True


class TestServices:
    """Test service layer following CLAUDE.MD principles."""

    def test_display_service(self, app):
        """Test DisplayService extracts display logic."""
        with app.app_context():
            assert DisplayService.get_display_name(Task) == "Task"
            assert DisplayService.get_display_name_plural(Task) == "Tasks"

    def test_metadata_service(self, app):
        """Test MetadataService handles field metadata."""
        with app.app_context():
            metadata = MetadataService.get_field_metadata(Task)
            assert isinstance(metadata, dict)
            # Verify single responsibility - only metadata
            assert "description" in metadata

    def test_serialization_service(self, app):
        """Test SerializationService handles model serialization."""
        with app.app_context():
            task = Task(description="Test task", status=TaskStatus.TODO)
            db.session.add(task)
            db.session.commit()

            serialized = SerializationService.serialize_model(task)
            assert isinstance(serialized, dict)
            assert serialized["description"] == "Test task"
            assert serialized["status"] == TaskStatus.TODO


class TestModelRefactoring:
    """Test model refactoring - pure data models."""

    def test_task_model_size(self):
        """Verify Task model is under 200 lines."""
        import inspect
        import app.models.task as task_module
        source = inspect.getsource(task_module.Task)
        lines = source.count('\n')
        assert lines < 200, f"Task model is {lines} lines (should be < 200)"

    def test_opportunity_model_size(self):
        """Verify Opportunity model is under 150 lines."""
        import inspect
        import app.models.opportunity as opp_module
        source = inspect.getsource(opp_module.Opportunity)
        lines = source.count('\n')
        assert lines < 150, f"Opportunity model is {lines} lines (should be < 150)"

    def test_models_have_no_business_logic(self, app):
        """Verify models delegate to utils/services."""
        with app.app_context():
            task = Task(description="Test")
            # These should delegate to utils
            assert hasattr(task, 'can_start')
            assert hasattr(task, 'completion_percentage')

            opp = Opportunity(name="Test", value=10000)
            # These should delegate to utils
            assert hasattr(opp, 'calculated_priority')
            assert hasattr(opp, 'deal_age')


class TestCLAUDEMDCompliance:
    """Test CLAUDE.MD principles are followed."""

    def test_no_mutable_defaults(self):
        """Verify no mutable default arguments."""
        import app.utils.task_utils as task_utils
        import app.utils.opportunity_utils as opp_utils
        import inspect

        # Check all functions in utils
        for module in [task_utils, opp_utils]:
            for name, func in inspect.getmembers(module, inspect.isfunction):
                sig = inspect.signature(func)
                for param in sig.parameters.values():
                    if param.default not in (inspect.Parameter.empty, None, 0, "", False, True):
                        # Check if default is mutable
                        assert not isinstance(param.default, (list, dict, set)), \
                            f"{name} has mutable default: {param.default}"

    def test_functions_under_50_lines(self):
        """Verify all functions are under 50 lines."""
        import app.utils.task_utils as task_utils
        import app.utils.opportunity_utils as opp_utils
        import inspect

        for module in [task_utils, opp_utils]:
            for name, func in inspect.getmembers(module, inspect.isfunction):
                source = inspect.getsource(func)
                lines = source.count('\n')
                assert lines < 50, f"{name} is {lines} lines (should be < 50)"

    def test_single_responsibility(self):
        """Verify services have single responsibility."""
        from app.services.display_service import DisplayService
        from app.services.search_service import SearchService

        # DisplayService should only handle display
        display_methods = [m for m in dir(DisplayService) if not m.startswith('_')]
        for method in display_methods:
            assert 'display' in method.lower() or 'name' in method.lower(), \
                f"DisplayService.{method} violates single responsibility"

        # SearchService should only handle search
        search_methods = [m for m in dir(SearchService) if not m.startswith('_')]
        for method in search_methods:
            assert 'search' in method.lower() or 'format' in method.lower(), \
                f"SearchService.{method} violates single responsibility"


class TestExceptionHandling:
    """Test proper exception handling - fail loudly."""

    def test_custom_exceptions_exist(self):
        """Verify custom exceptions are defined."""
        from app.exceptions import (
            CRMException, ValidationError, NotFoundError,
            DuplicateError, InvalidStateError
        )

        # All should inherit from CRMException
        assert issubclass(ValidationError, CRMException)
        assert issubclass(NotFoundError, CRMException)
        assert issubclass(DuplicateError, CRMException)
        assert issubclass(InvalidStateError, CRMException)

    def test_exceptions_have_clear_messages(self):
        """Verify exceptions provide clear messages."""
        error = ValidationError("Email already exists")
        assert str(error) == "Email already exists"

        error = NotFoundError("Task with ID 123 not found")
        assert "123" in str(error)
        assert "not found" in str(error).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])