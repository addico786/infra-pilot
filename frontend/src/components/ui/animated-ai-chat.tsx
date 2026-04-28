"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { cn } from "@/lib/utils";
import { apiUrl } from "@/api/client";
import {
  Paperclip, Command, Sparkles, XIcon,
  LoaderIcon, ChevronDown, FileCode, Server, Cloud,
  Mail, AlertCircle, CheckCircle2, ArrowUpIcon,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import * as React from "react";
import { AnalyzeResponse, FileType } from "@/types";
import DriftScore from "@/components/DriftScore";
import SummaryCard from "@/components/SummaryCard";
import Timeline from "@/components/Timeline";
import IssueCard from "@/components/IssueCard";

const MODEL_OPTIONS = [
  { label: "Llama 3 (Local)", value: "llama3:latest" },
  { label: "DeepSeek-R1 (Local)", value: "deepseek-r1:latest" },
  { label: "WizardLM2 7B (Local)", value: "wizardlm2:7b" },
  { label: "Oumi RL (Specialized)", value: "oumi-rl" },
  { label: "Gemini 2.5 Flash (Cloud)", value: "gemini-2.5-flash" },
];

const FILE_TYPES: { label: string; value: FileType; icon: React.ReactNode }[] = [
  { label: "Terraform", value: "terraform", icon: <Server className="w-3.5 h-3.5" /> },
  { label: "Kubernetes", value: "kubernetes", icon: <Cloud className="w-3.5 h-3.5" /> },
];

type UserMessage = { id: string; role: "user"; content: string; fileName?: string };
type AssistantMessage = {
  id: string; role: "assistant"; content?: string;
  analysisResult?: AnalyzeResponse; isLoading?: boolean; error?: string;
};
type Message = UserMessage | AssistantMessage;

function useAutoResizeTextarea(minHeight: number, maxHeight?: number) {
  const ref = useRef<HTMLTextAreaElement>(null);
  const adjust = useCallback(
    (reset?: boolean) => {
      const el = ref.current;
      if (!el) return;
      if (reset) { el.style.height = `${minHeight}px`; return; }
      el.style.height = `${minHeight}px`;
      el.style.height = `${Math.min(Math.max(minHeight, el.scrollHeight), maxHeight ?? Infinity)}px`;
    },
    [minHeight, maxHeight]
  );
  useEffect(() => { adjust(); }, [adjust]);
  useEffect(() => {
    const handler = () => adjust();
    window.addEventListener("resize", handler);
    return () => window.removeEventListener("resize", handler);
  }, [adjust]);
  return { textareaRef: ref, adjustHeight: adjust };
}

export function AnimatedAIChat() {
  const [value, setValue] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Welcome to InfraPilot. Paste your Terraform or Kubernetes code below and I'll analyze it for drift, security risks, and best practices.",
    },
  ]);
  const [attachments, setAttachments] = useState<{ name: string; content: string }[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [model, setModel] = useState("llama3:latest");
  const [fileType, setFileType] = useState<FileType>("terraform");
  const [email, setEmail] = useState("");
  const [showSettings, setShowSettings] = useState(false);
  const [errorToast, setErrorToast] = useState<string | null>(null);
  const [inputFocused, setInputFocused] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const { textareaRef, adjustHeight } = useAutoResizeTextarea(60, 200);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  useEffect(() => {
    const handler = (e: MouseEvent) => setMousePosition({ x: e.clientX, y: e.clientY });
    window.addEventListener("mousemove", handler);
    return () => window.removeEventListener("mousemove", handler);
  }, []);

  useEffect(() => {
    if (!errorToast) return;
    const t = setTimeout(() => setErrorToast(null), 5000);
    return () => clearTimeout(t);
  }, [errorToast]);

  const handleSend = () => {
    const contentToAnalyze = value.trim() || attachments.map((a) => a.content).join("\n\n");
    if (!contentToAnalyze) return;
    const userMsg: UserMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      content: value.trim() || `[${attachments.length} file(s) attached]`,
      fileName: attachments[0]?.name,
    };
    const thinking: AssistantMessage = { id: `t-${Date.now()}`, role: "assistant", isLoading: true };
    setMessages((prev) => [...prev, userMsg, thinking]);
    setValue("");
    setAttachments([]);
    adjustHeight(true);
    setIsAnalyzing(true);
    void performAnalysis(contentToAnalyze);
  };

  const performAnalysis = async (content: string) => {
    try {
      const body: Record<string, unknown> = { content, file_type: fileType, model };
      if (email.trim()) body.email = email.trim();
      const res = await fetch(apiUrl("/analyze"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`${res.status} ${res.statusText}: ${text}`);
      }
      const data: AnalyzeResponse = await res.json();
      setMessages((prev) => prev.map((m) =>
        m.id.startsWith("t-") ? { ...m, isLoading: false, analysisResult: data } : m
      ));
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Analysis failed";
      setMessages((prev) => prev.map((m) =>
        m.id.startsWith("t-") ? { ...m, isLoading: false, error: msg } : m
      ));
      setErrorToast(msg);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAttach = () => fileInputRef.current?.click();

  const detectFileType = (name: string): FileType => {
    const ext = name.split('.').pop()?.toLowerCase();
    if (ext === 'tf' || ext === 'tfvars' || ext === 'hcl') return 'terraform';
    if (ext === 'yml' || ext === 'yaml' || ext === 'json') return 'kubernetes';
    return fileType;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;
    Array.from(files).forEach((file) => {
      const detected = detectFileType(file.name);
      if (detected !== fileType) setFileType(detected);
      const r = new FileReader();
      r.onload = (ev) => {
        const content = (ev.target?.result as string) || "";
        setAttachments((prev) => [...prev, { name: file.name, content }]);
        if (!value.trim()) { setValue(content); adjustHeight(); }
      };
      r.readAsText(file);
    });
    e.target.value = "";
  };

  const removeAttachment = (i: number) => setAttachments((prev) => prev.filter((_, idx) => idx !== i));

  const currentModelLabel = MODEL_OPTIONS.find((m) => m.value === model)?.label || model;

  return (
    <div className="min-h-screen flex flex-col w-full bg-[#0A0A0B] text-white p-4 md:p-6 relative overflow-hidden">
      {/* Ambient orbs */}
      <div className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet-500/10 rounded-full mix-blend-normal filter blur-[128px] animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full mix-blend-normal filter blur-[128px] animate-pulse delay-700" />
        <div className="absolute top-1/4 right-1/3 w-64 h-64 bg-fuchsia-500/10 rounded-full mix-blend-normal filter blur-[96px] animate-pulse delay-1000" />
      </div>

      {inputFocused && (
        <motion.div
          className="fixed w-[50rem] h-[50rem] rounded-full pointer-events-none z-0 opacity-[0.02] bg-gradient-to-r from-violet-500 via-fuchsia-500 to-indigo-500 blur-[96px]"
          animate={{ x: mousePosition.x - 400, y: mousePosition.y - 400 }}
          transition={{ type: "spring", damping: 25, stiffness: 150, mass: 0.5 }}
        />
      )}

      {/* Error toast */}
      <AnimatePresence>
        {errorToast && (
          <motion.div
            initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}
            className="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-red-500/90 backdrop-blur-md text-white px-4 py-2.5 rounded-lg text-sm font-medium shadow-lg flex items-center gap-2"
          >
            <AlertCircle className="w-4 h-4" /> {errorToast}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <motion.header
        className="relative z-30 flex items-center justify-between mb-6"
        initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}
      >
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-500 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <span className="font-semibold text-lg tracking-tight">InfraPilot</span>
        </div>
        <div className="relative z-30 group">
          <button className="flex items-center gap-1.5 px-3 py-1.5 bg-white/5 hover:bg-white/10 rounded-lg text-xs text-white/70 hover:text-white transition-colors border border-white/5">
            <Server className="w-3 h-3" />
            <span className="max-w-[120px] truncate">{currentModelLabel}</span>
            <ChevronDown className="w-3 h-3 opacity-50" />
          </button>
          <div className="absolute right-0 top-full mt-1 w-56 bg-[#141414] border border-white/10 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50 overflow-hidden">
            {MODEL_OPTIONS.map((m) => (
              <button
                key={m.value}
                onClick={() => setModel(m.value)}
                className={cn(
                  "w-full text-left px-3 py-2 text-xs transition-colors flex items-center gap-2",
                  model === m.value ? "bg-white/10 text-white" : "text-white/60 hover:bg-white/5 hover:text-white/90"
                )}
              >
                {m.value.startsWith("gemini") ? <Cloud className="w-3 h-3" /> : <Server className="w-3 h-3" />}
                {m.label}
              </button>
            ))}
          </div>
        </div>
      </motion.header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto relative z-10 space-y-6 max-w-3xl mx-auto w-full pb-4">
        <AnimatePresence mode="popLayout">
          {messages.map((msg) => (
            <motion.div
              key={msg.id} layout initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, scale: 0.98 }}
              transition={{ duration: 0.3 }}
              className={cn("flex", msg.role === "user" ? "justify-end" : "justify-start")}
            >
              {msg.role === "user" ? (
                <div className="max-w-[85%] md:max-w-[75%] bg-white/10 backdrop-blur-md rounded-2xl rounded-tr-sm px-4 py-3 border border-white/5">
                  {msg.fileName && (
                    <div className="flex items-center gap-2 text-xs text-white/50 mb-2">
                      <FileCode className="w-3.5 h-3.5" /> {msg.fileName}
                    </div>
                  )}
                  <pre className="text-sm text-white/90 whitespace-pre-wrap font-mono leading-relaxed overflow-x-auto">{msg.content}</pre>
                </div>
              ) : msg.isLoading ? (
                <div className="max-w-[85%] md:max-w-[75%] bg-white/[0.03] backdrop-blur-md rounded-2xl rounded-tl-sm px-4 py-3 border border-white/5">
                  <div className="flex items-center gap-3 text-sm text-white/60">
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-violet-500 to-indigo-500 flex items-center justify-center">
                      <Sparkles className="w-3.5 h-3.5 text-white" />
                    </div>
                    <span>Analyzing infrastructure...</span>
                    <TypingDots />
                  </div>
                </div>
              ) : msg.error ? (
                <div className="max-w-[85%] md:max-w-[75%] bg-red-500/10 backdrop-blur-md rounded-2xl rounded-tl-sm px-4 py-3 border border-red-500/20">
                  <div className="flex items-center gap-2 text-sm text-red-300">
                    <AlertCircle className="w-4 h-4" /> {msg.error}
                  </div>
                </div>
              ) : msg.analysisResult ? (
                <div className="w-full max-w-3xl space-y-4">
                  <div className="flex items-center gap-2 text-sm text-emerald-400 mb-2">
                    <CheckCircle2 className="w-4 h-4" /> <span>Analysis complete</span>
                  </div>
                  <div className="bg-white/[0.03] backdrop-blur-md rounded-xl border border-white/5 p-4">
                    <DriftScore score={msg.analysisResult.drift_score} />
                  </div>
                  <div className="bg-white/[0.03] backdrop-blur-md rounded-xl border border-white/5 p-4">
                    <SummaryCard result={msg.analysisResult} />
                  </div>
                  <div className="bg-white/[0.03] backdrop-blur-md rounded-xl border border-white/5 p-4">
                    <Timeline events={msg.analysisResult.timeline} />
                  </div>
                  {msg.analysisResult.issues.length > 0 && (
                    <div className="space-y-3">
                      <h3 className="text-sm font-medium text-white/70 flex items-center gap-2">
                        <AlertCircle className="w-4 h-4" />
                        Found {msg.analysisResult.issues.length} issue{msg.analysisResult.issues.length > 1 ? "s" : ""}
                      </h3>
                      {msg.analysisResult.issues.map((issue) => (
                        <div key={issue.id} className="bg-white/[0.03] backdrop-blur-md rounded-xl border border-white/5 p-4">
                          <IssueCard issue={issue} />
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="max-w-[85%] md:max-w-[75%] bg-white/[0.03] backdrop-blur-md rounded-2xl rounded-tl-sm px-4 py-3 border border-white/5">
                  <div className="flex items-start gap-3">
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-violet-500 to-indigo-500 flex items-center justify-center shrink-0 mt-0.5">
                      <Sparkles className="w-3.5 h-3.5 text-white" />
                    </div>
                    <p className="text-sm text-white/80 whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <motion.div
        className="relative z-10 w-full max-w-3xl mx-auto mt-4"
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.2 }}
      >
        <AnimatePresence>
          {showSettings && (
            <motion.div
              initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}
              className="mb-2 bg-white/[0.03] backdrop-blur-md rounded-xl border border-white/5 p-3 flex flex-wrap items-center gap-3 overflow-hidden"
            >
              <div className="flex items-center gap-1">
                <span className="text-xs text-white/40 mr-1">Type:</span>
                {FILE_TYPES.map((ft) => (
                  <button
                    key={ft.value}
                    onClick={() => setFileType(ft.value)}
                    className={cn(
                      "flex items-center gap-1 px-2.5 py-1 rounded-md text-xs transition-colors",
                      fileType === ft.value ? "bg-white/15 text-white" : "bg-white/5 text-white/50 hover:bg-white/10 hover:text-white/80"
                    )}
                  >
                    {ft.icon} {ft.label}
                  </button>
                ))}
              </div>
              <div className="flex items-center gap-1.5 flex-1 min-w-[200px]">
                <Mail className="w-3.5 h-3.5 text-white/30" />
                <input
                  type="email"
                  placeholder="Email results to..."
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="bg-transparent text-xs text-white/70 placeholder:text-white/30 outline-none w-full"
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="relative backdrop-blur-2xl bg-white/[0.02] rounded-2xl border border-white/[0.05] shadow-2xl">
          <div className="p-4">
            <textarea
              ref={textareaRef}
              value={value}
              onChange={(e) => { setValue(e.target.value); adjustHeight(); }}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  if (value.trim() || attachments.length > 0) handleSend();
                }
              }}
              onFocus={() => setInputFocused(true)}
              onBlur={() => setInputFocused(false)}
              placeholder="Paste your Terraform or Kubernetes code here..."
              className="w-full resize-none bg-transparent border-none text-white/90 text-sm focus:outline-none placeholder:text-white/25 min-h-[60px]"
              style={{ overflow: "hidden" }}
              rows={1}
            />
          </div>

          <AnimatePresence>
            {attachments.length > 0 && (
              <motion.div className="px-4 pb-2 flex gap-2 flex-wrap" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}>
                {attachments.map((file, i) => (
                  <motion.div key={i} className="flex items-center gap-2 text-xs bg-white/[0.05] py-1.5 px-3 rounded-lg text-white/70 border border-white/5" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }}>
                    <FileCode className="w-3 h-3" /> <span>{file.name}</span>
                    <button onClick={() => removeAttachment(i)} className="text-white/40 hover:text-white transition-colors"><XIcon className="w-3 h-3" /></button>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          <div className="p-3 border-t border-white/[0.05] flex items-center justify-between gap-3">
            <div className="flex items-center gap-1.5">
              <input ref={fileInputRef} type="file" className="hidden" onChange={handleFileChange} accept=".tf,.tfvars,.yml,.yaml,.json,.txt" />
              <motion.button type="button" onClick={handleAttach} whileTap={{ scale: 0.94 }} className="p-2 text-white/40 hover:text-white/90 rounded-lg transition-colors" title="Attach file">
                <Paperclip className="w-4 h-4" />
              </motion.button>
              <motion.button type="button" onClick={() => setShowSettings((p) => !p)} whileTap={{ scale: 0.94 }} className={cn("p-2 text-white/40 hover:text-white/90 rounded-lg transition-colors", showSettings && "bg-white/10 text-white/90")} title="Settings">
                <Command className="w-4 h-4" />
              </motion.button>
              <div className="hidden sm:flex items-center gap-1 px-2 py-1 bg-white/5 rounded-md text-xs text-white/40">
                {FILE_TYPES.find((ft) => ft.value === fileType)?.icon}
                <span>{FILE_TYPES.find((ft) => ft.value === fileType)?.label}</span>
              </div>
            </div>
            <motion.button
              type="button"
              onClick={handleSend}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              disabled={isAnalyzing || (!value.trim() && attachments.length === 0)}
              className={cn(
                "px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2",
                value.trim() || attachments.length > 0
                  ? "bg-white text-[#0A0A0B] shadow-lg shadow-white/10 hover:bg-white/90"
                  : "bg-white/[0.05] text-white/30 cursor-not-allowed"
              )}
            >
              {isAnalyzing ? <LoaderIcon className="w-4 h-4 animate-spin" /> : <ArrowUpIcon className="w-4 h-4" />}
              <span>{isAnalyzing ? "Analyzing..." : "Analyze"}</span>
            </motion.button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

function TypingDots() {
  return (
    <div className="flex items-center ml-1">
      {[1, 2, 3].map((dot) => (
        <motion.div
          key={dot}
          className="w-1.5 h-1.5 bg-white/90 rounded-full mx-0.5"
          initial={{ opacity: 0.3 }}
          animate={{ opacity: [0.3, 0.9, 0.3], scale: [0.85, 1.1, 0.85] }}
          transition={{ duration: 1.2, repeat: Infinity, delay: dot * 0.15, ease: "easeInOut" }}
        />
      ))}
    </div>
  );
}
