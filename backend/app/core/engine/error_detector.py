"""
Error detection and classification utilities.
Uses Levenshtein distance and detailed edit distance analysis.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
from enum import Enum


class ErrorType(str, Enum):
    """Classification of typing errors."""
    SUBSTITUTION = "substitution"      # Typed wrong character
    INSERTION = "insertion"            # Typed extra character
    DELETION = "deletion"              # Skipped a character
    TRANSPOSITION = "transposition"    # Swapped adjacent characters


@dataclass
class KeystrokeError:
    """Detailed record of a single error event."""
    error_type: ErrorType
    position: int                       # Position in expected text
    expected_char: str
    actual_char: str
    timestamp_ms: int                   # Milliseconds from test start
    context_before: str                 # 5 chars before
    context_after: str                  # 5 chars after


@dataclass
class ErrorAnalysis:
    """Comprehensive error analysis for a typing session."""
    total_errors: int
    errors_by_type: Dict[str, int]      # Count per error type
    error_details: List[KeystrokeError]
    error_positions: List[int]          # Positions of all errors
    levenshtein_distance: int           # Total edit distance


class LevenshteinCalculator:
    """
    Calculates Levenshtein distance and identifies edit operations.
    """
    
    @staticmethod
    def distance(s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance (minimum edits to transform s1 → s2).
        
        Args:
            s1: Expected text
            s2: Typed text
            
        Returns:
            Edit distance (0 = identical)
        """
        if len(s1) == 0:
            return len(s2)
        if len(s2) == 0:
            return len(s1)
        
        # Create distance matrix
        rows = len(s1) + 1
        cols = len(s2) + 1
        distance = [[0] * cols for _ in range(rows)]
        
        # Initialize first row/column
        for i in range(1, rows):
            distance[i][0] = i
        for j in range(1, cols):
            distance[0][j] = j
        
        # Calculate distances
        for i in range(1, rows):
            for j in range(1, cols):
                if s1[i - 1] == s2[j - 1]:
                    distance[i][j] = distance[i - 1][j - 1]
                else:
                    distance[i][j] = 1 + min(
                        distance[i - 1][j],      # Deletion
                        distance[i][j - 1],      # Insertion
                        distance[i - 1][j - 1]   # Substitution
                    )
        
        return distance[rows - 1][cols - 1]
    
    @staticmethod
    def get_operations(s1: str, s2: str) -> List[Tuple[str, int, str, str]]:
        """
        Get the sequence of edit operations to transform s1 → s2.
        
        Returns:
            List of (operation, position, expected_char, actual_char)
        """
        if len(s1) == 0:
            return [("insertion", i, "", c) for i, c in enumerate(s2)]
        if len(s2) == 0:
            return [("deletion", i, c, "") for i, c in enumerate(s1)]
        
        # Build distance matrix with traceback
        rows = len(s1) + 1
        cols = len(s2) + 1
        distance = [[0] * cols for _ in range(rows)]
        
        for i in range(1, rows):
            distance[i][0] = i
        for j in range(1, cols):
            distance[0][j] = j
        
        for i in range(1, rows):
            for j in range(1, cols):
                if s1[i - 1] == s2[j - 1]:
                    distance[i][j] = distance[i - 1][j - 1]
                else:
                    distance[i][j] = 1 + min(
                        distance[i - 1][j],
                        distance[i][j - 1],
                        distance[i - 1][j - 1]
                    )
        
        # Traceback to find operations
        operations = []
        i, j = rows - 1, cols - 1
        
        while i > 0 or j > 0:
            if i > 0 and j > 0 and s1[i - 1] == s2[j - 1]:
                i -= 1
                j -= 1
            elif i > 0 and j > 0 and distance[i - 1][j - 1] < distance[i - 1][j] and distance[i - 1][j - 1] < distance[i][j - 1]:
                # Substitution
                operations.append(("substitution", i - 1, s1[i - 1], s2[j - 1]))
                i -= 1
                j -= 1
            elif j > 0 and distance[i][j - 1] < distance[i - 1][j]:
                # Insertion
                operations.append(("insertion", i, "", s2[j - 1]))
                j -= 1
            elif i > 0:
                # Deletion
                operations.append(("deletion", i - 1, s1[i - 1], ""))
                i -= 1
            else:
                # Insertion (at beginning)
                operations.append(("insertion", 0, "", s2[j - 1]))
                j -= 1
        
        return list(reversed(operations))


class ErrorClassifier:
    """
    Classifies and categorizes typing errors in detail.
    """
    
    @staticmethod
    def analyze(expected_text: str, typed_text: str, keystroke_events: List[Dict]) -> ErrorAnalysis:
        """
        Perform comprehensive error analysis on a typing session.
        
        Args:
            expected_text: The text user should have typed
            typed_text: What user actually typed
            keystroke_events: List of keystroke events with timestamps
            
        Returns:
            ErrorAnalysis with detailed error breakdown
        """
        calculator = LevenshteinCalculator()
        
        # Get edit operations
        operations = calculator.get_operations(expected_text, typed_text)
        
        # Build error details
        error_details = []
        errors_by_type = {e.value: 0 for e in ErrorType}
        error_positions = []
        
        # Map keystroke events for quick lookup
        keystroke_map = {i: e for i, e in enumerate(keystroke_events)}
        
        for operation, position, expected_char, actual_char in operations:
            error_type = ErrorType(operation)
            errors_by_type[error_type.value] += 1
            error_positions.append(position)
            
            # Get timing from keystroke event
            timestamp_ms = keystroke_map.get(position, {}).get("timestamp_ms", 0)
            
            # Get context
            context_before = expected_text[max(0, position - 5):position]
            context_after = expected_text[position:min(len(expected_text), position + 5)]
            
            error_details.append(KeystrokeError(
                error_type=error_type,
                position=position,
                expected_char=expected_char,
                actual_char=actual_char,
                timestamp_ms=timestamp_ms,
                context_before=context_before,
                context_after=context_after
            ))
        
        return ErrorAnalysis(
            total_errors=len(error_details),
            errors_by_type=errors_by_type,
            error_details=error_details,
            error_positions=error_positions,
            levenshtein_distance=calculator.distance(expected_text, typed_text)
        )
    
    @staticmethod
    def get_character_classification(
        expected_text: str,
        typed_text: str
    ) -> Dict[int, Dict]:
        """
        Classify each character in typed text as correct/incorrect.
        
        Returns:
            Dict mapping position → {is_correct, expected_char, actual_char, error_type}
        """
        result = {}
        
        for i in range(len(typed_text)):
            if i < len(expected_text):
                is_correct = typed_text[i] == expected_text[i]
                result[i] = {
                    "is_correct": is_correct,
                    "expected_char": expected_text[i],
                    "actual_char": typed_text[i],
                    "error_type": "none" if is_correct else "substitution"
                }
            else:
                # Extra character
                result[i] = {
                    "is_correct": False,
                    "expected_char": "",
                    "actual_char": typed_text[i],
                    "error_type": "insertion"
                }
        
        # Mark missing characters
        for i in range(len(typed_text), len(expected_text)):
            # These are handled via deletion in error analysis
            pass
        
        return result
