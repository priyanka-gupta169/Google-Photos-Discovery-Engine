"""Relevance classifier distinguishing Problem B from Problem A.

Isolates personal retrieval UX friction (Problem B) from cloud backup/sync failures (Problem A).
"""

from typing import Tuple


class RelevanceClassifier:
    """Classifies user feedback as Problem B (Retrieval Friction) vs Problem A (Storage/Sync)."""

    def classify(self, text: str) -> Tuple[bool, str, str, float]:
        """Classifies text into (is_relevant, class_name, reason, confidence).
        
        Returns:
            Tuple[bool, str, str, float]: (is_relevant, class_name, reason, confidence)
        """
        content = text.lower()
        prob_a_indicators = [
            "backup stopped", "lost all my photos", "deleted from device",
            "cloud sync", "out of storage", "free up space", "cannot upload",
            "limited access to photo library", "photo uploads don’t work",
            "backing up", "backup issue", "syncing issue"
        ]
        is_prob_a = any(p in content for p in prob_a_indicators) and not any(
            k in content for k in ["can't find", "cannot find", "search", "retrieve", "scrolling", "looking for"]
        )

        if is_prob_a:
            return (
                False,
                "NOT_RELEVANT",
                "Problem A data availability/backup failure rather than personal retrieval friction.",
                0.92,
            )

        # Problem B indicators
        retrieval_indicators = [
            "search", "find", "retrieve", "scroll", "lost", "remember",
            "album", "receipt", "screenshot", "pet", "date", "trip", "face",
            "look for", "cannot find", "can't find", "cant find", "scrolling",
            "filter", "keyword", "query", "gallery", "old photo", "memories"
        ]
        if any(r in content for r in retrieval_indicators):
            return (
                True,
                "DIRECTLY_RELEVANT",
                "Explicit personal photo or document retrieval friction (Problem B).",
                0.95,
            )

        return (
            True,
            "INDIRECTLY_RELEVANT",
            "General photo browsing or organizational workflow challenge.",
            0.80,
        )
