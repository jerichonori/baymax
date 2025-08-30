import { useMemo, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Avatar } from "../components/ui/avatar";
import { Modal } from "../components/ui/modal";
import {
  ArrowLeft,
  CheckCircle2,
  User,
  Calendar,
  Phone,
  Paperclip,
  MessageSquare,
  FileText,
  ChevronRight,
  AlertCircle,
  Activity,
} from "lucide-react";

type Attachment = {
  id: string;
  type: "image";
  name: string;
  url: string;
};

type TranscriptItem = {
  role: "patient" | "ai";
  text: string;
};

const MOCK_ENCOUNTERS = {
  "e-1001": {
    id: "e-1001",
    patient: {
      name: "Rahul Sharma",
      dob: "1990-04-02",
      phone: "+91 98XXXXXX90",
    },
    status: "awaiting-review" as const,
    intake: {
      summary: {
        chiefComplaint: "Knee pain after fall",
        redFlags: [],
      },
      attachments: [
        {
          id: "att-1",
          type: "image",
          name: "knee-lateral.jpg",
          url: "https://images.unsplash.com/photo-1526253038957-bce54e05968a?w=600",
        },
        {
          id: "att-2",
          type: "image",
          name: "knee-front.jpg",
          url: "https://images.unsplash.com/photo-1584556812952-905ffd0b5b1b?w=600",
        },
        {
          id: "att-3",
          type: "image",
          name: "knee-mri-1.jpg",
          url: "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=600",
        },
        {
          id: "att-4",
          type: "image",
          name: "knee-mri-2.jpg",
          url: "https://images.unsplash.com/photo-1579154204601-01588f351e67?w=600",
        },
        {
          id: "att-5",
          type: "image",
          name: "knee-xray.jpg",
          url: "https://images.unsplash.com/photo-1580281657527-47e60fc7d4a5?w=600",
        },
      ],
    },
    aiSummary: {
      details:
        "Patient slipped on stairs two days ago, presenting with lateral knee pain, swelling, and difficulty weight-bearing. No locking or giving way reported.",
      diagnosis:
        "Probable lateral collateral ligament sprain. Rule out meniscal injury if locking/catching emerges. No red flags detected.",
    },
    transcript: [
      { role: "patient", text: "I slipped on the stairs and my knee hurts." },
      { role: "ai", text: "I'm sorry to hear that. When did the pain start?" },
      { role: "patient", text: "Two days ago." },
      { role: "ai", text: "Is the pain constant or does it come and go?" },
      { role: "patient", text: "Mostly constant, worse when I bend the knee." },
      { role: "ai", text: "Any swelling or bruising that you noticed?" },
      { role: "patient", text: "Yes, there is swelling on the outside." },
      { role: "ai", text: "Can you bear weight on that leg?" },
      { role: "patient", text: "Yes but it is uncomfortable to climb stairs." },
      { role: "ai", text: "Any clicking, locking, or the knee giving way?" },
      { role: "patient", text: "No locking or giving way." },
      { role: "ai", text: "Have you tried any medicine or ice? Did it help?" },
      {
        role: "patient",
        text: "I took paracetamol and iced it. It helped a bit.",
      },
      { role: "ai", text: "Any previous knee injuries or surgeries?" },
      { role: "patient", text: "No previous injuries." },
      {
        role: "ai",
        text: "I'll summarize what I heard and suggest next steps for the doctor.",
      },
    ],
  },
  "e-1002": {
    id: "e-1002",
    patient: {
      name: "Anita Singh",
      dob: "1986-11-12",
      phone: "+91 99XXXXXX12",
    },
    status: "in-progress" as const,
    intake: {
      summary: {
        chiefComplaint: "Back pain radiating to leg",
        redFlags: ["radiculopathy"],
      },
      attachments: [
        {
          id: "att-1",
          type: "image",
          name: "lumbar-xray.jpg",
          url: "https://images.unsplash.com/photo-1581594693700-12f9a6f22d7b?w=600",
        },
      ],
    },
    aiSummary: {
      details:
        "Subacute low-back pain with right-sided radicular symptoms for one week, worse at night. No bowel/bladder changes.",
      diagnosis:
        "Likely lumbar radiculopathy (L5/S1). Advise exam and straight leg raise; imaging if persistent or progressive deficits.",
    },
    transcript: [
      { role: "patient", text: "Pain shoots down my right leg" },
      { role: "ai", text: "Any change in bladder or bowel control?" },
      { role: "patient", text: "No changes there." },
      { role: "ai", text: "When did this pain start?" },
      { role: "patient", text: "About a week ago." },
    ],
  },
} as const;

