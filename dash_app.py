import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import random
from datetime import datetime
from collections import deque
import time

# =================================================================================
# --- UI REDESIGN CONFIGURATION: BRIGHT, AIRY, AND VIBRANT ---
# =================================================================================

# Color Palette: Bright, Clean, and Professional
ACCENT_PRIMARY = "#3A86FF"  # Bright Sky Blue (Main action/level data)
ACCENT_SECONDARY = "#FF6B6B"  # Vibrant Coral (Anomaly/Warning)
TEXT_DARK = "#333A40"  # Near-black for high contrast text
TEXT_MUTED = "#95A5A6"  # Soft Gray for secondary text
BG_LIGHT = "#F4F7F9"  # Lightest Blue-Gray Background
CARD_BG = "#FFFFFF"  # Pure White for floating cards
SUCCESS_COLOR = "#2ECC71"  # Emerald Green (Positive trend)
DANGER_COLOR = ACCENT_SECONDARY  # Use Coral for danger
WARNING_COLOR = "#FDCB6E"  # Soft Yellow/Orange (Low Alert)

# Enhanced Modern Shadow Configuration for depth
SOFT_SHADOW_SM = "0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)"
SOFT_SHADOW_MD = "0 6px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04)"
SOFT_SHADOW_LG = "0 15px 30px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.04)"

GRID_STYLE = {
    "background": BG_LIGHT,
    "minHeight": "100vh",
    "padding": "20px",
    "color": TEXT_DARK,
    "fontFamily": "Inter, sans-serif"
}

MAX_HISTORY_POINTS = 20

# --- NEW METRIC WEIGHTS ---
WEIGHT_LEVEL_DISPARITY = 0.4
WEIGHT_RESILIENCE = 0.4
# -------------------------

# =================================================================================
# --- I18n TRANSLATION DICTIONARY AND FUNCTION ---
# =================================================================================

# Define the supported languages
LANGUAGES = {
    'en': 'English',
    'hi': 'हिन्दी',
    'ta': 'தமிழ்'
}

# The translation dictionary (English is the default/source)
TRANSLATIONS = {
    "Aqua-Sight | DWLR CONSOLE": {"hi": "एक्वा-साइट | DWLR कंसोल", "ta": "அக்வா-சைட் | DWLR கன்சோல்"},
    "Real-Time Subsurface Water Dynamics and Predictive Forecasting": {
        "hi": "वास्तविक समय उपसतह जल गतिशीलता और भविष्य कहनेवाला पूर्वानुमान",
        "ta": "நிகழ் நேர மேற்பரப்பு நீரின் இயக்கவியல் மற்றும் முன்னறிவிப்பு"
    },
    "Water Level": {"hi": "जल स्तर", "ta": "நீர் மட்டம்"},
    "Rainfall": {"hi": "वर्षा", "ta": "மழைப்பொழிவு"},
    "Temperature": {"hi": "तापमान", "ta": "வெப்பநிலை"},
    "Evapotranspiration": {"hi": "वाष्पोत्सर्जन", "ta": "நீராவிப்போக்கு"},
    "Trend Disparity Index (MTDI)": {"hi": "प्रवृत्ति असमानता सूचकांक (MTDI)", "ta": "போக்கு வேறுபாடு குறியீடு (MTDI)"},
    "Resilience Score (HCRS)": {"hi": "लचीलापन स्कोर (HCRS)", "ta": "நெகிழ்ச்சி மதிப்பெண் (HCRS)"},
    "Predicted Conflict Score": {"hi": "पूर्वानुमानित संघर्ष स्कोर", "ta": "முன்னறிவிக்கப்பட்ட மோதல் மதிப்பெண்"},
    "Sensor Trust Index (STI)": {"hi": "सेंसर विश्वास सूचकांक (STI)", "ta": "சென்சார் நம்பிக்கை குறியீடு (STI)"},
    "24hr Level Forecast": {"hi": "24 घंटे स्तर का पूर्वानुमान", "ta": "24 மணிநேர மட்ட முன்னறிவிப்பு"},
    "Drought Risk Probability": {"hi": "सूखा जोखिम की संभावना", "ta": "வறட்சி இடர் நிகழ்தகவு"},
    "30-Day Net Recharge": {"hi": "30-दिन शुद्ध पुनर्भरण", "ta": "30-நாள் நிகர ரீசார்ஜ்"},
    "Forecasting & Risk Assessment": {"hi": "पूर्वानुमान और जोखिम मूल्यांकन",
                                      "ta": "முன்னறிவிப்பு மற்றும் இடர் மதிப்பீடு"},
    "Primary Forecast Vector": {"hi": "प्राथमिक पूर्वानुमान वेक्टर", "ta": "முதன்மை முன்னறிவிப்பு திசையன்"},
    " 'What If' Simulation": {"hi": " 'क्या हो अगर' अनुकरण", "ta": " 'என்ன நடந்தால்' உருவகப்படுத்துதல்"},
    "Simulated 24hr Rainfall (mm):": {"hi": "सिम्युलेटेड 24hr वर्षा (मिमी):",
                                      "ta": "உருவகப்படுத்தப்பட்ட 24 மணிநேர மழை (மிமீ):"},
    "The 24hr forecast level instantly adapts to this input.": {
        "hi": "24 घंटे का पूर्वानुमान स्तर इस इनपुट के अनुसार तुरंत अनुकूलित होता है।",
        "ta": "24 மணிநேர முன்னறிவிப்பு நிலை இந்த உள்ளீட்டிற்கு உடனடியாக மாறுகிறது."
    },
    "Core Analytical Dashboard": {"hi": "मुख्य विश्लेषणात्मक डैशबोर्ड", "ta": "முக்கிய பகுப்பாய்வு டாஷ்போர்டு"},
    "Water Level Trajectory (Last 20 Readings)": {
        "hi": "जल स्तर प्रक्षेपवक्र (अंतिम 20 रीडिंग)",
        "ta": "நீர் மட்டப் பாதை (கடைசி 20 அளவீடுகள்)"
    },
    "Geospatial Network Monitor (Mainland Distribution)": {
        "hi": "भौगोलिक नेटवर्क मॉनिटर (मुख्य भूमि वितरण)",
        "ta": "புவிசார் பிணைய கண்காணிப்பு (நிலப்பரப்பு விநியோகம்)"
    },
    "System Integrity Report": {"hi": "सिस्टम अखंडता रिपोर्ट", "ta": "கணினி ஒருமைப்பாடு அறிக்கை"},
    "Data Feed Time:": {"hi": "डेटा फ़ीड समय:", "ta": "தரவு ஊட்ட நேரம்:"},
    "Station:": {"hi": "स्टेशन:", "ta": "நிலையம்:"},
    "Type/Elevation:": {"hi": "प्रकार/ऊंचाई:", "ta": "வகை/உயரம்:"},
    "Anomaly Check:": {"hi": "विसंगति जांच:", "ta": "அசாதாரண சோதனை:"},
    "Simulated Extraction Rate:": {"hi": "सिम्युलेटेड निष्कर्षण दर:",
                                   "ta": "உருவகப்படுத்தப்பட்ட பிரித்தெடுப்பு விகிதம்:"},
    "m": {"hi": "मी", "ta": "மீ"},
    "mm": {"hi": "मिमी", "ta": "மிமீ"},
    "°C": {"hi": "°C", "ta": "°C"},
    "Critical Disparity": {"hi": "महत्वपूर्ण असमानता", "ta": "முக்கிய வேறுபாடு"},
    "Watch Trend": {"hi": "प्रवृत्ति देखें", "ta": "போக்கைக் கண்காணிக்கவும்"},
    "Stable Trend": {"hi": "स्थिर प्रवृत्ति", "ta": "நிலையான போக்கு"},
    "High Risk": {"hi": "उच्च जोखिम", "ta": "அதிக ஆபத்து"},
    "Moderate Risk": {"hi": "मध्यम जोखिम", "ta": "மிதமான ஆபத்து"},
    "Low Risk": {"hi": "कम जोखिम", "ta": "குறைந்த ஆபத்து"},
    "High Conflict Risk": {"hi": "उच्च संघर्ष जोखिम", "ta": "அதிக மோதல் ஆபத்து"},
    "Moderate Tension": {"hi": "मध्यम तनाव", "ta": "மிதமான பதற்றம்"},
    "Low Tension": {"hi": "कम तनाव", "ta": "குறைந்த பதற்றம்"},
    "Integrity Compromised": {"hi": "अखंडता से समझौता", "ta": "ஒருமைப்பாடு சமரசம்"},
    "Review Data Source": {"hi": "डेटा स्रोत की समीक्षा करें", "ta": "தரவு மூலத்தை மதிப்பாய்வு செய்யவும்"},
    "Data Trusted": {"hi": "डेटा विश्वसनीय", "ta": "தரவு நம்பகமானது"},
    "m/day": {"hi": "मी³/दिन", "ta": "மீ³/நாள்"},
    "m (24hr)": {"hi": "मी (24घं)", "ta": "மீ (24ம)"},
    "CRITICAL ALERT: Anomaly Detected. Immediate action required for ": {
        "hi": "महत्वपूर्ण चेतावनी: विसंगति का पता चला। के लिए तत्काल कार्रवाई आवश्यक है ",
        "ta": " முக்கியமான எச்சரிக்கை: அசாதாரணத்தைக் கண்டறிந்தது. இதற்கு உடனடியாக நடவடிக்கை தேவை "
    },
    " System Operational: Data feed active and stable for ": {
        "hi": " सिस्टम चालू: डेटा फ़ीड सक्रिय और स्थिर है ",
        "ta": " கணினி செயல்பாட்டில் உள்ளது: தரவு ஊட்டம் செயல்பட்டு நிலையானது "
    },
    "Last updated: ": {"hi": "अंतिम बार अपडेट किया गया: ", "ta": "கடைசியாக புதுப்பிக்கப்பட்டது: "},
    "Login": {"hi": "लॉग इन करें", "ta": "உள்நுழை"},
    "Logout": {"hi": "लॉग आउट करें", "ta": "வெளியேறு"},
    "Username": {"hi": "उपयोगकर्ता नाम", "ta": "பயனர்பெயர்"},
    "Password": {"hi": "पासवर्ड", "ta": "கடவுச்சொல்"},
    "Acknowledge": {"hi": "स्वीकार करें", "ta": "அங்கீகரிக்கவும்"},
    "Resolve": {"hi": "हल करें", "ta": "தீர்க்கவும்"},
    "Clear Filter": {"hi": "फ़िल्टर साफ़ करें", "ta": "வடிப்பானை அகற்று"},
    "Comparative Analytics": {"hi": "तुलनात्मक विश्लेषण", "ta": "ஒப்பீட்டு பகுப்பாய்வு"},
    "Alert Log": {"hi": "चेतावनी लॉग", "ta": "எச்சரிக்கை பதிவு"},
    "Core Dashboard": {"hi": "मुख्य डैशबोर्ड", "ta": "முக்கிய டாஷ்போர்டு"},
    "State Median Water Level Comparison": {"hi": "राज्य माध्य जल स्तर तुलना", "ta": "மாநில சராசரி நீர் மட்ட ஒப்பீடு"},
    "Peer Group Benchmarking (P-Conflict Score)": {"hi": "समूह बेंचमार्किंग (P-Conflict स्कोर)",
                                                   "ta": "சக குழு அளவுகோல் (P-Conflict மதிப்பெண்)"},
    "P-Conflict Distribution for Peer Group": {"hi": "सहकर्मी समूह के लिए P-Conflict वितरण",
                                               "ta": "சக குழுவிற்கான P-Conflict விநியோகம்"}
}


