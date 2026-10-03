import React, { useState, useEffect, useRef } from "react";

// ==============================================================================
// PRESET EVALUATION TASKS (Derived strictly from Part 3 & 4 Research)
// ==============================================================================
const EVALUATION_TASKS = [
  {
    id: "TASK-1",
    title: "Task 1: Fuzzy Travel Memory (R7 & R8)",
    description: "Find an old beach sunset photo taken with friend Rohan roughly 3 years ago. No exact date is remembered.",
    defaultPrompt: "Trip to Goa with my friend Rohan around 3 years back at a beach sunset",
    targetPhotoId: "PHOTO-007",
    targetTitle: "Goa Beach Sunset with Rohan",
  },
  {
    id: "TASK-2",
    title: "Task 2: Utility Marksheet Scan (R12 & CLUST-06)",
    description: "Urgently find a saved degree marksheet or transcript scan from college around 2022. Exact filename is unknown.",
    defaultPrompt: "I need to find my university marksheet or degree certificate from college around 2022",
    targetPhotoId: "PHOTO-031",
    targetTitle: "Bachelor of Technology Final Marksheet",
  },
  {
    id: "TASK-3",
    title: "Task 3: Visual Collision Disambiguation (R9 & R14)",
    description: "Find a photo wearing a black and gold outfit on stage during a college ramp walk, rather than at the annual formal dinner.",
    defaultPrompt: "College fest ramp walk on stage wearing a black and gold dress with Maya",
    targetPhotoId: "PHOTO-023",
    targetTitle: "College Fest Ramp Walk in Black & Gold",
  },
  {
    id: "FREEFORM",
    title: "Custom Freeform Memory",
    description: "Search any informal episodic memory in natural language using your own words.",
    defaultPrompt: "",
    targetPhotoId: null,
    targetTitle: null,
  },
];

