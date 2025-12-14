import { AnalyzeResponse } from "../types";

interface SummaryCardProps {
  result: AnalyzeResponse;
}

/**
 * Summary card component displaying key analysis metrics.
 * Shows drift score, issue count, AI provider, and model used.
 */
export default function SummaryCard({ result }: SummaryCardProps) {
  const percentage = Math.round(result.drift_score * 100);
  const issuesCount = result.issues.length;
  const timelineEventsCount = result.timeline.length;

  const getScoreColor = () => {
    if (result.drift_score < 0.3) return "#34a853"; // Green
    if (result.drift_score < 0.6) return "#fbbc04"; // Yellow
    if (result.drift_score < 0.8) return "#ff9800"; // Orange
    return "#ea4335"; // Red
  };

  return (
    <div className="summary-card">
      <h2>Analysis Summary</h2>
      <div className="summary-grid">
        <div className="summary-item">
          <div className="summary-label">Drift Score</div>
          <div className="summary-value" style={{ color: getScoreColor() }}>
            {percentage}%
          </div>
        </div>
        <div className="summary-item">
          <div className="summary-label">Issues Found</div>
          <div className="summary-value">{issuesCount}</div>
        </div>
        <div className="summary-item">
          <div className="summary-label">Timeline Events</div>
          <div className="summary-value">{timelineEventsCount}</div>
        </div>
        {result.provider && (
          <div className="summary-item">
            <div className="summary-label">AI Provider</div>
            <div className="summary-value">{result.provider}</div>
          </div>
        )}
        {result.model && (
          <div className="summary-item">
            <div className="summary-label">Model Used</div>
            <div className="summary-value">{result.model}</div>
          </div>
        )}
      </div>
    </div>
  );
}