def get_text(key, lang_code):
    """Retrieves the translated text for a key, falling back to English."""
    if lang_code == 'en':
        return key
    return TRANSLATIONS.get(key, {}).get(lang_code, key)


# =================================================================================
# --- DWLR SENSORS DATA (Distributed based on Foreign Border Criteria & Mainland Only) ---
# (Data generation and setup remains the same, but now ALL_RAW_STATIONS is stored for global use)
# =================================================================================

# Status simulation options (weighted towards NORMAL)
STATUS_OPTIONS = ['NORMAL', 'NORMAL', 'NORMAL', 'NORMAL', 'LOW_ALERT', 'ANOMALY']

# --- Geospatial Data: Bounding Boxes for Indian States/UTs (Excluding Islands) ---
INDIAN_REGIONS = {
    "Haryana": (27.5, 30.7, 74.5, 77.7), "Madhya Pradesh": (21.0, 26.9, 74.0, 82.8),
    "Chhattisgarh": (17.5, 23.5, 80.0, 84.0), "Jharkhand": (22.0, 25.5, 83.5, 88.0),
    "Telangana": (15.7, 19.5, 77.0, 81.8), "Jammu and Kashmir (UT)": (32.5, 36.0, 73.5, 76.5),
    "Ladakh (UT)": (32.0, 36.5, 75.0, 80.0), "Himachal Pradesh": (30.0, 33.5, 75.5, 79.0),
    "Punjab": (29.5, 32.5, 73.5, 77.5), "Uttarakhand": (29.0, 31.5, 77.5, 81.0),
    "Delhi (NCT)": (28.3, 28.8, 76.8, 77.3), "Uttar Pradesh": (23.5, 31.0, 77.0, 84.8),
    "Chandigarh (UT)": (30.7, 30.8, 76.7, 76.8), "Rajasthan": (23.0, 30.0, 69.5, 78.5),
    "Gujarat": (20.0, 24.5, 68.0, 74.5), "Maharashtra": (15.5, 22.0, 72.5, 80.8),
    "Goa": (14.9, 15.9, 73.7, 74.5), "Daman, Diu, Dadra & Nagar Haveli (UT)": (20.0, 20.7, 72.8, 73.5),
    "Bihar": (24.0, 27.5, 83.5, 88.5), "West Bengal": (21.5, 27.5, 86.0, 89.5),
    "Odisha": (17.5, 22.5, 81.5, 87.5), "Andhra Pradesh": (12.5, 19.5, 77.0, 84.5),
    "Karnataka": (11.5, 18.5, 74.0, 78.5), "Kerala": (8.0, 12.8, 74.8, 77.5),
    "Tamil Nadu": (8.0, 13.5, 76.5, 80.5), "Puducherry (UT)": (11.8, 12.0, 79.8, 80.0),
    "Sikkim": (27.0, 28.0, 88.0, 88.8), "Arunachal Pradesh": (26.5, 29.5, 91.5, 97.0),
    "Assam": (24.5, 27.8, 89.8, 96.0), "Meghalaya": (25.0, 26.0, 90.0, 92.5),
    "Nagaland": (25.0, 27.0, 93.5, 95.5), "Manipur": (23.8, 25.7, 93.0, 95.0),
    "Mizoram": (21.5, 24.5, 92.2, 93.5), "Tripura": (22.5, 24.5, 91.0, 92.5),
}
MOCK_STATES = list(INDIAN_REGIONS.keys())
LANDLOCKED_STATES = ["Haryana", "Madhya Pradesh", "Chhattisgarh", "Jharkhand", "Telangana"]
COASTAL_BORDER_REGIONS = [state for state in MOCK_STATES if state not in LANDLOCKED_STATES]

RAW_STATION_DATA = [
    {"Agency_Name": "Andhra Pradesh GW", "State_Name": "Andhra Pradesh", "District_Name": "KURNOOL",
     "Tahsil_Name": "KURNOOL", "Station_Name": "KURNOOL -AWS", "Latitude": 15.75064, "Longitude": 78.0668,
     "Station_Type": "SURFACE", "Station_Status": "INSTALLED"},
    {"Agency_Name": "Tamil Nadu GW", "State_Name": "Tamil Nadu", "District_Name": "CHENNAI",
     "Tahsil_Name": "CHENNAI", "Station_Name": "CHENNAI -CITY", "Latitude": 13.0827, "Longitude": 80.2707,
     "Station_Type": "GROUND", "Station_Status": "INSTALLED"},
    {"Agency_Name": "Maharashtra GW", "State_Name": "Maharashtra", "District_Name": "PUNE",
     "Tahsil_Name": "PUNE", "Station_Name": "PUNE -WEST", "Latitude": 18.5204, "Longitude": 73.8567,
     "Station_Type": "GROUND", "Station_Status": "INSTALLED"},
]
NUM_REAL_STATIONS = len(RAW_STATION_DATA)
TOTAL_TARGET_DOTS = 1000
TARGET_LANDLOCKED = 100
TARGET_COASTAL_BORDER = 20
TOTAL_MOCK_DOTS = TARGET_LANDLOCKED + TARGET_COASTAL_BORDER
TOTAL_DOTS = NUM_REAL_STATIONS + TOTAL_MOCK_DOTS
NUM_RANDOM_STATIONS = TOTAL_DOTS - NUM_REAL_STATIONS

ALLOCATION = {}
points_per_landlocked = TARGET_LANDLOCKED // len(LANDLOCKED_STATES)
for state in LANDLOCKED_STATES:
    ALLOCATION[state] = points_per_landlocked
points_per_coastal_border_base = TARGET_COASTAL_BORDER // len(COASTAL_BORDER_REGIONS)
coastal_border_remainder = TARGET_COASTAL_BORDER % len(COASTAL_BORDER_REGIONS)
for idx, state in enumerate(COASTAL_BORDER_REGIONS):
    ALLOCATION[state] = points_per_coastal_border_base + (1 if idx < coastal_border_remainder else 0)


def generate_random_station(i, state_name):
    region_key = state_name if state_name in INDIAN_REGIONS else random.choice(MOCK_STATES)
    lat_min, lat_max, lon_min, lon_max = INDIAN_REGIONS[region_key]
    lat = round(random.uniform(lat_min, lat_max), 5)
    lon = round(random.uniform(lon_min, lon_max), 5)
    station_name = f"MOCK-{state_name.split()[0].upper()}-{i}"
    return {
        "Agency_Name": "Mock Network", "State_Name": region_key,
        "District_Name": f"Mock District {i % 10}",
        "Tahsil_Name": "Mock Tahsil", "Station_Name": station_name,
        "Latitude": lat, "Longitude": lon,
        "Station_Type": random.choice(["GROUND", "SURFACE"]),
        "Station_Status": "INSTALLED"
    }


RANDOM_STATIONS = []
station_counter = 0
for state, num_points in ALLOCATION.items():
    for i in range(num_points):
        RANDOM_STATIONS.append(generate_random_station(station_counter, state))
        station_counter += 1

ALL_RAW_STATIONS = RAW_STATION_DATA + RANDOM_STATIONS  # Global for map/comparative data

MOCK_DWLR_SENSORS = []
STATION_IDS = []

for i, item in enumerate(ALL_RAW_STATIONS):
    station_id = f"{item['Station_Name'].replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '').upper()}_{i}"
    state_name = item['State_Name'].replace(' (UT)', '').replace(' (NCT)', '')
    simulated_status = random.choice(STATUS_OPTIONS) if 'MOCK-' in item['Station_Name'] else STATUS_OPTIONS[
        i % len(STATUS_OPTIONS)]
    simulated_level = round(100.0 + random.uniform(-5.0, 5.0), 2)

    MOCK_DWLR_SENSORS.append({
        'id': station_id, 'lat': item['Latitude'], 'lon': item['Longitude'],
        'status': simulated_status, 'level': simulated_level, 'type': item['Station_Type'],
        'Station_Name_Full': item['Station_Name'], 'District': item['District_Name'],
        'Tahsil': item['Tahsil_Name'], 'State': item['State_Name'],
        'PConflict_Initial': 0.0  # Placeholder for initial calculation
    })
    STATION_IDS.append(station_id)

