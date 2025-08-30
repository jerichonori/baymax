import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./index.css";
import App from "./App.tsx";
import LandingPage from "./pages/Landing.tsx";
import HomePage from "./pages/Home.tsx";
import IntakePage from "./pages/Intake.tsx";
import DoctorDashboardPage from "./pages/DoctorDashboard.tsx";
import EncounterDetailPage from "./pages/EncounterDetail.tsx";

const queryClient = new QueryClient();

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <LandingPage /> },
      { path: "intake", element: <IntakePage /> },
      { path: "doctor", element: <DoctorDashboardPage /> },
      { path: "doctor/:encounterId", element: <EncounterDetailPage /> },
    ],
  },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>
);
