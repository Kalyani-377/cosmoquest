import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { SignedIn, SignedOut } from "@clerk/clerk-react";

import OpeningPage from "./pages/OpeningPage";
import LoginPage from "./pages/LoginPage";
import LoadingPage from "./pages/loadingpage";
import SignupPage from "./pages/signupPage";
import Home from "./pages/homepage";
import Talk from "./pages/talk";
import EventDetails from "./pages/EventDetails";
import EventsPage from "./pages/EventsPage";
import Learn from "./pages/learn";
import DomainDetail from "./pages/DomainDetail";
import Layout from "./components/Layout";

export default function App() {
  return (
    <Router>
      <Routes>

        {/* Public Pages */}
        <Route path="/" element={<OpeningPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/loading" element={<LoadingPage />} />
        <Route path="/signup" element={<SignupPage />} />

        {/* Protected Main App Pages */}
        <Route element={<Layout />}>

          <Route
            path="/homepage"
            element={
              <>
                <SignedIn>
                  <Home />
                </SignedIn>

                <SignedOut>
                  <Navigate to="/login" replace />
                </SignedOut>
              </>
            }
          />

          <Route path="/talk" element={<Talk />} />
          <Route
            path="/events"
            element={
              <>
                <SignedIn>
                  <EventsPage />
                </SignedIn>
                <SignedOut>
                  <Navigate to="/login" replace />
                </SignedOut>
              </>
            }
          />
          <Route
            path="/events/:id"
            element={
              <>
                <SignedIn>
                  <EventDetails />
                </SignedIn>
                <SignedOut>
                  <Navigate to="/login" replace />
                </SignedOut>
              </>
            }
          />
          <Route path="/learn" element={<Learn />} />
          <Route path="/learn/domain/:id" element={<DomainDetail />} />

        </Route>

      </Routes>
    </Router>
  );
}