DROPDOWN_SAMPLE_SIZE = min(100, len(MOCK_DWLR_SENSORS))
SAMPLED_STATIONS = MOCK_DWLR_SENSORS[:DROPDOWN_SAMPLE_SIZE]

DROPDOWN_OPTIONS = [
    {
        'label': f"{s['Station_Name_Full']} ({s['State']})",
        'value': s['id']
    }
    for s in SAMPLED_STATIONS
]

# --- Global Alert Log (Deque for fixed size) ---
MAX_ALERTS = 50
ALERT_LOG = deque(maxlen=MAX_ALERTS)
ALERT_ID_COUNTER = 0

# =================================================================================
# --- AUTHENTICATION CONFIGURATION ---
# =================================================================================
MOCK_USERNAME = "admin"
MOCK_PASSWORD = "password"


# =================================================================================
# --- DATA FETCHING AND PROCESSING ---
# =================================================================================

def get_station_by_id(station_id):
    """Retrieves the full sensor data for the selected ID."""
    for sensor in MOCK_DWLR_SENSORS:
        if sensor['id'] == station_id:
            return sensor
    return MOCK_DWLR_SENSORS[0] if MOCK_DWLR_SENSORS else None


def generate_live_data(last_level, selected_station_id, override_rainfall_str):
    """MOCK data generation, calculates MTDI, HCRS, PConflict, STI."""
    selected_station = get_station_by_id(selected_station_id)
    if not selected_station:
        selected_station = MOCK_DWLR_SENSORS[0]

    last_level = selected_station.get('level', 100.0)
    water_level = round(last_level + random.uniform(-0.1, 0.1), 2)
    water_level = max(95.0, min(105.0, water_level))

    # --- Rainfall Override and Level Change ---
    rainfall_factor = 0.0
    try:
        override_rainfall = float(override_rainfall_str) if override_rainfall_str is not None else 0.0
        rainfall_factor = override_rainfall * 0.05
    except (ValueError, TypeError):
        override_rainfall = 0.0
        pass

    level_change_base = random.uniform(-0.5, 0.75)
    next_day_level = round(water_level + level_change_base + rainfall_factor, 2)
    next_day_level = max(95.0, min(105.0, next_day_level))

    rainfall = round(random.uniform(0, 5) + override_rainfall, 2)
    avg_temp = round(random.uniform(20, 35), 1)
    pet = round(random.uniform(3, 7), 2)

    # --- Metrics Calculation ---
    mtdi = round(abs(water_level - 100) * 0.1 + random.uniform(0.05, 0.2), 4)
    hcrs = round((105.0 - water_level) / 0.1, 0)
    hcrs = max(0, min(100, hcrs))
    risk_proba = random.uniform(0.1, 0.75)
    is_anomaly = "FALSE"
    anomaly_score = round(random.uniform(0.01, 0.1), 4)

    if water_level < 97.0 or selected_station['status'] == 'ANOMALY':
        risk_proba = random.uniform(0.75, 0.95)
        is_anomaly = "TRUE"
        anomaly_score = round(random.uniform(0.5, 0.9), 4)

    # P-Conflict Score Calculation
    lat, lon = selected_station['lat'], selected_station['lon']
    density_base = 0.05
    if lat < 20 and lon > 78: density_base = 0.3
    pop_density_factor = density_base + random.uniform(0.0, 0.1)

    p_conflict_score = (mtdi * WEIGHT_LEVEL_DISPARITY) + \
                       ((100 - hcrs) / 100 * WEIGHT_RESILIENCE) + \
                       pop_density_factor
    p_conflict_score = round(min(1.0, p_conflict_score), 4)

    # STI Calculation
    data_gap_factor = random.uniform(0.0, 0.1)
    sti = round(100.0 - (anomaly_score * 500) - (data_gap_factor * 10), 0)
    sti = max(0, min(100, sti))

    # Update the level and PConflict in the MOCK_DWLR_SENSORS list for consistency
    selected_station['level'] = water_level
    selected_station['PConflict_Initial'] = p_conflict_score

    # Global update of MOCK_DWLR_SENSORS data for the comparative analytics
    for sensor in MOCK_DWLR_SENSORS:
        if sensor['id'] == selected_station_id:
            # We already updated the selected one, so skip it
            continue

        # Simulate a slight variation in all other stations for the comparative view
        sensor['level'] = max(95.0, min(105.0, sensor['level'] + random.uniform(-0.01, 0.01)))

        # Recalculate PConflict for all for comparative view
        simulated_mtdi = round(abs(sensor['level'] - 100) * 0.1 + random.uniform(0.05, 0.2), 4)
        simulated_hcrs = max(0, min(100, round((105.0 - sensor['level']) / 0.1, 0)))

        # Keep density factor roughly constant for non-selected stations
        sim_lat, sim_lon = sensor['lat'], sensor['lon']
        sim_density_base = 0.05
        if sim_lat < 20 and sim_lon > 78: sim_density_base = 0.3

        sim_p_conflict_score = (simulated_mtdi * WEIGHT_LEVEL_DISPARITY) + \
                               ((100 - simulated_hcrs) / 100 * WEIGHT_RESILIENCE) + \
                               sim_density_base + random.uniform(-0.01, -0.01)  # Small random noise
        sensor['PConflict_Initial'] = round(min(1.0, sim_p_conflict_score), 4)
    # --- END Global update ---

    return {
        "Real_Time_Input": {
            "water_level": water_level, "rainfall_mm": rainfall, "avg_temp_c": avg_temp,
            "pet_mm": pet, "station_type": selected_station['type'],
            "district": selected_station['District'], "elevation": 150 + random.randint(-10, 10),
            "lat": selected_station['lat'], "lon": selected_station['lon']
        },
        "Water_Level_Prediction": {"Next_Day_Level": next_day_level},
        "Drought_Risk_Index": {"Probability_Critical_Drop": risk_proba},
        "Estimated_Recharge": {"30_Day_Net_Change": round(random.uniform(-3.0, 3.0), 2)},
        "Simulated_Extraction": {"Rate": round(random.uniform(5.0, 15.0), 2)},
        "Anomaly_Check": {"Is_Anomaly": is_anomaly, "Score": anomaly_score},
        "MTDI": mtdi,
        "HCRS": hcrs,
        "PConflict": p_conflict_score,
        "STI": sti
    }


# --- Alert Generation Logic ---
def check_for_alerts(station_id, station_name, results):
    """Checks for conditions that warrant an alert and adds them to the log."""
    global ALERT_ID_COUNTER

    alerts_triggered = []
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 1. Anomaly Alert
    if results['Anomaly_Check']['Is_Anomaly'] == 'TRUE' and results['Anomaly_Check']['Score'] > 0.7:
        ALERT_ID_COUNTER += 1
        alerts_triggered.append({
            'id': ALERT_ID_COUNTER,
            'timestamp': current_time,
            'station_id': station_id,
            'station_name': station_name,
            'priority': 'CRITICAL',
            'type': 'SENSOR_ANOMALY',
            'message': f"High Anomaly Score detected: {results['Anomaly_Check']['Score']:.4f}. Water Level: {results['Real_Time_Input']['water_level']:.2f}m.",
            'status': 'NEW'
        })

    # 2. P-Conflict Alert (High tension)
    if results['PConflict'] > 0.8:
        ALERT_ID_COUNTER += 1
        alerts_triggered.append({
            'id': ALERT_ID_COUNTER,
            'timestamp': current_time,
            'station_id': station_id,
            'station_name': station_name,
            'priority': 'HIGH',
            'type': 'P_CONFLICT_SPIKE',
            'message': f"Predicted Conflict Score is high at {results['PConflict']:.4f}.",
            'status': 'NEW'
        })

    # 3. Low Resilience Alert
    if results['HCRS'] < 40:
        ALERT_ID_COUNTER += 1
        alerts_triggered.append({
            'id': ALERT_ID_COUNTER,
            'timestamp': current_time,
            'station_id': station_id,
            'station_name': station_name,
            'priority': 'MEDIUM',
            'type': 'LOW_RESILIENCE',
            'message': f"HCRS score dropped to {results['HCRS']:.0f}. Near Critical Drop.",
            'status': 'NEW'
        })

    # Add new alerts to the global deque
    for alert in alerts_triggered:
        ALERT_LOG.appendleft(alert)

    # Return the log as a list for dcc.Store
    return list(ALERT_LOG)


# =================================================================================
# --- DASHBOARD COMPONENTS (REDESIGNED) ---
# =================================================================================

def get_color_and_icon(delta_value, base_color_name, custom_metric=None):
    """Maps color name to hex value and determines the icon."""
    color_map = {'success': SUCCESS_COLOR, 'danger': DANGER_COLOR, 'warning': WARNING_COLOR, 'primary': ACCENT_PRIMARY}

    if custom_metric == 'MTDI':
        color = DANGER_COLOR if delta_value > 0.5 else (WARNING_COLOR if delta_value > 0.3 else SUCCESS_COLOR)
        return color, '⚡'
    elif custom_metric == 'HCRS':
        color = DANGER_COLOR if delta_value < 50 else (WARNING_COLOR if delta_value < 75 else SUCCESS_COLOR)
        return color, '💡'
    elif custom_metric == 'PConflict':
        color = DANGER_COLOR if delta_value > 0.6 else (WARNING_COLOR if delta_value > 0.3 else SUCCESS_COLOR)
        return color, '🔥'
    elif custom_metric == 'STI':
        color = DANGER_COLOR if delta_value < 80 else (WARNING_COLOR if delta_value < 90 else SUCCESS_COLOR)
        return color, '🛡️'

    if delta_value is None:
        return color_map.get(base_color_name, TEXT_MUTED), '—'

    color = color_map.get(base_color_name, TEXT_MUTED)
    icon = '▲' if delta_value > 0 else ('▼' if delta_value < 0 else '—')
    return color, icon


