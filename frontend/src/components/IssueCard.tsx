import { Issue, IssueSeverity } from "../types";

interface IssueCardProps {
  issue: Issue;
  onAutofix?: (issue: Issue) => void;
  fileContent?: string;
}

/**
 * Component to display a single issue with AI-enhanced fields.
 * Shows title, severity, explanation, fix suggestion, future impact, and resource.
 */
export default function IssueCard({ issue, onAutofix, fileContent }: IssueCardProps) {
  const getSeverityColor = (severity: IssueSeverity): string => {
    switch (severity) {
      case "low":
        return "#34a853"; // Green
      case "medium":
        return "#fbbc04"; // Yellow
      case "high":
        return "#ff9800"; // Orange
      case "critical":
        return "#ea4335"; // Red
      default:
        return "#5f6368"; // Gray
    }
  };

  const severity = issue.severity;
  const severityColor = getSeverityColor(severity);

  return (
    <div className="issue-card">
      <div className="issue-header">
        <h3 className="issue-title">{issue.title}</h3>
        <span
          className="issue-severity-badge"
          style={{ backgroundColor: severityColor }}
        >
          {severity.toUpperCase()}
        </span>
      </div>

      <div className="issue-id">ID: {issue.id}</div>

      <div className="issue-resource">
        <strong>Resource:</strong> {issue.resource}
      </div>

      {/* AI-enhanced explanation (preferred) or fallback to description */}
      <div className="issue-section">
        <h4>Description</h4>
        <p>{issue.explanation || issue.description}</p>
      </div>

      {/* AI-enhanced fix suggestion */}
      {issue.fix_suggestion && (
        <div className="issue-section issue-fix">
          <h4>Fix Suggestion</h4>
          <p>{issue.fix_suggestion}</p>
        </div>
      )}

      {/* AI-enhanced future impact */}
      {issue.future_impact && (
        <div className="issue-section issue-impact">
          <h4>Future Impact</h4>
          <p>{issue.future_impact}</p>
        </div>
      )}

      {/* Autofix button */}
      {onAutofix && (
        <div className="issue-actions">
          <button
            className="autofix-btn"
            onClick={() => onAutofix(issue)}
            title="Generate automatic fix patch using Cline"
          >
            AutoFix (Beta)
          </button>
        </div>
      )}
    </div>
  );
}
