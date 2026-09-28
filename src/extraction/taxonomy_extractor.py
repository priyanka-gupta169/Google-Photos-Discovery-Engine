"""Taxonomy extractor for extracting 8 behavioral dimensions.

Extracts:
1. Retrieval Scenario
2. Retrieval Object
3. Memory Cues
4. Missing Information
5. Search Behavior
6. Failure Stage
7. Workaround
8. Outcome
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from src.models.schema import RawEvidenceRecord, NormalizedEvidenceRecord
from src.extraction.extractor import EvidenceExtractor
from scripts.deploy_production_pipeline import classify_record_heuristically


class TaxonomyExtractor:
    """Extracts 8-variable taxonomy from user feedback text."""

    def __init__(self, extractor: Optional[EvidenceExtractor] = None):
        self.extractor = extractor or EvidenceExtractor()

    def extract_from_text(
        self,
        text: str,
        source: str = "Streamlit Interactive Tester",
        source_url: str = "https://streamlit.io",
    ) -> NormalizedEvidenceRecord:
        """Extracts taxonomy variables from raw text."""
        raw = RawEvidenceRecord(
            id=str(uuid.uuid4()),
            source=source,
            source_url=source_url,
            title="User Interactive Feedback",
            author="interactive_user",
            published_at=datetime.now(timezone.utc).isoformat(),
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            raw_text=text,
            language="en",
        )

        # Try LLM extraction if Groq API is available and configured
        try:
            norm = self.extractor.process_record(raw)
            if norm.retrieval_relevance is not None and norm.retrieval_scenario:
                return norm
        except Exception:
            pass

        # Robust deterministic heuristic fallback
        return classify_record_heuristically(raw)