def create_metric_card(title, value, unit="", delta_value=None, delta_color_name="primary", icon_emoji="📊",
                       custom_metric=None, lang_code='en'):
    delta_hex_color, icon = get_color_and_icon(delta_value, delta_color_name, custom_metric)
    display_value = f"{value}"
    delta_text = html.Div()

    # Translate the title and unit
    title_translated = get_text(title, lang_code)
    unit_translated = get_text(unit, lang_code)

    if delta_value is not None:
        delta_sign = '+' if delta_value > 0 else ''

        if custom_metric == 'STI':
            status_text = get_text("Integrity Compromised", lang_code) if delta_value < 80 else (
                get_text("Review Data Source", lang_code) if delta_value < 90 else get_text("Data Trusted", lang_code))
        elif custom_metric == 'PConflict':
            status_text = get_text("High Conflict Risk", lang_code) if delta_value > 0.6 else (
                get_text("Moderate Tension", lang_code) if delta_value > 0.3 else get_text("Low Tension", lang_code))
        elif custom_metric == 'MTDI':
            status_text = get_text("Critical Disparity", lang_code) if delta_value > 0.5 else (
                get_text("Watch Trend", lang_code) if delta_value > 0.3 else get_text("Stable Trend", lang_code))
        elif custom_metric == 'HCRS':
            status_text = get_text("High Risk", lang_code) if delta_value < 50 else (
                get_text("Moderate Risk", lang_code) if delta_value < 75 else get_text("Low Risk", lang_code))
        else:
            # Standard delta display
            delta_unit = get_text("m (24hr)", lang_code) if unit == 'm' else unit_translated
            delta_text = html.Span(
                [
                    html.Span(icon, className="me-1"),
                    f"{delta_sign}{delta_value:.2f} {delta_unit}"
                ],
                style={'color': delta_hex_color, 'fontSize': '0.9rem', 'fontWeight': '600'}
            )
            status_text = None

        if status_text:
            delta_text = html.Span(
                [
                    html.Span(icon, className="me-1"),
                    status_text
                ],
                style={'color': delta_hex_color, 'fontSize': '0.9rem', 'fontWeight': '600'}
            )

    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div([
                        html.Span(icon_emoji, style={'fontSize': '1.5rem', 'color': delta_hex_color}),
                        html.P(title_translated, className="mb-0 ms-2",
                               style={"fontSize": "1.0rem", "color": TEXT_MUTED, "fontWeight": 500}),
                    ], className="d-flex align-items-center mb-2"),

                    html.Div([
                        html.Span(
                            display_value,
                            style={"color": TEXT_DARK, "fontWeight": "900", "fontSize": "2.5rem"}
                        ),
                        html.Span(
                            f" {unit_translated}",
                            style={"color": TEXT_MUTED, "fontWeight": "500", "fontSize": "1.1rem", "marginLeft": "5px"}
                        )
                    ], className="d-flex align-items-baseline mb-2"),

                    delta_text,
                ],
                style={"padding": "20px"}
            )
        ],
        className="border-0 hover-lift",
        style={
            "borderRadius": "18px",
            "backgroundColor": CARD_BG,
            "boxShadow": SOFT_SHADOW_MD,
            "transition": "all 0.3s ease",
            "borderLeft": f"5px solid {delta_hex_color}"
        },
    )


# --- Login Modal ---
login_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Login")),
        dbc.ModalBody(
            [
                dbc.Input(id="login-username", placeholder="Username", type="text", className="mb-3"),
                dbc.Input(id="login-password", placeholder="Password", type="password", className="mb-3"),
                html.Div(id="login-status-message", style={"color": DANGER_COLOR, "fontWeight": 600}),
            ]
        ),
        dbc.ModalFooter(
            dbc.Button("Submit", id="login-submit", className="ms-auto", n_clicks=0, color="primary")
        ),
    ],
    id="login-modal",
    is_open=False,
)

# =================================================================================
# --- APPLICATION LAYOUT (REDESIGNED) ---
# =================================================================================

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
server = app.server

custom_css = f"""
.hover-lift:hover {{
    transform: translateY(-5px);
    box-shadow: {SOFT_SHADOW_LG};
}}
.card-title-redesign {{
    font-size: 1.5rem;
    font-weight: 700;
    color: {ACCENT_PRIMARY};
    margin-bottom: 1.5rem;
    border-bottom: 2px solid {BG_LIGHT};
    padding-bottom: 10px;
}}
.dash-dropdown .Select-control {{
    border-radius: 8px !important;
    border-color: {BG_LIGHT} !important;
    box-shadow: {SOFT_SHADOW_SM};
    height: 50px !important;
}}
.dash-dropdown .Select-value-label {{
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.input-redesign {{
    border-radius: 8px !important;
    border: 1px solid {BG_LIGHT} !important;
    padding: 10px !important;
    font-size: 1.1rem !important;
    box-shadow: {SOFT_SHADOW_SM};
}}
.input-redesign:focus {{
    border-color: {ACCENT_PRIMARY} !important;
    box-shadow: 0 0 0 0.25rem {ACCENT_PRIMARY}30 !important;
}}
.header-titles h1 {{
    white-space: normal;
    word-break: break-word;
    line-height: 1.2;
    color: {TEXT_DARK} !important;
}}
.custom-tab-style {{
    font-size: 1.1rem;
    font-weight: 600;
    color: {TEXT_MUTED};
    border-radius: 8px 8px 0 0 !important;
}}
.custom-tab-selected-style {{
    color: {ACCENT_PRIMARY} !important;
    background-color: {CARD_BG} !important;
    border-color: {ACCENT_PRIMARY} !important;
    border-bottom: none !important;
}}
@keyframes flash {{
  0% {{ opacity: 1; }}
  50% {{ opacity: 0.3; }}
  100% {{ opacity: 1; }}
}}
.bell-notification {{
    animation: flash 1s infinite;
}}
"""

# FIX: Corrected the app.index_string to use string concatenation
# for custom_css injection, thus preserving the required Dash {%...%} placeholders.
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
        """ + custom_css + """
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

# Layout structure for the Comparative Analytics Tab
comparative_analytics_layout = html.Div([
    html.H4(get_text("State Median Water Level Comparison", 'en'), className="card-title-redesign",
            id="title-state-comparison"),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dcc.Loading(
                        dcc.Graph(id='state-median-chart', config={'displayModeBar': False}, style={'height': '450px'}))
                ]),
                className="border-0 hover-lift mb-5",
                style={"backgroundColor": CARD_BG, "borderRadius": "18px", "boxShadow": SOFT_SHADOW_MD}
            ),
            width=12
        )
    ]),
    html.H4(get_text("Peer Group Benchmarking (P-Conflict Score)", 'en'), className="card-title-redesign",
            id="title-peer-benchmarking"),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dcc.Loading(dcc.Graph(id='pconflict-benchmark-chart', config={'displayModeBar': False},
                                          style={'height': '450px'}))
                ]),
                className="border-0 hover-lift mb-5",
                style={"backgroundColor": CARD_BG, "borderRadius": "18px", "boxShadow": SOFT_SHADOW_MD}
            ),
            width=12
        )
    ])
])

# Layout structure for the Alert Log Tab
alert_log_layout = html.Div([
    html.H4(get_text("Alert Log", 'en'), className="card-title-redesign", id="title-alert-log"),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(html.P("Filter Status:"), width=2),
                        dbc.Col(dcc.Dropdown(
                            id='alert-status-filter',
                            options=[
                                {'label': 'NEW', 'value': 'NEW'},
                                {'label': 'ACKNOWLEDGED', 'value': 'ACKNOWLEDGED'},
                                {'label': 'RESOLVED', 'value': 'RESOLVED'},
                                {'label': 'ALL', 'value': 'ALL'},
                            ],
                            value='NEW',
                            clearable=False,
                            className="dash-dropdown"
                        ), width=4),
                        dbc.Col(
                            html.Div([
                                dbc.Button(get_text("Acknowledge", 'en'), id='acknowledge-button', color="warning",
                                           className="me-2", disabled=True),
                                dbc.Button(get_text("Resolve", 'en'), id='resolve-button', color="success",
                                           disabled=True),
                            ], id='alert-action-buttons', className="d-flex justify-content-end"),
                            width=6
                        )
                    ], className="mb-3 align-items-center"),
                    dash_table.DataTable(
                        id='alert-log-table',
                        columns=[
                            {"name": "ID", "id": "id", "type": "numeric"},
                            {"name": "Timestamp", "id": "timestamp"},
                            {"name": "Station", "id": "station_name"},
                            {"name": "Priority", "id": "priority"},
                            {"name": "Type", "id": "type"},
                            {"name": "Message", "id": "message"},
                            {"name": "Status", "id": "status", "presentation": "dropdown"},
                        ],
                        style_header={'backgroundColor': BG_LIGHT, 'fontWeight': 'bold'},
                        style_data_conditional=[
                            {'if': {'filter_query': '{priority} = "CRITICAL"', 'column_id': 'priority'},
                             'backgroundColor': DANGER_COLOR, 'color': CARD_BG},
                            {'if': {'filter_query': '{priority} = "HIGH"', 'column_id': 'priority'},
                             'backgroundColor': WARNING_COLOR, 'color': TEXT_DARK},
                            {'if': {'filter_query': '{status} = "RESOLVED"', 'column_id': 'status'},
                             'color': SUCCESS_COLOR, 'textDecoration': 'line-through'},
                        ],
                        page_action='native',
                        page_current=0,
                        page_size=10,
                        sort_action='native',
                        filter_action='native',
                        row_selectable='multi',
                    )
                ]),
                className="border-0 hover-lift mb-5",
                style={"backgroundColor": CARD_BG, "borderRadius": "18px", "boxShadow": SOFT_SHADOW_MD}
            ),
            width=12
        )
    ])
])

