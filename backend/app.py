from flask import Flask, jsonify, request
from flask_cors import CORS
from db import engine, Base, SessionLocal
from models import Event
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
    return {"message": "Backend running"}

# ------------------------------
# Protected events route
# ------------------------------
@app.route("/events")
def get_events():
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

    # CURATED GLOBAL EVENTS (Irrespective of location)
    curated_events = [
        {
            "id": "iss-global-1",
            "event_type": "ISS Transcontinental Pass",
            "type": "iss",
            "description": "The ISS will be visible across multiple continents tonight. A bright streak of light.",
            "location": "Global",
            "visibility": "High"
        },
        {
            "id": "planet-global-1",
            "event_type": "Venus Peak Visibility",
            "type": "planet",
            "description": "Venus reaches its highest point in the evening sky.",
            "location": "Global",
            "visibility": "Very High"
        },
        {
            "id": "meteor-global-1",
            "event_type": "Geminids Peak",
            "type": "meteor",
            "description": "The most reliable annual meteor shower peaking worldwide.",
            "location": "Global",
            "visibility": "High"
        },
        {
             "id": "eclipse-global-1",
            "event_type": "Solar Eclipse 2026",
            "type": "eclipse",
            "description": "Upcoming total solar eclipse visible in certain regions.",
            "location": "North America",
            "visibility": "Extreme"
        }
    ]

    db = SessionLocal()
    db_events = db.query(Event).all()
    
    local_results = [
        {
            "id": f"db-{e.id}",
            "type": e.type or "star",
            "event_type": e.event_type,
            "description": e.description,
            "location": e.location or "Unknown",
            "visibility": e.visibility or "Medium"
        }
        for e in db_events
    ]
    db.close()

    return jsonify({
        "events": curated_events + local_results
    })

# ------------------------------
# NEW: Protected dashboard route
# ------------------------------


WEATHER_API_KEY = os.getenv("WEATHER_API")

