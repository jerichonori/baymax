import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";

export default function HomePage() {
  return (
    <section className="grid gap-10 py-8 lg:grid-cols-2 lg:items-center">
      <div className="space-y-6">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          AI Patient Intake for India
        </h1>
        <p className="text-lg text-gray-600">
          Multilingual conversational intake with safety guardrails. English
          summaries for doctors and a lightweight EMR.
        </p>
        <div className="flex gap-3">
          <Button asChild>
            <Link to="/intake">Start Intake</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to="/doctor">Doctor Dashboard</Link>
          </Button>
        </div>
        <ul className="grid gap-3 text-sm text-gray-600 sm:grid-cols-2">
          <li>• Multilingual chat + voice</li>
          <li>• Red flag detection</li>
          <li>• Structured ortho HPI</li>
          <li>• Secure by default</li>
        </ul>
      </div>
      <div className="relative hidden aspect-[4/3] overflow-hidden rounded-xl border bg-gradient-to-br from-blue-50 to-indigo-50 lg:block">
        <div className="absolute inset-0 grid place-items-center text-blue-700">
          <span className="text-7xl">🩺</span>
        </div>
      </div>
    </section>
  );
}
