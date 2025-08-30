import { useMemo, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Avatar } from "../components/ui/avatar";
import { Modal } from "../components/ui/modal";

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
        onset: "2 days ago",
        painScale: 6,
        redFlags: [],
      },
      rosHits: ["swelling", "difficulty weight-bearing"],
      meds: ["paracetamol"],
      allergies: [],
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
          name: "clinic-photo-1.jpg",
          url: "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=600",
        },
        {
          id: "att-6",
          type: "image",
          name: "clinic-photo-2.jpg",
          url: "https://images.unsplash.com/photo-1583912086096-c9b3f8a3d2aa?w=600",
        },
        {
          id: "att-7",
          type: "image",
          name: "knee-ultrasound.jpg",
          url: "https://images.unsplash.com/photo-1559757175-08fda9f7d7ea?w=600",
        },
        {
          id: "att-8",
          type: "image",
          name: "knee-xray-1.jpg",
          url: "https://images.unsplash.com/photo-1580281657527-47e60fc7d4a5?w=600",
        },
        {
          id: "att-9",
          type: "image",
          name: "knee-xray-2.jpg",
          url: "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=600",
        },
        {
          id: "att-10",
          type: "image",
          name: "knee-xray-3.jpg",
          url: "https://images.unsplash.com/photo-1582719478145-3b3f6466b740?w=600",
        },
        {
          id: "att-11",
          type: "image",
          name: "report-page-1.png",
          url: "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=600",
        },
        {
          id: "att-12",
          type: "image",
          name: "report-page-2.png",
          url: "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600",
        },
      ],
    },
    aiSummary: {
      details:
        "Patient slipped on stairs two days ago, presenting with lateral knee pain, swelling, and difficulty weight-bearing. No locking or giving way reported. Pain moderate at 6/10, worse with flexion and stairs.",
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
      {
        role: "ai",
        text: "On a scale of 0–10, how bad is the pain right now?",
      },
      { role: "patient", text: "Around six out of ten." },
      {
        role: "ai",
        text: "Any numbness or tingling sensations in the foot or leg?",
      },
      { role: "patient", text: "No numbness or tingling." },
      { role: "ai", text: "Have you tried any medicine or ice? Did it help?" },
      {
        role: "patient",
        text: "I took paracetamol and iced it. It helped a bit.",
      },
      { role: "ai", text: "Any previous knee injuries or surgeries?" },
      { role: "patient", text: "No previous injuries." },
      {
        role: "ai",
        text: "Do you play sports or have any physical job demands?",
      },
      { role: "patient", text: "I jog occasionally, desk job otherwise." },
      {
        role: "ai",
        text: "Does the pain travel to other areas like the calf or thigh?",
      },
      { role: "patient", text: "It stays near the outer side of the knee." },
      { role: "ai", text: "Any fever, redness, or wounds around the knee?" },
      { role: "patient", text: "No." },
      {
        role: "ai",
        text: "I'll summarize what I heard and suggest next steps for the doctor.",
      },
      { role: "patient", text: "Okay." },
      // extended transcript to test long scrolling
      { role: "ai", text: "Do stairs or hills make the pain worse?" },
      { role: "patient", text: "Yes, especially going down stairs." },
      { role: "ai", text: "Any popping sound when the injury happened?" },
      { role: "patient", text: "No pop, just immediate pain." },
      { role: "ai", text: "Are you using any support like a brace?" },
      { role: "patient", text: "I wrapped it with a crepe bandage." },
      {
        role: "ai",
        text: "Understood. I will relay these details to your doctor.",
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
        onset: "1 week",
        painScale: 7,
        redFlags: ["radiculopathy"],
      },
      rosHits: ["tingling", "worse at night"],
      meds: ["ibuprofen"],
      allergies: ["penicillin"],
      attachments: [
        {
          id: "att-3",
          type: "image",
          name: "lumbar-xray.jpg",
          url: "https://images.unsplash.com/photo-1581594693700-12f9a6f22d7b?w=600",
        },
      ],
    },
    aiSummary: {
      details:
        "Subacute low-back pain with right-sided radicular symptoms for one week, worse at night. No bowel/bladder changes. Tingling noted over lateral calf.",
      diagnosis:
        "Likely lumbar radiculopathy (L5/S1). Advise exam and straight leg raise; imaging if persistent or progressive deficits.",
    },
    transcript: [
      { role: "patient", text: "Pain shoots down my right leg" },
      { role: "ai", text: "Any change in bladder or bowel control?" },
    ],
  },
} satisfies Record<string, any>;

