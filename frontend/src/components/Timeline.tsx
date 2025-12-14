import { TimelineEvent } from "../types";

interface TimelineProps {
  events: TimelineEvent[];
}

/**
 * Vertical timeline component displaying drift events chronologically.
 * Mobile-friendly with responsive design.
 */
export default function Timeline({ events }: TimelineProps) {
  const getSeverityColor = (severity: string): string => {
    switch (severity) {
      case "info":
        return "#4285f4"; // Blue
      case "low":
        return "#34a853"; // Green
      case "medium":
        return "#fbbc04"; // Yellow
      case "high":
        return "#ea4335"; // Red
      default:
        return "#5f6368"; // Gray
    }
  };

  if (events.length === 0) {
    return (
      <div className="timeline-container">
        <h2>Timeline</h2>
        <p className="empty-state">No timeline events available.</p>
      </div>
    );
  }

  return (
    <div className="timeline-container">
      <h2>Drift Timeline</h2>
      <div className="timeline">
        {events.map((event, index) => (
          <div key={index} className="timeline-item">
            <div
              className="timeline-dot"
              style={{ backgroundColor: getSeverityColor(event.severity) }}
            />
            <div className="timeline-content">
              <div className="timeline-header">
                <span className="timeline-day">Day {event.day}</span>
                <span
                  className="timeline-severity"
                  style={{ color: getSeverityColor(event.severity) }}
                >
                  {event.severity.toUpperCase()}
                </span>
              </div>
              <div className="timeline-event">{event.event}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
