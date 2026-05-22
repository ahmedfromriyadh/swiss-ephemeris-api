from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import swisseph as swe
from datetime import datetime
import os

app = FastAPI()

# ✅ CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ IMPORTANT: Use built-in Moshier ephemeris (no external files needed)
# This flag tells Swiss Ephemeris to use internal calculations
MOSEPH_FLAG = swe.FLG_SPEED | swe.FLG_MOSEPH

@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

@app.post("/api/v1/calculate")
async def calculate(request: Request, data: dict):
    try:
        # Extract and validate input
        year = int(data.get("year"))
        month = int(data.get("month"))
        day = int(data.get("day"))
        hour = int(data.get("hour"))
        minute = int(data.get("minute"))
        lat = float(data.get("lat"))
        lon = float(data.get("lon"))
        
        # Calculate Julian Day (UT)
        jd = swe.julday(year, month, day, hour + minute/60)
        
        planets = {}
        p_map = {
            "sun": swe.SUN, "moon": swe.MOON, "mercury": swe.MERCURY,
            "venus": swe.VENUS, "mars": swe.MARS, "jupiter": swe.JUPITER,
            "saturn": swe.SATURN, "uranus": swe.URANUS, "neptune": swe.NEPTUNE,
            "pluto": swe.PLUTO, "node": swe.MEAN_NODE, "chiron": swe.CHIRON
        }
        ar_names = {
            "sun":"الشمس","moon":"القمر","mercury":"عطارد","venus":"الزهرة",
            "mars":"المريخ","jupiter":"المشتري","saturn":"زحل","uranus":"أورانوس",
            "neptune":"نبتون","pluto":"بلوتو","node":"عقدة الشمال","chiron":"تشيرون"
        }
        signs = ['الحمل','الثور','الجوزاء','السرطان','الأسد','العذراء','الميزان','العقرب','القوس','الجدي','الدلو','الحوت']
        
        # Calculate each planet using MOSEPH (built-in ephemeris)
        for k, pid in p_map.items():
            res = swe.calc_ut(jd, pid, MOSEPH_FLAG)
            lon_val = float(res[0][0])  # [0][0] = longitude
            
            # Normalize to 0-360°
            lon_norm = lon_val % 360
            sign_idx = int(lon_norm // 30)
            deg = lon_norm % 30
            
            planets[k] = {
                "name_ar": ar_names[k], 
                "sign": signs[sign_idx], 
                "degree": round(deg, 4), 
                "longitude": round(lon_norm, 6)
            }
        
        # Calculate houses (Ascendant & MC)
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b"P", MOSEPH_FLAG)
        
        asc_lon = float(ascmc[0]) % 360
        mc_lon = float(ascmc[1]) % 360
        
        return {
            "success": True, 
            "planets": planets, 
            "ascendant": {
                "sign": signs[int(asc_lon // 30)], 
                "degree": round(asc_lon % 30, 4), 
                "longitude": asc_lon
            }, 
            "mc": {
                "sign": signs[int(mc_lon // 30)], 
                "degree": round(mc_lon % 30, 4), 
                "longitude": mc_lon
            }
        }
        
    except Exception as e:
        import traceback
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e), "traceback": traceback.format_exc()}
        )

# Handle 404 for undefined routes
@app.on_event("startup")
async def startup_event():
    print(f"✅ Swiss Ephemeris API started | MOSEPH mode: Built-in ephemeris active")
