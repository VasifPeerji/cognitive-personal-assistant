"""
B1 — Language & Script Detection Module.

Foundational infrastructure for the Cognitive Personal Assistant (CPA).
Determines linguistic form using a hybrid, conservative approach.

This module performs NO normalization, translation, or interpretation.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from langdetect import detect_langs, LangDetectException

from app.core.logging import logger
from app.common.exceptions import LanguageDetectionError


# ---------------------------
# Data Contracts
# ---------------------------

@dataclass(frozen=True)
class B1Input:
    """Atomic input contract for B1."""
    text: str
    speaker: str
    timestamp: str
    source: str


@dataclass(frozen=True)
class ScriptDetectionResult:
    """Result of Unicode script detection."""
    scripts: List[str]
    is_mixed: bool
    is_empty_or_symbolic: bool


@dataclass(frozen=True)
class LanguageProbability:
    """Statistical language probability."""
    language: str
    probability: float


@dataclass(frozen=True)
class B1Output:
    """Immutable output contract for B1."""
    scripts: List[str]
    languages: List[str]
    language_probabilities: Dict[str, float]
    primary_language: str
    confidence: float
    notes: Optional[str]


# ---------------------------
# Script Detection
# ---------------------------

class ScriptDetector:
    """Deterministic Unicode-based script detector."""

    DEVANAGARI_RANGE: Tuple[int, int] = (0x0900, 0x097F)

    @classmethod
    def detect(cls, text: str) -> ScriptDetectionResult:
        """Detect scripts present in the text."""
        if not text.strip():
            return ScriptDetectionResult([], False, True)

        scripts_found: set[str] = set()
        has_letters: bool = False

        for char in text:
            code = ord(char)

            if cls.DEVANAGARI_RANGE[0] <= code <= cls.DEVANAGARI_RANGE[1]:
                scripts_found.add("devanagari")
                has_letters = True
            elif char.isalpha():
                scripts_found.add("latin")
                has_letters = True

        if not has_letters:
            return ScriptDetectionResult([], False, True)

        return ScriptDetectionResult(
            scripts=sorted(scripts_found),
            is_mixed=len(scripts_found) > 1,
            is_empty_or_symbolic=False,
        )


# ---------------------------
# Statistical Language Detection
# ---------------------------

class StatisticalLanguageDetector:
    """Advisory statistical language detector."""

    @staticmethod
    def detect(text: str) -> List[LanguageProbability]:
        try:
            results = detect_langs(text)
        except LangDetectException:
            logger.warning("Statistical language detection failed for text: %s", text)
            return []

        return [
            LanguageProbability(item.lang, float(item.prob))
            for item in results
        ]


# ---------------------------
# Lexical Hinglish Signal Detection
# ---------------------------

class HinglishLexicalDetector:
    """Detects Romanized Hindi lexical signals."""

    HINDI_FUNCTION_WORDS: set[str] = {
        "hai", "haan", "nahi", "kyun", "ka", "ki", "ke",
        "mera", "meri", "tum", "aap", "mein",
        "kal", "par", "aur", "tha", "thi", "hoga",
    }

    @classmethod
    def score(cls, text: str) -> float:
        tokens = [t.lower() for t in text.split() if t.isalpha()]
        if not tokens:
            return 0.0

        matches = sum(1 for t in tokens if t in cls.HINDI_FUNCTION_WORDS)
        return matches / len(tokens)


# ---------------------------
# Fusion & Decision Logic
# ---------------------------

class LanguageFusionEngine:
    """Conservative fusion of all detection signals."""

    @staticmethod
    def decide(
        script_result: ScriptDetectionResult,
        statistical: List[LanguageProbability],
        hinglish_score: float,
    ) -> Tuple[str, float, str]:

        if script_result.is_empty_or_symbolic:
            return "unknown", 0.2, "No linguistic characters detected"

        if "devanagari" in script_result.scripts:
            return "hindi", 0.95, "Devanagari script detected"

        if hinglish_score >= 0.25:
            return "hinglish", 0.85, "Strong Romanized Hindi lexical signal"

        if statistical:
            top = max(statistical, key=lambda x: x.probability)
            if top.language == "en" and top.probability >= 0.90:
                return "english", top.probability, "High-confidence English classification"

        return "mixed", 0.5, "Ambiguous linguistic signals"


# ---------------------------
# Public B1 Interface
# ---------------------------

class LanguageAndScriptDetector:
    """Public async interface for B1."""

    @staticmethod
    async def detect(input_data: B1Input) -> B1Output:
        try:
            script_result = ScriptDetector.detect(input_data.text)

            statistical = await asyncio.to_thread(
                StatisticalLanguageDetector.detect,
                input_data.text,
            )

            hinglish_score = HinglishLexicalDetector.score(input_data.text)

            primary_language, confidence, notes = LanguageFusionEngine.decide(
                script_result,
                statistical,
                hinglish_score,
            )

            language_probabilities = {
                lp.language: lp.probability for lp in statistical
            }

            languages = list(language_probabilities.keys())
            if not languages and primary_language != "unknown":
                languages = [primary_language]

            return B1Output(
                scripts=script_result.scripts,
                languages=languages,
                language_probabilities=language_probabilities,
                primary_language=primary_language,
                confidence=round(confidence, 2),
                notes=notes,
            )

        except Exception as exc:
            logger.exception("B1 language detection failed")
            raise LanguageDetectionError("Failed to detect language") from exc