export default function MemoryAssistant({ onSwitchToWorkbench }) {
  // Session State
  const [selectedTask, setSelectedTask] = useState(EVALUATION_TASKS[0]);
  const [queryText, setQueryText] = useState(EVALUATION_TASKS[0].defaultPrompt);
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

  // Refinement UI State
  const [isRefinementOpen, setIsRefinementOpen] = useState(false);
  const [newClueInput, setNewClueInput] = useState("");
  const [selectedRefinementChip, setSelectedRefinementChip] = useState("");

  // Modals & Completion State
  const [completedSuccessPhoto, setCompletedSuccessPhoto] = useState(null);
  const [isAbandonmentOpen, setIsAbandonmentOpen] = useState(false);
  const [abandonmentReason, setAbandonmentReason] = useState("");
  const [seqRating, setSeqRating] = useState(6);
  const [isDatasetModalOpen, setIsDatasetModalOpen] = useState(false);
  const [datasetRecords, setDatasetRecords] = useState([]);

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

  // Handle Task Switching
  const handleSelectTask = (task) => {
    setSelectedTask(task);
    setQueryText(task.defaultPrompt);
    resetSession(task);
  };

  const resetSession = (task = selectedTask) => {
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
    setIsRefinementOpen(false);
    setNewClueInput("");
    setCompletedSuccessPhoto(null);
    setIsAbandonmentOpen(false);
  };

  // ----------------------------------------------------------------------------
  // 1. EXECUTE INITIAL SEARCH
  // ----------------------------------------------------------------------------
  const handleSearch = async () => {
    if (!queryText.trim()) return;
    setIsLoading(true);
    setSystemMessage("Extracting memory cues and retrieving candidates...");
    const nextAttempts = attemptCount + 1;
    setAttemptCount(nextAttempts);

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
      setCandidates(searchData.results || []);
      setEventClusters(searchData.event_clusters || []);

      setSystemMessage(
        `Retrieved ${searchData.total_candidates} candidate photos matched across ${
          extractedCues.companions?.length || 0
        } person(s), approximate time (${extractedCues.approximate_time || "fuzzy"}), and visual cues.`
      );
    } catch (err) {
      console.error("Search error:", err);
      setSystemMessage("Search encountered an issue. Using offline fallback retrieval.");
    } finally {
      setIsLoading(false);
    }
  };

  // ----------------------------------------------------------------------------
  // 2. ITERATIVE REFINEMENT
  // ----------------------------------------------------------------------------
  const handleRefine = async (explicitChip = null) => {
    const clueToAdd = explicitChip || newClueInput.trim();
    if (!clueToAdd && !explicitChip && rejectedPhotoIds.length === 0) return;

    setIsLoading(true);
    setSystemMessage("Merging new memory cues and re-scoring candidate pool...");
    const nextRefinements = refinementCount + 1;
    setRefinementCount(nextRefinements);
    setAttemptCount((prev) => prev + 1);

    try {
      const res = await fetch("/api/mvp/refine", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          previous_cues: activeCues || {},
          new_clue_text: clueToAdd || "Refining based on rejected candidates",
          selected_chip: explicitChip,
          rejected_photo_ids: rejectedPhotoIds,
          active_task_id: selectedTask.id,
        }),
      });
      const data = await res.json();
      setActiveCues(data.updated_cues);
      setCandidates(data.results || []);
      setSuggestedRefinements(data.suggested_refinements || []);
      setSystemMessage(data.system_message || `Updated candidate pool to ${data.total_candidates} photos.`);
      setNewClueInput("");
      setIsRefinementOpen(false);
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
    setSystemMessage("Removed this photo from suggestions. Using this feedback to narrow your search.");
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

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "var(--bg-main)", color: "var(--text-primary)" }}>
      {/* ==================================================================== */}
      {/* TOP NOTIFICATION & PROTOTYPE BOUNDARY BANNER */}
      {/* ==================================================================== */}
      <div
        style={{
          backgroundColor: "rgba(66, 133, 244, 0.12)",
          borderBottom: "1px solid rgba(66, 133, 244, 0.3)",
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
            Google Photos Memory Retrieval Assistant • Grounded in Part 4 Problem Definition • Controlled Representative Dataset ($N=40$)
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
      <main style={{ maxWidth: "1200px", margin: "0 auto", padding: "24px 20px" }}>
        {/* Title Header */}
        <div style={{ textAlign: "center", marginBottom: "24px" }}>
          <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "28px", fontWeight: "800", color: "#fff", letterSpacing: "-0.5px" }}>
            AI Memory Retrieval Assistant
          </h1>
          <p style={{ color: "var(--text-primary)", fontSize: "16px", fontWeight: "600", marginTop: "6px" }}>
            Can't remember the exact date or filename? Tell me what you remember about the photo.
          </p>
          <p style={{ color: "var(--text-secondary)", fontSize: "13px", marginTop: "4px", maxWidth: "700px", margin: "4px auto 0" }}>
            Describe the people, place, approximate time, event, appearance, or anything else you remember. The AI will turn your memory into searchable clues and help you narrow down the results.
          </p>
          <div
            style={{
              display: "inline-block",
              marginTop: "12px",
              padding: "6px 14px",
              backgroundColor: "rgba(245, 158, 11, 0.12)",
              border: "1px solid rgba(245, 158, 11, 0.35)",
              borderRadius: "20px",
              fontSize: "12px",
              color: "#FBBF24",
              fontWeight: "500",
            }}
          >
            ⚠️ <strong>Prototype Notice</strong>: This is a prototype using a representative photo dataset. It does not access your personal Google Photos.
          </div>
        </div>

        {/* Task Selection Bar */}
        <div
          style={{
            backgroundColor: "var(--bg-surface)",
            border: "1px solid var(--border-subtle)",
            borderRadius: "12px",
            padding: "16px 20px",
            marginBottom: "24px",
          }}
        >
          <div style={{ fontSize: "12px", fontWeight: "600", textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "10px" }}>
            Select a test scenario (or try your own in Freeform):
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "10px" }}>
            {EVALUATION_TASKS.map((t) => {
              const isSelected = selectedTask.id === t.id;
              return (
                <div
                  key={t.id}
                  onClick={() => handleSelectTask(t)}
                  style={{
                    padding: "12px",
                    borderRadius: "8px",
                    cursor: "pointer",
                    border: isSelected ? "2px solid var(--accent-google-blue)" : "1px solid var(--border-subtle)",
                    backgroundColor: isSelected ? "rgba(66, 133, 244, 0.12)" : "var(--bg-card)",
                    transition: "all 0.2s ease",
                  }}
                >
                  <div style={{ fontWeight: "700", fontSize: "13px", color: isSelected ? "#fff" : "var(--text-primary)" }}>
                    {t.title}
                  </div>
                  <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "4px", lineHeight: "1.4" }}>
                    {t.description}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* ================================================================== */}
        {/* CONVERSATIONAL MEMORY INPUT BAR */}
        {/* ================================================================== */}
        <div
          style={{
            backgroundColor: "var(--bg-card)",
            border: "1px solid var(--border-highlight)",
            borderRadius: "16px",
            padding: "20px",
            boxShadow: "var(--shadow-glow)",
            marginBottom: "20px",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <label style={{ fontSize: "14px", fontWeight: "700", color: "#fff" }}>
              Tell me what you remember
            </label>
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                Session: <code>{sessionId}</code> • Attempt #{attemptCount} • Refinements: {refinementCount}
              </span>
              <button
                onClick={handleResetSession}
                title="Start a new photo search and clear the current memory and results."
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
              rows={2}
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              placeholder="I remember a Goa trip with Rohan around 3 years ago, near sunset..."
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
                padding: "14px 24px",
                fontWeight: "700",
                fontSize: "14px",
                cursor: isLoading ? "not-allowed" : "pointer",
                boxShadow: "0 4px 12px rgba(66, 133, 244, 0.4)",
                minWidth: "160px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
              }}
            >
              {isLoading ? "Translating..." : "🔍 Search Memories"}
            </button>
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
        {/* ACTIVE EXTRACTED MEMORY CUES HUD */}
        {/* ================================================================== */}
        {/* ================================================================== */}
        {/* ACTIVE EXTRACTED MEMORY CUES HUD */}
        {/* ================================================================== */}
        {activeCues && (
          <div
            style={{
              backgroundColor: "var(--bg-surface)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "12px",
              padding: "16px 20px",
              marginBottom: "24px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
              <span style={{ fontSize: "14px", fontWeight: "700", color: "#fff" }}>
                🧠 What I understood
              </span>
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                (The AI translated your memory into structured retrieval clues)
              </span>
            </div>

            <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "8px" }}>
              {activeCues.companions?.map((p, i) => (
                <span key={i} style={{ backgroundColor: "rgba(99, 102, 241, 0.15)", color: "#A5B4FC", border: "1px solid rgba(99, 102, 241, 0.3)", padding: "4px 12px", borderRadius: "16px", fontSize: "12px", fontWeight: "600" }}>
                  👤 Person: {p}
                </span>
              ))}

              {activeCues.location && (
                <span style={{ backgroundColor: "rgba(16, 185, 129, 0.15)", color: "#34D399", border: "1px solid rgba(16, 185, 129, 0.3)", padding: "4px 12px", borderRadius: "16px", fontSize: "12px", fontWeight: "600" }}>
                  📍 Location: {activeCues.location}
                </span>
              )}

              {activeCues.approximate_time && (
                <span style={{ backgroundColor: "rgba(245, 158, 11, 0.15)", color: "#FBBF24", border: "1px solid rgba(245, 158, 11, 0.3)", padding: "4px 12px", borderRadius: "16px", fontSize: "12px", fontWeight: "600" }}>
                  🕒 Approximate time: {activeCues.approximate_time}
                </span>
              )}

              {activeCues.visual_attributes?.map((v, i) => (
                <span key={i} style={{ backgroundColor: "rgba(6, 182, 212, 0.15)", color: "#22D3EE", border: "1px solid rgba(6, 182, 212, 0.3)", padding: "4px 12px", borderRadius: "16px", fontSize: "12px", fontWeight: "600" }}>
                  🎨 Visual clue: {v}
                </span>
              ))}

              {activeCues.activity && (
                <span style={{ backgroundColor: "rgba(236, 72, 153, 0.15)", color: "#F472B6", border: "1px solid rgba(236, 72, 153, 0.3)", padding: "4px 12px", borderRadius: "16px", fontSize: "12px", fontWeight: "600" }}>
                  🎯 Activity: {activeCues.activity}
                </span>
              )}

              {activeCues.text_ocr && (
                <span style={{ backgroundColor: "rgba(168, 85, 247, 0.15)", color: "#C084FC", border: "1px solid rgba(168, 85, 247, 0.3)", padding: "4px 12px", borderRadius: "16px", fontSize: "12px", fontWeight: "600" }}>
                  📄 Text / Doc: {activeCues.text_ocr}
                </span>
              )}

              {activeCues.uncertainty && (
                <span style={{ backgroundColor: "rgba(148, 163, 184, 0.15)", color: "#94A3B8", border: "1px solid rgba(148, 163, 184, 0.3)", padding: "4px 12px", borderRadius: "16px", fontSize: "12px", fontWeight: "600" }}>
                  ❓ {activeCues.uncertainty}
                </span>
              )}

              {rejectedPhotoIds.length > 0 && (
                <span style={{ backgroundColor: "rgba(239, 68, 68, 0.15)", color: "#F87171", border: "1px solid rgba(239, 68, 68, 0.3)", padding: "4px 12px", borderRadius: "16px", fontSize: "12px", fontWeight: "600" }}>
                  ✕ {rejectedPhotoIds.length} Excluded
                </span>
              )}
            </div>
          </div>
        )}

        {/* ================================================================== */}
        {/* REFINEMENT DRAWER / PROMPTS */}
        {/* ================================================================== */}
        {(candidates.length > 0 || isRefinementOpen) && (
          <div
            style={{
              backgroundColor: "rgba(14, 20, 36, 0.95)",
              border: "1px solid var(--border-medium)",
              borderRadius: "14px",
              padding: "18px 22px",
              marginBottom: "24px",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "10px" }}>
              <div>
                <div style={{ fontSize: "15px", fontWeight: "700", color: "#fff" }}>
                  🔍 Didn't find the exact photo? Add another clue.
                </div>
                <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "3px" }}>
                  Add anything else you remember — what was happening, what someone was wearing, where you were, what the photo looked like, or another approximate time/place clue.
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

            {/* Quick Refinement Chips */}
            {suggestedRefinements.length > 0 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginBottom: "12px" }}>
                <span style={{ fontSize: "11px", color: "var(--text-muted)", alignSelf: "center" }}>Suggested questions:</span>
                {suggestedRefinements.map((s, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setNewClueInput(s);
                      setIsRefinementOpen(true);
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
            <div style={{ display: "flex", gap: "10px" }}>
              <input
                type="text"
                value={newClueInput}
                onChange={(e) => setNewClueInput(e.target.value)}
                placeholder="e.g., It was on an auditorium stage under spotlights, or he was wearing a blue shirt..."
                style={{
                  flex: 1,
                  backgroundColor: "var(--bg-inset)",
                  border: "1px solid var(--border-medium)",
                  borderRadius: "8px",
                  color: "#fff",
                  padding: "8px 12px",
                  fontSize: "13px",
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
                  padding: "8px 18px",
                  fontWeight: "600",
                  fontSize: "13px",
                  cursor: "pointer",
                }}
              >
                Apply New Clue
              </button>
            </div>
          </div>
        )}

        {/* ================================================================== */}
        {/* CANDIDATE PHOTO RESULTS GRID */}
        {/* ================================================================== */}
        {candidates.length > 0 ? (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
              <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "18px", fontWeight: "700" }}>
                Candidate Photos ({candidates.length} matches)
              </h2>
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                Organized by episodic event context to reduce visual evaluation fatigue
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "18px" }}>
              {candidates.map((cand) => {
                const p = cand.photo;
                const isTarget = selectedTask.targetPhotoId === p.id;
                const isRejected = rejectedPhotoIds.includes(p.id);

                return (
                  <div
                    key={p.id}
                    style={{
                      backgroundColor: "var(--bg-card)",
                      border: isTarget && completedSuccessPhoto?.id === p.id ? "2px solid var(--accent-emerald)" : "1px solid var(--border-subtle)",
                      borderRadius: "14px",
                      overflow: "hidden",
                      display: "flex",
                      flexDirection: "column",
                      boxShadow: "var(--shadow-md)",
                      opacity: isRejected ? 0.35 : 1,
                      transition: "transform 0.2s ease",
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
                              ? "rgba(16, 185, 129, 0.85)"
                              : cand.confidence_level === "EXPLORATORY"
                              ? "rgba(66, 133, 244, 0.85)"
                              : "rgba(148, 163, 184, 0.75)",
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
                    <div style={{ padding: "14px", flex: 1, display: "flex", flexDirection: "column" }}>
                      <div style={{ fontWeight: "700", fontSize: "14px", color: "#fff", marginBottom: "4px" }}>
                        {p.title}
                      </div>
                      <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginBottom: "10px", lineHeight: "1.4" }}>
                        {p.description}
                      </div>

                      {/* Transparent Match Rationales */}
                      <div style={{ backgroundColor: "rgba(255, 255, 255, 0.04)", borderRadius: "8px", padding: "8px 10px", marginBottom: "12px" }}>
                        <div style={{ fontSize: "11px", fontWeight: "700", color: "var(--text-brand)", marginBottom: "4px" }}>
                          Why this result?
                        </div>
                        <ul style={{ listStyle: "none", padding: 0, margin: 0, fontSize: "11px", color: "var(--text-secondary)" }}>
                          {cand.match_reasons.slice(0, 4).map((r, rIdx) => {
                            const cleanR = r.replace("✓", "").trim();
                            return <li key={rIdx} style={{ marginBottom: "2px" }}>✓ {cleanR}</li>;
                          })}
                        </ul>
                      </div>

                      {/* Action Buttons */}
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
          </div>
        ) : (
          !isLoading && (
            <div
              style={{
                backgroundColor: "var(--bg-surface)",
                border: "1px dashed var(--border-medium)",
                borderRadius: "14px",
                padding: "48px 24px",
                textAlign: "center",
                color: "var(--text-secondary)",
              }}
            >
              <div style={{ fontSize: "36px", marginBottom: "12px" }}>📸</div>
              <div style={{ fontSize: "15px", fontWeight: "600", color: "#fff", marginBottom: "6px" }}>
                Ready to search personal memories
              </div>
              <p style={{ maxWidth: "480px", margin: "0 auto", fontSize: "13px", lineHeight: "1.5" }}>
                Select one of the 3 research evaluation tasks above, or describe an informal memory in the search box to test multi-cue retrieval.
              </p>
            </div>
          )
        )}

        {/* ================================================================== */}
        {/* TELEMETRY HUD FOOTER */}
        {/* ================================================================== */}
        <div
          style={{
            marginTop: "36px",
            borderTop: "1px solid var(--border-subtle)",
            paddingTop: "16px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontSize: "12px",
            color: "var(--text-muted)",
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
                const nextTaskIndex = (EVALUATION_TASKS.findIndex((t) => t.id === selectedTask.id) + 1) % EVALUATION_TASKS.length;
                handleSelectTask(EVALUATION_TASKS[nextTaskIndex]);
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
              Log Session & Try Next Retrieval Task →
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
              In accordance with Part 4 research, recording when and why a user gives up is critical for telemetry. Please select the primary reason:
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