app.layout = html.Div(style=GRID_STYLE, children=[
    # --- Hidden Stores ---
    dcc.Interval(id='interval-component', interval=1 * 1000, n_intervals=0),
    dcc.Store(id='water-level-history', data={'time': [], 'current_level': [], 'predicted_level': []}),
    dcc.Store(id='auth-status-store', data={'logged_in': False, 'username': None}),
    dcc.Store(id='alert-log-store', data=list(ALERT_LOG)),
    dcc.Store(id='selected-state-ut-store', data=None),  # For Map Drill-down
    dcc.Store(id='language-store', data='en'),  # Default Language
    login_modal,

    dbc.Container([
        # --- HEADER ROW (Title, Selector, Language, Auth) ---
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        dbc.Row(
                            [
                                # Col 1: Title and Subtitle
                                dbc.Col(
                                    html.Div([
                                        html.H1(
                                            get_text("Aqua-Sight | DWLR CONSOLE", 'en'),
                                            className="mb-1",
                                            id="main-title",
                                            style={"color": ACCENT_PRIMARY, "fontWeight": "900", "letterSpacing": "1px",
                                                   "fontSize": "2.8rem"}
                                        ),
                                        html.P(
                                            get_text("Real-Time Subsurface Water Dynamics and Predictive Forecasting",
                                                     'en'),
                                            id="subtitle",
                                            style={"fontSize": "1.2rem", "color": TEXT_MUTED}
                                        )
                                    ], className="header-titles"),
                                    align="center",
                                    width={"size": 12, "lg": 5}
                                ),

                                # Col 2: Controls (Station, Language, Auth, Alerts)
                                dbc.Col(
                                    dbc.Row([
                                        # Station Selector
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id='station-selector',
                                                options=DROPDOWN_OPTIONS,
                                                value=MOCK_DWLR_SENSORS[0]['id'],
                                                clearable=False,
                                                className="dash-dropdown",
                                            ),
                                            width={"size": 12, "md": 5},
                                            className="mb-3 mb-md-0"
                                        ),
                                        # Language Selector
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id='language-selector',
                                                options=[{'label': v, 'value': k} for k, v in LANGUAGES.items()],
                                                value='en',
                                                clearable=False,
                                                className="dash-dropdown",
                                            ),
                                            width={"size": 4, "md": 2},
                                            className="mb-3 mb-md-0"
                                        ),
                                        # Alert Icon and Auth Buttons
                                        dbc.Col(
                                            html.Div([
                                                # Alert Bell Icon
                                                dbc.Button(
                                                    [
                                                        html.I(className="bi bi-bell-fill me-1"),
                                                        dbc.Badge(0, id='alert-badge', color="danger", pill=True,
                                                                  className="p-1", style={"verticalAlign": "top"})
                                                    ],
                                                    id="alert-bell",
                                                    color="light",
                                                    className="me-3 position-relative",
                                                    style={'border': 'none', 'fontSize': '1.3rem'}
                                                ),
                                                # Login/Logout Button
                                                dbc.Button(
                                                    get_text("Login", 'en'),
                                                    id='auth-button',
                                                    color='primary',
                                                    n_clicks=0,
                                                    style={"fontWeight": 600}
                                                )
                                            ], className="d-flex align-items-center justify-content-end"),
                                            width={"size": 8, "md": 5}
                                        ),
                                    ], className="g-3 align-items-center"),
                                    className="d-flex align-items-center justify-content-md-end mt-3 mt-lg-0",
                                    align="center",
                                    width={"size": 12, "lg": 7}
                                )
                            ],
                            className="g-0 align-items-center"
                        )
                    ),
                    className="border-0 hover-lift",
                    style={"borderRadius": "20px", "boxShadow": SOFT_SHADOW_LG}
                ),
                width=12
            ),
            className="mb-4"
        ),

        # --- Tabs Container ---
        dbc.Tabs(
            id="main-tabs",
            active_tab="tab-core-dashboard",
            className="mb-4",
            children=[
                dbc.Tab(
                    label=get_text("Core Dashboard", 'en'),
                    tab_id="tab-core-dashboard",
                    id="tab-label-core-dashboard",
                    className="custom-tab-style",
                    active_tab_style=dict(borderBottom='none'),
                    active_label_style=dict(color=ACCENT_PRIMARY),
                    children=html.Div(id='core-dashboard-content', children=[
                        # Status and Real-Time Metrics Row
                        dbc.Row([
                            dbc.Col(
                                html.Div(id='status-message', className="p-3 mb-4",
                                         style={"borderRadius": "10px", "fontWeight": "700"}),
                                width=12
                            ),
                            dbc.Row(id='real-time-metrics-row', className="mb-5 g-4"),
                        ]),

                        # Primary Forecast and Simulation Section
                        html.H4(get_text("Forecasting & Risk Assessment", 'en'), className="card-title-redesign",
                                id="title-forecast-risk"),
                        dbc.Row([
                            # Left Column: Prediction Metrics
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody([
                                        html.H5(get_text("Primary Forecast Vector", 'en'), id="title-forecast-vector",
                                                style={'color': TEXT_DARK, 'fontWeight': 600}),
                                        dbc.Row(id='prediction-metrics-row', className="mt-3 g-3"),
                                    ]),
                                    className="border-0 hover-lift",
                                    style={"backgroundColor": CARD_BG, "borderRadius": "18px",
                                           "boxShadow": SOFT_SHADOW_MD}
                                ),
                                lg=8, className="mb-4 mb-lg-0"
                            ),
                            # Right Column: "What If" Simulation Control
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody([
                                        html.H5(get_text("🧪 'What If' Simulation", 'en'), id="title-what-if",
                                                className="card-title", style={'color': ACCENT_PRIMARY}),
                                        html.P(get_text("Simulated 24hr Rainfall (mm):", 'en'),
                                               id="label-rainfall-input", className="mb-2",
                                               style={'color': TEXT_DARK, 'fontWeight': 500}),
                                        dcc.Input(
                                            id='what-if-rainfall-input',
                                            type='number',
                                            value=0.0,
                                            placeholder="Enter rainfall in mm",
                                            min=0.0,
                                            className="input-redesign",
                                            style={'width': '100%'}
                                        ),
                                        html.Small(
                                            get_text("The 24hr forecast level instantly adapts to this input.", 'en'),
                                            id="note-rainfall-input",
                                            className="text-muted mt-2 d-block")
                                    ]),
                                    className="border-0 hover-lift",
                                    style={
                                        "backgroundColor": CARD_BG, "borderRadius": "18px",
                                        "border": f"3px solid {WARNING_COLOR}", "boxShadow": SOFT_SHADOW_MD
                                    }
                                ),
                                lg=4
                            )
                        ], className="mb-5 g-4"),

                        # Core Analytics: Chart and Complex Metrics
                        html.H4(get_text("Core Analytical Dashboard", 'en'), className="card-title-redesign",
                                id="title-core-analytics"),
                        dbc.Row([
                            # Live Chart
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody([
                                        html.H5(get_text("Water Level Trajectory (Last 20 Readings)", 'en'),
                                                id="title-level-trajectory",
                                                style={'color': TEXT_DARK, 'fontWeight': 600}),
                                        dcc.Graph(id='water-level-chart', config={'displayModeBar': False},
                                                  style={'height': '350px'})
                                    ]),
                                    className="border-0 hover-lift",
                                    style={"backgroundColor": CARD_BG, "borderRadius": "18px",
                                           "boxShadow": SOFT_SHADOW_MD}
                                ),
                                lg=8, className="mb-4 mb-lg-0"
                            ),
                            # Unique Metrics (MTDI, HCRS, P-Conflict, STI)
                            dbc.Col(
                                dbc.Row([
                                    dbc.Col(html.Div(id='hcrs-card'), md=6, className="mb-4"),
                                    dbc.Col(html.Div(id='mtdi-card'), md=6, className="mb-4"),
                                    dbc.Col(html.Div(id='pconflict-card'), md=6, className="mb-md-0"),
                                    dbc.Col(html.Div(id='sti-card'), md=6, className="mb-md-0"),
                                ], className="g-4"),
                                lg=4
                            )
                        ], className="mb-5 g-4"),

                        # Geospatial Monitoring Array (Map)
                        html.H4(get_text("Geospatial Network Monitor (Mainland Distribution)", 'en'),
                                className="card-title-redesign", id="title-map-monitor"),
                        dbc.Row([
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody([
                                        dbc.Row([
                                            dbc.Col(html.P(id='map-filter-info', className="mb-0",
                                                           style={'fontWeight': 600, 'color': ACCENT_PRIMARY}),
                                                    width=9),
                                            dbc.Col(dbc.Button(get_text("Clear Filter", 'en'), id='clear-map-filter',
                                                               color="danger", size="sm", className="ms-auto",
                                                               style={'display': 'none'}), width=3)
                                        ], className="mb-2"),
                                        dcc.Graph(id='dwlr-map', style={'height': '65vh'})
                                    ]),
                                    className="border-0 hover-lift",
                                    style={"backgroundColor": CARD_BG, "borderRadius": "18px",
                                           "boxShadow": SOFT_SHADOW_LG}
                                ),
                                width=12
                            )
                        ], className="mb-5"),

                        # Detailed Report Section
                        html.H4(get_text("System Integrity Report", 'en'), className="card-title-redesign",
                                id="title-integrity-report"),
                        dbc.Row([
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody([
                                        html.Div(id='detailed-report', style={'color': TEXT_DARK})
                                    ]),
                                    className="border-0 hover-lift",
                                    style={"backgroundColor": CARD_BG, "borderRadius": "18px",
                                           "boxShadow": SOFT_SHADOW_MD}
                                ),
                                width=12
                            )
                        ])
                    ])
                ),
                # Comparative Analytics Tab
                dbc.Tab(
                    label=get_text("Comparative Analytics", 'en'),
                    tab_id="tab-comparative-analytics",
                    id="tab-label-comparative-analytics",
                    className="custom-tab-style",
                    active_tab_style=dict(borderBottom='none'),
                    active_label_style=dict(color=ACCENT_PRIMARY),
                    children=comparative_analytics_layout
                ),
                # Alert Log Tab
                dbc.Tab(
                    label=get_text("Alert Log", 'en'),
                    tab_id="tab-alert-log",
                    id="tab-label-alert-log",
                    className="custom-tab-style",
                    active_tab_style=dict(borderBottom='none'),
                    active_label_style=dict(color=ACCENT_PRIMARY),
                    children=alert_log_layout
                )
            ]
        )
    ], fluid=True)
])


