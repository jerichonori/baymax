import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Avatar } from "../components/ui/avatar";
import { SegmentedToggle } from "../components/ui/segmented-toggle";

type Status = "to-review" | "done";
type Filter = "all" | Status;

const encounters: Array<{
  id: string;
  patient: string;
  complaint: string;
  status: Status;
  updatedAt: string;
}> = [
  {
    id: "e-1001",
    patient: "Rahul Sharma",
    complaint: "Knee pain after fall",
    status: "to-review",
    updatedAt: "2m ago",
  },
  {
    id: "e-1002",
    patient: "Anita Singh",
    complaint: "Back pain, radiating",
    status: "done",
    updatedAt: "10m ago",
  },
];

export default function DoctorDashboardPage() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState<Filter>("all");

  const filtered = encounters.filter(
    (e) => filter === "all" || e.status === filter
  );

  return (
    <section className="grid gap-6">
      <Card>
        <CardHeader className="flex items-center justify-between gap-3">
          <CardTitle>Patients</CardTitle>
          <SegmentedToggle<Filter>
            options={[
              { label: "All", value: "all" },
              { label: "To review", value: "to-review" },
              { label: "Done", value: "done" },
            ]}
            value={filter}
            onChange={setFilter}
          />
        </CardHeader>
        <CardContent>
          <div className="grid gap-2">
            {filtered.map((e) => (
              <button
                key={e.id}
                className="group flex w-full items-center justify-between gap-4 rounded-xl bg-white/70 p-4 text-left shadow-sm ring-1 ring-black/5 transition hover:bg-white/80 hover:shadow-md"
                onClick={() => navigate(`/doctor/${e.id}`)}
                aria-label={`Open encounter for ${e.patient}`}
              >
                <div className="flex items-center gap-3">
                  <Avatar alt={e.patient} />
                  <div>
                    <div className="font-medium tracking-tight">
                      {e.patient}
                    </div>
                    <div className="text-sm text-gray-600">{e.complaint}</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {e.status === "to-review" && <Badge>To review</Badge>}
                  {e.status === "done" && <Badge variant="success">Done</Badge>}
                  <span className="text-xs text-gray-500">{e.updatedAt}</span>
                </div>
              </button>
            ))}
            {!filtered.length && (
              <div className="grid place-items-center rounded-xl bg-white/60 p-6 text-sm text-gray-600 ring-1 ring-black/5">
                All caught up. No patients in this filter.
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </section>
  );
}