export default function EncounterDetailPage() {
  const { encounterId } = useParams<{ encounterId: string }>();
  const data = useMemo(
    () =>
      encounterId
        ? MOCK_ENCOUNTERS[encounterId as keyof typeof MOCK_ENCOUNTERS]
        : undefined,
    [encounterId]
  );
  const [view, setView] = useState<"summary" | "transcript">("summary");
  const [done, setDone] = useState(false);
  const [attachmentsOpen, setAttachmentsOpen] = useState(false);
  const [selectedImage, setSelectedImage] = useState<Attachment | null>(null);

  if (!data) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex min-h-[50vh] items-center justify-center"
      >
        <div className="text-center space-y-4">
          <AlertCircle className="h-12 w-12 text-gray-400 mx-auto" />
          <p className="text-lg font-medium text-gray-600">
            Encounter not found
          </p>
          <Button asChild variant="outline" className="gap-2">
            <Link to="/doctor">
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Link>
          </Button>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.section
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="min-h-screen p-4 pt-2 md:p-6 md:pt-3 lg:p-8 lg:pt-4"
    >
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="mb-4 flex items-center justify-between"
        >
          <Button
            variant="ghost"
            asChild
            className="group gap-2 hover:bg-white/50 transition-all duration-200 p-2 sm:px-3"
          >
            <Link to="/doctor">
              <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
              <span className="hidden sm:inline">Back to Dashboard</span>
            </Link>
          </Button>
          <AnimatePresence mode="wait">
            {done ? (
              <motion.div
                key="done"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.8, opacity: 0 }}
                className="flex items-center gap-2"
              >
                <Badge className="gap-1.5 bg-green-100 text-green-700 border-green-200">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  <span className="hidden sm:inline">Completed</span>
                </Badge>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setDone(false)}
                  className="hover:bg-white/50"
                >
                  Undo
                </Button>
              </motion.div>
            ) : (
              <motion.div
                key="not-done"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.8, opacity: 0 }}
              >
                <Button
                  onClick={() => setDone(true)}
                  className="gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl p-2.5 sm:px-4"
                >
                  <CheckCircle2 className="h-5 w-5 sm:h-4 sm:w-4" />
                  <span className="hidden sm:inline">Mark as Complete</span>
                </Button>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Main Content Grid */}
        <div className="flex flex-col lg:grid lg:gap-6 lg:grid-cols-3 gap-4">
          {/* Main Column - order 2 on mobile, spans 2 cols on desktop */}
          <div className="space-y-6 lg:col-span-2 order-2 lg:order-none">
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="overflow-hidden rounded-2xl bg-white/80 backdrop-blur-xl shadow-xl ring-1 ring-gray-200/50"
            >
              <div className="border-b border-gray-100 bg-gradient-to-r from-gray-50/50 to-white/50 p-4 sm:p-6">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg">
                      {view === "summary" ? (
                        <FileText className="h-5 w-5 text-white" />
                      ) : (
                        <MessageSquare className="h-5 w-5 text-white" />
                      )}
                    </div>
                    <h2 className="text-xl font-semibold text-gray-900">
                      {view === "summary"
                        ? "Clinical Summary"
                        : "Interview Transcript"}
                    </h2>
                  </div>
                  <div className="relative inline-flex w-full sm:w-auto items-center gap-0 rounded-2xl bg-gray-100/80 p-1 backdrop-blur">
                    <button
                      type="button"
                      className={`flex-1 sm:flex-initial flex items-center justify-center gap-1.5 rounded-xl px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm font-medium transition-all duration-200 ${
                        view === "summary"
                          ? "bg-white text-gray-900 shadow-sm"
                          : "text-gray-600 hover:text-gray-900 hover:bg-white/50"
                      }`}
                      onClick={() => setView("summary")}
                    >
                      <FileText className="h-3.5 w-3.5" />
                      <span>Summary</span>
                    </button>
                    <button
                      type="button"
                      className={`flex-1 sm:flex-initial flex items-center justify-center gap-1.5 rounded-xl px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm font-medium transition-all duration-200 ${
                        view === "transcript"
                          ? "bg-white text-gray-900 shadow-sm"
                          : "text-gray-600 hover:text-gray-900 hover:bg-white/50"
                      }`}
                      onClick={() => setView("transcript")}
                    >
                      <MessageSquare className="h-3.5 w-3.5" />
                      <span>Transcript</span>
                    </button>
                  </div>
                </div>
              </div>
              <AnimatePresence mode="wait">
                {view === "summary" ? (
                  <motion.div
                    key="summary"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.2 }}
                    className="p-4 sm:p-6 space-y-6"
                  >
                    <div className="space-y-4">
                      <div className="group rounded-xl bg-gradient-to-br from-blue-50/50 to-indigo-50/50 p-4 transition-all hover:shadow-md">
                        <div className="mb-2 flex items-center gap-2">
                          <Activity className="h-4 w-4 text-blue-600" />
                          <h3 className="font-semibold text-gray-900">
                            Clinical Details
                          </h3>
                        </div>
                        <p className="text-gray-700 leading-relaxed">
                          {data.aiSummary.details}
                        </p>
                      </div>

                      <div className="group rounded-xl bg-gradient-to-br from-purple-50/50 to-pink-50/50 p-4 transition-all hover:shadow-md">
                        <div className="mb-2 flex items-center gap-2">
                          <FileText className="h-4 w-4 text-purple-600" />
                          <h3 className="font-semibold text-gray-900">
                            Assessment
                          </h3>
                        </div>
                        <p className="font-medium text-gray-800 leading-relaxed">
                          {data.aiSummary.diagnosis}
                        </p>
                      </div>

                    </div>
                  </motion.div>
                ) : (
                  <motion.div
                    key="transcript"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                    className="h-[60vh] overflow-y-auto p-4 sm:p-6"
                  >
                    <div className="space-y-3">
                      {data.transcript.map((t: TranscriptItem, i: number) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: i * 0.02, duration: 0.2 }}
                          className={`flex ${
                            t.role === "patient"
                              ? "justify-start"
                              : "justify-end"
                          }`}
                        >
                          <div
                            className={`group relative max-w-[85%] sm:max-w-[75%] lg:max-w-[65%] ${
                              t.role === "patient" ? "order-2" : "order-1"
                            }`}
                          >
                            <div
                              className={`rounded-2xl px-4 py-2.5 shadow-sm transition-all hover:shadow-md ${
                                t.role === "patient"
                                  ? "bg-white/90 text-gray-900 ring-1 ring-gray-200/50"
                                  : "bg-gradient-to-br from-blue-600 to-indigo-600 text-white"
                              }`}
                            >
                              <div
                                className={`text-xs font-medium mb-1 opacity-70 ${
                                  t.role === "patient"
                                    ? "text-gray-500"
                                    : "text-blue-100"
                                }`}
                              >
                                {t.role === "patient"
                                  ? "Patient"
                                  : "AI Assistant"}
                              </div>
                              <p className="text-sm leading-relaxed break-words">
                                {t.text}
                              </p>
                            </div>
                          </div>
                          {t.role === "patient" ? (
                            <div className="order-1 mr-2 mt-auto">
                              <Avatar className="h-8 w-8 ring-2 ring-white shadow-sm" />
                            </div>
                          ) : (
                            <div className="order-2 ml-2 mt-auto">
                              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 shadow-sm ring-2 ring-white">
                                <Activity className="h-4 w-4 text-white" />
                              </div>
                            </div>
                          )}
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </div>

          {/* Right sidebar: stack patient info and attachments together on desktop */}
          <div className="order-1 lg:order-none lg:col-start-3 flex flex-col gap-4 lg:gap-6">
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="overflow-hidden rounded-2xl bg-white/80 backdrop-blur-xl shadow-xl ring-1 ring-gray-200/50"
            >
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-4">
                <h3 className="flex items-center gap-2 text-sm font-semibold text-white">
                  <User className="h-4 w-4" />
                  Patient Information
                </h3>
              </div>
              <div className="p-4">
                <div className="flex items-start gap-3">
                  <Avatar
                    alt={data.patient.name}
                    className="h-12 w-12 ring-2 ring-white shadow-lg"
                  />
                  <div className="flex-1 space-y-2">
                    <div className="font-semibold text-gray-900">
                      {data.patient.name}
                    </div>
                    <div className="space-y-1 text-sm">
                      <div className="flex items-center gap-2 text-gray-600">
                        <Calendar className="h-3.5 w-3.5" />
                        <span>{data.patient.dob}</span>
                      </div>
                      <div className="flex items-center gap-2 text-gray-600">
                        <Phone className="h-3.5 w-3.5" />
                        <span>{data.patient.phone}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Status Badge */}
                <div className="mt-4 flex items-center justify-between rounded-lg bg-gradient-to-r from-amber-50 to-orange-50 p-2">
                  <span className="text-xs font-medium text-amber-700">
                    Status
                  </span>
                  <Badge className="bg-amber-100 text-amber-700 border-amber-200">
                    {data.status === "awaiting-review"
                      ? "Awaiting Review"
                      : "In Progress"}
                  </Badge>
                </div>
              </div>
            </motion.div>

            {/* Desktop-only attachments inside sidebar to avoid grid row gap */}
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="hidden lg:block overflow-hidden rounded-2xl bg-white/80 backdrop-blur-xl shadow-xl ring-1 ring-gray-200/50"
            >
              <div className="border-b border-gray-100 bg-gradient-to-r from-gray-50/50 to-white/50 p-4">
                <h3 className="flex items-center gap-2 text-sm font-semibold text-gray-900">
                  <Paperclip className="h-4 w-4" />
                  Attachments
                  {data.intake.attachments?.length > 0 && (
                    <span className="ml-auto rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
                      {data.intake.attachments.length}
                    </span>
                  )}
                </h3>
              </div>
              <div className="p-4">
                {data.intake.attachments?.length ? (
                  <>
                    <div className="grid grid-cols-2 gap-3">
                      {data.intake.attachments
                        .slice(0, 4)
                        .map((att: Attachment, index: number) => (
                          <motion.button
                            key={att.id}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.5 + index * 0.05 }}
                            onClick={() => setSelectedImage(att)}
                            className="group relative overflow-hidden rounded-xl bg-white ring-1 ring-gray-200/50 shadow-sm transition-all hover:shadow-lg hover:ring-gray-300/50"
                          >
                            <div className="aspect-square overflow-hidden bg-gray-50">
                              <img
                                src={att.url}
                                alt={att.name}
                                className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-110"
                                loading="lazy"
                              />
                            </div>
                            <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent opacity-0 transition-opacity group-hover:opacity-100" />
                            <div className="absolute bottom-0 left-0 right-0 p-2 text-white opacity-0 transition-opacity group-hover:opacity-100">
                              <p className="truncate text-xs font-medium">
                                {att.name}
                              </p>
                            </div>
                          </motion.button>
                        ))}
                    </div>
                    {data.intake.attachments.length > 4 && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.7 }}
                        className="mt-4"
                      >
                        <Button
                          variant="outline"
                          className="w-full gap-2 hover:bg-gray-50"
                          onClick={() => setAttachmentsOpen(true)}
                        >
                          View All {data.intake.attachments.length} Attachments
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </motion.div>
                    )}
                  </>
                ) : (
                  <div className="text-center py-6">
                    <Paperclip className="mx-auto h-8 w-8 text-gray-300" />
                    <p className="mt-2 text-sm text-gray-500">No attachments</p>
                  </div>
                )}
              </div>
            </motion.div>
          </div>

          {/* Mobile-only attachments so order remains 3 on small screens */}
          <div className="order-3 lg:hidden">
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="overflow-hidden rounded-2xl bg-white/80 backdrop-blur-xl shadow-xl ring-1 ring-gray-200/50"
            >
              <div className="border-b border-gray-100 bg-gradient-to-r from-gray-50/50 to-white/50 p-4">
                <h3 className="flex items-center gap-2 text-sm font-semibold text-gray-900">
                  <Paperclip className="h-4 w-4" />
                  Attachments
                  {data.intake.attachments?.length > 0 && (
                    <span className="ml-auto rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
                      {data.intake.attachments.length}
                    </span>
                  )}
                </h3>
              </div>
              <div className="p-4">
                {data.intake.attachments?.length ? (
                  <>
                    <div className="grid grid-cols-2 gap-3">
                      {data.intake.attachments
                        .slice(0, 4)
                        .map((att: Attachment, index: number) => (
                          <motion.button
                            key={att.id}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.5 + index * 0.05 }}
                            onClick={() => setSelectedImage(att)}
                            className="group relative overflow-hidden rounded-xl bg-white ring-1 ring-gray-200/50 shadow-sm transition-all hover:shadow-lg hover:ring-gray-300/50"
                          >
                            <div className="aspect-square overflow-hidden bg-gray-50">
                              <img
                                src={att.url}
                                alt={att.name}
                                className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-110"
                                loading="lazy"
                              />
                            </div>
                            <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent opacity-0 transition-opacity group-hover:opacity-100" />
                            <div className="absolute bottom-0 left-0 right-0 p-2 text-white opacity-0 transition-opacity group-hover:opacity-100">
                              <p className="truncate text-xs font-medium">
                                {att.name}
                              </p>
                            </div>
                          </motion.button>
                        ))}
                    </div>
                    {data.intake.attachments.length > 4 && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.7 }}
                        className="mt-4"
                      >
                        <Button
                          variant="outline"
                          className="w-full gap-2 hover:bg-gray-50"
                          onClick={() => setAttachmentsOpen(true)}
                        >
                          View All {data.intake.attachments.length} Attachments
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </motion.div>
                    )}
                  </>
                ) : (
                  <div className="text-center py-6">
                    <Paperclip className="mx-auto h-8 w-8 text-gray-300" />
                    <p className="mt-2 text-sm text-gray-500">No attachments</p>
                  </div>
                )}
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Modals */}
      <AnimatePresence>
        {attachmentsOpen && (
          <Modal
            open={attachmentsOpen}
            onClose={() => setAttachmentsOpen(false)}
            title="All Attachments"
          >
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {data.intake.attachments.map((att: Attachment, index: number) => (
                <motion.button
                  key={att.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.02 }}
                  onClick={() => {
                    setSelectedImage(att);
                    setAttachmentsOpen(false);
                  }}
                  className="group relative overflow-hidden rounded-xl bg-white ring-1 ring-gray-200/50 shadow-sm transition-all hover:shadow-lg hover:ring-gray-300/50"
                >
                  <div className="aspect-square overflow-hidden bg-gray-50">
                    <img
                      src={att.url}
                      alt={att.name}
                      className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-110"
                      loading="lazy"
                    />
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent opacity-0 transition-opacity group-hover:opacity-100" />
                  <div className="absolute bottom-0 left-0 right-0 p-3 text-white opacity-0 transition-opacity group-hover:opacity-100">
                    <p className="truncate text-sm font-medium">{att.name}</p>
                  </div>
                </motion.button>
              ))}
            </div>
          </Modal>
        )}

        {selectedImage && (
          <Modal
            open={!!selectedImage}
            onClose={() => setSelectedImage(null)}
            title={selectedImage.name}
          >
            <div className="relative overflow-hidden rounded-xl">
              <img
                src={selectedImage.url}
                alt={selectedImage.name}
                className="w-full h-auto"
              />
            </div>
          </Modal>
        )}
      </AnimatePresence>
    </motion.section>
  );
}
