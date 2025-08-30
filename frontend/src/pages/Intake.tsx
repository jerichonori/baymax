import { useEffect, useRef, useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Button } from "../components/ui/button";
import { SegmentedToggle } from "../components/ui/segmented-toggle";

type Message = {
  id: string;
  role: "user" | "ai";
  content: string;
  language?: string;
};

// language auto-detect is handled heuristically from content (stub)

export default function IntakePage() {
  const [detectedLang, setDetectedLang] = useState("en");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "m1",
      role: "ai",
      content:
        "Welcome. I will ask a few questions to understand your concern. I won't diagnose. What brings you in today?",
      language: "en",
    },
  ]);

  // Voice recording (stubbed)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordError, setRecordError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"voice" | "text">("voice");
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const [showComposerFade, setShowComposerFade] = useState(false);

  function autoResize() {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    const max = 80; // px; ~3 lines
    const next = Math.min(el.scrollHeight, max);
    el.style.height = `${next}px`;
    const isOverflowing = el.scrollHeight > max;
    el.style.overflowY = isOverflowing ? "auto" : "hidden";
    setShowComposerFade(isOverflowing);
  }

  useEffect(() => {
    autoResize();
  }, [input]);
  const [showTranscript, setShowTranscript] = useState(false);

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream);
      const chunks: BlobPart[] = [];
      mr.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data);
      };
      mr.onstop = () => {
        // In production, send chunks to STT; here we simulate a transcript
        const fakeTranscript = "I have knee pain";
        handleTranscript(fakeTranscript);
        stream.getTracks().forEach((t) => t.stop());
      };
      mediaRecorderRef.current = mr;
      mr.start();
      setIsRecording(true);
      setRecordError(null);
    } catch (_err) {
      setRecordError("Microphone permission denied or unsupported.");
    }
  }

  function stopRecording() {
    const mr = mediaRecorderRef.current;
    if (mr && mr.state !== "inactive") {
      mr.stop();
      setIsRecording(false);
    }
  }

  function handleTranscript(text: string) {
    const looksHindi = /[\u0900-\u097F]/.test(text);
    setDetectedLang(looksHindi ? "hi" : "en");
    setInput(text);
  }

  function send() {
    if (!input.trim()) return;
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: input,
      language: detectedLang,
    };
    const aiMsg: Message = {
      id: crypto.randomUUID(),
      role: "ai",
      content: "Thanks. When did this start? Any injury? (stub)",
      language: detectedLang,
    };
    setMessages((prev) => [...prev, userMsg, aiMsg]);
    setInput("");
  }

  return (
    <section className="grid gap-6">
      <div className="space-y-6">
        {/* External controls bar */}
        <div className="flex items-center justify-end gap-2">
          <label className="inline-flex cursor-pointer items-center gap-1 rounded-md bg-white/70 px-2.5 py-1.5 text-xs text-gray-700 shadow-sm ring-1 ring-black/5 backdrop-blur transition hover:bg-white/90">
            <Input type="file" className="hidden" />
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-3.5 w-3.5"
            >
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 1 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66L9.88 16.75a2 2 0 1 1-2.83-2.83l8.49-8.49" />
            </svg>
            <span>Attach</span>
          </label>
          <SegmentedToggle<"voice" | "text">
            options={[
              { label: "Voice", value: "voice" },
              { label: "Text", value: "text" },
            ]}
            value={viewMode}
            onChange={setViewMode}
          />
        </div>

        {viewMode === "voice" ? (
          <Card>
            <CardContent className="grid min-h-[70vh] place-items-center py-6">
              <div className="flex flex-col items-center gap-6">
                <button
                  type="button"
                  onClick={() =>
                    isRecording ? stopRecording() : startRecording()
                  }
                  className={`relative grid h-28 w-28 place-items-center rounded-2xl shadow-md transition ${
                    isRecording
                      ? "bg-gradient-to-br from-rose-600 to-red-600 text-white hover:brightness-110"
                      : "bg-white/70 text-blue-700 ring-1 ring-black/5 backdrop-blur hover:bg-white/80"
                  }`}
                  aria-pressed={isRecording}
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-9 w-9"
                    aria-hidden
                  >
                    <path d="M12 3a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V6a3 3 0 0 1 3-3" />
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                    <path d="M12 19v3" />
                    <path d="M8 22h8" />
                  </svg>
                  {isRecording && (
                    <span className="absolute -inset-2 rounded-2xl ring-2 ring-rose-400/50 animate-pulse" />
                  )}
                </button>

                {isRecording && (
                  <div className="flex items-end gap-1 text-blue-700">
                    <span
                      className="eq-bar"
                      style={{ animationDelay: "0ms" }}
                    />
                    <span
                      className="eq-bar"
                      style={{ animationDelay: "120ms" }}
                    />
                    <span
                      className="eq-bar"
                      style={{ animationDelay: "240ms" }}
                    />
                    <span
                      className="eq-bar"
                      style={{ animationDelay: "360ms" }}
                    />
                    <span
                      className="eq-bar"
                      style={{ animationDelay: "480ms" }}
                    />
                  </div>
                )}

                {recordError && (
                  <div className="text-xs text-red-600">{recordError}</div>
                )}

                <div className="text-xs text-gray-600">
                  {isRecording ? "Listening…" : "Tap to start speaking"}
                </div>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="flex h-[70vh] flex-col gap-3">
              <div className="flex-1 min-h-0 space-y-2 overflow-auto p-3">
                {messages.map((m) => (
                  <div
                    key={m.id}
                    className={m.role === "user" ? "text-right" : "text-left"}
                  >
                    <div
                      className={
                        m.role === "user"
                          ? "inline-block rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 px-3 py-2 text-white shadow max-w-[85%] sm:max-w-[75%] md:max-w-[65%] break-words overflow-wrap-anywhere"
                          : "inline-block rounded-2xl bg-white/80 backdrop-blur px-3 py-2 text-gray-900 shadow ring-1 ring-black/5 max-w-[85%] sm:max-w-[75%] md:max-w-[65%] break-words overflow-wrap-anywhere"
                      }
                    >
                      <p className="text-sm leading-relaxed whitespace-pre-wrap break-words overflow-wrap-anywhere word-break-break-all text-left">
                        {m.content}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              <div className="grid gap-2 pt-3">
                <div className="flex items-end gap-2">
                  <div className="relative flex-1">
                    <Textarea
                      ref={textareaRef}
                      rows={1}
                      placeholder="Type your message..."
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onInput={autoResize}
                    />
                    {showComposerFade && (
                      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-6 rounded-b-md bg-gradient-to-t from-white/60 to-transparent" />
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={send}
                    disabled={!input.trim()}
                    className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 text-white shadow-sm transition hover:brightness-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                    aria-label="Send message"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="h-4 w-4"
                    >
                      <path d="M22 2L11 13" />
                      <path d="M22 2l-7 20-4-9-9-4 20-7z" />
                    </svg>
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </section>
  );
}
