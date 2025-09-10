"""
JSON schemas for validating LLM extraction outputs.
These ensure consistent structure and data quality from LLM responses.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass


# JSON Schema for meeting extraction validation
MEETING_EXTRACTION_SCHEMA = {
    "type": "object",
    "required": [
        "attendees",
        "technologies_mentioned",
        "action_items",
        "key_decisions",
        "sentiment_analysis",
        "topics_discussed",
        "summary",
    ],
    "properties": {
        "attendees": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "role": {"type": "string"},
                    "sentiment": {
                        "type": "string",
                        "enum": ["positive", "neutral", "negative"],
                    },
                },
            },
        },
        "technologies_mentioned": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
        },
        "action_items": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["task"],
                "properties": {
                    "task": {"type": "string", "minLength": 5},
                    "assignee": {"type": "string"},
                    "deadline": {
                        "oneOf": [
                            {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
                            {"type": "null"},
                        ]
                    },
                },
            },
        },
        "key_decisions": {"type": "array", "items": {"type": "string", "minLength": 5}},
        "sentiment_analysis": {
            "type": "object",
            "required": ["overall"],
            "properties": {
                "overall": {
                    "type": "string",
                    "enum": ["positive", "neutral", "negative"],
                },
                "concerns": {"type": "array", "items": {"type": "string"}},
            },
        },
        "topics_discussed": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
        },
        "summary": {"type": "string", "minLength": 10, "maxLength": 500},
    },
}


@dataclass
class ValidationResult:
    """Result of schema validation"""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    cleaned_data: Optional[Dict[str, Any]] = None


class ExtractionValidator:
    """Validator for LLM extraction results"""

    def __init__(self):
        self.schemas = {"meeting": MEETING_EXTRACTION_SCHEMA}

    def validate_meeting_extraction(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate meeting extraction data against schema

        Args:
            data: Extracted data to validate

        Returns:
            ValidationResult with validation status and cleaned data
        """

        errors = []
        warnings = []

        try:
            # Basic type and structure validation
            if not isinstance(data, dict):
                return ValidationResult(
                    is_valid=False, errors=["Data must be a dictionary"], warnings=[]
                )

            # Validate required fields
            required_fields = [
                "attendees",
                "technologies_mentioned",
                "action_items",
                "key_decisions",
                "sentiment_analysis",
                "topics_discussed",
                "summary",
            ]

            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                errors.append(f"Missing required fields: {', '.join(missing_fields)}")

            # Clean and validate each field
            cleaned_data = {}

            # Attendees validation
            attendees = data.get("attendees", [])
            if not isinstance(attendees, list):
                errors.append("Attendees must be a list")
                attendees = []

            cleaned_attendees = []
            for i, attendee in enumerate(attendees):
                if isinstance(attendee, dict) and attendee.get("name"):
                    clean_attendee = {
                        "name": str(attendee["name"]).strip(),
                        "role": str(attendee.get("role", "")).strip() or None,
                        "sentiment": self._validate_sentiment(
                            attendee.get("sentiment")
                        ),
                    }
                    cleaned_attendees.append(clean_attendee)
                else:
                    warnings.append(f"Invalid attendee at index {i}, skipping")

            cleaned_data["attendees"] = cleaned_attendees

            # Technologies validation
            technologies = data.get("technologies_mentioned", [])
            if not isinstance(technologies, list):
                warnings.append("Technologies must be a list, converting")
                technologies = []

            cleaned_data["technologies_mentioned"] = [
                str(tech).strip()
                for tech in technologies
                if isinstance(tech, str) and tech.strip()
            ]

            # Action items validation
            action_items = data.get("action_items", [])
            if not isinstance(action_items, list):
                errors.append("Action items must be a list")
                action_items = []

            cleaned_actions = []
            for i, action in enumerate(action_items):
                if isinstance(action, dict) and action.get("task"):
                    clean_action = {
                        "task": str(action["task"]).strip(),
                        "assignee": str(action.get("assignee", "")).strip() or None,
                        "deadline": self._validate_date(action.get("deadline")),
                    }
                    if len(clean_action["task"]) >= 5:
                        cleaned_actions.append(clean_action)
                    else:
                        warnings.append(f"Action item {i} too short, skipping")
                else:
                    warnings.append(f"Invalid action item at index {i}, skipping")

            cleaned_data["action_items"] = cleaned_actions

            # Key decisions validation
            decisions = data.get("key_decisions", [])
            if not isinstance(decisions, list):
                warnings.append("Key decisions must be a list, converting")
                decisions = []

            cleaned_data["key_decisions"] = [
                str(decision).strip()
                for decision in decisions
                if isinstance(decision, str) and len(decision.strip()) >= 5
            ]

            # Sentiment analysis validation
            sentiment = data.get("sentiment_analysis", {})
            if not isinstance(sentiment, dict):
                errors.append("Sentiment analysis must be an object")
                sentiment = {}

            cleaned_data["sentiment_analysis"] = {
                "overall": self._validate_sentiment(sentiment.get("overall")),
                "concerns": [
                    str(concern).strip()
                    for concern in sentiment.get("concerns", [])
                    if isinstance(concern, str) and concern.strip()
                ],
            }

            # Topics validation
            topics = data.get("topics_discussed", [])
            if not isinstance(topics, list):
                warnings.append("Topics must be a list, converting")
                topics = []

            cleaned_data["topics_discussed"] = [
                str(topic).strip()
                for topic in topics
                if isinstance(topic, str) and topic.strip()
            ]

            # Summary validation
            summary = data.get("summary", "")
            if not isinstance(summary, str):
                warnings.append("Summary must be a string, converting")
                summary = str(summary)

            summary = summary.strip()
            if len(summary) < 10:
                warnings.append("Summary is very short, may not be meaningful")
            elif len(summary) > 500:
                warnings.append("Summary is long, truncating")
                summary = summary[:500] + "..."

            cleaned_data["summary"] = summary

            # Determine if validation passed
            is_valid = len(errors) == 0

            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                cleaned_data=cleaned_data if is_valid else None,
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False, errors=[f"Validation error: {str(e)}"], warnings=[]
            )

    def _validate_sentiment(self, sentiment: Any) -> str:
        """Validate and normalize sentiment value"""
        if isinstance(sentiment, str):
            sentiment_lower = sentiment.lower()
            if sentiment_lower in ["positive", "neutral", "negative"]:
                return sentiment_lower
        raise ValueError(
            f"Invalid sentiment value: {sentiment}. Must be one of: positive, neutral, negative"
        )

    def _validate_date(self, date_str: Any) -> Optional[str]:
        """Validate and normalize date string"""
        if not date_str or date_str == "null":
            return None

        if isinstance(date_str, str):
            date_str = date_str.strip()
            # Basic YYYY-MM-DD validation
            if len(date_str) == 10 and date_str.count("-") == 2:
                try:
                    year, month, day = date_str.split("-")
                    if (
                        len(year) == 4
                        and year.isdigit()
                        and len(month) == 2
                        and month.isdigit()
                        and len(day) == 2
                        and day.isdigit()
                    ):
                        return date_str
                except ValueError:
                    pass

        return None  # Invalid date format


# Singleton instance
_validator: Optional[ExtractionValidator] = None


def get_extraction_validator() -> ExtractionValidator:
    """Get the singleton extraction validator instance"""
    global _validator
    if _validator is None:
        _validator = ExtractionValidator()
    return _validator
