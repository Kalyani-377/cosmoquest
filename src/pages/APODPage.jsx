import TopNavbar from "../components/topnav";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function APODPage() {
    const navigate = useNavigate();
    const [apod, setApod] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const cached = sessionStorage.getItem("dashboardData");
        if (cached) {
            const data = JSON.parse(cached);
            if (data.apod) {
                setApod(data.apod);
                setLoading(false);
                return;
            }
        }

        // If not in cache, we could fetch it, but usually the homepage handles it.
        // For robustness, redirecting to home if no data.
        const timer = setTimeout(() => {
            if (!apod) navigate('/homepage');
        }, 2000);
        return () => clearTimeout(timer);
    }, [navigate]);

    if (loading) {
        return (
            <div className="bg-black min-h-screen text-white flex flex-col items-center justify-center font-orbitron">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
                <p>Decoding Cosmic Signals...</p>
            </div>
        );
    }

    return (
        <div className="bg-black min-h-screen text-white font-orbitron">
            <TopNavbar />

            <main className="max-w-6xl mx-auto px-6 pt-32 pb-20">
                <button
                    onClick={() => navigate('/homepage')}
                    className="mb-8 flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors font-bold uppercase text-sm tracking-widest"
                >
                    ← Back to Mission Control
                </button>

                <div className="grid lg:grid-cols-2 gap-12 items-start">
                    <div className="relative group">
                        <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000"></div>
                        <div className="relative bg-black rounded-2xl border border-white/10 overflow-hidden shadow-2xl">
                            <img
                                src={apod.image}
                                alt={apod.title}
                                className="w-full h-auto"
                            />
                        </div>
                        <div className="mt-4 flex justify-between items-center text-white/40 text-xs uppercase tracking-widest">
                            <span>Source: NASA APOD</span>
                            <span>{new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
                        </div>
                    </div>

                    <div className="flex flex-col gap-6">
                        <div>
                            <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-blue-200 to-blue-400 tracking-tight leading-tight">
                                {apod.title}
                            </h1>
                            <div className="h-1 w-20 bg-blue-500 mt-4"></div>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-8 backdrop-blur-sm">
                            <h3 className="text-blue-400 text-sm font-bold uppercase tracking-[0.3em] mb-4">Astronomy Insight</h3>
                            <p className="text-white/80 leading-relaxed text-lg font-light">
                                {apod.explanation}
                            </p>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4">
                                <span className="block text-white/40 text-[10px] uppercase tracking-widest mb-1">Frequency</span>
                                <span className="text-white font-bold">Daily Updates</span>
                            </div>
                            <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-4">
                                <span className="block text-white/40 text-[10px] uppercase tracking-widest mb-1">Status</span>
                                <span className="text-green-400 font-bold">Live Stream</span>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
