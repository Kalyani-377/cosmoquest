from flask import Flask, jsonify, request

from flask_cors import CORS
from db import engine, Base, SessionLocal
from models import Event
from datetime import date
from jose import jwt
from dotenv import load_dotenv
import requests
import os

load_dotenv()  # Load variables from .env file

NASA_API_KEY = "9vHqOmdd1WmG3l4Q4bBaN3Mn9imUsoyYFdw4C3vB"
# 🔐 Clerk domain
CLERK_DOMAIN = "curious-donkey-17.clerk.accounts.dev"
JWKS_URL = f"https://{CLERK_DOMAIN}/.well-known/jwks.json"

# Global JWKS cache
JWKS_CACHE = None

def get_jwks():
    global JWKS_CACHE
    if JWKS_CACHE is None:
        response = requests.get(JWKS_URL)
        response.raise_for_status()
        JWKS_CACHE = response.json()
    return JWKS_CACHE

def verify_clerk_token(token):
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    jwks_data = get_jwks()

    rsa_key = next(
        (key for key in jwks_data["keys"] if key["kid"] == kid),
        None
    )

    if not rsa_key:
        raise Exception("No matching key found")

    return jwt.decode(
        token,
        rsa_key,
        algorithms=["RS256"],
        options={
            "verify_aud": False,
            "verify_nbf": False
        }
    )

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

Base.metadata.create_all(bind=engine)

# ------------------------------
# Basic test route
# ------------------------------
@app.route("/")
def home():
    return {"message": "CosmoQuest Backend Signal Active"}

# 🚀 GLOBAL CURATED MISSIONS (2026 Calendar)
GLOBAL_CURATED_EVENTS = [
    {
        "id": "iss-global-1",
        "event_type": "ISS Transcontinental Pass",
        "type": "iss",
        "description": "The International Space Station will be visible as a bright, steady light crossing the sky over multiple continents tonight.",
        "location": "Global",
        "visibility": "High",
        "date": "2026-02-23"
    },
    {
        "id": "planet-global-1",
        "event_type": "Venus: Evening Star Peak",
        "type": "planet",
        "description": "Venus reaches its highest point in the evening sky, shining brighter than any star.",
        "location": "Global",
        "visibility": "Very High",
        "date": "2026-02-24"
    },
    {
        "id": "eclipse-lunar-2026",
        "event_type": "Total Lunar Eclipse (Blood Moon)",
        "type": "eclipse",
        "description": "The Moon passes through the Earth's shadow, turning a deep copper-red color. Visible across North America and Asia.",
        "location": "Global",
        "visibility": "High",
        "date": "2026-03-03"
    },
    {
        "id": "meteor-lyrids-2026",
        "event_type": "Lyrids Meteor Shower Peak",
        "type": "meteor",
        "description": "The oldest recorded meteor shower. Expect up to 18 meteors per hour under dark skies.",
        "location": "Northern Hemisphere",
        "visibility": "Medium",
        "date": "2026-04-22"
    },
    {
        "id": "planet-jupiter-2026",
        "event_type": "Jupiter-Venus Conjunction",
        "type": "planet",
        "description": "The two brightest planets will appear extremely close together in the morning sky. A rare celestial double-act.",
        "location": "Global",
        "visibility": "Extreme",
        "date": "2026-06-09"
    },
    {
        "id": "eclipse-solar-2026",
        "event_type": "Total Solar Eclipse 2026",
        "type": "eclipse",
        "description": "The first total solar eclipse in Europe for over 20 years. Path of totality crosses Greenland, Iceland, and Northern Spain.",
        "location": "Europe/North America",
        "visibility": "Extreme",
        "date": "2026-08-12"
    },
    {
        "id": "meteor-perseids-2026",
        "event_type": "Perseids Meteor Shower",
        "type": "meteor",
        "description": "The most popular meteor shower of the year. Known for fast, bright meteors and frequent fireballs.",
        "location": "Global",
        "visibility": "High",
        "date": "2026-08-13"
    },
    {
        "id": "planet-saturn-2026",
        "event_type": "Saturn at Opposition",
        "type": "planet",
        "description": "The ringed planet is at its closest to Earth and fully illuminated by the Sun. Best time for telescopic viewing.",
        "location": "Global",
        "visibility": "High",
        "date": "2026-10-04"
    },
    {
        "id": "meteor-orionids-2026",
        "event_type": "Orionids Meteor Shower",
        "type": "meteor",
        "description": "Meteors produced by debris from the famous Halley's Comet.",
        "location": "Global",
        "visibility": "Medium",
        "date": "2026-10-21"
    },
    {
        "id": "meteor-geminids-2026",
        "event_type": "Geminids Peak Visibility",
        "type": "meteor",
        "description": "Widely considered to be the best meteor shower in the heavens, producing up to 120 multicolored meteors per hour.",
        "location": "Global",
        "visibility": "High",
        "date": "2026-12-14"
    },
    {
        "id": "constellation-orion",
        "event_type": "Orion: The Hunter Emerges",
        "type": "constellation",
        "description": "One of the most recognizable constellations. Look for the three stars of Orion's Belt in a straight line.",
        "location": "Global",
        "visibility": "Very High",
        "date": "2026-02-23"
    },
    {
        "id": "constellation-ursa-major",
        "event_type": "Ursa Major (The Big Dipper)",
        "type": "constellation",
        "description": "High in the northern sky. Use its pointer stars to find Polaris, the North Star.",
        "location": "Northern Hemisphere",
        "visibility": "High",
        "date": "2026-03-21"
    },
    {
        "id": "constellation-canis-major",
        "event_type": "Canis Major (The Great Dog)",
        "type": "constellation",
        "description": "Home to Sirius, the brightest star in the sky. It follows Orion the Hunter across the heavens.",
        "location": "Global",
        "visibility": "Extreme",
        "date": "2026-02-24"
    }
]

