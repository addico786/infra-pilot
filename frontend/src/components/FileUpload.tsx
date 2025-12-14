import { useRef, ChangeEvent } from "react";

interface FileUploadProps {
  onFileLoad: (content: string, filename: string) => void;
  accept?: string;
}

/**
 * Reusable file upload component that reads text files.
 * Accepts .tf, .yaml, .yml files and passes content to parent via callback.
 */
export default function FileUpload({ onFileLoad, accept = ".tf,.yaml,.yml" }: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file extension
    const fileName = file.name.toLowerCase();
    const validExtensions = [".tf", ".yaml", ".yml"];
    const isValidExtension = validExtensions.some((ext) => fileName.endsWith(ext));

    if (!isValidExtension) {
      alert("Please select a .tf, .yaml, or .yml file");
      return;
    }

    // Read file content as text
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      onFileLoad(content, file.name);
    };
    reader.onerror = () => {
      alert("Error reading file. Please try again.");
    };
    reader.readAsText(file);
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="file-upload">
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        onChange={handleFileChange}
        style={{ display: "none" }}
      />
      <button type="button" onClick={handleButtonClick} className="file-upload-button">
        Choose File
      </button>
    </div>
  );
}

