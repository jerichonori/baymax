import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Avatar } from "../components/ui/avatar";
import { SegmentedToggle } from "../components/ui/segmented-toggle";
import { Clock, ChevronRight, Activity } from "lucide-react";

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
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  const filtered = encounters.filter(
    (e) => filter === "all" || e.status === filter
  );

  return (
    <motion.section 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50/20 p-6"
    >
      <div className="mx-auto max-w-7xl">
        <Card className="overflow-hidden border-0 bg-white/80 shadow-xl backdrop-blur-sm">
          <CardHeader className="border-b border-gray-100 bg-gradient-to-r from-white to-gray-50/50 px-4 py-4 sm:px-6 sm:py-5">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <CardTitle className="text-xl sm:text-2xl font-bold text-gray-900">Patient Encounters</CardTitle>
                <p className="mt-0.5 text-xs sm:text-sm text-gray-500">Manage and review patient consultations</p>
              </div>
              <SegmentedToggle<Filter>
                options={[
                  { label: "All", value: "all" },
                  { label: "To review", value: "to-review" },
                  { label: "Done", value: "done" },
                ]}
                value={filter}
                onChange={setFilter}
                className="w-full sm:w-auto bg-gray-100/50"
              />
            </div>
          </CardHeader>
          <CardContent className="p-3 sm:p-6">
            <AnimatePresence mode="wait">
              <motion.div 
                key={filter}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="grid gap-2 sm:gap-3">
                {filtered.map((e, index) => (
                  <motion.button
                    key={e.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="group relative flex w-full flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4 overflow-hidden rounded-xl sm:rounded-2xl bg-white p-4 sm:p-5 text-left shadow-md ring-1 ring-gray-200/50 transition-all hover:shadow-xl hover:ring-gray-300/50"
                    onClick={() => navigate(`/doctor/${e.id}`)}
                    onMouseEnter={() => setHoveredId(e.id)}
                    onMouseLeave={() => setHoveredId(null)}
                    aria-label={`Open encounter for ${e.patient}`}
                  >
                    <motion.div 
                      className="absolute inset-0 bg-gradient-to-r from-blue-50 to-indigo-50 opacity-0 transition-opacity group-hover:opacity-100"
                      initial={false}
                      animate={{ opacity: hoveredId === e.id ? 1 : 0 }}
                    />
                    
                    <div className="relative flex items-start sm:items-center gap-3 sm:gap-4 flex-1">
                      <motion.div
                        whileHover={{ scale: 1.05 }}
                        className="relative flex-shrink-0"
                      >
                        <Avatar alt={e.patient} className="h-10 w-10 sm:h-12 sm:w-12 ring-2 ring-white shadow-md" />
                      </motion.div>
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold text-gray-900 text-sm sm:text-base">
                          {e.patient}
                        </div>
                        <div className="mt-0.5 sm:mt-1 flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm text-gray-600">
                          <Activity className="h-3 w-3 flex-shrink-0" />
                          <span className="truncate">{e.complaint}</span>
                        </div>
                        <div className="mt-2 flex items-center gap-2 sm:hidden">
                          {e.status === "to-review" && (
                            <Badge className="bg-gradient-to-r from-amber-100 to-orange-100 text-orange-800 border-0 text-[10px] px-2 py-0.5">
                              To review
                            </Badge>
                          )}
                          {e.status === "done" && (
                            <Badge className="bg-gradient-to-r from-emerald-100 to-green-100 text-green-800 border-0 text-[10px] px-2 py-0.5">
                              Completed
                            </Badge>
                          )}
                          <span className="flex items-center gap-1 text-[10px] text-gray-500">
                            <Clock className="h-2.5 w-2.5" />
                            {e.updatedAt}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="relative hidden sm:flex items-center gap-3">
                      <div className="flex flex-col items-end gap-2">
                        {e.status === "to-review" && (
                          <Badge className="bg-gradient-to-r from-amber-100 to-orange-100 text-orange-800 border-0">
                            To review
                          </Badge>
                        )}
                        {e.status === "done" && (
                          <Badge className="bg-gradient-to-r from-emerald-100 to-green-100 text-green-800 border-0">
                            Completed
                          </Badge>
                        )}
                        <span className="flex items-center gap-1 text-xs text-gray-500">
                          <Clock className="h-3 w-3" />
                          {e.updatedAt}
                        </span>
                      </div>
                      <ChevronRight className="h-5 w-5 text-gray-400 transition-transform group-hover:translate-x-1 group-hover:text-gray-600" />
                    </div>
                    
                    <ChevronRight className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 transition-transform group-hover:translate-x-1 group-hover:text-gray-600 sm:hidden" />
                  </motion.button>
                ))}
                {!filtered.length && (
                  <motion.div 
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="grid place-items-center rounded-2xl bg-gradient-to-br from-gray-50 to-gray-100/50 p-12"
                  >
                    <div className="text-center">
                      <p className="text-lg font-medium text-gray-700">All caught up!</p>
                      <p className="mt-1 text-sm text-gray-500">No patients match this filter</p>
                    </div>
                  </motion.div>
                )}
              </motion.div>
            </AnimatePresence>
          </CardContent>
        </Card>
      </div>
    </motion.section>
  );
}
