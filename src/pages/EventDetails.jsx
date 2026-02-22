import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { useAuth } from "@clerk/clerk-react";
import TopNavbar from "../components/topnav";

export default function EventDetails() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { getToken } = useAuth();
    const [event, setEvent] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchEvent = async () => {
            const token = await getToken();
            const cachedData = JSON.parse(sessionStorage.getItem("dashboardData") || "{}");
            const lat = cachedData.location?.lat || "";
            const lng = cachedData.location?.lng || "";

            try {
                const res = await fetch(`http://localhost:5000/event-details/${id}?lat=${lat}&lng=${lng}`, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                if (!res.ok) {
                    const errorData = await res.json();
                    setError(errorData.error || "Failed to fetch event details");
                    return;
                }

                const data = await res.json();
                setEvent(data);
            } catch (err) {
                console.error("Fetch error:", err);
                setError("Network error or server unreachable");
            }
        };

        fetchEvent();
    }, [id]);

    if (error) {
        return (
            <div className="min-h-screen bg-black text-white text-center flex flex-col items-center justify-center p-6">
                <p className="text-red-400 text-xl font-orbitron mb-6">{error}</p>
                <button
                    onClick={() => navigate("/")}
                    className="px-8 py-3 bg-blue-600 rounded-full hover:bg-blue-500 transition-all font-orbitron shadow-lg shadow-blue-500/20"
                >
                    Back to Home
                </button>
            </div>
        );
    }

    if (!event) {
        return (
            <div className="min-h-screen bg-black text-white text-center flex items-center justify-center font-orbitron">
                <div className="animate-pulse">Locating Cosmic Event...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-black text-white font-orbitron">
            <TopNavbar />

            {/* HERO HERO SECTION */}
            <div className="relative h-[50vh] w-full overflow-hidden">
                <img
                    src={event.image}
                    alt={event.name}
                    className="w-full h-full object-cover opacity-60"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-black/40"></div>

                <div className="absolute bottom-10 left-0 right-0 px-6 max-w-6xl mx-auto">
                    <button
                        onClick={() => navigate(-1)}
                        className="mb-8 flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-all group"
                    >
                        <span className="group-hover:-translate-x-1 transition-transform">←</span> BACK TO COSMOS
                    </button>
                    <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-2">
                        {event.name}
                    </h1>
                    <div className="flex flex-wrap gap-4 mt-4">
                        <span className="px-4 py-1.5 bg-blue-500/20 border border-blue-500/50 rounded-full text-xs font-bold tracking-widest text-blue-300">
                            ID: {event.id.toUpperCase()}
                        </span>
                        <span className="px-4 py-1.5 bg-green-500/20 border border-green-500/50 rounded-full text-xs font-bold tracking-widest text-green-300">
                            STATUS: ACTIVE
                        </span>
                    </div>
                </div>
            </div>

            <div className="max-w-6xl mx-auto px-6 py-16 grid md:grid-cols-3 gap-12">

                {/* LEFT CONTENT */}
                <div className="md:col-span-2 space-y-12">
                    <section>
                        <h2 className="text-2xl font-bold mb-6 text-blue-400 border-b border-white/10 pb-2">Analysis</h2>
                        <p className="text-white/70 text-lg leading-relaxed">
                            {event.description}
                        </p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-6 text-green-400 border-b border-white/10 pb-2">Observation Tips</h2>
                        <ul className="space-y-4">
                            {event.tips?.map((tip, i) => (
                                <li key={i} className="flex items-start gap-4 text-white/70">
                                    <span className="text-green-500 mt-1">✦</span>
                                    <span>{tip}</span>
                                </li>
                            ))}
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-6 text-purple-400 border-b border-white/10 pb-2">Optimal Dark Spots</h2>
                        <div className="grid sm:grid-cols-2 gap-4">
                            {event.dark_spots?.map((spot, i) => (
                                <div key={i} className="p-4 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-all group">
                                    <h4 className="font-bold text-white group-hover:text-blue-300">{spot.name}</h4>
                                    <p className="text-sm text-white/50">{spot.level} pollution level</p>
                                </div>
                            ))}
                        </div>
                    </section>
                </div>

                {/* RIGHT SIDEBAR */}
                <div className="space-y-8">
                    <div className="p-8 bg-blue-500/5 border border-blue-500/20 rounded-3xl">
                        <h3 className="text-xs uppercase tracking-widest text-blue-400 font-bold mb-6">Observation Metrics</h3>

                        <div className="space-y-6">
                            <div>
                                <label className="text-[10px] text-white/30 uppercase tracking-widest block mb-1">Visibility Ranking</label>
                                <span className="text-xl font-bold text-white">{event.visibility}</span>
                            </div>
                            <div>
                                <label className="text-[10px] text-white/30 uppercase tracking-widest block mb-1">Sky Conditions</label>
                                <span className="text-xl font-bold text-white">{event.weather.condition}</span>
                            </div>
                            <div>
                                <label className="text-[10px] text-white/30 uppercase tracking-widest block mb-1">Equipment Suggested</label>
                                <span className="text-sm font-bold text-white uppercase tracking-tighter">70mm Refractor + Viewfinder</span>
                            </div>
                        </div>
                    </div>

                    <div className="p-8 bg-purple-500/5 border border-purple-500/20 rounded-3xl">
                        <p className="text-xs text-purple-400/80 italic leading-relaxed">
                            "The universe is under no obligation to make sense to you."
                        </p>
                    </div>
                </div>

            </div>
        </div>
    );
}