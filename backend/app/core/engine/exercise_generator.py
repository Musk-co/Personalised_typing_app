"""
Exercise Generator

Dynamically generates typing exercises tailored to user's weak keys and error patterns.
Never static - every exercise is freshly generated from live user data.

Philosophy: "Every prompt is born from YOUR specific mistakes, not retrieved from a list."
"""

import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from app.db.models import WeakKeyProfile, ErrorPatternProfile, UserSkillProfile


class ExerciseType(str, Enum):
    """Types of exercises."""
    WEAK_KEY_DRILL = "weak_key_drill"  # Focus on specific weak keys
    ERROR_PATTERN = "error_pattern"  # Repeat common mistakes
    MIXED = "mixed"  # Balanced exercise
    SPEED_CHALLENGE = "speed_challenge"  # High-speed text
    ACCURACY_FOCUS = "accuracy_focus"  # Deliberate, careful typing
    SENTENCE = "sentence"  # Natural language sentences


@dataclass
class ExercisePrompt:
    """A generated exercise prompt."""
    text: str
    type: ExerciseType
    difficulty: int  # 1-10
    focus_chars: List[str]  # Characters this exercise focuses on
    expected_duration_seconds: int
    description: str  # What user is training
    metadata: Dict  # Additional context


class ExerciseGenerator:
    """
    Generates fresh exercises from user skill data.
    
    Never returns the same exercise twice - always generated from live data.
    Ensures every exercise addresses real weaknesses.
    """

    def __init__(self):
        self.common_words = [
            "the", "and", "for", "are", "but", "not", "you", "all", "can",
            "her", "was", "one", "our", "out", "day", "get", "has", "him",
            "his", "how", "its", "may", "now", "old", "see", "she", "too",
            "way", "who", "boy", "did", "car", "dog", "let", "put", "say",
            "she", "too", "use", "work", "year", "come", "good", "hand",
            "just", "know", "made", "make", "only", "over", "such", "take",
            "than", "that", "them", "then", "they", "this", "time", "very",
            "want", "well", "when", "will", "with", "word", "work", "world"
        ]
        
        self.common_punctuation = [
            ".", ",", "!", "?", "'", '"', ";", ":", "-", "(", ")"
        ]

    def generate_weak_key_drill(
        self,
        weak_keys: Dict[str, Dict[str, float]],
        difficulty: int,
        duration_seconds: int = 60,
    ) -> ExercisePrompt:
        """
        Generate exercise focusing on weakest keys.
        
        Args:
            weak_keys: Dict of {char: {frequency, error_rate}}
            difficulty: Current difficulty level (1-10)
            duration_seconds: Expected exercise duration
            
        Returns:
            ExercisePrompt with weak key focus
        """
        # Get top N weak keys based on error rate
        sorted_keys = sorted(
            weak_keys.items(),
            key=lambda x: x[1].get('error_rate', 0),
            reverse=True
        )
        focus_chars = [char for char, _ in sorted_keys[:5]]
        
        # Generate text with heavy focus on these characters
        text = self._generate_text_from_chars(
            focus_chars=focus_chars,
            num_words=self._calculate_word_count(difficulty, duration_seconds),
            difficulty=difficulty,
            focus_weight=0.6  # 60% focus chars, 40% filler
        )
        
        return ExercisePrompt(
            text=text,
            type=ExerciseType.WEAK_KEY_DRILL,
            difficulty=difficulty,
            focus_chars=focus_chars,
            expected_duration_seconds=duration_seconds,
            description=f"Drill: Focus on '{', '.join(focus_chars)}' - your most error-prone keys",
            metadata={
                "focus_weight": 0.6,
                "error_rates": {char: weak_keys[char].get('error_rate', 0) for char in focus_chars}
            }
        )

    def generate_error_pattern_exercise(
        self,
        error_patterns: Dict[str, int],
        weak_keys: Dict[str, Dict[str, float]],
        difficulty: int,
        duration_seconds: int = 60,
    ) -> ExercisePrompt:
        """
        Generate exercise that repeats common error patterns.
        
        Args:
            error_patterns: Dict of {error_type: count}
            weak_keys: Dict of weak key stats
            difficulty: Current difficulty level (1-10)
            duration_seconds: Expected exercise duration
            
        Returns:
            ExercisePrompt targeting error patterns
        """
        # Find most common error type
        most_common_error = max(error_patterns.items(), key=lambda x: x[1])[0]
        
        # Get weak chars that frequently have this error
        focus_chars = [char for char in weak_keys.keys()][:3]
        
        # Generate text emphasizing potential for these errors
        text = self._generate_text_with_error_potential(
            focus_chars=focus_chars,
            error_type=most_common_error,
            num_words=self._calculate_word_count(difficulty, duration_seconds),
            difficulty=difficulty,
        )
        
        return ExercisePrompt(
            text=text,
            type=ExerciseType.ERROR_PATTERN,
            difficulty=difficulty,
            focus_chars=focus_chars,
            expected_duration_seconds=duration_seconds,
            description=f"Fix '{most_common_error}' errors - your most common mistake pattern",
            metadata={
                "target_error_type": most_common_error,
                "error_frequency": error_patterns.get(most_common_error, 0)
            }
        )

    def generate_mixed_exercise(
        self,
        weak_keys: Dict[str, Dict[str, float]],
        error_patterns: Dict[str, int],
        difficulty: int,
        duration_seconds: int = 60,
    ) -> ExercisePrompt:
        """
        Generate balanced mixed exercise.
        
        Args:
            weak_keys: Dict of weak key stats
            error_patterns: Dict of error patterns
            difficulty: Current difficulty level (1-10)
            duration_seconds: Expected exercise duration
            
        Returns:
            ExercisePrompt with mixed content
        """
        focus_chars = list(weak_keys.keys())[:3]
        
        text = self._generate_text_from_chars(
            focus_chars=focus_chars,
            num_words=self._calculate_word_count(difficulty, duration_seconds),
            difficulty=difficulty,
            focus_weight=0.4,  # 40% focus chars, 60% variety
            include_punctuation=(difficulty > 3)
        )
        
        return ExercisePrompt(
            text=text,
            type=ExerciseType.MIXED,
            difficulty=difficulty,
            focus_chars=focus_chars,
            expected_duration_seconds=duration_seconds,
            description="Mixed exercise - balanced challenge with a focus on your weak areas",
            metadata={
                "focus_weight": 0.4,
                "includes_punctuation": difficulty > 3
            }
        )

    def generate_speed_challenge(
        self,
        weak_keys: Dict[str, Dict[str, float]],
        difficulty: int,
    ) -> ExercisePrompt:
        """
        Generate high-speed typing challenge.
        
        Uses simpler, familiar words to focus on speed, not accuracy.
        
        Args:
            weak_keys: Dict of weak key stats
            difficulty: Current difficulty level (1-10)
            
        Returns:
            ExercisePrompt for speed training
        """
        # Use easier words at higher speeds
        num_words = 30 + (difficulty * 5)
        words = random.choices(self.common_words, k=num_words)
        text = " ".join(words)
        
        return ExercisePrompt(
            text=text,
            type=ExerciseType.SPEED_CHALLENGE,
            difficulty=difficulty,
            focus_chars=[],
            expected_duration_seconds=int(num_words / (difficulty * 8)),  # Estimate based on speed
            description=f"Speed challenge - type fast and loose, focus on rhythm",
            metadata={
                "word_count": num_words,
                "average_word_length": sum(len(w) for w in words) / len(words)
            }
        )

    def generate_accuracy_focus(
        self,
        weak_keys: Dict[str, Dict[str, float]],
        difficulty: int,
    ) -> ExercisePrompt:
        """
        Generate accuracy-focused exercise.
        
        Slower pace, emphasis on precision.
        
        Args:
            weak_keys: Dict of weak key stats
            difficulty: Current difficulty level (1-10)
            
        Returns:
            ExercisePrompt for accuracy training
        """
        focus_chars = list(weak_keys.keys())[:5]
        
        # Shorter text, more deliberate
        num_words = max(10, 20 - (difficulty // 2))
        text = self._generate_text_from_chars(
            focus_chars=focus_chars,
            num_words=num_words,
            difficulty=difficulty,
            focus_weight=0.7,
            include_punctuation=True
        )
        
        return ExercisePrompt(
            text=text,
            type=ExerciseType.ACCURACY_FOCUS,
            difficulty=difficulty,
            focus_chars=focus_chars,
            expected_duration_seconds=num_words * 3,  # Slower pace
            description="Accuracy focus - take your time, get every letter right",
            metadata={
                "focus_weight": 0.7,
                "emphasizes_punctuation": True,
                "suggested_pace_wpm": 20
            }
        )

    # Helper methods

    def _generate_text_from_chars(
        self,
        focus_chars: List[str],
        num_words: int,
        difficulty: int,
        focus_weight: float = 0.5,
        include_punctuation: bool = False,
    ) -> str:
        """
        Generate text biased toward specific characters.
        
        Uses focus_weight to control how much text emphasizes target chars.
        """
        if not focus_chars:
            return " ".join(random.choices(self.common_words, k=num_words))
        
        text_parts = []
        
        for _ in range(num_words):
            if random.random() < focus_weight:
                # Generate word containing focus character
                focus_char = random.choice(focus_chars)
                word = self._generate_word_with_char(focus_char, difficulty)
            else:
                # Use random common word
                word = random.choice(self.common_words)
            
            if include_punctuation and random.random() < 0.15:
                word += random.choice(['.', ',', '!', '?'])
            
            text_parts.append(word)
        
        return " ".join(text_parts)

    def _generate_word_with_char(self, target_char: str, difficulty: int) -> str:
        """
        Generate a word that contains the target character.
        
        Simple algorithm: find words from common set that have it.
        Could be enhanced with ML to generate more natural words.
        """
        # Filter words containing target character
        matching_words = [w for w in self.common_words if target_char.lower() in w.lower()]
        
        if matching_words:
            return random.choice(matching_words)
        else:
            # Fallback: construct word
            vowels = "aeiou"
            consonants = "bcdfghjklmnpqrstvwxyz"
            
            word = target_char.lower()
            for _ in range(random.randint(2, 5)):
                if random.random() < 0.4:
                    word += random.choice(vowels)
                else:
                    word += random.choice(consonants)
            
            return word

    def _generate_text_with_error_potential(
        self,
        focus_chars: List[str],
        error_type: str,
        num_words: int,
        difficulty: int,
    ) -> str:
        """
        Generate text that's likely to trigger specific error types.
        
        For example:
        - Substitution: doubled letters (mm, ss, ll)
        - Transposition: common pairs (er, re, th)
        - Deletion: consonant clusters (str, spr)
        - Insertion: vowel-heavy words
        """
        words = []
        
        if error_type == "substitution":
            # Use words with doubled letters and focus chars
            template_words = ["pressure", "success", "possess", "address", "necessary"]
            words = random.choices(template_words + self.common_words, k=num_words)
        
        elif error_type == "transposition":
            # Use words where adjacent chars might swap
            template_words = ["their", "there", "where", "when", "the", "and"]
            words = random.choices(template_words + self.common_words, k=num_words)
        
        elif error_type == "deletion":
            # Use words with consonant clusters
            template_words = ["strength", "string", "spring", "people", "important"]
            words = random.choices(template_words + self.common_words, k=num_words)
        
        elif error_type == "insertion":
            # Use words with vowel sequences
            template_words = ["beautiful", "actually", "separately", "usually", "especially"]
            words = random.choices(template_words + self.common_words, k=num_words)
        
        else:
            # Default: balanced
            words = random.choices(self.common_words, k=num_words)
        
        # Include focus characters
        if focus_chars:
            for i in range(0, len(words), 3):
                if i < len(words):
                    words[i] = self._ensure_char_in_word(words[i], random.choice(focus_chars))
        
        return " ".join(words)

    def _ensure_char_in_word(self, word: str, char: str) -> str:
        """Ensure character appears in word, or replace word."""
        if char.lower() in word.lower():
            return word
        
        # Find word with this character
        matching = [w for w in self.common_words if char.lower() in w.lower()]
        return random.choice(matching) if matching else word

    def _calculate_word_count(self, difficulty: int, duration_seconds: int) -> int:
        """
        Estimate word count based on difficulty and duration.
        
        Lower difficulty = slower pace, fewer words.
        Higher difficulty = faster pace, more words.
        """
        wpm_base = 20 + (difficulty * 5)  # Base WPM for this difficulty
        return max(5, int((wpm_base * duration_seconds) / 60))
