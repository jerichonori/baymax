import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
// import { Button } from "../components/ui/button";
import { SegmentedToggle } from "../components/ui/segmented-toggle";
import {
  AudioVisualizer,
  CircularAudioVisualizer,
} from "../components/AudioVisualizer";

type Message = {
  id: string;
  role: "user" | "ai";
  content: string;
  language?: string;
};

// language auto-detect is handled heuristically from content (stub)

function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia(query);
    const handler = (e: MediaQueryListEvent) => setMatches(e.matches);
    setMatches(mq.matches);
    try {
      mq.addEventListener("change", handler);
    } catch (_err) {
      // Safari fallback
      // @ts-ignore
      mq.addListener(handler);
    }
    return () => {
      try {
        mq.removeEventListener("change", handler);
      } catch (_err) {
        // @ts-ignore
        mq.removeListener(handler);
      }
    };
  }, [query]);
  return matches;
}

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
  const [audioStream, setAudioStream] = useState<MediaStream | null>(null);
  const isNarrow = useMediaQuery("(max-width: 420px)");
  const placeholderText = isNarrow
    ? "Your concern…"
    : "Describe your health concerns…";

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
  // const [showTranscript, setShowTranscript] = useState(false);

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setAudioStream(stream);
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
        setAudioStream(null);
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
    <div className="h-[calc(100dvh-152px)] min-h-0">
      <motion.div
        className="h-full min-h-0 flex flex-col mx-auto px-3 sm:px-4"
        animate={{
          maxWidth:
            viewMode === "voice" ? "min(1024px, 100vw)" : "min(1400px, 100vw)",
        }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
      >
        {/* External controls bar */}
        <div className="flex w-full items-center justify-between gap-3 sm:gap-4 mb-3 sm:mb-4 flex-shrink-0">
          <label className="inline-flex cursor-pointer items-center gap-1.5 sm:gap-2 rounded-xl bg-white/70 px-3 sm:px-4 py-2 sm:py-2.5 text-xs sm:text-sm font-medium text-gray-700 shadow-sm backdrop-blur transition hover:bg-white/80 hover:shadow-md">
            <Input type="file" className="hidden" />
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-3.5 w-3.5 sm:h-4 sm:w-4"
            >
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 1 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66L9.88 16.75a2 2 0 1 1-2.83-2.83l8.49-8.49" />
            </svg>
            <span className="hidden xs:inline sm:inline">Attach Files</span>
            <span className="xs:hidden sm:hidden">Attach</span>
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

        <AnimatePresence mode="wait">
          {viewMode === "voice" ? (
            <motion.div
              key="voice"
              className="relative flex-1 min-h-0"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="border-0 shadow-xl bg-white/30 backdrop-blur-xl h-full">
                <CardContent className="grid h-full place-items-center py-6 sm:py-10">
                  <div className="flex flex-col items-center gap-6 sm:gap-8">
                    <div className="relative">
                      <button
                        type="button"
                        onClick={() =>
                          isRecording ? stopRecording() : startRecording()
                        }
                        className={`relative grid h-[clamp(84px,16vmin,176px)] w-[clamp(84px,16vmin,176px)] place-items-center rounded-full shadow-2xl transition-all duration-300 transform ${
                          isRecording
                            ? "bg-gradient-to-br from-rose-500 to-red-600 text-white scale-105 hover:scale-110"
                            : "bg-white/90 text-blue-600 hover:bg-white hover:scale-105 hover:shadow-xl"
                        }`}
                        aria-pressed={isRecording}
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="1.5"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="h-12 w-12 sm:h-14 sm:w-14 relative z-10"
                          aria-hidden
                        >
                          <path d="M12 3a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V6a3 3 0 0 1 3-3" />
                          <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                          <path d="M12 19v3" />
                          <path d="M8 22h8" />
                        </svg>
                        <div className="absolute -inset-6 sm:-inset-8">
                          <CircularAudioVisualizer
                            isRecording={isRecording}
                            stream={audioStream}
                          />
                        </div>
                      </button>

                      {/* Ambient glow */}
                      {isRecording && (
                        <div className="absolute inset-0 rounded-full bg-red-400/20 animate-ping pointer-events-none" />
                      )}
                    </div>

                    <div className="w-[clamp(160px,36vmin,288px)]">
                      <AudioVisualizer
                        isRecording={isRecording}
                        stream={audioStream}
                      />
                    </div>

                    {recordError && (
                      <div className="flex items-center gap-2 bg-red-50 text-red-700 px-4 py-2 rounded-xl text-sm">
                        <svg
                          className="h-4 w-4"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                            clipRule="evenodd"
                          />
                        </svg>
                        {recordError}
                      </div>
                    )}

                    <div
                      className={`text-center transition-all duration-300 ${
                        isRecording ? "text-gray-700" : "text-gray-500"
                      }`}
                    >
                      <div
                        className={`text-sm sm:text-base font-medium mb-1 ${
                          isRecording ? "text-red-600" : "text-gray-700"
                        }`}
                      >
                        {isRecording ? "Listening..." : "Ready to listen"}
                      </div>
                      <div className="text-xs sm:text-sm px-4 max-[700px]:hidden">
                        {isRecording
                          ? "Speak naturally about your health concerns"
                          : "Tap the microphone to start"}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ) : (
            <motion.div
              key="text"
              className="relative flex-1 min-h-0"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="border-0 shadow-xl bg-white/30 backdrop-blur-xl h-full">
                <CardContent className="flex h-full flex-col gap-4">
                  <div className="flex-1 min-h-0 overflow-y-auto space-y-4 px-2 pb-2">
                    <AnimatePresence>
                      {messages.map((m, index) => (
                        <motion.div
                          key={m.id}
                          className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
                          initial={{ opacity: 0, y: 20, scale: 0.95 }}
                          animate={{ opacity: 1, y: 0, scale: 1 }}
                          transition={{
                            duration: 0.3,
                            delay: index * 0.05,
                            type: "spring",
                            stiffness: 400,
                            damping: 25,
                          }}
                        >
                          <div
                            className={
                              m.role === "user"
                                ? "inline-block rounded-3xl bg-gradient-to-r from-blue-600 to-indigo-600 px-5 py-3 text-white shadow-md max-w-[85%] sm:max-w-[75%] md:max-w-[65%] break-words overflow-wrap-anywhere"
                                : "inline-block rounded-3xl bg-white/80 backdrop-blur-sm px-5 py-3 text-gray-900 shadow-md max-w-[85%] sm:max-w-[75%] md:max-w-[65%] break-words overflow-wrap-anywhere"
                            }
                          >
                            <p className="text-xs sm:text-sm leading-relaxed whitespace-pre-wrap break-words overflow-wrap-anywhere text-left">
                              {m.content}
                            </p>
                          </div>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                  <div className="flex-shrink-0">
                    <div className="flex items-end gap-3">
                      <div className="relative flex-1">
                        <Textarea
                          ref={textareaRef}
                          rows={1}
                          placeholder={placeholderText}
                          value={input}
                          onChange={(e) => setInput(e.target.value)}
                          onInput={autoResize}
                          className="border-0 ring-1 ring-white/40 bg-white/80 backdrop-blur-sm shadow-md focus-visible:ring-blue-500/50 transition-all duration-200 rounded-2xl resize-none"
                        />
                        {showComposerFade && (
                          <div className="pointer-events-none absolute inset-x-0 bottom-0 h-6 rounded-b-2xl bg-gradient-to-t from-white/90 to-transparent" />
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={send}
                        disabled={!input.trim()}
                        className="grid h-10 w-10 sm:h-11 sm:w-11 shrink-0 place-items-center rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg transition-all duration-200 hover:scale-105 hover:shadow-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/50 disabled:opacity-50 disabled:cursor-not-allowed disabled:scale-100"
                        aria-label="Send message"
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="1.5"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="h-4 w-4 sm:h-5 sm:w-5"
                        >
                          <path d="M22 2L11 13" />
                          <path d="M22 2l-7 20-4-9-9-4 20-7z" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
