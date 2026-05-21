from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import swisseph as swe
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

@app.post("/api/v1/calculate")
def calculate(data: dict):
    try:
        # Extract data with defaults
        year = int(data.get("year"))
        month = int(data.get("month"))
        day = int(data.get("day"))
        hour = int(data.get("hour"))
        minute = int(data.get("minute"))
        lat = float(data.get("lat"))
        lon = float(data.get("lon"))
        
        # Calculate Julian Day
        jd = swe.julday(year, month, day, hour + minute/60)
        
        # Flags: Standard tropical zodiac, high speed
        flag = swe.FLG_SPEED
        
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
        
        for k, pid in p_map.items():
            res = swe.calc_ut(jd, pid, flag)
            # res is (lon, lat, dist, speed, serr)
            # Ensure we get a float
            lon_val = float(res[0])
            
            # Normalize longitude to 0-360
            lon_norm = lon_val % 360
            sign_idx = int(lon_norm // 30)
            deg = lon_norm % 30
            
            planets[k] = {
                "name_ar": ar_names[k], 
                "sign": signs[sign_idx], 
                "degree": round(deg, 4), 
                "longitude": round(lon_norm, 6)
            }
            
        # Calculate Houses
        # houses_ex returns (cusps, ascmc)
        # ascmc is [Asc, MC, ARMC, Vertex]
        cusps, ascmc = swe.houses_ex(jd, lat, lon, "P".encode(), flag)
        
        # Ensure ascmc values are floats
        asc_lon = float(ascmc[0]) % 360
        mc_lon = float(ascmc[1]) % 360
        
        asc_sign_idx = int(asc_lon // 30)
        mc_sign_idx = int(mc_lon // 30)
        
        return {
            "success": True, 
            "planets": planets, 
            "ascendant": {
                "sign": signs[asc_sign_idx], 
                "degree": round(asc_lon % 30, 4), 
                "longitude": asc_lon
            }, 
            "mc": {
                "sign": signs[mc_sign_idx], 
                "degree": round(mc_lon % 30, 4), 
                "longitude": mc_lon
            }
        }
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}