@app.route("/dashboard", methods=["POST"])
def dashboard():
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

    # CURATED LOCATION-BASED EVENTS
    event_list = []

    # 1. REAL ISS PASS (Based on user coordinates)
    try:
        iss_req = requests.get(f"http://api.open-notify.org/iss-pass.json?lat={lat}&lon={lng}&n=1")
        if iss_req.status_code == 200:
            iss_data = iss_req.json()
            pass_time = iss_data['response'][0]['risetime']
            event_list.append({
                "id": f"iss_ISS-Overpass-{pass_time}",
                "name": "ISS Overpass",
                "type": "iss",
                "visibility": "High",
                "description": f"The ISS will pass directly over your location tonight. Look for a bright, steady light moving across the sky."
            })
    except:
        event_list.append({
            "id": "iss_ISS-Visible-Tonight",
            "name": "ISS Visible Tonight",
            "type": "iss",
            "visibility": "Medium",
            "description": "The ISS is currently visible in your region. Check local charts for exact timing."
        })

    # 2. PLANETS
    event_list.append({
        "id": "planet_Jupiter-Brightness",
        "name": "Jupiter Brightness",
        "type": "planets",
        "visibility": "Very High" if cloud_cover < 20 else "Medium",
        "description": f"Visible in the Eastern sky. Currently at its brightest point from your location."
    })

    # 3. METEORS
    import datetime
    today = datetime.date.today()
    if today.month == 4:
        event_list.append({"id":"meteor_Lyrids-Meteor-Shower", "name":"Lyrids Meteor Shower", "type":"meteors", "visibility":"High", "description":"Active tonight! Best viewed from dark spots."})
    elif today.month == 8:
        event_list.append({"id":"meteor_Perseids-Meteor-Shower", "name":"Perseids Meteor Shower", "type":"meteors", "visibility":"High", "description":"Peak activity tonight!"})
    else:
         event_list.append({"id":"meteor_Sporadic-Meteors", "name":"Sporadic Meteors", "type":"meteors", "visibility":"Low", "description":"Occasional shooting stars visible during peak darkness."})

    # 4. ECLIPSES
    event_list.append({
        "id": "eclipse_Next-Lunar-Alignment",
        "name": "Next Lunar Alignment",
        "type": "eclipses",
        "visibility": "Information",
        "description": "No immediate eclipses tonight, but the moon is in an optimal phase for telescope viewing."
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

    # Mapping to correct singular type and extracting the user-visible name
    # ID format: type_Name-With-Dashes-Or-Numbers
    if "_" in event_id:
        raw_type, slug_name = event_id.split("_", 1)
        display_name = slug_name.replace("-", " ")
        # If there's a numeric suffix (like risetime), keep it clean
        if display_name.split()[-1].isdigit():
             display_name = " ".join(display_name.split()[:-1])
    else:
        # Handle old/fallback IDs (e.g., planet-1, iss-fallback)
        raw_type = event_id.split("-")[0].lower()
        base_name_map = {
            "iss": "ISS Overpass",
            "planet": "Jupiter Brightness",
            "meteor": "Meteor Shower",
            "eclipse": "Lunar Alignment"
        }
        temp_base = raw_type[:-1] if raw_type.endswith('s') and raw_type != 'iss' else raw_type
        display_name = base_name_map.get(temp_base, "Cosmic Event")

    base_type = raw_type[:-1] if raw_type.endswith('s') and raw_type != 'iss' else raw_type
    
    details = {
        "iss": {
            "image": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&q=80&w=2000",
            "spots": ["Satellite Viewpoint", "Outer Rim Observatory", "North Hill Clearing"],
            "tips": ["Look for a bright 'star' moving steadily without blinking.", "Use a sky tracking app to know exactly where it will emerge.", "No telescope needed - it's best seen with the naked eye!"]
        },
        "planet": {
            "image": "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?auto=format&fit=crop&q=80&w=2000",
            "spots": ["Planetary Vista", "Stargazer Flat", "Lake View Ridge"],
            "tips": ["Planets don't twinkle like stars - they shine with a steady light.", "Binoculars will reveal Jupiter's four largest moons.", "Look slightly to the side of the planet (averted vision) to see more detail."]
        },
        "meteor": {
            "image": "https://images.unsplash.com/photo-1543362906-acfc16c67562?auto=format&fit=crop&q=80&w=2000",
            "spots": ["Meteor Peak", "Comet Valley", "Dark Wood Plateau"],
            "tips": ["Lie flat on your back and look straight up to see the most sky.", "Give your eyes at least 20 minutes to adjust to the total darkness.", "Avoid looking at your phone - the blue light will ruin your night vision."]
        },
        "eclipse": {
            "image": "https://images.unsplash.com/photo-1504333638930-c873ef699851?auto=format&fit=crop&q=80&w=2000",
            "spots": ["Shadow Ridge", "Lunar Hollow", "Ancient Stone Lookout"],
            "tips": ["Lunar eclipses are perfectly safe to view with the naked eye.", "Watch for the 'Blood Moon' effect as the moon turns deep red.", "Try long-exposure photography to capture the subtle color shifts."]
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

        return jsonify({
            "id": event_id,
            "name": display_name,
            "description": f"This event is currently in peak visibility from your location. For the best experience, we recommend moving away from city lights to one of the dark spots suggested below.",
            "visibility": "High",
            "image": details[base_type]["image"],
            "dark_spots": dynamic_spots,
            "tips": details[base_type]["tips"],
            "weather": {"condition": "Optimal Viewing"}
        })

    return {"error": "Event not found"}, 404

    # 2. Handle database IDs (marked with db-)
    if event_id.startswith("db-"):
        actual_id = int(event_id.replace("db-", ""))
        db = SessionLocal()
        event = db.query(Event).filter(Event.id == actual_id).first()
        db.close()
        
        if event:
            return jsonify({
                "id": event_id,
                "name": event.event_type,
                "description": event.description,
                "visibility": "High",
                "image": "https://images-assets.nasa.gov/image/PIA12348/PIA12348~medium.jpg",
                "dark_spots": [{"name": "Local Park", "level": "Average"}],
                "weather": {"condition": "Clear"}
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
            visibility="High"
        ),
        Event(
            type="planet",
            event_type="Jupiter Moon Transit",
            description="Io and Europa will be visible crossing Jupiter's disk.",
            location="Hyderabad, India",
            visibility="Very High"
        ),
        Event(
            type="meteor",
            event_type="Orionids Shower",
            description="Best viewed from the high altitude parks.",
            location="Bangalore, India",
            visibility="Medium"
        ),
        Event(
            type="eclipse",
            event_type="Partial Moon Shadow",
            description="Subtle shading on the northern lunar limb.",
            location="New Delhi, India",
            visibility="Low"
        ),
        Event(
            type="iss",
            event_type="ISS Transcontinental",
            description="Visible for 6 minutes straight.",
            location="Global",
            visibility="High"
        )
    ]

    for e in events:
        db.add(e)
    
    db.commit()
    db.close()

    return {"status": "Universal Database Ready. Events added for Kerala, Hyderabad, Bangalore, and Global."}

if __name__ == "__main__":
    app.run(debug=True)