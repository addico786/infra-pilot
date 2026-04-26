import { useState } from "react";
import { FileType } from "../types";
import FileUpload from "./FileUpload";

interface AnalyzeFormProps {
  onAnalyze: (content: string, fileType: FileType, model: string, email?: string) => void;
  loading: boolean;
  error: string | null;
}

/**
 * AI Model options with labels.
 * 
 * Model Selection Flow:
 * 1. User selects a model from this dropdown
 * 2. The selected model value (e.g., "gemini-2.5-flash") is stored in selectedModel state
 * 3. When user clicks "Analyze", handleSubmit() calls onAnalyze(content, fileType, selectedModel)
 * 4. App.tsx receives the model name and includes it in the API request: { content, file_type, model }
 * 5. Backend receives the model parameter and routes to the appropriate AI provider:
 *    - "gemini-2.5-flash" → GeminiClient with model="gemini-2.5-flash"
 *    - "llama3:latest" → LocalOllamaClient with model="llama3:latest"
 *    - "oumi-rl" → Uses Oumi RL for scoring, falls back to default provider for analysis
 * 
 * The backend's _get_provider_and_model() function maps these friendly names to actual
 * provider clients and model IDs.
 * 
 * IMPORTANT: Local model names must match what's available in your Ollama installation.
 * To see available models, run: `ollama list`
 * To change which model is used, either:
 *   - Select a different model from this dropdown, OR
 *   - Set OLLAMA_MODEL in your backend .env file (e.g., OLLAMA_MODEL=llama3:latest)
 * 
 * Common Ollama model names:
 * - llama3:latest (or llama3:8b, llama3:70b for specific versions)
 * - wizardlm2:latest (or wizardlm2:7b for specific version)
 * - qwen2.5:latest (or qwen2.5:7b, qwen2.5:14b for specific versions)
 * - deepseek-r1:latest (or deepseek-r1:8b for specific version)
 */
export const MODEL_OPTIONS = [
  // Local models (require Ollama running)
  // NOTE: Use ":latest" tag to use the latest version of the model, or specify version like ":7b"
  // To see available models: run `ollama list` in your terminal
  { value: "llama3:latest", label: "Llama 3 (Local)" },
  { value: "deepseek-r1:latest", label: "DeepSeek-R1 (Local)" },
  { value: "wizardlm2:7b", label: "WizardLM2 7B (Local)" },
  // Cloud models (require GEMINI_API_KEY)
  { value: "gemini-2.5-flash", label: "Gemini 2.5 Flash (Cloud)" },
  // Scoring-only option
  { value: "oumi-rl", label: "Oumi RL (Specialized)" },
] as const;

/**
 * Form component for infrastructure analysis.
 * Supports both textarea input and file upload.
 * Auto-loads file content into textarea when file is selected.
 * Includes AI model selector for choosing the analysis engine.
 */
export default function AnalyzeForm({ onAnalyze, loading, error }: AnalyzeFormProps) {
  const [content, setContent] = useState<string>("");
  const [fileType, setFileType] = useState<FileType>("terraform");
  // Default to llama3:latest (most common Ollama model)
  // Users can change this via the dropdown, or backend will use OLLAMA_MODEL from .env if no model is sent
  const [selectedModel, setSelectedModel] = useState<string>("llama3:latest");
  const [selectedFileName, setSelectedFileName] = useState<string>("");
  const [email, setEmail] = useState<string>("");

  const handleFileLoad = (fileContent: string, filename: string) => {
    setContent(fileContent);
    setSelectedFileName(filename);
    
    // Auto-detect file type based on extension
    const ext = filename.toLowerCase().split(".").pop();
    if (ext === "tf") {
      setFileType("terraform");
    } else if (ext === "yaml" || ext === "yml") {
      setFileType("kubernetes");
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) {
      return;
    }
    // Pass the selected model to the parent component
    // The model value (e.g., "gemini-2.5-flash") will be sent to the backend API
    // Backend will route to the appropriate AI provider based on this model name
    const trimmedEmail = email.trim();
    onAnalyze(content.trim(), fileType, selectedModel, trimmedEmail ? trimmedEmail : undefined);
  };

  return (
    <form className="analyze-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="content">
          Infrastructure Code
          {selectedFileName && <span className="file-name"> ({selectedFileName})</span>}
        </label>
        <div className="input-wrapper">
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Paste your Terraform or Kubernetes YAML here, or upload a file..."
            rows={12}
            className="code-textarea"
            disabled={loading}
          />
          <div className="file-upload-wrapper">
            <FileUpload onFileLoad={handleFileLoad} />
          </div>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="file-type">File Type</label>
        <select
          id="file-type"
          value={fileType}
          onChange={(e) => setFileType(e.target.value as FileType)}
          disabled={loading}
        >
          <option value="terraform">Terraform</option>
          <option value="kubernetes">Kubernetes</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="model">AI Model</label>
        <select
          id="model"
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          disabled={loading}
        >
          {MODEL_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <p className="form-hint">
          Select the AI model to use for analysis. Local models require Ollama running.
          <br />
          <strong>Tip:</strong> If your model isn't listed, set OLLAMA_MODEL in backend .env file.
          To see available models, run: <code>ollama list</code>
        </p>
      </div>

      <div className="form-group">
        <label htmlFor="email">Email results to (optional)</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          disabled={loading}
        />
        <p className="form-hint">
          If provided, the backend can email the analysis summary (must be enabled in backend `.env`).
        </p>
      </div>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      <button type="submit" className="analyze-button" disabled={loading || !content.trim()}>
        {loading ? "Analyzing..." : "Analyze"}
      </button>
    </form>
  );
}
