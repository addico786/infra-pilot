import { useState, useCallback } from "react";
import { ToastType } from "../components/Toast";

interface ToastState {
  message: string;
  type: ToastType;
  id: number;
}

/**
 * Custom hook for managing toast notifications.
 * Provides functions to show toasts and manages toast queue.
 */
export function useToast() {
  const [toasts, setToasts] = useState<ToastState[]>([]);

  const showToast = useCallback((message: string, type: ToastType = "info") => {
    const id = Date.now();
    setToasts((prev) => [...prev, { message, type, id }]);
    return id;
  }, []);

  const removeToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const showSuccess = useCallback((message: string) => showToast(message, "success"), [showToast]);
  const showError = useCallback((message: string) => showToast(message, "error"), [showToast]);
  const showInfo = useCallback((message: string) => showToast(message, "info"), [showToast]);
  const showWarning = useCallback((message: string) => showToast(message, "warning"), [showToast]);

  return {
    toasts,
    showToast,
    removeToast,
    showSuccess,
    showError,
    showInfo,
    showWarning,
  };
}

