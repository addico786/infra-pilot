import { useState } from "react";

interface PatchViewerProps {
  patch: string;
  onClose: () => void;
  onApply?: () => void;
}

/**
 * Component for displaying and interacting with generated patches.
 * Shows unified diff format patches with syntax highlighting.
 * Supports copying to clipboard and applying patches.
 */
export default function PatchViewer({ patch, onClose, onApply }: PatchViewerProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(patch);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy patch:", err);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content patch-viewer" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Generated Patch</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          <pre className="patch-content">{patch || "No patch generated."}</pre>
        </div>
        <div className="modal-footer">
          <button onClick={handleCopy} className="copy-button">
            {copied ? "✓ Copied!" : "Copy to Clipboard"}
          </button>
          {onApply && (
            <button onClick={onApply} className="apply-button">
              Apply Patch
            </button>
          )}
          <button onClick={onClose} className="close-button">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

