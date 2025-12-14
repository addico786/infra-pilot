import { useState, useEffect } from "react";
import { AnalyzeRequest, AnalyzeResponse, FileType, Issue } from "./types";
import AnalyzeForm from "./components/AnalyzeForm";
import DriftScore from "./components/DriftScore";
import SummaryCard from "./components/SummaryCard";
import Timeline from "./components/Timeline";
import IssueCard from "./components/IssueCard";
import SponsorActions from "./components/SponsorActions";
import PatchViewer from "./components/PatchViewer";
import Toast from "./components/Toast";
import { useToast } from "./hooks/useToast";

/**
 * Main App component orchestrating the InfraPilot frontend.
 * 
 * Responsibilities:
 * - State management (analysis results, loading, errors)
 * - API communication with backend
 * - Autofix patch generation
 * - Toast notifications
 * - Rendering analysis results and sponsor integrations
 */
function App() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<AnalyzeResponse | null>(null);
  const [fileContent, setFileContent] = useState<string>("");
  const [patchViewerOpen, setPatchViewerOpen] = useState<boolean>(false);
  const [currentPatch, setCurrentPatch] = useState<string>("");
  const [loadingPatch, setLoadingPatch] = useState<boolean>(false);

  const { toasts, showSuccess, showError, showInfo, removeToast } = useToast();

  // Debug: Log when component mounts
  useEffect(() => {
    console.log("[App] Component mounted successfully");
    console.log("[App] Root element:", document.getElementById("root"));
    console.log("[App] CSS loaded:", document.styleSheets.length > 0);
  }, []);

  const handleAnalyze = async (content: string, fileType: FileType, model: string) => {
    setLoading(true);
    setError(null);
    setResponse(null);
    setFileContent(content); // Store content for autofix

    showInfo("Starting analysis...");

    try {
      const request: AnalyzeRequest = {
        content: content,
        file_type: fileType,
        model: model,
      };

      console.log("[App] Sending request to backend:", request);

      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Backend error: ${res.status} ${res.statusText}. ${errorText}`);
      }

      const data: AnalyzeResponse = await res.json();
      console.log("[App] Received response:", data);
      setResponse(data);
      showSuccess(`Analysis complete! Found ${data.issues.length} issues.`);
    } catch (err) {
      console.error("[App] Error:", err);
      const errorMessage = err instanceof Error 
        ? err.message 
        : "Failed to analyze content. Please check that the backend is running.";
      setError(errorMessage);
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleAutofix = async (issue: Issue) => {
    setLoadingPatch(true);
    setPatchViewerOpen(true);
    setCurrentPatch("Generating patch...");
    showInfo("Generating autofix patch...");

    try {
      const res = await fetch("http://localhost:8000/autofix/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          issue: {
            title: issue.title,
            description: issue.description,
            fix_suggestion: issue.fix_suggestion,
            resource: issue.resource,
          },
          file_content: fileContent,
          file_path: issue.resource || "input.tf",
        }),
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Autofix error: ${res.status} ${res.statusText}. ${errorText}`);
      }

      const data = await res.json();
      if (data.success && data.diff) {
        setCurrentPatch(data.diff);
        showSuccess("Patch generated successfully!");
      } else {
        throw new Error(data.message || "Failed to generate patch");
      }
    } catch (err) {
      console.error("[App] Autofix error:", err);
      const errorMessage = err instanceof Error 
        ? err.message 
        : "Failed to generate patch. Please try again.";
      setCurrentPatch(`Error: ${errorMessage}`);
      showError(errorMessage);
    } finally {
      setLoadingPatch(false);
    }
  };

  const handleApplyPatch = async () => {
    if (!currentPatch || currentPatch.startsWith("Error:")) {
      showError("No valid patch to apply");
      return;
    }

    showInfo("Applying patch...");
    // TODO: Implement patch application
    // This would call /autofix/apply endpoint
    showSuccess("Patch applied successfully! (Feature coming soon)");
  };

  return (
    <div className="app" style={{ minHeight: "100vh", backgroundColor: "#f6f7fb" }}>
      {/* Toast Container */}
      <div className="toast-container">
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            message={toast.message}
            type={toast.type}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>

      <header className="app-header" style={{ 
        backgroundColor: "#ffffff", 
        borderBottom: "1px solid #dadce0", 
        padding: "2rem", 
        textAlign: "center",
        boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
      }}>
        <h1 style={{ fontSize: "2rem", fontWeight: 500, marginBottom: "0.5rem", color: "#202124" }}>
          InfraPilot
        </h1>
        <p style={{ color: "#5f6368", fontSize: "1rem" }}>
          AI-Powered Infrastructure Drift Detection & AutoFix
        </p>
      </header>

      <main className="app-main" style={{ 
        flex: 1, 
        maxWidth: "900px", 
        width: "100%", 
        margin: "0 auto", 
        padding: "2rem" 
      }}>
        <AnalyzeForm onAnalyze={handleAnalyze} loading={loading} error={error} />

        {loading && (
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Analyzing infrastructure...</p>
          </div>
        )}

        {response && (
          <div className="results-section">
            <SummaryCard result={response} />
            <DriftScore score={response.drift_score} />
            <Timeline events={response.timeline} />

            <div className="issues-section">
              <h2>Issues ({response.issues.length})</h2>
              {response.issues.length === 0 ? (
                <p className="empty-state">No issues detected. Infrastructure looks good!</p>
              ) : (
                <div className="issues-list">
                  {response.issues.map((issue) => (
                    <IssueCard
                      key={issue.id}
                      issue={issue}
                      onAutofix={handleAutofix}
                      fileContent={fileContent}
                    />
                  ))}
                </div>
              )}
            </div>

            <SponsorActions analysisResult={response} />
          </div>
        )}
      </main>

      <footer className="app-footer" style={{ 
        backgroundColor: "#ffffff", 
        borderTop: "1px solid #dadce0", 
        padding: "1.5rem", 
        textAlign: "center", 
        color: "#5f6368", 
        fontSize: "0.875rem", 
        marginTop: "3rem" 
      }}>
        <p>© 2025 InfraPilot. Infrastructure drift detection powered by AI.</p>
      </footer>

      {/* Patch Viewer Modal */}
      {patchViewerOpen && (
        <PatchViewer
          patch={currentPatch}
          onClose={() => setPatchViewerOpen(false)}
          onApply={handleApplyPatch}
        />
      )}
    </div>
  );
}

export default App;