# =================================================================================
# --- DASH CALLBACKS (ENHANCED) ---
# =================================================================================

# 0. Translation Callback
@app.callback(
    [Output('main-title', 'children'),
     Output('subtitle', 'children'),
     Output('tab-label-core-dashboard', 'label'),
     Output('tab-label-comparative-analytics', 'label'),
     Output('tab-label-alert-log', 'label'),
     Output('title-forecast-risk', 'children'),
     Output('title-forecast-vector', 'children'),
     Output('title-what-if', 'children'),
     Output('label-rainfall-input', 'children'),
     Output('note-rainfall-input', 'children'),
     Output('title-core-analytics', 'children'),
     Output('title-level-trajectory', 'children'),
     Output('title-map-monitor', 'children'),
     Output('title-integrity-report', 'children'),
     # FIX: Added allow_duplicate=True here to resolve the conflict with handle_auth callback
     Output('auth-button', 'children', allow_duplicate=True),
     Output('title-state-comparison', 'children'),
     Output('title-peer-benchmarking', 'children'),
     Output('title-alert-log', 'children'),
     Output('clear-map-filter', 'children'),
     Output('acknowledge-button', 'children'),
     Output('resolve-button', 'children'),
     Output('language-store', 'data')],
    [Input('language-selector', 'value')],
    # FIX: Added prevent_initial_call=True to resolve the DuplicateCallback error
    prevent_initial_call=True
)
def update_translations(lang_code):
    """Updates all static text elements based on the selected language."""
    if not lang_code:
        lang_code = 'en'

    # Update translation for data table columns - needs to be handled separately in the table's definition/update,
    # but the action buttons and titles can be translated here.

    return [
        get_text("Aqua-Sight | DWLR CONSOLE", lang_code),
        get_text("Real-Time Subsurface Water Dynamics and Predictive Forecasting", lang_code),
        get_text("Core Dashboard", lang_code),
        get_text("Comparative Analytics", lang_code),
        get_text("Alert Log", lang_code),
        get_text("Forecasting & Risk Assessment", lang_code),
        get_text("Primary Forecast Vector", lang_code),
        get_text(" 'What If' Simulation", lang_code),
        get_text("Simulated 24hr Rainfall (mm):", lang_code),
        get_text("The 24hr forecast level instantly adapts to this input.", lang_code),
        get_text("Core Analytical Dashboard", lang_code),
        get_text("Water Level Trajectory (Last 20 Readings)", lang_code),
        get_text("Geospatial Network Monitor (Mainland Distribution)", lang_code),
        get_text("System Integrity Report", lang_code),
        get_text("Logout", lang_code) if dash.callback_context.triggered_id != 'language-selector' else get_text(
            "Login", lang_code),  # Default to login unless auth status updates it
        get_text("State Median Water Level Comparison", lang_code),
        get_text("Peer Group Benchmarking (P-Conflict Score)", lang_code),
        get_text("Alert Log", lang_code),
        get_text("Clear Filter", lang_code),
        get_text("Acknowledge", lang_code),
        get_text("Resolve", lang_code),
        lang_code
    ]


# 1. Callback to Handle Login/Logout
@app.callback(
    [Output('login-modal', 'is_open'),
     Output('auth-status-store', 'data'),
     Output('auth-button', 'children'),
     Output('login-status-message', 'children')],
    [Input('auth-button', 'n_clicks'),
     Input('login-submit', 'n_clicks')],
    [State('auth-status-store', 'data'),
     State('login-modal', 'is_open'),
     State('login-username', 'value'),
     State('login-password', 'value'),
     State('language-store', 'data')],
    # FIX: Added prevent_initial_call=True as this is a user-triggered callback
    prevent_initial_call=True
)
def handle_auth(auth_n, login_n, auth_data, is_open, username, password, lang_code):
    ctx = dash.callback_context

    if not ctx.triggered:
        # This case is now theoretically covered by prevent_initial_call=True
        return dash.no_update, dash.no_update, get_text("Login", lang_code), ""

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'auth-button' and auth_data['logged_in']:
        # Logout
        return False, {'logged_in': False, 'username': None}, get_text("Login", lang_code), ""

    if trigger_id == 'auth-button' and not auth_data['logged_in']:
        # Open Login Modal
        return True, dash.no_update, dash.no_update, ""

    if trigger_id == 'login-submit' and login_n > 0:
        if username == MOCK_USERNAME and password == MOCK_PASSWORD:
            # Successful Login
            return False, {'logged_in': True, 'username': username}, get_text("Logout", lang_code), ""
        else:
            # Failed Login
            return True, dash.no_update, dash.no_update, "Invalid username or password"

    return is_open, dash.no_update, get_text("Logout", lang_code) if auth_data['logged_in'] else get_text("Login",
                                                                                                          lang_code), ""


