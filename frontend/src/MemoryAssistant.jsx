import React, { useState, useEffect, useRef } from "react";

// ==============================================================================
// PRESET EVALUATION TASKS (Derived strictly from Part 3 & 4 Research)
// ==============================================================================
const BENCHMARK_TASKS = [
  {
    id: "TASK-1",
    title: "Task 1 — Fuzzy Travel Memory",
    researchTag: "R7 & R8",
    description: "Find an old beach sunset photo taken with friend Rohan roughly 3 years ago. No exact date is remembered.",
    defaultPrompt: "Trip to Goa with my friend Rohan around 3 years back at a beach sunset",
    targetPhotoId: "PHOTO-007",
    targetTitle: "Goa Beach Sunset with Rohan",
  },
  {
    id: "TASK-2",
    title: "Task 2 — University Marksheet",
    researchTag: "R12 & CLUST-06",
    description: "Urgently find a saved degree marksheet or transcript scan from college around 2022. Exact filename is unknown.",
    defaultPrompt: "I need to find my university marksheet or degree certificate from college around 2022",
    targetPhotoId: "PHOTO-031",
    targetTitle: "Bachelor of Technology Final Marksheet",
  },
  {
    id: "TASK-3",
    title: "Task 3 — College Ramp Walk",
    researchTag: "R9 & R14",
    description: "Find a photo wearing a black and gold outfit on stage during a college ramp walk, rather than at the annual formal dinner.",
    defaultPrompt: "College fest ramp walk on stage wearing a black and gold dress with Maya",
    targetPhotoId: "PHOTO-023",
    targetTitle: "College Fest Ramp Walk in Black & Gold",
  },
];

const OPEN_ENDED_TASK = {
  id: "OPEN_ENDED",
  title: "Open-Ended Memory Search",
  description: "Search any informal episodic memory in natural language using your own words.",
  defaultPrompt: "",
  targetPhotoId: null,
  targetTitle: null,
};

const SUGGESTED_EXAMPLE_CHIPS = [
  { icon: "🏔️", label: "Mountain", prompt: "I remember a photo of a mountain from a trip" },
  { icon: "🪔", label: "Navratri", prompt: "Navratri photos in traditional outfit" },
  { icon: "🏖️", label: "Beach", prompt: "Trip to the beach with friends around sunset" },
  { icon: "🐶", label: "Dog", prompt: "A sunny day with the dog in the park" },
  { icon: "🎂", label: "Birthday", prompt: "Birthday cake cutting party with friends" },
  { icon: "🌅", label: "Sunset", prompt: "A beautiful sunset near the water" },
  { icon: "👨‍👩‍👧", label: "Family", prompt: "Family holiday celebration" },
  { icon: "🎓", label: "College", prompt: "College days with my friends" },
];