export default function EncounterDetailPage() {
  const { encounterId } = useParams<{ encounterId: string }>();
  const data = useMemo(
    () => (encounterId ? MOCK_ENCOUNTERS[encounterId] : undefined),
    [encounterId]
  );
  const [view, setView] = useState<"summary" | "transcript">("summary");
  const [done, setDone] = useState(false);
  const [attachmentsOpen, setAttachmentsOpen] = useState(false);

  if (!data) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-gray-600">Encounter not found.</p>
        <Button asChild>
          <Link to="/doctor">Back to Dashboard</Link>
        </Button>
      </div>
    );
  }

  return (
    <section className="grid gap-6 lg:grid-cols-3">
      <div className="space-y-4 lg:col-span-2">
        <div className="flex items-center justify-between">
          <Button variant="outline" asChild>
            <Link to="/doctor">Back</Link>
          </Button>
          {done ? (
            <Button variant="outline" onClick={() => setDone(false)}>
              Undo done
            </Button>
          ) : (
            <Button onClick={() => setDone(true)}>Mark as done</Button>
          )}
        </div>
        <Card>
          <CardHeader className="flex items-center justify-between gap-3">
            <CardTitle>
              {view === "summary" ? "AI Summary" : "Transcript"}
            </CardTitle>
            <div className="relative inline-flex items-center gap-0.5 rounded-xl bg-white/50 p-1 text-xs shadow-sm ring-1 ring-black/5 backdrop-blur">
              <button
                type="button"
                className={`rounded-lg px-3 py-1.5 transition ${
                  view === "summary"
                    ? "bg-gradient-to-br from-blue-600 to-indigo-600 text-white shadow"
                    : "text-gray-700 hover:bg-white/70 hover:text-gray-900"
                }`}
                onClick={() => setView("summary")}
              >
                Summary
              </button>
              <button
                type="button"
                className={`rounded-lg px-3 py-1.5 transition ${
                  view === "transcript"
                    ? "bg-gradient-to-br from-blue-600 to-indigo-600 text-white shadow"
                    : "text-gray-700 hover:bg-white/70 hover:text-gray-900"
                }`}
                onClick={() => setView("transcript")}
              >
                Transcript
              </button>
            </div>
          </CardHeader>
          {view === "summary" ? (
            <CardContent className="prose prose-sm max-w-none">
              <h4>Details</h4>
              <p>{data.aiSummary.details}</p>
              <h4>Diagnosis</h4>
              <p className="font-medium text-gray-900">
                {data.aiSummary.diagnosis}
              </p>
            </CardContent>
          ) : (
            <CardContent className="space-y-2 text-sm max-h-[60vh] overflow-auto">
              {data.transcript.map((t: any, i: number) => (
                <div
                  key={i}
                  className={t.role === "patient" ? "text-left" : "text-right"}
                >
                  <span
                    className={
                      t.role === "patient"
                        ? "inline-block rounded-2xl bg-white/80 backdrop-blur px-3 py-2 text-gray-900 shadow ring-1 ring-black/5 max-w-[85%] sm:max-w-[75%] md:max-w-[65%] break-words"
                        : "inline-block rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 px-3 py-2 text-white shadow max-w-[85%] sm:max-w-[75%] md:max-w-[65%] break-words"
                    }
                  >
                    <span className="whitespace-pre-wrap break-words">
                      {t.text}
                    </span>
                  </span>
                </div>
              ))}
            </CardContent>
          )}
        </Card>
      </div>

      <aside className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Patient</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-gray-700">
            <div className="flex items-center gap-3">
              <Avatar alt={data.patient.name} className="h-10 w-10" />
              <div>
                <div className="font-medium tracking-tight">
                  {data.patient.name}
                </div>
                <div className="text-xs text-gray-500">
                  DOB: {data.patient.dob}
                </div>
                <div className="text-xs text-gray-500">
                  Phone: {data.patient.phone}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Attachments</CardTitle>
          </CardHeader>
          <CardContent>
            {data.intake.attachments?.length ? (
              <>
                <div className="grid grid-cols-2 gap-3">
                  {data.intake.attachments.slice(0, 2).map((att: any) => (
                    <a
                      key={att.id}
                      href={att.url}
                      target="_blank"
                      rel="noreferrer"
                      className="group block overflow-hidden rounded-xl bg-white/70 backdrop-blur ring-1 ring-black/5 shadow-sm"
                    >
                      <img
                        src={att.url}
                        alt={att.name}
                        className="aspect-square h-auto w-full object-cover transition-transform group-hover:scale-[1.02]"
                        loading="lazy"
                      />
                      <div className="truncate px-2 py-1 text-xs text-gray-600">
                        {att.name}
                      </div>
                    </a>
                  ))}
                </div>
                {data.intake.attachments.length > 2 && (
                  <div className="pt-3">
                    <Button
                      variant="outline"
                      onClick={() => setAttachmentsOpen(true)}
                    >
                      Show all ({data.intake.attachments.length})
                    </Button>
                  </div>
                )}
                <Modal
                  open={attachmentsOpen}
                  onClose={() => setAttachmentsOpen(false)}
                  title="All attachments"
                >
                  <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3">
                    {data.intake.attachments.map((att: any) => (
                      <a
                        key={att.id}
                        href={att.url}
                        target="_blank"
                        rel="noreferrer"
                        className="group block overflow-hidden rounded-xl bg-white/70 backdrop-blur ring-1 ring-black/5 shadow-sm"
                      >
                        <img
                          src={att.url}
                          alt={att.name}
                          className="aspect-square h-auto w-full object-cover transition-transform group-hover:scale-[1.02]"
                          loading="lazy"
                        />
                        <div className="truncate px-2 py-1 text-xs text-gray-600">
                          {att.name}
                        </div>
                      </a>
                    ))}
                  </div>
                </Modal>
              </>
            ) : (
              <p className="text-sm text-gray-600">No attachments</p>
            )}
          </CardContent>
        </Card>
      </aside>
    </section>
  );
}