# 2. Callback to Fetch Data and Update Metrics/Store
@app.callback(
    [Output('status-message', 'children'),
     Output('real-time-metrics-row', 'children'),
     Output('prediction-metrics-row', 'children'),
     Output('detailed-report', 'children'),
     Output('water-level-history', 'data'),
     # --- THE CORE FIX IS HERE: TARGETING THE CHILDREN OF THE HTML.DIV DIRECTLY ---
     # We return the card component (which is already a dbc.Card) directly.
     Output('mtdi-card', 'children'),
     Output('hcrs-card', 'children'),
     Output('pconflict-card', 'children'),
     Output('sti-card', 'children'),
     # ----------------------------------------------------------------------------
     Output('alert-log-store', 'data')],  # Update alert log
    [Input('interval-component', 'n_intervals')],
    [State('station-selector', 'value'),
     State('water-level-history', 'data'),
     State('what-if-rainfall-input', 'value'),
     State('language-store', 'data')],  # Get language for card rendering
    # FIX: Added prevent_initial_call=True as this is an interval callback
    prevent_initial_call=True
)
def update_dashboard(n, selected_station_id, current_history, what_if_rainfall_input, lang_code):
    current_time = datetime.now().strftime('%H:%M:%S')

    last_level = 100.0
    if current_history and current_history.get('current_level') and current_history['current_level']:
        last_level = current_history['current_level'][-1]

    if not current_history:
        current_history = {'time': [], 'current_level': [], 'predicted_level': []}

    history_deques = {k: deque(current_history[k], maxlen=MAX_HISTORY_POINTS) for k in current_history}

    results = generate_live_data(
        last_level=last_level,
        selected_station_id=selected_station_id,
        override_rainfall_str=what_if_rainfall_input
    )

    current_station_details = get_station_by_id(selected_station_id)
    if not current_station_details:
        current_station_details = MOCK_DWLR_SENSORS[0]

    station_name_display = current_station_details['Station_Name_Full']

    # --- 1. Update Historical Store ---
    input_data = results["Real_Time_Input"]
    water_level = input_data['water_level']
    next_day_level = results['Water_Level_Prediction']['Next_Day_Level']

    history_deques['time'].append(current_time)
    history_deques['current_level'].append(water_level)
    history_deques['predicted_level'].append(next_day_level)
    new_history = {k: list(v) for k, v in history_deques.items()}

    # --- 2. Real-Time Inputs Row ---
    real_time_children = [
        dbc.Col(
            create_metric_card(get_text("Water Level", lang_code), f"{water_level:.2f}", unit=get_text("m", lang_code),
                               icon_emoji="💧", delta_value=None, lang_code=lang_code),
            lg=3, md=6),
        dbc.Col(create_metric_card(get_text("Rainfall", lang_code), f"{input_data['rainfall_mm']:.2f}",
                                   unit=get_text("mm", lang_code), icon_emoji="🌧️", delta_value=None,
                                   lang_code=lang_code),
                lg=3, md=6),
        dbc.Col(create_metric_card(get_text("Temperature", lang_code), f"{input_data['avg_temp_c']:.1f}",
                                   unit=get_text("°C", lang_code), icon_emoji="🌡️", delta_value=None,
                                   lang_code=lang_code),
                lg=3, md=6),
        dbc.Col(create_metric_card(get_text("Evapotranspiration", lang_code), f"{input_data['pet_mm']:.2f}",
                                   unit=get_text("mm", lang_code), icon_emoji="💨", delta_value=None,
                                   lang_code=lang_code),
                lg=3, md=6),
    ]

    # --- 3. Unique Metrics Cards ---
    mtdi = results["MTDI"]
    mtdi_card = create_metric_card(get_text("Trend Disparity Index (MTDI)", lang_code), f"{mtdi:.4f}", unit="",
                                   delta_value=mtdi, custom_metric='MTDI', lang_code=lang_code)
    hcrs = results["HCRS"]
    hcrs_card = create_metric_card(get_text("Resilience Score (HCRS)", lang_code), f"{hcrs:.0f}", unit="/ 100",
                                   delta_value=float(hcrs), custom_metric='HCRS', lang_code=lang_code)
    p_conflict = results["PConflict"]
    p_conflict_card = create_metric_card(get_text("Predicted Conflict Score", lang_code), f"{p_conflict:.4f}", unit="",
                                         delta_value=p_conflict, custom_metric='PConflict', lang_code=lang_code)
    sti_score = results["STI"]
    sti_card = create_metric_card(get_text("Sensor Trust Index (STI)", lang_code), f"{sti_score:.0f}", unit="/ 100",
                                  delta_value=float(sti_score), custom_metric='STI', lang_code=lang_code)

    # --- 4. Prediction Metrics Row ---
    level_change = next_day_level - water_level
    prediction_delta_color = 'success' if level_change >= 0 else 'danger'
    risk_proba = results['Drought_Risk_Index']['Probability_Critical_Drop']
    risk_color = 'success'
    if risk_proba > 0.7:
        risk_color = 'danger'
    elif risk_proba > 0.4:
        risk_color = 'warning'
    recharge_net_change = results['Estimated_Recharge']['30_Day_Net_Change']
    recharge_color = 'success' if recharge_net_change >= 0 else 'danger'

    prediction_children = [
        dbc.Col(create_metric_card(get_text("24hr Level Forecast", lang_code), f"{next_day_level:.2f}",
                                   unit=get_text("m", lang_code), delta_value=level_change,
                                   delta_color_name=prediction_delta_color, icon_emoji="🔮", lang_code=lang_code), md=4),
        dbc.Col(create_metric_card(get_text("Drought Risk Probability", lang_code), f"{risk_proba * 100:.1f}%", unit="",
                                   delta_value=risk_proba, delta_color_name=risk_color, icon_emoji="⚠️",
                                   lang_code=lang_code), md=4),
        dbc.Col(create_metric_card(get_text("30-Day Net Recharge", lang_code), f"{recharge_net_change:.2f}",
                                   unit=get_text("m", lang_code), delta_value=recharge_net_change,
                                   delta_color_name=recharge_color, icon_emoji="📈", lang_code=lang_code), md=4),
    ]

    # --- 5. Detailed Report ---
    anomaly_status = results['Anomaly_Check']['Is_Anomaly']
    anomaly_score = results['Anomaly_Check']['Score']
    anomaly_color = DANGER_COLOR if anomaly_status == 'TRUE' else SUCCESS_COLOR

    report_content = html.Div([
        html.Div([html.Span(get_text("Data Feed Time:", lang_code), className="fw-bold me-2"),
                  html.Span(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))], className="mb-2"),
        html.Div([html.Span(get_text("Station:", lang_code), className="fw-bold me-2"),
                  html.Span(f"{station_name_display} ({current_station_details['State']})")], className="mb-2"),
        html.Div([html.Span(get_text("Type/Elevation:", lang_code), className="fw-bold me-2"),
                  html.Span(f"{current_station_details['type']} / {input_data['elevation']}m")], className="mb-2"),
        html.Div([html.Span(get_text("Anomaly Check:", lang_code), className="fw-bold me-2"),
                  html.Span(f"{anomaly_status} (Score: {anomaly_score:.4f})",
                            style={'fontWeight': 'bold', 'color': anomaly_color, 'padding': '4px 8px',
                                   'borderRadius': '6px', 'backgroundColor': anomaly_color + '15'})], className="mb-2"),
        html.Div([html.Span(get_text("Simulated Extraction Rate:", lang_code), className="fw-bold me-2"),
                  html.Span(f"{results['Simulated_Extraction']['Rate']:.2f} {get_text('m/day', lang_code)}")],
                 className="mb-2"),
    ], style={'lineHeight': '1.6', 'fontSize': '0.95rem'})

    # Status Message
    if anomaly_status == 'TRUE':
        status_message_text = get_text("CRITICAL ALERT: Anomaly Detected. Immediate action required for ", lang_code)
        status_message_bg = DANGER_COLOR + '20'
        status_message_color = DANGER_COLOR
    else:
        status_message_text = get_text("✅ System Operational: Data feed active and stable for ", lang_code)
        status_message_bg = SUCCESS_COLOR + '20'
        status_message_color = SUCCESS_COLOR

    status_message = html.P(
        [
            html.Span(status_message_text),
            html.Span(f"{station_name_display}.", style={'fontWeight': 'bold', 'textDecoration': 'underline'}),
            html.Span(f" {get_text('Last updated: ', lang_code)}{current_time}"),
        ],
        style={
            'color': status_message_color, 'backgroundColor': status_message_bg,
            'padding': '12px 15px', 'borderRadius': '10px', 'fontWeight': 500, 'marginBottom': '0'
        }
    )

    # --- 6. Alert Log Update ---
    new_alert_log = check_for_alerts(selected_station_id, station_name_display, results)

    return (
        status_message,
        real_time_children,
        prediction_children,
        report_content,
        new_history,
        # *** CORRECTED RETURN: Cards are returned directly. ***
        mtdi_card,
        hcrs_card,
        p_conflict_card,
        sti_card,
        # ******************************************************
        new_alert_log
    )


