"""Multi-Cue Hybrid Retrieval & Scoring Engine for Part 5 MVP.

Implements:
1. Multi-attribute scoring over the controlled representative dataset (40 photos).
2. Transparent match rationale generation (human-readable bullets).
3. Contextual event clustering (grouping candidates into episodic moments).
4. Iterative refinement re-scoring with negative penalty on rejected candidates.
"""

from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import re

from src.models.mvp import (
    MemoryCues,
    RepresentativePhoto,
    ScoredCandidate,
    SearchResponse,
    RefineResponse,
)
from src.data.representative_dataset import get_representative_dataset, get_photo_by_id
from src.ai.cue_extractor import extract_memory_cues
from src.config.logger import logger


# ==============================================================================
# SCORING ENGINE IMPLEMENTATION
# ==============================================================================

class MemoryRetrievalEngine:
    """Scoring engine that matches unstructured episodic memory cues to representative assets."""

    def __init__(self, dataset: Optional[List[RepresentativePhoto]] = None):
        self.dataset = dataset or get_representative_dataset()

    def score_photo(
        self,
        photo: RepresentativePhoto,
        cues: MemoryCues,
        rejected_ids: Optional[List[str]] = None,
    ) -> Tuple[float, List[str], str]:
        """Calculates match score, human-readable match rationales, and event cluster."""
        rejected_ids = rejected_ids or []
        
        # Immediate exclusion penalty if user previously clicked "Not this"
        if photo.id in rejected_ids:
            return -20.0, ["Explicitly marked as 'Not this' by user"], "Excluded"

        score = 0.0
        match_reasons = []

        # ----------------------------------------------------------------------
        # 1. Companion / People Match (+3.0 per companion match)
        # ----------------------------------------------------------------------
        photo_people_lower = [p.lower() for p in photo.people]
        photo_desc_lower = photo.description.lower()
        photo_title_lower = photo.title.lower()

        FAMILY_RELATIONS = {"family", "parents", "mother", "father", "sister", "brother", "cousins", "cousin", "relatives"}

        for comp in cues.companions:
            comp_lower = comp.lower()
            matched_companion = False

            # Check direct companion list match
            if any(comp_lower in p or p in comp_lower for p in photo_people_lower):
                score += 3.0
                match_reasons.append(f"✓ Companion: {comp}")
                matched_companion = True
            # Natural family relationship hypernym: 'family' matches specific family members
            elif comp_lower == "family" and any(any(rel in p for rel in FAMILY_RELATIONS) for p in photo_people_lower):
                matched_members = [p for p in photo.people if any(rel in p.lower() for rel in FAMILY_RELATIONS)]
                score += 3.0
                match_reasons.append(f"✓ Family member: {', '.join(matched_members)}")
                matched_companion = True

            # Mentioned in title or description if not already matched
            if not matched_companion:
                if comp_lower in photo_title_lower:
                    score += 2.5
                    match_reasons.append(f"✓ Mentioned in photo title: {comp}")
                elif comp_lower in photo_desc_lower:
                    score += 2.0
                    match_reasons.append(f"✓ Companion mentioned in context: {comp}")

            # Modest category relevance alignment for Social & Family when querying family
            if comp_lower == "family" and photo.category == "Social & Family":
                score += 1.5
                match_reasons.append("✓ Category: Social & Family")

        # ----------------------------------------------------------------------
        # 2. Approximate Temporal Match (+2.5 exact year, +1.5 tolerance, +0.5 season)
        # ----------------------------------------------------------------------
        if cues.normalized_year is not None:
            year_diff = abs(photo.approx_year - cues.normalized_year)
            if year_diff == 0:
                score += 2.5
                match_reasons.append(f"✓ Approx. Time: ~{photo.approx_year} ({cues.approximate_time or 'Matching year'})")
            elif year_diff <= cues.year_tolerance:
                score += 1.5
                match_reasons.append(f"✓ Close Timeframe: {photo.approx_year} (within ±{cues.year_tolerance} yr)")

        if cues.season and photo.season:
            if cues.season.lower() in photo.season.lower():
                score += 0.5
                match_reasons.append(f"✓ Season: {photo.season}")

        # ----------------------------------------------------------------------
        # 3. Location / Setting Match (+2.5 exact/sub-location)
        # ----------------------------------------------------------------------
        if cues.location:
            loc_lower = cues.location.lower()
            photo_loc_lower = photo.location.lower()
            if loc_lower in photo_loc_lower or photo_loc_lower in loc_lower:
                score += 2.5
                match_reasons.append(f"✓ Location / Setting: {photo.location}")
            elif any(token in photo_loc_lower or token in photo_desc_lower or token in photo_title_lower for token in loc_lower.split()):
                score += 1.5
                match_reasons.append(f"✓ Setting overlap: {cues.location}")

        # ----------------------------------------------------------------------
        # 4. Activity / Event Match (+2.5)
        # ----------------------------------------------------------------------
        if cues.activity:
            act_lower = cues.activity.lower().replace("mark sheet", "marksheet")
            photo_act_lower = photo.activity.lower().replace("mark sheet", "marksheet")
            if act_lower in photo_act_lower or photo_act_lower in act_lower:
                score += 2.5
                match_reasons.append(f"✓ Activity / Event: {photo.activity}")
            elif any(token in photo_act_lower or token in photo_desc_lower or token in photo_title_lower for token in act_lower.split() if len(token) > 3):
                score += 1.5
                match_reasons.append(f"✓ Activity context: {cues.activity}")

        # ----------------------------------------------------------------------
        # 5. Visual Tags & Distinctive Styling (+1.5 per tag)
        # ----------------------------------------------------------------------
        photo_tags_lower = [t.lower() for t in photo.visual_tags]
        for vis in cues.visual_attributes:
            vis_lower = vis.lower()
            if any(vis_lower in t or t in vis_lower for t in photo_tags_lower):
                score += 1.5
                match_reasons.append(f"✓ Visual Detail: {vis}")
            elif vis_lower in photo_desc_lower:
                score += 1.0
                match_reasons.append(f"✓ Visual feature in scene: {vis}")

        # ----------------------------------------------------------------------
        # 6. Objects / Artifacts (+1.5 per object)
        # ----------------------------------------------------------------------
        for obj in cues.objects:
            obj_lower = obj.lower()
            if any(obj_lower in t for t in photo_tags_lower) or obj_lower in photo_desc_lower:
                score += 1.5
                match_reasons.append(f"✓ Object / Item: {obj}")

        # ----------------------------------------------------------------------
        # 7. OCR / Printed Document Text (+2.0 base + up to +3.0 proportional)
        # ----------------------------------------------------------------------
        if cues.text_ocr and photo.text_ocr:
            ocr_tokens = [t.lower() for t in cues.text_ocr.split() if len(t) >= 3]
            photo_ocr_lower = photo.text_ocr.lower()
            matched_tokens = [t for t in ocr_tokens if t in photo_ocr_lower]
            if matched_tokens:
                ocr_boost = 2.0 + min(len(matched_tokens) * 0.75, 3.0)
                score += ocr_boost
                match_reasons.append(f"✓ Document Text Match: '{', '.join(matched_tokens[:3])}'")

        # Determine Event Cluster
        if "goa" in photo.location.lower():
            event_cluster = f"Goa Vacation ({photo.approx_year})"
        elif "manali" in photo.location.lower():
            event_cluster = f"Manali Mountain Trip ({photo.approx_year})"
        elif "stage" in photo.location.lower() or "auditorium" in photo.location.lower():
            event_cluster = f"College Fest & Stage Events ({photo.approx_year})"
        elif photo.category == "Utility & Document":
            event_cluster = f"Academic & Utility Documents ({photo.approx_year})"
        elif "kerala" in photo.location.lower():
            event_cluster = f"Kerala Holiday ({photo.approx_year})"
        else:
            event_cluster = f"{photo.category} Moments ({photo.approx_year})"

        return score, match_reasons, event_cluster

    def search(
        self,
        cues: MemoryCues,
        rejected_ids: Optional[List[str]] = None,
        min_score: float = 1.0,
    ) -> SearchResponse:
        """Executes multi-cue scoring across dataset and returns ranked candidates."""
        scored_candidates: List[ScoredCandidate] = []
        clusters_found = set()

        for photo in self.dataset:
            score, reasons, cluster = self.score_photo(photo, cues, rejected_ids=rejected_ids)
            if score >= min_score:
                if score >= 6.0:
                    confidence = "HIGH_CONFIDENCE"
                elif score >= 3.0:
                    confidence = "EXPLORATORY"
                else:
                    confidence = "LOW_MATCH"

                scored_candidates.append(
                    ScoredCandidate(
                        photo=photo,
                        score=round(score, 2),
                        match_reasons=reasons,
                        event_cluster=cluster,
                        confidence_level=confidence,
                    )
                )
                clusters_found.add(cluster)

        # Sort descending by score
        scored_candidates.sort(key=lambda c: c.score, reverse=True)

        return SearchResponse(
            total_candidates=len(scored_candidates),
            results=scored_candidates,
            active_cues=cues,
            event_clusters=sorted(list(clusters_found)),
        )

    def refine(
        self,
        previous_cues: Optional[MemoryCues] = None,
        new_clue_text: str = "",
        selected_chip: Optional[str] = None,
        rejected_photo_ids: Optional[List[str]] = None,
        active_task_id: Optional[str] = None,
    ) -> RefineResponse:
        """Merges new memory clue into existing context and re-scores candidates."""
        rejected_photo_ids = rejected_photo_ids or []
        if previous_cues is None:
            previous_cues = MemoryCues()
        
        # 1. Parse additional memory clues from new text (skip extraction if pure rejection flag)
        if new_clue_text and new_clue_text.strip().lower() not in ["rejected photo", "not this photo", "not this"]:
            extraction_res = extract_memory_cues(new_clue_text)
            new_cues = extraction_res.cues
            suggested_refinements = extraction_res.suggested_refinements
        else:
            new_cues = MemoryCues()
            suggested_refinements = [
                "Add a person: Who was with you?",
                "Specify setting: Where was this taken (beach, cafe, indoor)?",
                "Describe clothing or visual colors",
            ]

        # 2. Merge into updated cues (delta enrichment)
        merged_companions = list(set((previous_cues.companions or []) + (new_cues.companions or [])))
        merged_visuals = list(set((previous_cues.visual_attributes or []) + (new_cues.visual_attributes or [])))
        merged_objects = list(set((previous_cues.objects or []) + (new_cues.objects or [])))

        updated_cues = MemoryCues(
            approximate_time=new_cues.approximate_time or previous_cues.approximate_time,
            normalized_year=new_cues.normalized_year or previous_cues.normalized_year,
            year_tolerance=min(previous_cues.year_tolerance or 1, new_cues.year_tolerance or 1),
            season=new_cues.season or previous_cues.season,
            companions=merged_companions,
            location=new_cues.location or previous_cues.location,
            activity=new_cues.activity or previous_cues.activity,
            objects=merged_objects,
            visual_attributes=merged_visuals,
            text_ocr=new_cues.text_ocr or previous_cues.text_ocr,
            uncertainty=new_cues.uncertainty or previous_cues.uncertainty,
        )

        # 3. Handle explicit selected chip (e.g. if user tapped [Outdoors] or [Black dress])
        if selected_chip:
            chip_clean = selected_chip.strip().lower()
            if chip_clean in ["outdoors", "indoor"]:
                if chip_clean not in updated_cues.visual_attributes:
                    updated_cues.visual_attributes.append(chip_clean)
            elif chip_clean not in updated_cues.visual_attributes:
                updated_cues.visual_attributes.append(chip_clean)

        # 4. Re-run search with compound constraints and rejected IDs
        search_res = self.search(updated_cues, rejected_ids=rejected_photo_ids)

        clues_added_str = []
        if new_cues.companions:
            clues_added_str.append(f"Person: {', '.join(new_cues.companions)}")
        if new_cues.location:
            clues_added_str.append(f"Location: {new_cues.location}")
        if new_cues.activity:
            clues_added_str.append(f"Activity: {new_cues.activity}")
        if new_cues.visual_attributes:
            clues_added_str.append(f"Visual: {', '.join(new_cues.visual_attributes)}")

        if rejected_photo_ids and not clues_added_str:
            system_message = (
                f"Updated candidate pool to {search_res.total_candidates} results "
                f"after removing rejected photo(s)."
            )
        else:
            system_message = (
                f"Narrowed candidate pool down to {search_res.total_candidates} results "
                f"by incorporating: {', '.join(clues_added_str) if clues_added_str else 'additional memory clues'}."
            )

        return RefineResponse(
            status="success",
            system_message=system_message,
            updated_cues=updated_cues,
            total_candidates=search_res.total_candidates,
            results=search_res.results,
            suggested_refinements=suggested_refinements,
        )
