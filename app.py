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
        # Extract data
        year = int(data.get("year"))
        month = int(data.get("month"))
        day = int(data.get("day"))
        hour = int(data.get("hour"))
        minute = int(data.get("minute"))
        lat = float(data.get("lat"))
        lon = float(data.get("lon"))
        
        # Calculate Julian Day
        jd = swe.julday(year, month, day, hour + minute/60)
        
        # Use simple flags - just speed calculation
        flag = swe.FLG_SPEED | swe.FLG_SWIEPH
        
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
            # Calculate planet position
            result = swe.calc_ut(jd, pid, flag)
            
            # result is a tuple: (longitude, latitude, distance, speed)
            # Extract longitude (first element)
            if isinstance(result, tuple) and len(result) >= 1:
                lon_val = result[0]
            else:
                lon_val = result
            
            # Ensure it's a number
            if not isinstance(lon_val, (int, float)):
                raise ValueError(f"Invalid longitude for {k}: {type(lon_val)}")
            
            # Normalize to 0-360
            lon_norm = lon_val % 360
            sign_idx = int(lon_norm // 30)
            deg = lon_norm % 30
            
            planets[k] = {
                "name_ar": ar_names[k], 
                "sign": signs[sign_idx], 
                "degree": round(deg, 4), 
                "longitude": round(lon_norm, 6)
            }
        
        # Calculate Houses using Placidus system
        # houses_ex returns (cusps, ascmc)
        house_result = swe.houses_ex(jd, lat, lon, b'P', flag)
        
        if isinstance(house_result, tuple) and len(house_result) >= 2:
            cusps, ascmc = house_result
        else:
            raise ValueError(f"Invalid houses result: {type(house_result)}")
        
        # Extract Ascendant and MC
        if isinstance(ascmc, (list, tuple)) and len(ascmc) >= 2:
            asc_lon = float(ascmc[0]) % 360
            mc_lon = float(ascmc[1]) % 360
        else:
            raise ValueError(f"Invalid ascmc result: {type(ascmc)}")
        
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
       
