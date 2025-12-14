interface DriftScoreProps {
  score: number;
}

/**
 * Component to display the drift score.
 * Score ranges from 0.0 to 1.0, displayed as a percentage.
 */
export default function DriftScore({ score }: DriftScoreProps) {
  const percentage = Math.round(score * 100);
  
  // Determine color based on score
  const getScoreColor = () => {
    if (score < 0.3) return "#34a853"; // Green (low drift)
    if (score < 0.6) return "#fbbc04"; // Yellow (medium drift)
    if (score < 0.8) return "#ff9800"; // Orange (high drift)
    return "#ea4335"; // Red (critical drift)
  };

  return (
    <div className="drift-score-card">
      <h2>Drift Score</h2>
      <div className="score-display">
        <div className="score-circle" style={{ color: getScoreColor() }}>
          {percentage}%
        </div>
        <div className="score-bar-container">
          <div 
            className="score-bar-fill" 
            style={{ 
              width: `${percentage}%`,
              backgroundColor: getScoreColor()
            }}
          />
        </div>
      </div>
      <p className="score-description">
        {score < 0.3 && "Low drift detected. Infrastructure is well-aligned."}
        {score >= 0.3 && score < 0.6 && "Moderate drift detected. Review recommended."}
        {score >= 0.6 && score < 0.8 && "High drift detected. Action required."}
        {score >= 0.8 && "Critical drift detected. Immediate attention needed."}
      </p>
    </div>
  );
}