export default function MemoryAssistant({ onSwitchToWorkbench }) {
  // Session State
  const [selectedTask, setSelectedTask] = useState(OPEN_ENDED_TASK);
  const [queryText, setQueryText] = useState("");
  const [sessionId, setSessionId] = useState(() => "session-" + Math.random().toString(36).substring(2, 9));
  const [sessionStartTime, setSessionStartTime] = useState(Date.now());
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // Search & Retrieval State
  const [activeCues, setActiveCues] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [eventClusters, setEventClusters] = useState([]);
  const [suggestedRefinements, setSuggestedRefinements] = useState([]);
  const [rejectedPhotoIds, setRejectedPhotoIds] = useState([]);
  const [attemptCount, setAttemptCount] = useState(0);
  const [refinementCount, setRefinementCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [systemMessage, setSystemMessage] = useState("");
  const [hasSearched, setHasSearched] = useState(false);
  const [previousCandidateCount, setPreviousCandidateCount] = useState(null);
  const [visibleCount, setVisibleCount] = useState(6);
  const [rejectedNotice, setRejectedNotice] = useState("");
  const [isHowItWorksOpen, setIsHowItWorksOpen] = useState(false);

  // Refinement UI State
  const [isRefinementOpen, setIsRefinementOpen] = useState(false);
  const [newClueInput, setNewClueInput] = useState("");

  // Modals & Completion State
  const [completedSuccessPhoto, setCompletedSuccessPhoto] = useState(null);
  const [isAbandonmentOpen, setIsAbandonmentOpen] = useState(false);
  const [abandonmentReason, setAbandonmentReason] = useState("");
  const [seqRating, setSeqRating] = useState(6);
  const [isDatasetModalOpen, setIsDatasetModalOpen] = useState(false);
  const [datasetRecords, setDatasetRecords] = useState([]);

  // DOM Refs
  const searchInputRef = useRef(null);
  const refinementInputRef = useRef(null);
  const resultsRef = useRef(null);
  const benchmarkRef = useRef(null);

  // Live Timer
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - sessionStartTime) / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, [sessionStartTime]);

  // Load dataset catalog for transparency modal
  useEffect(() => {
    fetch("/api/mvp/dataset")
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => setDatasetRecords(data))
      .catch((err) => console.warn("Dataset catalog fetch error:", err));
  }, []);

  // Handle Benchmark Task Switching
  const handleSelectBenchmarkTask = (task) => {
    setSelectedTask(task);
    setQueryText(task.defaultPrompt);
    resetSession(task);
    setTimeout(() => {
      searchInputRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
      searchInputRef.current?.focus();
    }, 100);
  };

  const handleChipClick = (prompt) => {
    setQueryText(prompt);
    setSelectedTask(OPEN_ENDED_TASK);
    if (searchInputRef.current) {
      searchInputRef.current.focus();
    }
  };

  const resetSession = (task = OPEN_ENDED_TASK) => {
    setSessionId("session-" + Math.random().toString(36).substring(2, 9));
    setSessionStartTime(Date.now());
    setElapsedSeconds(0);
    setActiveCues(null);
    setCandidates([]);
    setEventClusters([]);
    setSuggestedRefinements([]);
    setRejectedPhotoIds([]);
    setAttemptCount(0);
    setRefinementCount(0);
    setSystemMessage("");
    setHasSearched(false);
    setPreviousCandidateCount(null);
    setVisibleCount(6);
    setRejectedNotice("");
    setIsRefinementOpen(false);
    setNewClueInput("");
    setCompletedSuccessPhoto(null);
    setIsAbandonmentOpen(false);
  };

  const handleFullReset = () => {
    setSelectedTask(OPEN_ENDED_TASK);
    setQueryText("");
    resetSession(OPEN_ENDED_TASK);
  };

  // ----------------------------------------------------------------------------
  // 1. EXECUTE INITIAL SEARCH
  // ----------------------------------------------------------------------------
  const handleSearch = async () => {
    if (!queryText.trim()) return;
    setIsLoading(true);
    setSystemMessage("Translating your memory into structured clues...");
    const nextAttempts = attemptCount + 1;
    setAttemptCount(nextAttempts);
    setPreviousCandidateCount(null);
    setRejectedNotice("");
    setVisibleCount(6);

    try {
      // Step A: Extract structured memory cues
      const extractRes = await fetch("/api/mvp/extract-cues", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query_text: queryText }),
      });
      const extractData = await extractRes.json();
      const extractedCues = extractData.cues;
      setActiveCues(extractedCues);
      setSuggestedRefinements(extractData.suggested_refinements || []);

      // Step B: Search candidate pool
      const searchRes = await fetch("/api/mvp/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cues: extractedCues,
          active_task_id: selectedTask.id,
          query_text: queryText,
          rejected_ids: rejectedPhotoIds,
        }),
      });
      const searchData = await searchRes.json();
      const resultsList = searchData.results || [];
      setCandidates(resultsList);
      setEventClusters(searchData.event_clusters || []);
      setHasSearched(true);

      if (resultsList.length > 0) {
        setSystemMessage(
          `Identified ${resultsList.length} possible matches ranked by memory clues.`
        );
        setTimeout(() => {
          resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
        }, 150);
      } else {
        setSystemMessage("No strong matches found for this memory in the representative archive.");
      }
    } catch (err) {
      console.error("Search error:", err);
      setSystemMessage("Search encountered an issue. Using fallback retrieval.");
      setHasSearched(true);
    } finally {
      setIsLoading(false);
    }
  };

  // ----------------------------------------------------------------------------
  // 2. ITERATIVE REFINEMENT
  // ----------------------------------------------------------------------------
  const handleRefine = async (explicitClue = null) => {
    const clueToAdd = explicitClue || newClueInput.trim();
    if (!clueToAdd && rejectedPhotoIds.length === 0) return;

    setIsLoading(true);
    setSystemMessage("Merging new memory cues and re-scoring candidate pool...");
    const nextRefinements = refinementCount + 1;
    setRefinementCount(nextRefinements);
    setAttemptCount((prev) => prev + 1);
    setPreviousCandidateCount(candidates.length);
    setRejectedNotice("");

    try {
      const res = await fetch("/api/mvp/refine", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          previous_cues: activeCues || {},
          new_clue_text: clueToAdd || "Refining based on excluded candidates",
          selected_chip: explicitClue,
          rejected_photo_ids: rejectedPhotoIds,
          active_task_id: selectedTask.id,
        }),
      });
      const data = await res.json();
      setActiveCues(data.updated_cues);
      const updatedResults = data.results || [];
      setCandidates(updatedResults);
      setSuggestedRefinements(data.suggested_refinements || []);
      setSystemMessage(data.system_message || `Updated candidate pool to ${data.total_candidates} photos.`);
      setNewClueInput("");
      setVisibleCount(6);

      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 150);
    } catch (err) {
      console.error("Refine error:", err);
      setSystemMessage("Refinement failed to update candidates.");
    } finally {
      setIsLoading(false);
    }
  };

  // ----------------------------------------------------------------------------
  // 3. CANDIDATE FEEDBACK ACTIONS
  // ----------------------------------------------------------------------------
  const handleConfirmPhoto = (photo) => {
    setCompletedSuccessPhoto(photo);
    logSession("SUCCESS", photo.id);
  };

  const handleRejectPhoto = (photoId) => {
    const updatedRejected = [...rejectedPhotoIds, photoId];
    setRejectedPhotoIds(updatedRejected);
    setIsRefinementOpen(true);
    setRejectedNotice("Not the right photo? Add another clue to narrow the search.");
    setTimeout(() => {
      refinementInputRef.current?.focus();
      refinementInputRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
    }, 120);
  };

  // ----------------------------------------------------------------------------
  // 4. LOG SESSION TELEMETRY
  // ----------------------------------------------------------------------------
  const logSession = async (outcome, photoId = null, reason = null) => {
    const telemetryPayload = {
      session_id: sessionId,
      task_id: selectedTask.id,
      initial_query: queryText,
      extracted_cues: activeCues || {},
      retrieval_attempts: attemptCount,
      refinements_count: refinementCount,
      candidate_count: candidates.length,
      timeline_available: Boolean(activeCues?.normalized_year),
      user_selected_result: outcome === "SUCCESS",
      selected_photo_id: photoId,
      final_outcome: outcome,
      completion_time_seconds: Math.floor((Date.now() - sessionStartTime) / 1000),
      seq_score: outcome === "SUCCESS" ? seqRating : null,
      abandonment_reason: reason || abandonmentReason || null,
      timestamp: new Date().toISOString(),
    };

    try {
      await fetch("/api/mvp/log-session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(telemetryPayload),
      });
    } catch (err) {
      console.warn("Telemetry log error:", err);
    }
  };

  const handleAbandon = () => {
    logSession("ABANDONED", null, abandonmentReason || "User decided to stop search");
    setIsAbandonmentOpen(false);
    setSystemMessage("Search session was ended and logged as abandoned.");
  };

  // Cue Extraction Field Helper
  const hasExtractedCues = activeCues && (
    (activeCues.companions && activeCues.companions.length > 0) ||
    activeCues.location ||
    activeCues.approximate_time ||
    activeCues.activity ||
    (activeCues.visual_attributes && activeCues.visual_attributes.length > 0) ||
    (activeCues.objects && activeCues.objects.length > 0) ||
    activeCues.text_ocr ||
    activeCues.uncertainty
  );

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "var(--bg-main)", color: "var(--text-primary)" }}>
      {/* ==================================================================== */}
      {/* TOP NOTIFICATION & PROTOTYPE BOUNDARY BANNER */}
      {/* ==================================================================== */}
      <div
        style={{
          backgroundColor: "rgba(66, 133, 244, 0.1)",
          borderBottom: "1px solid rgba(66, 133, 244, 0.25)",
          padding: "8px 24px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: "12px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span style={{ backgroundColor: "#4285F4", color: "#fff", padding: "2px 8px", borderRadius: "4px", fontWeight: "700" }}>
            PART 5 MVP
          </span>
          <span style={{ color: "var(--text-secondary)" }}>
            AI-Assisted Memory Retrieval Assistant • Usability Testing Prototype • Controlled Representative Dataset (40 Photos)
          </span>
        </div>
        <div style={{ display: "flex", gap: "12px" }}>
          <button
            onClick={() => setIsDatasetModalOpen(true)}
            style={{
              background: "transparent",
              border: "1px solid var(--border-medium)",
              color: "var(--text-primary)",
              padding: "4px 10px",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "11px",
            }}
          >
            Audit 40 Prototype Photos
          </button>
          {onSwitchToWorkbench && (
            <button
              onClick={onSwitchToWorkbench}
              style={{
                background: "rgba(255, 255, 255, 0.08)",
                border: "1px solid var(--border-medium)",
                color: "var(--text-brand)",
                padding: "4px 10px",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: "11px",
              }}
            >
              Switch to Research Workbench (Parts 1-4) →
            </button>
          )}
        </div>
      </div>

      {/* ==================================================================== */}
      {/* MAIN CONTAINER */}
      {/* ==================================================================== */}
      <main style={{ maxWidth: "1180px", margin: "0 auto", padding: "28px 20px" }}>
        
        {/* ================================================================== */}
        {/* HEADER SECTION */}
        {/* ================================================================== */}
        <div style={{ textAlign: "center", marginBottom: "26px" }}>
          <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "32px", fontWeight: "800", color: "#fff", letterSpacing: "-0.5px" }}>
            📸 AI Memory Retrieval Assistant
          </h1>
          <p style={{ color: "var(--text-primary)", fontSize: "16px", fontWeight: "600", marginTop: "8px" }}>
            Can't remember the exact date or filename? Tell me what you remember about the photo.
          </p>
          <p style={{ color: "var(--text-secondary)", fontSize: "13.5px", marginTop: "5px", maxWidth: "680px", margin: "5px auto 0" }}>
            Describe anything you remember — a person, place, event, object, activity, appearance, or approximate time.
          </p>

          {/* Prototype Disclaimer */}
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
              marginTop: "14px",
              padding: "6px 16px",
              backgroundColor: "rgba(245, 158, 11, 0.1)",
              border: "1px solid rgba(245, 158, 11, 0.3)",
              borderRadius: "20px",
              fontSize: "12px",
              color: "#FBBF24",
            }}
          >
            <span>⚠️</span>
            <span>
              This is an experimental prototype using a controlled representative photo dataset (40 photos). It does not access your personal Google Photos.
            </span>
          </div>

          {/* Collapsible 'How it works' section */}
          <div style={{ marginTop: "14px" }}>
            <button
              onClick={() => setIsHowItWorksOpen(!isHowItWorksOpen)}
              style={{
                background: "transparent",
                border: "none",
                color: "var(--text-brand)",
                fontSize: "12px",
                cursor: "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: "5px",
                textDecoration: "underline",
              }}
            >
              <span>{isHowItWorksOpen ? "▲ Hide 'How it works'" : "▼ How it works"}</span>
            </button>

            {isHowItWorksOpen && (
              <div
                style={{
                  marginTop: "12px",
                  maxWidth: "840px",
                  margin: "12px auto 0",
                  backgroundColor: "rgba(14, 20, 36, 0.75)",
                  border: "1px solid var(--border-subtle)",
                  borderRadius: "12px",
                  padding: "16px 20px",
                  textAlign: "left",
                }}
              >
                <div style={{ fontSize: "12px", fontWeight: "700", color: "#fff", marginBottom: "10px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                  The 5-Step Interaction Model
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "10px" }}>
                  {[
                    { step: "1", title: "Tell what you remember", desc: "Speak or type in your natural words" },
                    { step: "2", title: "AI extracts clues", desc: "Translates memory into multiple dimensions" },
                    { step: "3", title: "See possible matches", desc: "Ranked candidates with transparent rationales" },
                    { step: "4", title: "Add another clue", desc: "Refine without restarting the search" },
                    { step: "5", title: "Retrieve your photo", desc: "Narrowed candidate pool down to target" },
                  ].map((s) => (
                    <div
                      key={s.step}
                      style={{
                        backgroundColor: "var(--bg-card)",
                        padding: "10px 12px",
                        borderRadius: "8px",
                        border: "1px solid var(--border-subtle)",
                      }}
                    >
                      <div style={{ color: "var(--accent-google-blue)", fontWeight: "800", fontSize: "13px" }}>
                        Step {s.step}
                      </div>
                      <div style={{ color: "#fff", fontWeight: "600", fontSize: "12px", marginTop: "2px" }}>
                        {s.title}
                      </div>
                      <div style={{ color: "var(--text-secondary)", fontSize: "11px", marginTop: "3px" }}>
                        {s.desc}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ================================================================== */}
        {/* PRIMARY CONVERSATIONAL MEMORY SEARCH BAR */}
        {/* ================================================================== */}
        <div
          style={{
            backgroundColor: "var(--bg-card)",
            border: "1px solid var(--border-highlight)",
            borderRadius: "18px",
            padding: "24px",
            boxShadow: "var(--shadow-glow)",
            marginBottom: "24px",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
            <div>
              <label style={{ fontSize: "15px", fontWeight: "700", color: "#fff" }}>
                What photo are you trying to find?
              </label>
              {selectedTask.id !== "OPEN_ENDED" && (
                <span
                  style={{
                    marginLeft: "10px",
                    backgroundColor: "rgba(66, 133, 244, 0.2)",
                    color: "#93C5FD",
                    fontSize: "11px",
                    padding: "2px 8px",
                    borderRadius: "4px",
                    fontWeight: "600",
                  }}
                >
                  Active Benchmark: {selectedTask.title}
                </span>
              )}
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                Session: <code>{sessionId}</code> • Attempt #{attemptCount}
              </span>
              <button
                onClick={handleFullReset}
                title="Start a fresh search and clear current memory and candidates."
                style={{
                  background: "transparent",
                  border: "1px solid var(--border-subtle)",
                  color: "var(--text-secondary)",
                  borderRadius: "6px",
                  padding: "4px 10px",
                  fontSize: "11px",
                  cursor: "pointer",
                }}
              >
                🔄 Reset Search
              </button>
            </div>
          </div>

          <div style={{ display: "flex", gap: "12px", alignItems: "flex-start" }}>
            <textarea
              ref={searchInputRef}
              rows={2}
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              placeholder="I remember a photo of a mountain from a trip..."
              style={{
                flex: 1,
                backgroundColor: "var(--bg-inset)",
                border: "1px solid var(--border-medium)",
                borderRadius: "10px",
                color: "#fff",
                padding: "12px 16px",
                fontSize: "14px",
                fontFamily: "var(--font-body)",
                resize: "vertical",
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSearch();
                }
              }}
            />
            <button
              onClick={handleSearch}
              disabled={isLoading || !queryText.trim()}
              style={{
                backgroundColor: "var(--accent-google-blue)",
                color: "#fff",
                border: "none",
                borderRadius: "10px",
                padding: "14px 26px",
                fontWeight: "700",
                fontSize: "14px",
                cursor: isLoading || !queryText.trim() ? "not-allowed" : "pointer",
                boxShadow: "0 4px 14px rgba(66, 133, 244, 0.4)",
                minWidth: "170px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
              }}
            >
              {isLoading ? "Searching..." : "🔍 Search Memories"}
            </button>
          </div>

          {/* Under-Input Guidance & Example Chips */}
          <div style={{ marginTop: "16px", paddingTop: "14px", borderTop: "1px solid var(--border-subtle)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px", marginBottom: "8px" }}>
              <span style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: "600" }}>
                Not sure what to type? Try something like:
              </span>
              <span style={{ fontSize: "11px", color: "var(--text-muted)", fontStyle: "italic" }}>
                You don't need the exact date, filename, or exact words.
              </span>
            </div>

            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
              {SUGGESTED_EXAMPLE_CHIPS.map((chip, idx) => (
                <button
                  key={idx}
                  onClick={() => handleChipClick(chip.prompt)}
                  style={{
                    backgroundColor: "rgba(255, 255, 255, 0.05)",
                    border: "1px solid var(--border-subtle)",
                    color: "var(--text-primary)",
                    borderRadius: "18px",
                    padding: "5px 12px",
                    fontSize: "12px",
                    cursor: "pointer",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    transition: "all 0.2s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = "rgba(66, 133, 244, 0.15)";
                    e.currentTarget.style.borderColor = "var(--accent-google-blue)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.05)";
                    e.currentTarget.style.borderColor = "var(--border-subtle)";
                  }}
                  title={`Fill prompt: "${chip.prompt}"`}
                >
                  <span>{chip.icon}</span>
                  <span>{chip.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* System Feedback Message */}
          {systemMessage && (
            <div
              style={{
                marginTop: "12px",
                padding: "8px 12px",
                backgroundColor: "rgba(255, 255, 255, 0.04)",
                borderRadius: "6px",
                fontSize: "12px",
                color: "var(--text-secondary)",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <span>ℹ️</span> {systemMessage}
            </div>
          )}
        </div>

        {/* ================================================================== */}
        {/* 'WHAT I UNDERSTOOD' CUES HUD */}
        {/* ================================================================== */}
        {hasExtractedCues && (
          <div
            style={{
              backgroundColor: "var(--bg-surface)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "14px",
              padding: "18px 22px",
              marginBottom: "24px",
            }}
          >
            <div style={{ display: "flex", alignItems: "baseline", gap: "10px", marginBottom: "8px" }}>
              <span style={{ fontSize: "15px", fontWeight: "700", color: "#fff" }}>
                🧠 What I understood
              </span>
              <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                I'll use these clues together to find possible matches.
              </span>
            </div>

            <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "8px" }}>
              {activeCues.companions?.map((p, i) => (
                <span
                  key={`person-${i}`}
                  style={{
                    backgroundColor: "rgba(99, 102, 241, 0.15)",
                    color: "#A5B4FC",
                    border: "1px solid rgba(99, 102, 241, 0.3)",
                    padding: "4px 12px",
                    borderRadius: "16px",
                    fontSize: "12px",
                    fontWeight: "600",
                  }}
                >
                  👤 Person: {p}
                </span>
              ))}

              {activeCues.approximate_time && (
                <span
                  style={{
                    backgroundColor: "rgba(245, 158, 11, 0.15)",
                    color: "#FBBF24",
                    border: "1px solid rgba(245, 158, 11, 0.3)",
                    padding: "4px 12px",
                    borderRadius: "16px",
                    fontSize: "12px",
                    fontWeight: "600",
                  }}
                >
                  🕒 Approximate time: {activeCues.approximate_time}
                </span>
              )}

              {activeCues.location && (
                <span
                  style={{
                    backgroundColor: "rgba(16, 185, 129, 0.15)",
                    color: "#34D399",
                    border: "1px solid rgba(16, 185, 129, 0.3)",
                    padding: "4px 12px",
                    borderRadius: "16px",
                    fontSize: "12px",
                    fontWeight: "600",
                  }}
                >
                  📍 Location: {activeCues.location}
                </span>
              )}

              {activeCues.activity && (
                <span
                  style={{
                    backgroundColor: "rgba(236, 72, 153, 0.15)",
                    color: "#F472B6",
                    border: "1px solid rgba(236, 72, 153, 0.3)",
                    padding: "4px 12px",
                    borderRadius: "16px",
                    fontSize: "12px",
                    fontWeight: "600",
                  }}
                >
                  🎯 Activity / Event: {activeCues.activity}
                </span>
              )}

              {activeCues.visual_attributes?.map((v, i) => (
                <span
                  key={`visual-${i}`}
                  style={{
                    backgroundColor: "rgba(6, 182, 212, 0.15)",
                    color: "#22D3EE",
                    border: "1px solid rgba(6, 182, 212, 0.3)",
                    padding: "4px 12px",
                    borderRadius: "16px",
                    fontSize: "12px",
                    fontWeight: "600",
                  }}
                >
                  🎨 Visual clue: {v}
                </span>
              ))}

              {activeCues.objects?.map((obj, i) => (
                <span
                  key={`object-${i}`}
                  style={{
                    backgroundColor: "rgba(139, 92, 246, 0.15)",
                    color: "#C4B5FD",
                    border: "1px solid rgba(139, 92, 246, 0.3)",
                    padding: "4px 12px",
                    borderRadius: "16px",
                    fontSize: "12px",
                    fontWeight: "600",
                  }}
                >
                  📦 Object: {obj}
                </span>
              ))}

              {activeCues.text_ocr && (
                <span
                  style={{
                    backgroundColor: "rgba(168, 85, 247, 0.15)",
                    color: "#C084FC",
                    border: "1px solid rgba(168, 85, 247, 0.3)",
                    padding: "4px 12px",
                    borderRadius: "16px",
                    fontSize: "12px",
                    fontWeight: "600",
                  }}
                >
                  📄 Document / OCR text: {activeCues.text_ocr}
                </span>
              )}

              {activeCues.uncertainty && (
                <span
                  style={{
                    backgroundColor: "rgba(148, 163, 184, 0.15)",
                    color: "#94A3B8",
                    border: "1px solid rgba(148, 163, 184, 0.3)",
                    padding: "4px 12px",
                    borderRadius: "16px",
                    fontSize: "12px",
                    fontWeight: "600",
                  }}
                >
                  ❓ Uncertainty: {activeCues.uncertainty}
                </span>
              )}

              {rejectedPhotoIds.length > 0 && (
                <span
                  style={{
                    backgroundColor: "rgba(239, 68, 68, 0.15)",
                    color: "#F87171",
                    border: "1px solid rgba(239, 68, 68, 0.3)",
                    padding: "4px 12px",
                    borderRadius: "16px",
                    fontSize: "12px",
                    fontWeight: "600",
                  }}
                >
                  ✕ {rejectedPhotoIds.length} Excluded
                </span>
              )}
            </div>
          </div>
        )}

        {/* ================================================================== */}
        {/* ITERATIVE REFINEMENT SECTION */}
        {/* ================================================================== */}
        {(candidates.length > 0 || isRefinementOpen) && (
          <div
            style={{
              backgroundColor: "rgba(14, 20, 36, 0.95)",
              border: "1px solid var(--border-medium)",
              borderRadius: "16px",
              padding: "20px 24px",
              marginBottom: "26px",
              boxShadow: "var(--shadow-md)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
              <div>
                <div style={{ fontSize: "16px", fontWeight: "700", color: "#fff" }}>
                  🔍 Didn't find the exact photo?
                </div>
                <div style={{ fontSize: "12.5px", color: "var(--text-secondary)", marginTop: "3px" }}>
                  Add another clue from what you remember — without starting over.
                </div>
              </div>

              <button
                onClick={() => setIsAbandonmentOpen(true)}
                style={{
                  background: "transparent",
                  border: "none",
                  color: "var(--accent-rose)",
                  fontSize: "12px",
                  cursor: "pointer",
                  textDecoration: "underline",
                  whiteSpace: "nowrap",
                  marginLeft: "12px",
                }}
              >
                Cannot find photo? Abandon Search
              </button>
            </div>

            {/* Rejection Notification / Guidance */}
            {rejectedNotice && (
              <div
                style={{
                  marginBottom: "12px",
                  padding: "8px 12px",
                  backgroundColor: "rgba(239, 68, 68, 0.12)",
                  border: "1px solid rgba(239, 68, 68, 0.3)",
                  borderRadius: "8px",
                  fontSize: "12px",
                  color: "#FCA5A5",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                }}
              >
                <span>ℹ️</span> {rejectedNotice}
              </div>
            )}

            {/* Quick Refinement Suggestions */}
            {suggestedRefinements.length > 0 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginBottom: "12px" }}>
                <span style={{ fontSize: "11px", color: "var(--text-muted)", alignSelf: "center" }}>
                  Suggested questions:
                </span>
                {suggestedRefinements.map((s, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setNewClueInput(s);
                      refinementInputRef.current?.focus();
                    }}
                    style={{
                      background: "rgba(255, 255, 255, 0.06)",
                      border: "1px solid var(--border-subtle)",
                      color: "var(--text-primary)",
                      padding: "4px 10px",
                      borderRadius: "14px",
                      fontSize: "11px",
                      cursor: "pointer",
                    }}
                  >
                    + {s}
                  </button>
                ))}
              </div>
            )}

            {/* Add Clue Input Box */}
            <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
              <input
                ref={refinementInputRef}
                type="text"
                value={newClueInput}
                onChange={(e) => setNewClueInput(e.target.value)}
                placeholder="Maybe we were laughing..."
                style={{
                  flex: 1,
                  backgroundColor: "var(--bg-inset)",
                  border: "1px solid var(--border-medium)",
                  borderRadius: "8px",
                  color: "#fff",
                  padding: "10px 14px",
                  fontSize: "13.5px",
                  fontFamily: "var(--font-body)",
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleRefine();
                  }
                }}
              />
              <button
                onClick={() => handleRefine()}
                disabled={isLoading || !newClueInput.trim()}
                style={{
                  backgroundColor: "var(--accent-primary)",
                  color: "#fff",
                  border: "none",
                  borderRadius: "8px",
                  padding: "10px 20px",
                  fontWeight: "700",
                  fontSize: "13.5px",
                  cursor: isLoading || !newClueInput.trim() ? "not-allowed" : "pointer",
                  whiteSpace: "nowrap",
                }}
              >
                Apply New Clue
              </button>
            </div>
          </div>
        )}

        {/* ================================================================== */}
        {/* CANDIDATE PHOTO RESULTS GRID / EMPTY STATE */}
        {/* ================================================================== */}
        <div ref={resultsRef}>
          {hasSearched && candidates.length > 0 && (
            <div>
              {/* Header with user-oriented title and progression */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: "16px" }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "20px", fontWeight: "800", color: "#fff" }}>
                      🔎 Possible matches
                    </h2>
                    <span
                      style={{
                        backgroundColor: "rgba(66, 133, 244, 0.2)",
                        color: "#93C5FD",
                        padding: "2px 10px",
                        borderRadius: "12px",
                        fontSize: "12px",
                        fontWeight: "700",
                      }}
                    >
                      {candidates.length} possible matches
                    </span>
                  </div>
                  <div style={{ fontSize: "12.5px", color: "var(--text-secondary)", marginTop: "4px" }}>
                    I've ranked these based on the clues you provided.
                  </div>
                </div>

                {/* Visible count toggle & Progression indicator */}
                <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                  {previousCandidateCount !== null && (
                    <div
                      style={{
                        backgroundColor: "rgba(16, 185, 129, 0.15)",
                        border: "1px solid rgba(16, 185, 129, 0.35)",
                        color: "#34D399",
                        borderRadius: "6px",
                        padding: "3px 10px",
                        fontSize: "11px",
                        fontWeight: "700",
                      }}
                    >
                      Progression: {previousCandidateCount} matches → {candidates.length} matches
                    </div>
                  )}

                  {candidates.length > 6 && (
                    <button
                      onClick={() => setVisibleCount((prev) => (prev >= candidates.length ? 6 : candidates.length))}
                      style={{
                        background: "rgba(255, 255, 255, 0.08)",
                        border: "1px solid var(--border-subtle)",
                        color: "var(--text-primary)",
                        borderRadius: "6px",
                        padding: "4px 12px",
                        fontSize: "12px",
                        cursor: "pointer",
                      }}
                    >
                      {visibleCount >= candidates.length ? "Show Top 6 Only" : `Show All ${candidates.length} Results`}
                    </button>
                  )}
                </div>
              </div>

              {/* Photo Card Grid */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "20px" }}>
                {candidates.slice(0, visibleCount).map((cand) => {
                  const p = cand.photo;
                  const isTarget = selectedTask.targetPhotoId === p.id;
                  const isRejected = rejectedPhotoIds.includes(p.id);

                  return (
                    <div
                      key={p.id}
                      style={{
                        backgroundColor: "var(--bg-card)",
                        border: isTarget && completedSuccessPhoto?.id === p.id
                          ? "2px solid var(--accent-emerald)"
                          : "1px solid var(--border-subtle)",
                        borderRadius: "14px",
                        overflow: "hidden",
                        display: "flex",
                        flexDirection: "column",
                        boxShadow: "var(--shadow-md)",
                        opacity: isRejected ? 0.35 : 1,
                        transition: "all 0.2s ease",
                      }}
                    >
                      {/* Photo Image Preview */}
                      <div style={{ position: "relative", height: "190px", backgroundColor: "#000", overflow: "hidden" }}>
                        <img
                          src={p.thumbnail_url}
                          alt={p.title}
                          style={{ width: "100%", height: "100%", objectFit: "cover" }}
                          onError={(e) => {
                            e.target.style.display = "none";
                          }}
                        />
                        <div
                          style={{
                            position: "absolute",
                            top: "10px",
                            left: "10px",
                            backgroundColor: "rgba(0, 0, 0, 0.65)",
                            color: "#fff",
                            padding: "2px 8px",
                            borderRadius: "4px",
                            fontSize: "11px",
                            fontWeight: "600",
                          }}
                        >
                          {p.category} • ~{p.approx_year}
                        </div>

                        <div
                          style={{
                            position: "absolute",
                            top: "10px",
                            right: "10px",
                            backgroundColor:
                              cand.confidence_level === "HIGH_CONFIDENCE"
                                ? "rgba(16, 185, 129, 0.9)"
                                : cand.confidence_level === "EXPLORATORY"
                                ? "rgba(66, 133, 244, 0.9)"
                                : "rgba(148, 163, 184, 0.8)",
                            color: "#fff",
                            padding: "2px 8px",
                            borderRadius: "4px",
                            fontSize: "10px",
                            fontWeight: "700",
                            textTransform: "uppercase",
                          }}
                        >
                          {cand.confidence_level === "HIGH_CONFIDENCE" ? "High Match" : "Possible Match"}
                        </div>
                      </div>

                      {/* Metadata & Match Rationales */}
                      <div style={{ padding: "16px", flex: 1, display: "flex", flexDirection: "column" }}>
                        <div style={{ fontWeight: "700", fontSize: "14px", color: "#fff", marginBottom: "4px" }}>
                          {p.title}
                        </div>
                        <div style={{ fontSize: "11.5px", color: "var(--text-secondary)", marginBottom: "12px", lineHeight: "1.4" }}>
                          {p.description}
                        </div>

                        {/* Transparent Match Rationales */}
                        <div
                          style={{
                            backgroundColor: "rgba(255, 255, 255, 0.04)",
                            border: "1px solid var(--border-subtle)",
                            borderRadius: "8px",
                            padding: "10px",
                            marginBottom: "14px",
                          }}
                        >
                          <div style={{ fontSize: "11px", fontWeight: "700", color: "var(--text-brand)", marginBottom: "4px" }}>
                            Why this result?
                          </div>
                          <ul style={{ listStyle: "none", padding: 0, margin: 0, fontSize: "11px", color: "var(--text-secondary)" }}>
                            {cand.match_reasons.slice(0, 4).map((r, rIdx) => {
                              const cleanR = r.replace("✓", "").trim();
                              return (
                                <li key={rIdx} style={{ marginBottom: "2px", display: "flex", alignItems: "baseline", gap: "4px" }}>
                                  <span style={{ color: "#34D399" }}>✓</span>
                                  <span>{cleanR}</span>
                                </li>
                              );
                            })}
                          </ul>
                        </div>

                        {/* Candidate Action Buttons */}
                        <div style={{ marginTop: "auto", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
                          <button
                            onClick={() => handleConfirmPhoto(p)}
                            style={{
                              backgroundColor: "rgba(16, 185, 129, 0.2)",
                              color: "#34D399",
                              border: "1px solid rgba(16, 185, 129, 0.4)",
                              borderRadius: "6px",
                              padding: "8px 10px",
                              fontWeight: "700",
                              fontSize: "12px",
                              cursor: "pointer",
                            }}
                          >
                            ✓ This is the photo
                          </button>
                          <button
                            onClick={() => handleRejectPhoto(p.id)}
                            style={{
                              backgroundColor: "rgba(239, 68, 68, 0.15)",
                              color: "#F87171",
                              border: "1px solid rgba(239, 68, 68, 0.3)",
                              borderRadius: "6px",
                              padding: "8px 10px",
                              fontWeight: "600",
                              fontSize: "12px",
                              cursor: "pointer",
                            }}
                          >
                            ✕ Not this photo
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Show more button at bottom if needed */}
              {candidates.length > visibleCount && (
                <div style={{ textAlign: "center", marginTop: "24px" }}>
                  <button
                    onClick={() => setVisibleCount(candidates.length)}
                    style={{
                      backgroundColor: "rgba(255, 255, 255, 0.08)",
                      border: "1px solid var(--border-medium)",
                      color: "#fff",
                      borderRadius: "8px",
                      padding: "10px 24px",
                      fontSize: "13px",
                      fontWeight: "600",
                      cursor: "pointer",
                    }}
                  >
                    View All {candidates.length} Ranked Candidates
                  </button>
                </div>
              )}
            </div>
          )}

          {/* ZERO MATCH / NO STRONG MATCHES STATE (DO NOT FABRICATE RESULTS) */}
          {hasSearched && candidates.length === 0 && !isLoading && (
            <div
              style={{
                backgroundColor: "var(--bg-card)",
                border: "1px dashed var(--border-medium)",
                borderRadius: "16px",
                padding: "36px 28px",
                textAlign: "center",
                maxWidth: "680px",
                margin: "0 auto",
              }}
            >
              <div style={{ fontSize: "36px", marginBottom: "12px" }}>🔍</div>
              <h3 style={{ fontFamily: "var(--font-heading)", fontSize: "18px", fontWeight: "700", color: "#fff", marginBottom: "8px" }}>
                No strong matches found for this memory.
              </h3>
              <p style={{ color: "var(--text-secondary)", fontSize: "13px", marginBottom: "18px", lineHeight: "1.5" }}>
                Our 40-photo representative archive couldn't find a confident match with the current clues.
              </p>

              <div
                style={{
                  backgroundColor: "var(--bg-inset)",
                  borderRadius: "10px",
                  padding: "14px 18px",
                  textAlign: "left",
                  fontSize: "12.5px",
                  color: "var(--text-primary)",
                  maxWidth: "420px",
                  margin: "0 auto 20px",
                  lineHeight: "1.7",
                }}
              >
                <div style={{ fontWeight: "700", color: "var(--text-brand)", marginBottom: "4px" }}>
                  Try adding another clue such as:
                </div>
                <div>• who was there</div>
                <div>• where you were</div>
                <div>• what was happening</div>
                <div>• what someone was wearing</div>
                <div>• what the photo looked like</div>
                <div>• an approximate time</div>
              </div>

              <button
                onClick={() => {
                  refinementInputRef.current?.focus();
                  refinementInputRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
                }}
                style={{
                  backgroundColor: "var(--accent-google-blue)",
                  color: "#fff",
                  border: "none",
                  borderRadius: "8px",
                  padding: "10px 22px",
                  fontWeight: "700",
                  fontSize: "13px",
                  cursor: "pointer",
                }}
              >
                🔍 Add another clue
              </button>
            </div>
          )}

          {/* Initial State (Before Search) */}
          {!hasSearched && !isLoading && (
            <div
              style={{
                backgroundColor: "var(--bg-surface)",
                border: "1px dashed var(--border-medium)",
                borderRadius: "14px",
                padding: "44px 24px",
                textAlign: "center",
                color: "var(--text-secondary)",
              }}
            >
              <div style={{ fontSize: "36px", marginBottom: "12px" }}>💭</div>
              <div style={{ fontSize: "16px", fontWeight: "700", color: "#fff", marginBottom: "6px" }}>
                Ready to search your memories
              </div>
              <p style={{ maxWidth: "480px", margin: "0 auto", fontSize: "13px", lineHeight: "1.5" }}>
                Type what you remember in the search box above, or choose an example chip to test how the AI translates fragmented memories into photos.
              </p>
            </div>
          )}
        </div>

        {/* ================================================================== */}
        {/* SECONDARY SECTION: RESEARCH BENCHMARK TASKS (For Part 6 Testing) */}
        {/* ================================================================== */}
        <div
          ref={benchmarkRef}
          style={{
            marginTop: "54px",
            backgroundColor: "rgba(10, 15, 28, 0.9)",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            borderRadius: "16px",
            padding: "24px",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "10px", marginBottom: "14px" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ fontSize: "18px" }}>🧪</span>
                <h3 style={{ fontFamily: "var(--font-heading)", fontSize: "17px", fontWeight: "800", color: "#fff" }}>
                  Research Benchmark Tasks
                </h3>
                <span style={{ backgroundColor: "rgba(99, 102, 241, 0.2)", color: "#A5B4FC", fontSize: "10.5px", padding: "2px 8px", borderRadius: "4px", fontWeight: "700" }}>
                  PART 6 RESEARCH MODE
                </span>
              </div>
              <p style={{ color: "var(--text-secondary)", fontSize: "12.5px", marginTop: "4px" }}>
                These are controlled scenarios used for usability testing. You can use them if you're participating in the research study.
              </p>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "14px" }}>
            {BENCHMARK_TASKS.map((task) => {
              const isSelected = selectedTask.id === task.id;
              return (
                <div
                  key={task.id}
                  onClick={() => handleSelectBenchmarkTask(task)}
                  style={{
                    backgroundColor: isSelected ? "rgba(66, 133, 244, 0.12)" : "var(--bg-card)",
                    border: isSelected ? "2px solid var(--accent-google-blue)" : "1px solid var(--border-subtle)",
                    borderRadius: "12px",
                    padding: "16px",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                    display: "flex",
                    flexDirection: "column",
                  }}
                  onMouseEnter={(e) => {
                    if (!isSelected) e.currentTarget.style.borderColor = "var(--border-medium)";
                  }}
                  onMouseLeave={(e) => {
                    if (!isSelected) e.currentTarget.style.borderColor = "var(--border-subtle)";
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "6px" }}>
                    <div style={{ fontWeight: "700", fontSize: "13.5px", color: isSelected ? "#fff" : "var(--text-primary)" }}>
                      {task.title}
                    </div>
                    <span style={{ fontSize: "10px", color: "var(--text-muted)", backgroundColor: "rgba(255, 255, 255, 0.05)", padding: "1px 6px", borderRadius: "4px" }}>
                      {task.researchTag}
                    </span>
                  </div>

                  <p style={{ fontSize: "11.5px", color: "var(--text-secondary)", lineHeight: "1.4", marginBottom: "10px" }}>
                    {task.description}
                  </p>

                  <div style={{ marginTop: "auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: "10.5px", color: "var(--text-brand)", fontWeight: "600" }}>
                      Target: {task.targetPhotoId}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSelectBenchmarkTask(task);
                      }}
                      style={{
                        backgroundColor: isSelected ? "var(--accent-google-blue)" : "transparent",
                        border: isSelected ? "none" : "1px solid var(--border-medium)",
                        color: "#fff",
                        padding: "4px 10px",
                        borderRadius: "6px",
                        fontSize: "11px",
                        fontWeight: "600",
                        cursor: "pointer",
                      }}
                    >
                      {isSelected ? "Active Task" : "Load Task →"}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* ================================================================== */}
        {/* TELEMETRY HUD FOOTER */}
        {/* ================================================================== */}
        <div
          style={{
            marginTop: "40px",
            borderTop: "1px solid var(--border-subtle)",
            paddingTop: "16px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontSize: "12px",
            color: "var(--text-muted)",
            flexWrap: "wrap",
            gap: "8px",
          }}
        >
          <div>
            ⏱️ Task Dwell Time: <strong>{elapsedSeconds}s</strong> • Searches Attempted: <strong>{attemptCount}</strong> • Refinements: <strong>{refinementCount}</strong>
          </div>
          <div>
            Controlled Prototype Dataset: <strong>40 Assets</strong> • Ground Truth Verification: <strong>Ready</strong>
          </div>
        </div>
      </main>

      {/* ==================================================================== */}
      {/* SUCCESS CONFIRMATION MODAL */}
      {/* ==================================================================== */}
      {completedSuccessPhoto && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.8)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
            padding: "20px",
          }}
        >
          <div
            style={{
              backgroundColor: "var(--bg-card)",
              border: "1px solid var(--accent-emerald)",
              borderRadius: "16px",
              padding: "28px",
              maxWidth: "520px",
              width: "100%",
              boxShadow: "0 0 32px rgba(16, 185, 129, 0.3)",
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: "42px", marginBottom: "10px" }}>🎉</div>
            <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "22px", fontWeight: "800", color: "#fff", marginBottom: "6px" }}>
              Target Photo Found!
            </h2>
            <p style={{ color: "var(--text-secondary)", fontSize: "13px", marginBottom: "16px" }}>
              Successfully retrieved: <strong>{completedSuccessPhoto.title}</strong>
            </p>

            {/* Task Ground Truth Check */}
            {selectedTask.targetPhotoId && (
              <div
                style={{
                  backgroundColor:
                    selectedTask.targetPhotoId === completedSuccessPhoto.id
                      ? "rgba(16, 185, 129, 0.15)"
                      : "rgba(239, 68, 68, 0.15)",
                  color:
                    selectedTask.targetPhotoId === completedSuccessPhoto.id ? "#34D399" : "#F87171",
                  padding: "8px 12px",
                  borderRadius: "8px",
                  fontSize: "12px",
                  fontWeight: "600",
                  marginBottom: "16px",
                }}
              >
                {selectedTask.targetPhotoId === completedSuccessPhoto.id
                  ? "✓ Ground Truth Target Matched for " + selectedTask.id
                  : "Note: Retrieved photo was an alternative match"}
              </div>
            )}

            {/* Telemetry Summary */}
            <div
              style={{
                backgroundColor: "var(--bg-surface)",
                borderRadius: "10px",
                padding: "12px",
                display: "grid",
                gridTemplateColumns: "1fr 1fr 1fr",
                gap: "8px",
                fontSize: "12px",
                marginBottom: "20px",
              }}
            >
              <div>
                <div style={{ color: "var(--text-muted)", fontSize: "10px" }}>TIME TO RETRIEVE</div>
                <div style={{ fontWeight: "700", color: "#fff", fontSize: "16px" }}>{elapsedSeconds}s</div>
              </div>
              <div>
                <div style={{ color: "var(--text-muted)", fontSize: "10px" }}>ATTEMPTS</div>
                <div style={{ fontWeight: "700", color: "#fff", fontSize: "16px" }}>{attemptCount}</div>
              </div>
              <div>
                <div style={{ color: "var(--text-muted)", fontSize: "10px" }}>REFINEMENTS</div>
                <div style={{ fontWeight: "700", color: "#fff", fontSize: "16px" }}>{refinementCount}</div>
              </div>
            </div>

            {/* Single-Ease Question (SEQ 1-7) */}
            <div style={{ marginBottom: "20px", textAlign: "left" }}>
              <label style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", display: "block", marginBottom: "6px" }}>
                How easy was it to find this photo? (Single-Ease Question: 1=Very Difficult, 7=Very Easy):
              </label>
              <div style={{ display: "flex", gap: "6px" }}>
                {[1, 2, 3, 4, 5, 6, 7].map((num) => (
                  <button
                    key={num}
                    onClick={() => setSeqRating(num)}
                    style={{
                      flex: 1,
                      padding: "8px 0",
                      borderRadius: "6px",
                      border: seqRating === num ? "2px solid var(--accent-emerald)" : "1px solid var(--border-medium)",
                      backgroundColor: seqRating === num ? "rgba(16, 185, 129, 0.25)" : "var(--bg-inset)",
                      color: seqRating === num ? "#fff" : "var(--text-secondary)",
                      fontWeight: "700",
                      cursor: "pointer",
                    }}
                  >
                    {num}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={() => {
                setCompletedSuccessPhoto(null);
                handleFullReset();
              }}
              style={{
                backgroundColor: "var(--accent-google-blue)",
                color: "#fff",
                border: "none",
                borderRadius: "10px",
                padding: "12px 24px",
                fontWeight: "700",
                fontSize: "14px",
                cursor: "pointer",
                width: "100%",
              }}
            >
              Log Session & Try Another Search →
            </button>
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* ABANDONMENT MODAL */}
      {/* ==================================================================== */}
      {isAbandonmentOpen && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.8)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
            padding: "20px",
          }}
        >
          <div
            style={{
              backgroundColor: "var(--bg-card)",
              border: "1px solid var(--accent-rose)",
              borderRadius: "16px",
              padding: "28px",
              maxWidth: "480px",
              width: "100%",
            }}
          >
            <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "20px", fontWeight: "800", color: "#fff", marginBottom: "8px" }}>
              Abandon Retrieval Search?
            </h2>
            <p style={{ color: "var(--text-secondary)", fontSize: "13px", marginBottom: "16px" }}>
              Recording when and why a user abandons search provides crucial Part 6 usability telemetry. Please select the primary reason:
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginBottom: "20px" }}>
              {[
                "Results were too irrelevant / false positives",
                "Cannot remember more details to narrow it down",
                "Encountered too many similar-looking photos",
                "Wanted to search in WhatsApp / local gallery instead",
              ].map((reason, idx) => (
                <button
                  key={idx}
                  onClick={() => setAbandonmentReason(reason)}
                  style={{
                    textAlign: "left",
                    padding: "10px 14px",
                    borderRadius: "8px",
                    border: abandonmentReason === reason ? "2px solid var(--accent-rose)" : "1px solid var(--border-subtle)",
                    backgroundColor: abandonmentReason === reason ? "rgba(239, 68, 68, 0.15)" : "var(--bg-surface)",
                    color: abandonmentReason === reason ? "#fff" : "var(--text-primary)",
                    fontSize: "12px",
                    cursor: "pointer",
                  }}
                >
                  {reason}
                </button>
              ))}
            </div>

            <div style={{ display: "flex", gap: "10px" }}>
              <button
                onClick={() => setIsAbandonmentOpen(false)}
                style={{
                  flex: 1,
                  backgroundColor: "transparent",
                  border: "1px solid var(--border-medium)",
                  color: "var(--text-secondary)",
                  borderRadius: "8px",
                  padding: "10px",
                  fontWeight: "600",
                  cursor: "pointer",
                }}
              >
                Keep Searching
              </button>
              <button
                onClick={handleAbandon}
                style={{
                  flex: 1,
                  backgroundColor: "var(--accent-rose)",
                  color: "#fff",
                  border: "none",
                  borderRadius: "8px",
                  padding: "10px",
                  fontWeight: "700",
                  cursor: "pointer",
                }}
              >
                Confirm Abandonment
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* DATASET AUDIT MODAL (Transparency & Ground Truth Inspection) */}
      {/* ==================================================================== */}
      {isDatasetModalOpen && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.85)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
            padding: "24px",
          }}
        >
          <div
            style={{
              backgroundColor: "var(--bg-surface)",
              border: "1px solid var(--border-medium)",
              borderRadius: "16px",
              padding: "24px",
              maxWidth: "960px",
              width: "100%",
              maxHeight: "85vh",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
              <div>
                <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "18px", fontWeight: "800", color: "#fff" }}>
                  Controlled Representative Photo Dataset ({datasetRecords.length} Assets)
                </h2>
                <p style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                  Representative prototype dataset — not real Google Photos user data.
                </p>
              </div>
              <button
                onClick={() => setIsDatasetModalOpen(false)}
                style={{ background: "transparent", border: "none", color: "#fff", fontSize: "20px", cursor: "pointer" }}
              >
                ✕
              </button>
            </div>

            <div style={{ overflowY: "auto", flex: 1, display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: "12px", paddingRight: "6px" }}>
              {datasetRecords.map((item) => (
                <div
                  key={item.id}
                  style={{
                    backgroundColor: "var(--bg-card)",
                    border: item.ground_truth_task_id ? "2px solid var(--accent-google-blue)" : "1px solid var(--border-subtle)",
                    borderRadius: "8px",
                    padding: "10px",
                    fontSize: "11px",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                    <span style={{ fontWeight: "700", color: "var(--text-brand)" }}>{item.id}</span>
                    <span style={{ color: "var(--text-muted)" }}>~{item.approx_year}</span>
                  </div>
                  <div style={{ fontWeight: "600", color: "#fff", marginBottom: "4px" }}>{item.title}</div>
                  <div style={{ color: "var(--text-secondary)", marginBottom: "4px" }}>{item.category} • {item.location}</div>
                  {item.ground_truth_task_id && (
                    <span style={{ backgroundColor: "rgba(66, 133, 244, 0.2)", color: "#93C5FD", padding: "1px 6px", borderRadius: "4px", fontWeight: "700" }}>
                      Target for {item.ground_truth_task_id}
                    </span>
                  )}
                  {item.is_distractor && (
                    <span style={{ backgroundColor: "rgba(245, 158, 11, 0.2)", color: "#FCD34D", padding: "1px 6px", borderRadius: "4px", fontWeight: "700", marginLeft: "4px" }}>
                      Distractor
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
