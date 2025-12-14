import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

// Debug: Check if root element exists
const rootElement = document.getElementById("root");
if (!rootElement) {
  const errorMsg = "[Main] ERROR: Root element not found!";
  console.error(errorMsg);
  document.body.innerHTML = `<div style="padding: 2rem; color: red; font-family: monospace;">${errorMsg}<br/>Please check index.html</div>`;
  throw new Error(errorMsg);
}

console.log("[Main] Root element found:", rootElement);
console.log("[Main] Starting React app...");
console.log("[Main] React version:", React.version);

try {
  const root = ReactDOM.createRoot(rootElement);
  
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
  
  console.log("[Main] React app mounted successfully");
  console.log("[Main] Root element content:", rootElement.innerHTML.substring(0, 100));
} catch (error) {
  const errorMsg = `[Main] ERROR mounting React: ${error}`;
  console.error(errorMsg, error);
  rootElement.innerHTML = `<div style="padding: 2rem; color: red; font-family: monospace;">${errorMsg}<br/>Check console for details</div>`;
  throw error;
}
