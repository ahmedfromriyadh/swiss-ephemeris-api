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
        jd = swe.julday(data["year"], data["month"], data["day"], 
                        data["hour"] + data["minute"]/60)
        flag = swe.FLG_SPEED | swe.FLG_SIDBIT
        
        planets = {}
        p_map = {"sun": swe.SUN, "moon": swe.MOON, "mercury": swe.MERCURY,
                 "venus": swe.VENUS, "mars": swe.MARS, "jupiter": swe.JUPITER,
                 "saturn": swe.SATURN, "uranus": swe.URANUS, "neptune": swe.NEPTUNE,
                 "pluto": swe.PLUTO, "node": swe.MEAN_NODE, "chiron": swe.CHIRON}
        ar_names = {"sun":"الشمس","moon":"القمر","mercury":"عطارد","venus":"الزهرة",
                    "mars":"المريخ","jupiter":"المشتري","saturn":"زحل","uranus":"أورانوس",
                    "neptune":"نبتون","pluto":"بلوتو","node":"عقدة الشمال","chiron":"تشيرون"}
        signs = ['الحمل','الثور','الجوزاء','السرطان','الأسد','العذراء','الميزان','العقرب','القوس','الجدي','الدلو','الحوت']
        
        for k, pid in p_map.items():
            res = swe.calc_ut(jd, pid, flag)
            lon = res[0] % 360
            sign_idx = int(lon // 30)
            deg = lon % 30
            planets[k] = {
                "name_ar": ar_names[k], 
                "sign": signs[sign_idx], 
                "degree": round(deg, 4), 
                "longitude": round(lon, 6)
            }
            
        cusps, ascmc = swe.houses_ex(jd, data["lat"], data["lon"], "P".encode(), flag)
        asc_lon = ascmc[0] % 360
        mc_lon = ascmc[1] % 360
        
        return {
            "success": True, 
            "planets": planets, 
            "ascendant": {"sign": signs[int(asc_lon//30)], "degree": round(asc_lon%30, 4), "longitude": asc_lon}, 
            "mc": {"sign": signs[int(mc_lon//30)], "degree": round(mc_lon%30, 4), "longitude": mc_lon}
        }
    except Exception as e:
        return {"success": False, "error": str(e)}