# 3. Callback to Update the Time-Series Chart
@app.callback(
    Output('water-level-chart', 'figure'),
    [Input('water-level-history', 'data')]
)
def update_graph_live(history_data):
    """Creates the Plotly figure from the dcc.Store data with refined styling."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=history_data['time'], y=history_data['current_level'], name='Current Level (m)',
        line=dict(color=ACCENT_PRIMARY, width=4, dash='solid'), mode='lines+markers',
        marker=dict(size=7, symbol='circle', color=CARD_BG, line=dict(width=2, color=ACCENT_PRIMARY))
    ))

    fig.add_trace(go.Scatter(
        x=history_data['time'], y=history_data['predicted_level'], name='Predicted Next Day Level (Simulated)',
        line=dict(color=ACCENT_SECONDARY, width=2, dash='dash'), mode='lines', opacity=0.7
    ))

    all_levels = history_data['current_level'] + history_data['predicted_level']
    if all_levels:
        y_min = min(all_levels) - 0.5
        y_max = max(all_levels) + 0.5
    else:
        y_min, y_max = 95.0, 105.0

    fig.update_layout(
        title=None, xaxis_title='Time of Reading', yaxis_title='Water Level (meters)',
        plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, font=dict(color=TEXT_DARK, size=11),
        margin=dict(l=40, r=20, t=10, b=40),
        legend=dict(orientation="h", yanchor="top", y=1.0, xanchor="left", x=0, bgcolor='rgba(255,255,255,0.7)',
                    bordercolor=BG_LIGHT, borderwidth=1, font=dict(size=10)),
        yaxis=dict(range=[y_min, y_max], fixedrange=True, gridcolor=BG_LIGHT, zerolinecolor=BG_LIGHT, showline=False),
        xaxis=dict(showgrid=False, showline=True, linecolor=BG_LIGHT),
        hovermode="x unified"
    )

    return fig


# 4. Callback to Handle Map Click (Drill-down filter) and Clear Filter Button
@app.callback(
    [Output('selected-state-ut-store', 'data'),
     Output('clear-map-filter', 'style'),
     Output('map-filter-info', 'children')],
    [Input('dwlr-map', 'clickData'),
     Input('clear-map-filter', 'n_clicks')],
    [State('language-store', 'data')],
    # FIX: Added prevent_initial_call=True as this is a user-triggered callback
    prevent_initial_call=True
)
def handle_map_click_and_filter_clear(clickData, n_clicks, lang_code):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Handle Clear Filter
    if triggered_id == 'clear-map-filter' and n_clicks > 0:
        return None, {'display': 'none'}, ""

    # Handle Map Click
    if triggered_id == 'dwlr-map' and clickData and 'points' in clickData:
        # Get the 'State' from the hovertext of the clicked point
        hover_text = clickData['points'][0]['hovertext']
        if hover_text:
            # Extract State from the formatted hover_text
            try:
                state_name = hover_text.split('(')[1].split(')')[0]
                filter_info = f"Filter Active: {state_name}"
                return state_name, {'display': 'block'}, filter_info
            except IndexError:
                # Fallback if parsing fails
                return dash.no_update, dash.no_update, dash.no_update

    # Default state (no filter)
    return dash.no_update, {'display': 'none'}, ""


# 5. Callback to Update the Map (Now with Drill-down)
@app.callback(
    Output('dwlr-map', 'figure'),
    [Input('station-selector', 'value'),
     Input('selected-state-ut-store', 'data')]
)
def update_dwlr_map(selected_station_id, selected_state_ut):
    df = pd.DataFrame(MOCK_DWLR_SENSORS)
    color_map = {
        'NORMAL': SUCCESS_COLOR,
        'LOW_ALERT': WARNING_COLOR,
        'ANOMALY': DANGER_COLOR
    }

    # 1. Apply Filter
    filtered_df = df
    map_zoom = 3.8
    center_lat = 22.0
    center_lon = 78.0

    if selected_state_ut:
        # Filter the DataFrame
        filtered_df = df[df['State'] == selected_state_ut]

        # Adjust Center and Zoom for the selected State/UT
        if selected_state_ut in INDIAN_REGIONS:
            lat_min, lat_max, lon_min, lon_max = INDIAN_REGIONS[selected_state_ut]
            center_lat = (lat_min + lat_max) / 2
            center_lon = (lon_min + lon_max) / 2

            # Simple heuristic for zoom level (adjust based on bounding box size)
            lat_range = lat_max - lat_min
            lon_range = lon_max - lon_min
            max_range = max(lat_range, lon_range)

            # Zoom levels from 1 (world) to 12 (street)
            # 3.8 is India. For small states, zoom up to 6-7.
            if max_range < 1.0:
                map_zoom = 7.0
            elif max_range < 3.0:
                map_zoom = 6.0
            elif max_range < 5.0:
                map_zoom = 5.0
            else:
                map_zoom = 4.5
        else:
            # Fallback to general India view if region not found
            pass

    # Generate hover text (needs to be done on the filtered_df)
    filtered_df['hover_text'] = filtered_df.apply(lambda row:
                                                  f"<b>{row['Station_Name_Full']} ({row['State']})</b><br>"
                                                  f"District: {row['District']}<br>"
                                                  f"Type: {row['type']}<br>"
                                                  f"Level: {row['level']:.2f} m<br>"
                                                  f"Status: {row['status']}", axis=1)

    # Base map trace for all stations (Filtered or All)
    fig = px.scatter_mapbox(
        filtered_df,
        lat="lat",
        lon="lon",
        hover_data={"hover_text": True, "lat": False, "lon": False, "status": False},
        color="status",
        color_discrete_map=color_map,
        size=[10] * len(filtered_df),
        zoom=map_zoom,
        center={"lat": center_lat, "lon": center_lon},
        mapbox_style="carto-positron",
        title=None
    )

    fig.update_traces(
        hovertemplate='%{hovertext}<extra></extra>',
        marker=dict(opacity=0.8, size=10)
    )

    # Highlight the currently selected station with a pulse effect
    if selected_station_id and selected_station_id in filtered_df['id'].values:
        selected_data = filtered_df[filtered_df['id'] == selected_station_id]
        if not selected_data.empty:
            # Selected Station Trace (Primary Blue)
            fig.add_trace(go.Scattermapbox(
                lat=selected_data['lat'], lon=selected_data['lon'], mode='markers',
                marker=go.scattermapbox.Marker(size=16, color=ACCENT_PRIMARY, opacity=1.0, symbol='circle'),
                name='Selected Station', hoverinfo='text', hovertext=selected_data['hover_text']
            ))

            # Pulse Effect Trace (Larger and Fainter)
            fig.add_trace(go.Scattermapbox(
                lat=selected_data['lat'], lon=selected_data['lon'], mode='markers',
                marker=go.scattermapbox.Marker(size=30, color=ACCENT_PRIMARY, opacity=0.2, symbol='circle'),
                name='Pulse Effect', hoverinfo='none',
            ))

    fig.update_layout(
        plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, font=dict(color=TEXT_DARK),
        margin=dict(l=0, r=0, t=0, b=0), clickmode='event+select', hovermode='closest',
        legend=dict(orientation="v", yanchor="top", y=0.99, xanchor="right", x=0.99,
                    bgcolor="rgba(255, 255, 255, 0.8)", bordercolor=BG_LIGHT, borderwidth=1),
        mapbox=dict(style="carto-positron", pitch=0, bearing=0, zoom=map_zoom,
                    center={"lat": center_lat, "lon": center_lon})
    )

    return fig


# 6. Comparative Analytics Callbacks
@app.callback(
    Output('state-median-chart', 'figure'),
    [Input('interval-component', 'n_intervals'),
     Input('selected-state-ut-store', 'data')]
)
def update_state_median_chart(n, selected_state_ut):
    """Generates the State Median Water Level Comparison chart."""
    df_all = pd.DataFrame(MOCK_DWLR_SENSORS)

    # Group by State and calculate the median level
    median_levels = df_all.groupby('State')['level'].median().reset_index()
    median_levels.columns = ['State', 'Median_Level']

    if selected_state_ut:
        # Highlight the selected state and possibly limit to relevant peers
        median_levels = median_levels.sort_values(by='Median_Level', ascending=False)

        # If the list is large, take the selected state + 9 others (top 10 for visibility)
        if len(median_levels) > 10:
            top_states = median_levels.head(10)['State'].tolist()
            if selected_state_ut not in top_states:
                # Ensure the selected state is in the chart
                median_levels = median_levels[median_levels['State'].isin(top_states) | (
                            median_levels['State'] == selected_state_ut)].drop_duplicates(subset=['State'])
                median_levels = median_levels.sort_values(by='Median_Level', ascending=False)
            else:
                median_levels = median_levels[median_levels['State'].isin(top_states)]

    # Sort for plotting
    median_levels = median_levels.sort_values(by='Median_Level', ascending=True)

    # Define colors
    colors = [ACCENT_PRIMARY] * len(median_levels)
    if selected_state_ut:
        try:
            # Highlight the selected state in a different color
            selected_index = median_levels[median_levels['State'] == selected_state_ut].index[0]
            colors[median_levels.index.get_loc(
                selected_index)] = DANGER_COLOR  # Use danger color to highlight the selection
        except IndexError:
            pass  # State not in the top 10 list

    fig = px.bar(
        median_levels,
        y='State',
        x='Median_Level',
        orientation='h',
        title=None
    )

    fig.update_traces(
        marker_color=colors,
        opacity=0.8,
        hovertemplate="<b>%{y}</b><br>Median Level: %{x:.2f} m<extra></extra>"
    )

    fig.update_layout(
        plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG,
        font=dict(color=TEXT_DARK),
        yaxis_title=None,
        xaxis_title="Median Water Level (m)",
        margin=dict(l=10, r=20, t=20, b=20),
        height=450
    )

    return fig


@app.callback(
    Output('pconflict-benchmark-chart', 'figure'),
    [Input('interval-component', 'n_intervals'),
     Input('station-selector', 'value')]
)
def update_pconflict_benchmark_chart(n, selected_station_id):
    """Generates the Peer Group Benchmarking box plot."""
    df_all = pd.DataFrame(MOCK_DWLR_SENSORS)
    selected_station = get_station_by_id(selected_station_id)

    if not selected_station:
        return go.Figure()

    selected_state = selected_station['State']
    selected_score = selected_station['PConflict_Initial']

    # Filter the peer group (stations in the same State/UT)
    peer_group = df_all[df_all['State'] == selected_state]

    # Create the box plot for the peer group distribution
    fig = go.Figure()

    # Box Plot for the Peer Group
    fig.add_trace(go.Box(
        y=peer_group['PConflict_Initial'],
        name=get_text("P-Conflict Distribution for Peer Group", 'en'),
        marker_color=ACCENT_PRIMARY,
        boxpoints=False,  # Don't show individual points for cleaner look
        hovertemplate="Median: %{y}<br>State: %{name}<extra></extra>"
    ))

    # Scatter plot for the Selected Station (to highlight it)
    fig.add_trace(go.Scatter(
        x=[get_text("P-Conflict Distribution for Peer Group", 'en')],  # Same x-position as the box plot
        y=[selected_score],
        mode='markers',
        name=f"Selected Station: {selected_station['Station_Name_Full']}",
        marker=dict(
            size=15,
            color=DANGER_COLOR,  # Highlight the selected station
            symbol='star',
            line=dict(width=2, color=CARD_BG)
        ),
        hovertemplate=f"<b>Selected Station:</b> {selected_station['Station_Name_Full']}<br>P-Conflict Score: %{{y:.4f}}<extra></extra>"
    ))

    fig.update_layout(
        plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG,
        font=dict(color=TEXT_DARK),
        title=f"Peer Group: {selected_state}",
        yaxis_title="P-Conflict Score (0.0 - 1.0)",
        xaxis_title=None,
        showlegend=True,
        margin=dict(l=40, r=20, t=40, b=40),
        height=450
    )

    return fig


# 7. Alert Log and Notification Callbacks
@app.callback(
    [Output('alert-log-table', 'data'),
     Output('alert-badge', 'children'),
     Output('alert-bell', 'className'),
     Output('alert-action-buttons', 'hidden')],
    [Input('alert-log-store', 'data'),
     Input('alert-status-filter', 'value'),
     Input('acknowledge-button', 'n_clicks'),
     Input('resolve-button', 'n_clicks')],
    [State('alert-log-table', 'selected_rows'),
     State('auth-status-store', 'data')],
    # FIX: Added prevent_initial_call=True as this is mainly triggered by Store/Clicks
    prevent_initial_call=True
)
def update_alert_log_table(alert_log_data, status_filter, ack_n, res_n, selected_rows_indices, auth_data):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Use global ALERT_LOG for state manipulation
    global ALERT_LOG

    # 1. Handle Acknowledge/Resolve Clicks
    if triggered_id in ['acknowledge-button', 'resolve-button'] and selected_rows_indices is not None and len(
            selected_rows_indices) > 0 and auth_data['logged_in']:
        action = 'ACKNOWLEDGED' if triggered_id == 'acknowledge-button' else 'RESOLVED'

        # Filter the current ALERT_LOG data based on the status filter for matching
        current_data = []
        if status_filter != 'ALL':
            current_data = [a for a in alert_log_data if a['status'] == status_filter]
        else:
            current_data = alert_log_data

        # Get the IDs from the currently displayed table rows
        selected_alert_ids = [current_data[i]['id'] for i in selected_rows_indices if i < len(current_data)]

        # Update the global ALERT_LOG (deque)
        new_alert_log = list(ALERT_LOG)  # Convert deque to list for modification
        for alert in new_alert_log:
            if alert['id'] in selected_alert_ids:
                alert['status'] = action

        ALERT_LOG.clear()
        ALERT_LOG.extend(new_alert_log)  # Re-populate the deque
        alert_log_data = new_alert_log  # Use the updated log for display filter

    # 2. Apply Status Filter for Display
    if status_filter == 'ALL' or triggered_id in ['acknowledge-button', 'resolve-button']:
        filtered_log = list(ALERT_LOG)
    else:
        filtered_log = [a for a in ALERT_LOG if a['status'] == status_filter]

    # 3. Calculate New Alert Count
    new_alerts_count = sum(1 for a in ALERT_LOG if a['status'] == 'NEW')

    # 4. Set Bell Icon Class
    bell_class = 'position-relative'
    if new_alerts_count > 0:
        bell_class = 'position-relative bell-notification'  # Flash the bell

    # 5. Hide Action Buttons if not logged in
    action_buttons_hidden = not auth_data['logged_in']


    return filtered_log, new_alerts_count, bell_class, action_buttons_hidden


if __name__ == '__main__':

    check_for_alerts(MOCK_DWLR_SENSORS[0]['id'], MOCK_DWLR_SENSORS[0]['Station_Name_Full'],
                     generate_live_data(100.0, MOCK_DWLR_SENSORS[0]['id'], 0.0))
    app.run(debug=True)