# ------------------------------
# Protected events route
# ------------------------------
@app.route("/events")
def get_events():
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return {"error": "Unauthorized"}, 401

        db = SessionLocal()
        db_events = db.query(Event).all()
        
        local_results = [
            {
                "id": f"db-{e.id}",
                "type": e.type or "star",
                "event_type": e.event_type,
                "description": e.description,
                "location": e.location or "Unknown",
                "visibility": e.visibility or "Medium",
                "date": e.date or str(date.today())
            }
            for e in db_events
        ]
        db.close()

        return jsonify({
            "events": GLOBAL_CURATED_EVENTS + local_results
        })
    except Exception as e:
        print(f"ERROR IN /events: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ------------------------------
# NEW: Protected dashboard route
# ------------------------------


WEATHER_API_KEY = os.getenv("WEATHER_API")

@app.route("/dashboard", methods=["POST"])
def dashboard():
    print("DASHBOARD REQUEST RECEIVED")
    today = date.today()
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return {"error": "Unauthorized"}, 401

    parts = auth_header.split(" ")
    if len(parts) != 2:
        return {"error": "Invalid Authorization header"}, 401
    token = parts[1]

    try:
        user_data = verify_clerk_token(token)
    except Exception:
        return {"error": "Invalid token"}, 401

    data = request.json
    lat = data.get("lat")
    lng = data.get("lng")

    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={WEATHER_API_KEY}&units=metric"
    try:
        weather_response = requests.get(weather_url).json()
        
        if weather_response.get("cod") != 200:
            return jsonify({"error": f"Weather API error: {weather_response.get('message', 'Unknown error')}"}), 500

        cloud_cover = weather_response["clouds"]["all"]
        condition = weather_response["weather"][0]["description"]
    except Exception as e:
        return jsonify({"error": f"Failed to fetch weather data: {str(e)}"}), 500

    # DYNAMIC CELESTIAL ENGINE ( Hemispheric & Seasonal Logic)
    visible_constellations = []
    month = today.month
    is_northern = lat > 0

    # Constellation Database (Hemisphere, Best Months, Description)
    CONSTELLATION_DATA = [
        {"name": "Orion (The Hunter)", "hemi": "both", "months": [12, 1, 2, 3], "desc": "The most famous winter constellation. Look for the three stars of Orion's Belt."},
        {"name": "Ursa Major (Big Dipper)", "hemi": "north", "months": list(range(1, 13)), "desc": "Visible year-round in the north. Its pointer stars lead to the North Star."},
        {"name": "Crux (Southern Cross)", "hemi": "south", "months": list(range(1, 13)), "desc": "The iconic symbol of the southern skies. Used for navigation for centuries."},
        {"name": "Scorpius (The Scorpion)", "hemi": "both", "months": [5, 6, 7, 8], "desc": "A magnificent constellation with the red supergiant star Antares at its heart."},
        {"name": "Leo (The Lion)", "hemi": "both", "months": [3, 4, 5, 6], "desc": "A sign of Spring in the north. Its brightest star Regulus sits on the ecliptic."},
        {"name": "Cygnus (The Swan)", "hemi": "north", "months": [7, 8, 9, 10], "desc": "Part of the Summer Triangle. Its cross shape is easily identified in the Milky Way."},
        {"name": "Cassiopeia (The Queen)", "hemi": "north", "months": list(range(1, 13)), "desc": "A distinct 'W' or 'M' shape across from the Big Dipper."},
        {"name": "Centaurus", "hemi": "south", "months": [3, 4, 5, 6, 7], "desc": "Home to Alpha Centauri, the closest star system to our Sun."},
        {"name": "Gemini (The Twins)", "hemi": "both", "months": [1, 2, 3, 4, 12], "desc": "Represented by the bright twin stars Castor and Pollux."},
        {"name": "Taurus (The Bull)", "hemi": "both", "months": [11, 12, 1, 2, 3], "desc": "Contains the bright Pleaides star cluster (The Seven Sisters)."},
        {"name": "Canis Major (The Great Dog)", "hemi": "both", "months": [12, 1, 2, 3, 4], "desc": "The constellation containing Sirius, the brightest star in the night sky. It represents the larger of Orion's two hunting dogs."}
    ]

    # Filter by user location, current time, AND WEATHER
    for c in CONSTELLATION_DATA:
        if month in c['months']:
            if c['hemi'] == 'both' or (c['hemi'] == 'north' and is_northern) or (c['hemi'] == 'south' and not is_northern):
                # WEATHER LOGIC: Adjust status based on cloud cover
                if cloud_cover < 30:
                    status = "PRIME VIEWING"
                    weather_advice = "Perfectly clear skies tonight."
                elif cloud_cover < 70:
                    status = "INTERMITTENT"
                    weather_advice = "Passing clouds might obscure viewing."
                else:
                    status = "OBSCURED"
                    weather_advice = "Heavy cloud cover detected. Use orbital data for tracking."

                visible_constellations.append({
                    "id": f"constellation_{c['name'].replace(' ', '-')}",
                    "event_type": c['name'],
                    "type": "constellations",
                    "visibility": status,
                    "date": str(today),
                    "description": f"{c['desc']} {weather_advice}"
                })

    # CURATED LOCATION-BASED EVENTS
    event_list = visible_constellations[:4] # Pick top 4 relevant ones

    # 1. REAL ISS PASS (Based on user coordinates)
    try:
        iss_req = requests.get(f"http://api.open-notify.org/iss-pass.json?lat={lat}&lon={lng}&n=1")
        if iss_req.status_code == 200:
            iss_data = iss_req.json()
            pass_time = iss_data['response'][0]['risetime']
            event_list.append({
                "id": f"iss_ISS-Overpass-{pass_time}",
                "event_type": "ISS Overpass",
                "type": "iss",
                "visibility": "HIGH (CLEAR SKIES)" if cloud_cover < 40 else "POOR (CLOUDY)",
                "date": str(date.fromtimestamp(pass_time)),
                "description": f"The ISS will pass over at {date.fromtimestamp(pass_time).strftime('%H:%M')}. {'Look for a bright streak!' if cloud_cover < 40 else 'Cloud cover may block the view.'}"
            })
    except:
        event_list.append({
            "id": "iss_ISS-Visible-Tonight",
            "event_type": "ISS Visible Tonight",
            "type": "iss",
            "visibility": "Medium",
            "description": "The ISS is currently visible in your region. Check local charts for exact timing."
        })

    # 2. PROMINENT STARS (Position Aware)
    brightest_stars = [
        {"name": "Sirius (The Dog Star)", "hemi": "both", "months": [12, 1, 2, 3, 4], "desc": "The brightest star in the entire night sky."},
        {"name": "Canopus", "hemi": "south", "months": [1, 2, 3], "desc": "The second brightest star, legendary in the Southern Hemisphere."},
        {"name": "Vega", "hemi": "north", "months": [6, 7, 8, 9], "desc": "A brilliant blue-white star, part of the Summer Triangle."}
    ]
    
    for s in brightest_stars:
        if month in s['months']:
             if s['hemi'] == 'both' or (s['hemi'] == 'north' and is_northern) or (s['hemi'] == 'south' and not is_northern):
                # WEATHER LOGIC for stars
                if cloud_cover < 20:
                    status = "BRIGHT PEAK"
                elif cloud_cover < 50:
                    status = "VISIBLE"
                else:
                    status = "LOW VISIBILITY"

                event_list.append({
                    "id": f"star_{s['name'].replace(' ', '-')}",
                    "event_type": s['name'],
                    "type": "constellations",
                    "visibility": status,
                    "date": str(today),
                    "description": f"{s['desc']} Current local cloud cover is {cloud_cover}%."
                })

    # 3. PLANETS
    try:
        donki_url = f"https://api.nasa.gov/DONKI/FLR?startDate={today}&api_key={NASA_API_KEY or 'DEMO_KEY'}"
        donki_res = requests.get(donki_url).json()
        if donki_res:
             flare = donki_res[-1]
             event_list.append({
                "id": f"solar_Flare-{flare['flrID']}",
                "event_type": f"Solar Flare {flare['classType']}",
                "type": "iss",
                "source": "NASA LIVE",
                "visibility": "Radio Aurora Possible",
                "date": flare['beginTime'].split('T')[0],
                "description": f"A {flare['classType']} class solar flare was detected peaking recently. This is real-time space weather data from NASA's DONKI system."
            })
    except:
        pass

    # 5. REAL-TIME ASTEROIDS (NASA NeoWs)
    try:
        neo_url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={today}&end_date={today}&api_key={NASA_API_KEY or 'DEMO_KEY'}"
        neo_res = requests.get(neo_url).json()
        neos = neo_res.get("near_earth_objects", {}).get(str(today), [])
        if neos:
            top_neo = neos[0]
            event_list.append({
                "id": f"asteroid_{top_neo['name'].replace(' ', '-')}",
                "event_type": f"Asteroid {top_neo['name']}",
                "type": "meteors",
                "source": "NASA LIVE",
                "visibility": "Live Tracking",
                "date": str(today),
                "description": f"Real-time tracking of Asteroid {top_neo['name']}. It is currently moving at {float(top_neo['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']):,.0f} km/h."
            })
    except:
        pass

    # 5. METEORS (Fallback)
    if today.month == 4:
        event_list.append({"id":"meteor_Lyrids-Shower", "event_type":"Lyrids Meteor Shower", "type":"meteors", "visibility":"High", "description":"Active tonight! Best viewed from dark spots."})
    elif today.month == 8:
        event_list.append({"id":"meteor_Perseids-Peak", "event_type":"Perseids Meteor Shower", "type":"meteors", "visibility":"High", "description":"Peak activity tonight!"})

    # 6. ECLIPSES / ALIGNMENT
    event_list.append({
        "id": "eclipse_Lunar-Alignment",
        "event_type": "Lunar Elevation",
        "type": "eclipses",
        "visibility": "Information",
        "date": str(today),
        "description": "The moon is in an optimal phase for crater observation with simple binoculars."
    })

    # Calculate dark spots based on cloud cover
    if cloud_cover < 40:
        dark_spots = [
            {
                "name": "Hilltop Viewpoint",
                "distance_km": 12,
                "light_pollution_level": "Low"
            },
            {
                "name": "Lake Side Open Field",
                "distance_km": 18,
                "light_pollution_level": "Very Low"
            }
        ]
    else:
        dark_spots = [
            {
                "message": "High cloud cover. Consider another night."
            }
        ]
    apod_url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"
    apod_response = requests.get(apod_url).json()

    apod_data = {
        "title": apod_response.get("title"),
        "image": apod_response.get("url"),
        "explanation": apod_response.get("explanation")
    }

    return jsonify({
        "location": {"lat": lat, "lng": lng},
        "weather": {
            "condition": condition,
            "cloud_cover": cloud_cover
        },
        "events": event_list,
        "dark_spots": dark_spots,
        "apod": apod_data
    })


# ------------------------------
# Single event details route
# ------------------------------
@app.route("/event-details/<event_id>")
def get_event_details(event_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return {"error": "Unauthorized"}, 401
    
    lat = request.args.get("lat", "Unknown")
    lng = request.args.get("lng", "Unknown")

    # FIRST: Check if it's a Global Curated Event
    curated = next((e for e in GLOBAL_CURATED_EVENTS if e["id"] == event_id), None)
    
    if curated:
        display_name = curated["event_type"]
        raw_type = curated["type"]
    elif "_" in event_id:
        raw_type, slug_name = event_id.split("_", 1)
        display_name = slug_name.replace("-", " ")
        if display_name.split()[-1].isdigit():
             display_name = " ".join(display_name.split()[:-1])
    else:
        raw_type = event_id.split("-")[0].lower()
        base_name_map = {
            "iss": "ISS Overpass",
            "planet": "Planetary View",
            "meteor": "Meteor Shower",
            "eclipse": "Lunar Alignment"
        }
        temp_base = raw_type[:-1] if raw_type.endswith('s') and raw_type != 'iss' else raw_type
        display_name = base_name_map.get(temp_base, "Cosmic Event")

    base_type = raw_type[:-1] if raw_type.endswith('s') and raw_type != 'iss' else raw_type
    
    # Keyword-based type detection for perfect accuracy
    name_lower = display_name.lower()
    if "iss" in name_lower: base_type = "iss"
    elif "solar eclipse" in name_lower: base_type = "solar_eclipse"
    elif "moon" in name_lower or "lunar" in name_lower: base_type = "moon"
    elif "jupiter" in name_lower: base_type = "jupiter"
    elif "venus" in name_lower: base_type = "venus"
    elif "meteor" in name_lower: base_type = "meteor"
    elif "asteroid" in name_lower: base_type = "asteroid"
    elif "solar" in name_lower or "flare" in name_lower: base_type = "solar"
    elif "saturn" in name_lower: base_type = "saturn"
    elif "ursa" in name_lower: base_type = "ursa"
    elif "orion" in name_lower: base_type = "orion"
    elif "constellation" in name_lower: base_type = "constellation"
    elif "sirius" in name_lower or "canis major" in name_lower: base_type = "sirius"
    
    details = {
        "orion": {
            "image": "https://c02.purpledshub.com/uploads/sites/48/2020/02/Orion-07db06a.jpg",
            "spots": ["Orion's Belt Lookout", "Celestial Hunter Station"],
            "tips": ["The three stars of the belt are Betelgeuse, Rigel, and Bellatrix.", "Look for the Orion Nebula (M42) just below the belt.", "Orion is one of the most recognizable constellations in the night sky."]
        },
        "ursa": {
            "image": "https://nineplanets.org/wp-content/uploads/2020/12/the-constellation-of-ursa-major-7.jpg",
            "spots": ["Northern Horizon Clearings", "North Hill Observatory"],
            "tips": ["The pointer stars in the bowl of the Big Dipper point directly to Polaris.", "Look for M81 and M82, two bright galaxies near the 'head' of the bear.", "Ursa Major is circumpolar in most of the northern hemisphere, meaning it never sets."]
        },
        "iss": {
            "image": "https://images.pexels.com/photos/586073/pexels-photo-586073.jpeg",
            "spots": ["Satellite Viewpoint", "Outer Rim Observatory", "North Hill Clearing"],
            "tips": ["Look for a bright 'star' moving steadily without blinking.", "Use a sky tracking app to know exactly where it will emerge.", "No telescope needed - it's best seen with the naked eye!"]
        },
        "asteroid": {
            "image": "https://images.unsplash.com/photo-1614314107768-6018063b1672?auto=format&fit=crop&q=80&w=2000",
            "spots": ["Deep Space Observatory", "Backyard Telescope Range"],
            "tips": ["Most asteroids require a telescope to see as they appear as small points of light.", "Track the object across the star field over several hours to notice its movement.", "Use a sky map to identify the exact constellation it is passing through."]
        },
        "solar_eclipse": {
            "image": "https://images.pexels.com/photos/580679/pexels-photo-580679.jpeg",
            "spots": ["Total Path Clearning", "Eclipse Ridge", "Summit Lookout"],
            "tips": ["NEVER look at a solar eclipse directly without certified eclipse glasses.", "Watch for the 'Diamond Ring' effect just before and after totality.", "Look for crescent-shaped shadows under trees during the partial phase."]
        },
        "solar": {
            "image": "https://images.pexels.com/photos/580679/pexels-photo-580679.jpeg",
            "spots": ["High Latitude Viewpoint", "Northern Horizon Clearing"],
            "tips": ["Solar flares can spark Auroras (Northern Lights) 1-3 days after the event.", "Check 'K-Index' values - a Kp of 5 or more indicates a solar storm.", "Move away from city lights and look towards the magnetic poles."]
        },
        "jupiter": {
            "image": "https://images.pexels.com/photos/20337592/pexels-photo-20337592.jpeg",
            "spots": ["Planetary Vista", "Stargazer Flat", "Lake View Ridge"],
            "tips": ["Jupiter is the largest planet in our solar system and very bright.", "Binoculars will reveal Jupiter's four largest moons as tiny dots.", "Look slightly to the side of the planet (averted vision) to see more detail."]
        },
        "venus": {
            "image": "https://images.pexels.com/photos/12498801/pexels-photo-12498801.jpeg",
            "spots": ["Evening Star Ridge", "Morning Vista Point"],
            "tips": ["Venus is the brightest object in the sky after the Sun and Moon.", "It is often called the 'Evening Star' as it's the first to appear after sunset.", "A small telescope will reveal its phases, which look like the Moon's phases."]
        },
        "saturn": {
            "image": "https://images.pexels.com/photos/12498805/pexels-photo-12498805.jpeg",
            "spots": ["Ring Viewpoint", "High Altitude Ridge", "Dark Sky Plateau"],
            "tips": ["Saturn's rings are visible even in a small telescope.", "Look for the moon Titan, which looks like a tiny star near the planet.", "Opposition is the best time to see the planet as it is brightest and closest."]
        },
        "planet": {
            "image": "https://images.pexels.com/photos/1819676/pexels-photo-1819676.jpeg",
            "spots": ["Planetary Vista", "Stargazer Flat", "Lake View Ridge"],
            "tips": ["Planets shine with a steady light, unlike stars which twinkle.", "Use an astronomy app to identify which planet you are looking at.", "Early evening is often the best time for planetary observation."]
        },
        "moon": {
            "image": "https://images.unsplash.com/photo-1446941611757-91d2c3bd3d45?auto=format&fit=crop&q=80&w=2000",
            "spots": ["Crater Viewmont", "Lunar Plateau", "Shadow Rim Ridge"],
            "tips": ["The line between light and dark (the terminator) is where craters are most visible.", "A moon filter for your telescope can reduce glare and show more detail.", "Even simple binoculars will reveal the moon's maria and major craters."]
        },
        "constellation": {
            "image": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&q=80&w=2000",
            "spots": ["Deep Space Lookout", "Mountain Vista", "Quiet Field Station"],
            "tips": ["Use a star map or app to connect the dots between major stars.", "Avert your vision (look slightly away) to see fainter stars in the pattern.", "Wait for a moonless night for the best contrast against the black sky."]
        },
        "meteor": {
            "image": "https://images.pexels.com/photos/11565999/pexels-photo-11565999.jpeg",
            "spots": ["Meteor Peak", "Comet Valley", "Dark Wood Plateau"],
            "tips": ["Lie flat on your back and look straight up to see the most sky.", "Give your eyes at least 20 minutes to adjust to the total darkness.", "Avoid looking at your phone - the blue light will ruin your night vision."]
        },
        "eclipse": {
            "image": "https://images.unsplash.com/photo-1532960401447-7ee053238bd1?auto=format&fit=crop&q=80&w=2000",
            "spots": ["Shadow Ridge", "Lunar Hollow", "Ancient Stone Lookout"],
            "tips": ["Lunar eclipses are perfectly safe to view with the naked eye.", "Watch for the 'Blood Moon' effect as the moon turns deep red.", "Try long-exposure photography to capture the subtle color shifts."]
        },
        "sirius": {
            "image": "https://upload.wikimedia.org/wikipedia/commons/c/c6/Sirius.jpg",
            "spots": ["Southern Horizon View", "Clear Sky Peak"],
            "tips": ["Sirius is the brightest star in the night sky and the focal point of Canis Major.", "It's also known as the Dog Star because it's in the constellation Canis Major (The Great Dog).", "To find it, follow the line of Orion's Belt down and to the left.", "The star's bright blue-white glow is unmistakable even in light-polluted areas."]
        }
    }

    if base_type in details:
        import random
        random.seed(lat)
        regions = ["North", "South", "West", "East", "Central"]
        dynamic_spots = [
            {"name": f"{random.choice(regions)} {details[base_type]['spots'][0]}", "level": "Excellent (Bortle 2)"},
            {"name": f"{details[base_type]['spots'][1]} Near You", "level": "Good (Bortle 4)"}
        ]

        # REAL-TIME WEATHER FOR DETAILS PAGE
        local_weather = {"condition": "Optimal Viewing", "cloud_cover": 0}
        if lat != "Unknown" and lng != "Unknown":
            try:
                w_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={WEATHER_API_KEY}&units=metric"
                w_res = requests.get(w_url).json()
                if w_res.get("cod") == 200:
                    local_weather = {
                        "condition": w_res["weather"][0]["description"].capitalize(),
                        "cloud_cover": w_res["clouds"]["all"]
                    }
            except:
                pass

        return jsonify({
            "id": event_id,
            "name": display_name,
            "description": f"This is a LIVE tracking mission. {display_name} has been identified in the current sector. For the best experience, move away from city lights.",
            "visibility": "High" if local_weather['cloud_cover'] < 40 else "Medium" if local_weather['cloud_cover'] < 70 else "Low",
            "date": curated["date"] if curated else str(date.today()),
            "image": details[base_type]["image"],
            "dark_spots": dynamic_spots,
            "tips": details[base_type]["tips"],
            "weather": local_weather
        })

    # 2. Handle database IDs (marked with db-)
    if event_id.startswith("db-"):
        actual_id = int(event_id.replace("db-", ""))
        db = SessionLocal()
        event = db.query(Event).filter(Event.id == actual_id).first()
        db.close()
        
        if event:
            # Re-use details if possible for images and tips
            ev_type = (event.type or "planet").lower()
            if ev_type.endswith('s') and ev_type != 'iss': ev_type = ev_type[:-1]
            
            # Keyword scan for database events
            name_lower = event.event_type.lower()
            if "iss" in name_lower: ev_type = "iss"
            elif "moon" in name_lower or "lunar" in name_lower: ev_type = "moon"
            elif "jupiter" in name_lower: ev_type = "jupiter"
            elif "venus" in name_lower: ev_type = "venus"
            elif "meteor" in name_lower: ev_type = "meteor"
            elif "asteroid" in name_lower: ev_type = "asteroid"
            elif "solar" in name_lower or "flare" in name_lower: ev_type = "solar"
            elif "saturn" in name_lower: ev_type = "saturn"

            info = details.get(ev_type, details["planet"])
            
            # REAL-TIME WEATHER FOR DATABASE EVENTS
            local_weather = {"condition": "Sky Scanning...", "cloud_cover": 0}
            if lat != "Unknown" and lng != "Unknown":
                try:
                    w_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={WEATHER_API_KEY}&units=metric"
                    w_res = requests.get(w_url).json()
                    if w_res.get("cod") == 200:
                        local_weather = {
                            "condition": w_res["weather"][0]["description"].capitalize(),
                            "cloud_cover": w_res["clouds"]["all"]
                        }
                except:
                    pass

            return jsonify({
                "id": event_id,
                "name": event.event_type,
                "description": event.description,
                "visibility": event.visibility or ("High" if local_weather['cloud_cover'] < 40 else "Low"),
                "date": event.date or str(date.today()),
                "image": info["image"],
                "dark_spots": [{"name": "Regional Observatory", "level": "Excellent (Bortle 2)"}, {"name": "Mountain Ridge", "level": "Good (Bortle 4)"}],
                "tips": info["tips"],
                "weather": local_weather
            })

    return {"error": "Event not found"}, 404
# ------------------------------
# Test event route
# ------------------------------
@app.route("/add-test-event")
def add_test_event():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()

    events = [
        Event(
            type="iss",
            event_type="ISS Overpass Kerala",
            description="Crystal clear visibility expected over coastal regions tonight.",
            location="Kochi, Kerala",
            visibility="High",
            date="2026-02-23"
        ),
        Event(
            type="planet",
            event_type="Jupiter Moon Transit",
            description="Io and Europa will be visible crossing Jupiter's disk.",
            location="Hyderabad, India",
            visibility="Very High",
            date="2026-02-24"
        ),
        Event(
            type="meteor",
            event_type="Orionids Shower",
            description="Best viewed from the high altitude parks.",
            location="Bangalore, India",
            visibility="Medium",
            date="2026-10-21"
        ),
        Event(
            type="eclipse",
            event_type="Total Lunar Eclipse",
            description="The 'Blood Moon' will be visible across North America and Asia.",
            location="Global",
            visibility="High",
            date="2026-03-03"
        ),
        Event(
            type="iss",
            event_type="ISS Transcontinental",
            description="Visible for 6 minutes straight over the horizon.",
            location="Global",
            visibility="High",
            date="2026-02-23"
        )
    ]

    for e in events:
        db.add(e)
    
    db.commit()
    db.close()

    return {"status": "Universal Database Ready. Events added for Kerala, Hyderabad, Bangalore, and Global."}

if __name__ == "__main__":
    app.run(debug=True)