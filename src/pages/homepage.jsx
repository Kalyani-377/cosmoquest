import TopNavbar from "../components/topnav";
import spaceVideo from "../assets/space.mp4";
import "./homepage.css";
import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@clerk/clerk-react";

export default function Home() {
  const navigate = useNavigate();
  const eventsRef = useRef(null);
  const { getToken } = useAuth();

  const [dashboardData, setDashboardData] = useState(() => {
    const cached = sessionStorage.getItem("dashboardData");
    return cached ? JSON.parse(cached) : null;
  });
  const [loading, setLoading] = useState(!dashboardData);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    // Force refresh if cache doesn't have the new curated event types
    const hasCuratedEvents = dashboardData?.events?.some((e) =>
      ["iss", "planets", "meteors"].includes(e.type),
    );

    if (dashboardData && dashboardData.apod && hasCuratedEvents) return;

    const fetchDashboard = async (lat, lng) => {
      try {
        const token = await getToken();

        const res = await fetch(
          `${import.meta.env.VITE_API_BASE_URL}/dashboard`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ lat, lng }),
          },
        );

        const data = await res.json();

        // Save to cache
        sessionStorage.setItem("dashboardData", JSON.stringify(data));

        setDashboardData(data);
        setLoading(false);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
        setLoading(false);
      }
    };

    navigator.geolocation.getCurrentPosition(
      (position) => {
        fetchDashboard(position.coords.latitude, position.coords.longitude);
      },
      () => {
        setLoading(false);
      },
    );
  }, []);

  if (loading) {
    return (
      <div className="text-white text-center mt-40 font-orbitron">
        Loading Cosmic Dashboard...
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="text-white text-center mt-40 font-orbitron">
        No cosmic data available
      </div>
    );
  }

  const filteredEvents =
    filter === "all"
      ? dashboardData.events
      : dashboardData.events.filter((event) =>
          event.type?.toLowerCase().includes(filter.toLowerCase()),
        );

  return (
    <div className="text-white font-orbitron min-h-screen bg-black">
      <TopNavbar />

      {/* HERO SECTION */}
      <section className="relative min-h-[90vh] flex flex-col items-center justify-center px-6 z-10 pt-20">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="absolute inset-0 w-full h-full object-cover -z-10 opacity-70 brightness-90"
        >
          <source src={spaceVideo} type="video/mp4" />
        </video>

        <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-transparent to-black -z-10"></div>

        <div className="relative z-10 flex flex-col items-center text-center max-w-4xl">
          <h1 className="text-6xl font-bold mb-6 tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-white via-blue-200 to-white/50">
            Explore the Universe
          </h1>

          {dashboardData.apod && (
            <div
              className="mb-12 group cursor-pointer max-w-lg"
              onClick={() => navigate("/apod")}
            >
              <div className="relative overflow-hidden rounded-2xl border border-white/10 shadow-[0_0_50px_rgba(0,100,255,0.1)] group-hover:border-blue-500/30 transition-all duration-500">
                <img
                  src={dashboardData.apod.image}
                  alt={dashboardData.apod.title}
                  className="w-full h-auto group-hover:scale-105 transition-transform duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-60"></div>
              </div>
              <h3 className="mt-4 text-xl font-semibold text-blue-300 group-hover:text-blue-200 transition-colors">
                {dashboardData.apod.title}
              </h3>
              <p className="text-white/40 mt-1 text-xs uppercase tracking-[0.2em]">
                NASA Astronomy Picture of the Day
              </p>
            </div>
          )}

          <p className="text-white/70 mb-10 text-lg max-w-2xl leading-relaxed">
            Your portal to the stars. Real-time natural events tracked by NASA
            and local astronomical sightings.
          </p>

          {/* FILTERS */}
          <div className="flex flex-wrap justify-center gap-4 mb-10">
            <CategoryCard
              label="🌌 All"
              active={filter === "all"}
              onClick={() => setFilter("all")}
            />
            <CategoryCard
              label="🛰 ISS"
              active={filter === "iss"}
              onClick={() => setFilter("iss")}
            />
            <CategoryCard
              label="🪐 Planets"
              active={filter === "planets"}
              onClick={() => setFilter("planets")}
            />
            <CategoryCard
              label="☄ Meteors"
              active={filter === "meteors"}
              onClick={() => setFilter("meteors")}
            />
            <CategoryCard
              label="🌑 Eclipses"
              active={filter === "eclipses"}
              onClick={() => setFilter("eclipses")}
            />
          </div>
        </div>
      </section>

      {/* EVENTS SECTION */}
      <section ref={eventsRef} className="px-6 py-10 max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold mb-10 text-center tracking-tight">
          Cosmic Events
        </h2>

        {filteredEvents.length === 0 ? (
          <p className="text-center text-white/40 italic py-10">
            No events found in this category.
          </p>
        ) : (
          <div className="grid md:grid-cols-2 gap-6">
            {filteredEvents.map((event) => (
              <div
                key={event.id}
                onClick={() => navigate(`/events/${event.id}`)}
                className="bg-white/5 border border-white/10 rounded-2xl p-6 cursor-pointer hover:bg-white/10 transition-all hover:-translate-y-1"
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-semibold">
                    {event.event_type || event.name}
                  </h3>
                  {event.source === "NASA LIVE" && (
                    <span className="px-2 py-0.5 bg-red-500/20 border border-red-500/50 rounded text-[8px] font-bold text-red-400 animate-pulse">
                      LIVE NASA DATA
                    </span>
                  )}
                </div>
                <p className="text-white/60 text-sm mb-4">
                  Visibility: {event.visibility}
                </p>
                <p className="text-white/40 text-sm line-clamp-2">
                  {event.description}
                </p>
                <div className="mt-4 text-blue-400 text-xs font-bold tracking-widest">
                  VIEW DETAILS →
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function CategoryCard({ label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`px-6 py-2 rounded-full border text-sm transition-all ${
        active
          ? "bg-blue-600 border-blue-500 text-white"
          : "bg-white/5 border-white/10 text-white/60 hover:border-white/30"
      }`}
    >
      {label}
    </button>
  );
}
