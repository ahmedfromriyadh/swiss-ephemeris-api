from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import swisseph as swe
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ IMPORTANT: Do NOT set ephemeris path - use built-in data
# This avoids all file download issues

@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

@app.post("/api/v1/calculate")
async def calculate(request: Request):
    try:
        body = await request.json()
        
        year = int(body.get("year"))
        month = int(body.get("month"))
        day = int(body.get("day"))
        hour = int(body.get("hour"))
        minute = int(body.get("minute"))
        lat = float(body.get("lat"))
        lon = float(body.get("lon"))
        
        jd = swe.julday(year, month, day, hour + minute/60)
        
        # ✅ Use built-in ephemeris (no external files)
        flag = swe.FLG_SPEED
        
        planets = {}
        
        # 🌟 PLANETS THAT WORK WITH BUILT-IN EPHEMERIS (no asteroids)
        p_map = {
            "sun": swe.SUN, "moon": swe.MOON, "mercury": swe.MERCURY,
            "venus": swe.VENUS, "mars": swe.MARS, "jupiter": swe.JUPITER,
            "saturn": swe.SATURN, "uranus": swe.URANUS, "neptune": swe.NEPTUNE,
            "pluto": swe.PLUTO, "node": swe.MEAN_NODE
            # ❌ REMOVED: "chiron": swe.CHIRON (requires asteroid files)
        }
        
        ar_names = {
            "sun":"الشمس","moon":"القمر","mercury":"عطارد","venus":"الزهرة",
            "mars":"المريخ","jupiter":"المشتري","saturn":"زحل","uranus":"أورانوس",
            "neptune":"نبتون","pluto":"بلوتو","node":"عقدة الشمال"
        }
        
        signs = ['الحمل','الثور','الجوزاء','السرطان','الأسد','العذراء','الميزان','العقرب','القوس','الجدي','الدلو','الحوت']
        
        for k, pid in p_map.items():
            res = swe.calc_ut(jd, pid, flag)
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
        
        # Calculate houses (works with built-in ephemeris)
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b"P", flag)
        
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
