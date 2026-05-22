from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import swisseph as swe
from datetime import datetime
from pydantic import BaseModel

app = FastAPI()

# CORS - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request body model
class AstroRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    lat: float
    lon: float

# MOSEPH flag for built-in ephemeris
MOSEPH_FLAG = swe.FLG_SPEED | swe.FLG_MOSEPH

@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

@app.post("/api/v1/calculate")
async def calculate(request: AstroRequest):
    try:
        # Calculate Julian Day (UT)
        jd = swe.julday(request.year, request.month, request.day, 
                       request.hour + request.minute/60)
        
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
        
        # Calculate each planet
        for k, pid in p_map.items():
            res = swe.calc_ut(jd, pid, MOSEPH_FLAG)
            lon_val = float(res[0][0])
            
            lon_norm = lon_val % 360
            sign_idx = int(lon_norm // 30)
            deg = lon_norm % 30
            
            planets[k] = {
                "name_ar": ar_names[k], 
                "sign": signs[sign_idx], 
                "degree": round(deg, 4), 
                "longitude": round(lon_norm, 6)
            }
        
        # Calculate houses
        cusps, ascmc = swe.houses_ex(jd, request.lat, request.lon, b"P", MOSEPH_FLAG)
        
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

@app.on_event("startup")
async def startup_event():
    print(f"✅ Swiss Ephemeris API started | MOSEPH mode active")
