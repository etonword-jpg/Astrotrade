import streamlit as st
import yfinance as yf
import google.generativeai as genai
import ephem
import math
import pandas as pd
import random
from datetime import datetime, timedelta

st.set_page_config(page_title="AstroTrade", page_icon="🌟", layout="centered")

# ============================================================
# CSS
# ============================================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Space+Grotesk:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; background-color: #080810; color: #e8e8f0; }
    .stApp { background: radial-gradient(ellipse at top left, #1a0533 0%, #080810 50%, #001a33 100%); min-height: 100vh; }
    .brand-wrap { text-align: center; padding: 20px 0 8px 0; }
    .brand-title {
        font-family: 'Playfair Display', serif; font-size: 3.2em; font-weight: 900;
        background: linear-gradient(135deg, #fff 0%, #e040fb 40%, #7c4dff 70%, #40c4ff 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        letter-spacing: 6px; text-transform: uppercase;
        filter: drop-shadow(0 0 20px rgba(224,64,251,0.5));
    }
    .brand-sub { font-weight: 300; color: #b39ddb; font-size: 0.9em; letter-spacing: 3px; text-transform: uppercase; margin-top: -4px; }
    .brand-line { width: 80px; height: 2px; background: linear-gradient(90deg, transparent, #e040fb, #7c4dff, transparent); margin: 12px auto; }
    .glass-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(224,64,251,0.2); border-radius: 16px; padding: 20px; margin: 12px 0; backdrop-filter: blur(10px); }
    .signal-buy  { background: rgba(0,230,118,0.08);  border: 1px solid rgba(0,230,118,0.4);  border-radius: 16px; padding: 20px; }
    .signal-sell { background: rgba(255,23,68,0.08);  border: 1px solid rgba(255,23,68,0.4);  border-radius: 16px; padding: 20px; }
    .signal-wait { background: rgba(255,160,0,0.08);  border: 1px solid rgba(255,160,0,0.4);  border-radius: 16px; padding: 20px; }
    .tarot-card { background: linear-gradient(145deg, rgba(124,77,255,0.15), rgba(224,64,251,0.08)); border: 1px solid rgba(224,64,251,0.3); border-radius: 16px; padding: 14px 8px; text-align: center; }
    .section-header { font-family: 'Playfair Display', serif; font-size: 1.3em; font-weight: 700; background: linear-gradient(90deg, #e040fb, #7c4dff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 1px; margin: 20px 0 10px 0; }
    [data-testid="metric-container"] { background: rgba(255,255,255,0.04); border: 1px solid rgba(124,77,255,0.2); border-radius: 12px; padding: 12px; }
    .stButton > button { background: linear-gradient(135deg, #7c4dff, #e040fb) !important; color: white !important; border: none !important; border-radius: 50px !important; font-weight: 700 !important; letter-spacing: 2px !important; padding: 14px !important; box-shadow: 0 0 25px rgba(224,64,251,0.4) !important; }
    .stTextInput > div > div > input, .stSelectbox > div > div { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(124,77,255,0.3) !important; border-radius: 12px !important; color: #e8e8f0 !important; }
    .stRadio > div { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 8px; }
    [data-testid="stSidebar"] { background: rgba(8,8,16,0.95) !important; border-right: 1px solid rgba(124,77,255,0.2) !important; }
    hr { border-color: rgba(124,77,255,0.2) !important; }
    .poll-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(124,77,255,0.25); border-radius: 14px; padding: 14px 18px; margin: 8px 0; }
    .poll-bar-bg { background: rgba(255,255,255,0.08); border-radius: 20px; height: 8px; margin: 4px 0; }
    .footer-text { text-align: center; color: #5c5c7a; font-size: 0.78em; letter-spacing: 1px; padding: 10px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="brand-wrap">
    <div class="brand-title">✦ AstroTrade</div>
    <div class="brand-line"></div>
    <div class="brand-sub">Where the Stars Meet the Market</div>
</div>
""", unsafe_allow_html=True)
st.divider()

# Sidebar
with st.sidebar:
    st.markdown("<div style='font-family:Playfair Display,serif;font-size:1.3em;color:#e040fb;letter-spacing:2px'>⚙ SETTINGS</div>", unsafe_allow_html=True)
    gemini_key = st.text_input("🔑 Gemini API Key", type="password", placeholder="AIza...")
    st.divider()
    st.markdown("<div style='color:#b39ddb;font-size:0.85em;letter-spacing:1px'>HOW TO USE</div>", unsafe_allow_html=True)
    st.markdown("1. ใส่ Gemini API Key")
    st.markdown("2. เลือกประเภท: หุ้น / Crypto")
    st.markdown("3. เลือกชื่อจากรายการ")
    st.markdown("4. เลือกไพ่ยิปซี 3 ใบ")
    st.markdown("5. กด **วิเคราะห์** (วันเกิดไม่บังคับ)")
    st.divider()
    st.caption("✦ AstroTrade 2025 | ไม่ใช่คำแนะนำทางการเงิน")

# ============================================================
# รายการหุ้น/Crypto
# ============================================================
CRYPTO_LIST = {
    "Bitcoin (BTC)": "BTC-USD", "Ethereum (ETH)": "ETH-USD",
    "Solana (SOL)": "SOL-USD", "XRP": "XRP-USD", "BNB": "BNB-USD",
    "Dogecoin (DOGE)": "DOGE-USD", "Cardano (ADA)": "ADA-USD",
    "Avalanche (AVAX)": "AVAX-USD", "Chainlink (LINK)": "LINK-USD",
    "Polkadot (DOT)": "DOT-USD", "Shiba Inu (SHIB)": "SHIB-USD",
    "Pepe (PEPE)": "PEPE-USD", "Sui (SUI)": "SUI-USD",
    "🔍 พิมพ์เอง": "CUSTOM",
}
STOCK_LIST = {
    "NVIDIA (NVDA)": "NVDA", "Apple (AAPL)": "AAPL", "Tesla (TSLA)": "TSLA",
    "Microsoft (MSFT)": "MSFT", "Meta (META)": "META", "Amazon (AMZN)": "AMZN",
    "Google (GOOGL)": "GOOGL", "AMD": "AMD",
    "CPALL (ไทย)": "CPALL.BK", "PTT (ไทย)": "PTT.BK",
    "SCB (ไทย)": "SCB.BK", "KBANK (ไทย)": "KBANK.BK",
    "AOT (ไทย)": "AOT.BK", "MINT (ไทย)": "MINT.BK",
    "🔍 พิมพ์เอง": "CUSTOM",
}

# ============================================================
# ไพ่ Tarot
# ============================================================
TAROT_CARDS = [
    {"name": "The Fool",           "th": "คนโง่เขลา",    "emoji": "🃏", "meaning": "จุดเริ่มต้นใหม่ โอกาสที่ไม่คาดคิด"},
    {"name": "The Magician",       "th": "นักมายากล",     "emoji": "🎩", "meaning": "มีทักษะและพลัง พร้อมลงมือทำ"},
    {"name": "The High Priestess", "th": "นักบวชหญิง",    "emoji": "🌙", "meaning": "ใช้สัญชาตญาณ รอเวลาที่เหมาะสม"},
    {"name": "The Empress",        "th": "จักรพรรดินี",   "emoji": "👑", "meaning": "ความอุดมสมบูรณ์ ผลตอบแทนดี"},
    {"name": "The Emperor",        "th": "จักรพรรดิ",     "emoji": "⚔️", "meaning": "ความมั่นคง โครงสร้างแข็งแกร่ง"},
    {"name": "The Lovers",         "th": "คู่รัก",        "emoji": "💕", "meaning": "ต้องตัดสินใจเลือก จุดเปลี่ยนสำคัญ"},
    {"name": "The Chariot",        "th": "รถศึก",         "emoji": "🏆", "meaning": "ชัยชนะ ก้าวหน้าอย่างแข็งแกร่ง"},
    {"name": "Strength",           "th": "ความแข็งแกร่ง", "emoji": "🦁", "meaning": "ใจเย็น ควบคุมสถานการณ์ได้"},
    {"name": "The Hermit",         "th": "ฤๅษี",          "emoji": "🏮", "meaning": "ใคร่ครวญก่อน อย่าเร่งรีบ"},
    {"name": "Wheel of Fortune",   "th": "วงล้อโชคชะตา", "emoji": "🎡", "meaning": "โชคกำลังเปลี่ยน จังหวะกำลังมา"},
    {"name": "Justice",            "th": "ความยุติธรรม",  "emoji": "⚖️", "meaning": "ผลลัพธ์สมเหตุสมผล ตลาดสมดุล"},
    {"name": "The Star",           "th": "ดวงดาว",        "emoji": "⭐", "meaning": "ความหวัง สัญญาณบวกกำลังมา"},
    {"name": "The Moon",           "th": "ดวงจันทร์",     "emoji": "🌕", "meaning": "ความไม่แน่นอน ระวังข้อมูลลวง"},
    {"name": "The Sun",            "th": "ดวงอาทิตย์",    "emoji": "☀️", "meaning": "ความสำเร็จ ผลตอบแทนสดใส"},
    {"name": "Judgement",          "th": "การตัดสิน",     "emoji": "🎺", "meaning": "ถึงเวลาตัดสินใจครั้งสำคัญ"},
    {"name": "The World",          "th": "โลก",           "emoji": "🌍", "meaning": "สำเร็จครบถ้วน จบรอบสมบูรณ์"},
    {"name": "The Tower",          "th": "หอคอย",         "emoji": "⚡", "meaning": "เปลี่ยนแปลงฉับพลัน ระวังความเสี่ยง"},
    {"name": "The Devil",          "th": "ปีศาจ",         "emoji": "😈", "meaning": "ระวังความโลภ อย่าตกใจขายหมู"},
    {"name": "Death",              "th": "ความตาย",       "emoji": "💀", "meaning": "เปลี่ยนแปลงครั้งใหญ่ ยุคใหม่มา"},
    {"name": "Temperance",         "th": "ความพอดี",      "emoji": "🏺", "meaning": "สมดุล อย่า FOMO อย่า Panic"},
]

# ============================================================
# ฟังก์ชันวิเคราะห์หุ้น
# ============================================================
def calc_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = -delta.clip(upper=0).rolling(period).mean()
    rs    = gain / loss
    return 100 - (100 / (1 + rs))

def calc_atr(high, low, close, period=14):
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def calc_bollinger(series, period=20):
    ma = series.rolling(period).mean()
    return ma + 2*series.rolling(period).std(), ma - 2*series.rolling(period).std()

def get_support_resistance_levels(df):
    """คำนวณแนวรับ-แนวต้านหลายระดับ"""
    price = df["Close"].iloc[-1]
    atr   = calc_atr(df["High"], df["Low"], df["Close"]).iloc[-1]

    # Pivot points
    high  = df["High"].tail(20).max()
    low   = df["Low"].tail(20).min()
    pivot = (high + low + df["Close"].iloc[-1]) / 3

    r1 = round(2 * pivot - low,  2)
    r2 = round(pivot + (high - low), 2)
    r3 = round(high + 2 * (pivot - low), 2)
    s1 = round(2 * pivot - high, 2)
    s2 = round(pivot - (high - low), 2)
    s3 = round(low - 2 * (high - pivot), 2)

    resistances = sorted([r for r in [r1, r2, r3] if r > price])
    supports    = sorted([s for s in [s1, s2, s3] if s < price], reverse=True)

    return resistances[:3], supports[:3]

def get_elliott_wave(df):
    """วิเคราะห์ Elliott Wave แบบง่าย"""
    close  = df["Close"].tail(50)
    recent = close.tail(10)
    mid    = close.tail(30)

    trend_long  = "ขาขึ้น" if close.iloc[-1] > close.iloc[0]  else "ขาลง"
    trend_short = "ขาขึ้น" if recent.iloc[-1] > recent.iloc[0] else "ขาลง"

    # นับคลื่น
    changes = close.diff().dropna()
    waves   = []
    current = 0
    for c in changes:
        if c > 0:
            if current <= 0: waves.append(current); current = c
            else: current += c
        else:
            if current >= 0: waves.append(current); current = c
            else: current += c
    waves = [w for w in waves if w != 0][-5:]

    if len(waves) >= 3:
        if waves[-1] > 0 and waves[-2] < 0 and waves[-3] > 0:
            wave_pos  = "Wave 5 (คลื่นสุดท้ายของขาขึ้น — ระวังพลิก)"
            wave_emoji = "⚠️"
        elif waves[-1] < 0 and waves[-2] > 0:
            wave_pos  = "Wave C (แก้ไขลงมา — รอจังหวะซื้อ)"
            wave_emoji = "🔄"
        elif waves[-1] > 0 and waves[-2] < 0:
            wave_pos  = "Wave 3 (คลื่นแรงที่สุด — โอกาสทำกำไร)"
            wave_emoji = "🚀"
        else:
            wave_pos  = "Wave 1-2 (เริ่มต้นรอบใหม่ — ช่วงสะสม)"
            wave_emoji = "🌱"
    else:
        wave_pos  = "ไม่พอข้อมูล"
        wave_emoji = "❓"

    return {
        "trend_long" : trend_long,
        "trend_short": trend_short,
        "wave_pos"   : wave_pos,
        "wave_emoji" : wave_emoji,
    }

def get_stock_data(symbol, is_crypto=False):
    try:
        df = yf.Ticker(symbol).history(period="3mo")
        if df.empty:
            return None

        df["RSI"]  = calc_rsi(df["Close"])
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()
        df["ATR"]  = calc_atr(df["High"], df["Low"], df["Close"])
        df["BB_upper"], df["BB_lower"] = calc_bollinger(df["Close"])

        price      = df["Close"].iloc[-1]
        prev_price = df["Close"].iloc[-2]
        rsi        = df["RSI"].iloc[-1]
        ma20       = df["MA20"].iloc[-1]
        ma50       = df["MA50"].iloc[-1]
        atr        = df["ATR"].iloc[-1]
        bb_upper   = df["BB_upper"].iloc[-1]
        bb_lower   = df["BB_lower"].iloc[-1]
        change_pct = ((price - prev_price) / prev_price) * 100

        resistances, supports = get_support_resistance_levels(df)
        elliott = get_elliott_wave(df)

        # BUY/WAIT/SELL
        if rsi <= 40 and price <= bb_lower:
            signal = "🟢 ซื้อ"; signal_en = "BUY"
            entry  = round(price, 2)
            sl     = round(price - atr * 1.5, 2)
            # TP แบบขั้นบันได 4 ระดับ
            tp1 = round(price + atr * 1.0, 2)
            tp2 = round(price + atr * 2.0, 2)
            tp3 = round(price + atr * 3.0, 2)
            tp4 = round(price + atr * 4.5, 2)
            desc = "ราคาต่ำเกินจริง — จังหวะสะสมที่ดี"
            cls  = "signal-buy"
        elif rsi >= 70 and price >= bb_upper:
            signal = "🔴 ขาย"; signal_en = "SELL"
            entry  = round(price, 2)
            sl     = round(price - atr * 1.5, 2)
            tp1 = round(price + atr * 0.5, 2)
            tp2 = round(price + atr * 1.0, 2)
            tp3 = round(price + atr * 1.5, 2)
            tp4 = round(price + atr * 2.0, 2)
            desc = "ราคาสูงเกินไป — ถ้าถืออยู่ควรขายทำกำไร"
            cls  = "signal-sell"
        else:
            signal = "🟡 รอดูก่อน"; signal_en = "WAIT"
            entry  = round(bb_lower, 2)
            sl     = round(bb_lower - atr * 1.5, 2)
            tp1 = round(bb_lower + atr * 1.0, 2)
            tp2 = round(bb_lower + atr * 2.0, 2)
            tp3 = round(bb_lower + atr * 3.0, 2)
            tp4 = round(bb_upper, 2)
            desc = "ยังไม่ถึงจังหวะที่ดี — รอราคาลงมาก่อน"
            cls  = "signal-wait"

        d = 6 if is_crypto and price < 0.01 else (4 if is_crypto and price < 1 else 2)

        return {
            "symbol": symbol, "price": round(price, d),
            "change_pct": round(change_pct, 2), "arrow": "▲" if change_pct >= 0 else "▼",
            "rsi": round(rsi, 2),
            "rsi_signal": "สูงเกินไป" if rsi >= 70 else ("ต่ำเกินไป" if rsi <= 30 else "ปกติ"),
            "ma20": round(ma20, d), "ma50": round(ma50, d),
            "ma_signal": "แนวโน้มขาขึ้น ☀️" if ma20 > ma50 else "แนวโน้มขาลง 📉",
            "signal": signal, "signal_en": signal_en, "desc": desc, "cls": cls,
            "entry": round(entry, d), "sl": round(sl, d),
            "tp1": round(tp1, d), "tp2": round(tp2, d),
            "tp3": round(tp3, d), "tp4": round(tp4, d),
            "resistances": resistances, "supports": supports,
            "elliott": elliott, "is_crypto": is_crypto,
            "close_series": df["Close"],
        }
    except Exception as e:
        st.error(f"❌ ดึงข้อมูลไม่ได้: {e}")
        return None

# ============================================================
# ฟังก์ชันโพล: หุ้นน่าสนใจ อัปเดตรายชั่วโมง
# ============================================================
WATCHLIST = {
    "หุ้นสหรัฐ": ["NVDA", "AAPL", "TSLA", "META", "AMD", "MSFT", "AMZN", "GOOGL"],
    "Crypto":    ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD"],
    "หุ้นไทย":  ["CPALL.BK", "PTT.BK", "SCB.BK", "KBANK.BK", "AOT.BK"],
}

@st.cache_data(ttl=3600)
def get_hot_picks(category):
    """ดึงข้อมูลหุ้นน่าสนใจ อัปเดตทุก 1 ชั่วโมง"""
    symbols = WATCHLIST.get(category, [])
    results = []
    for sym in symbols:
        try:
            df = yf.Ticker(sym).history(period="5d")
            if df.empty or len(df) < 2:
                continue
            price      = df["Close"].iloc[-1]
            prev       = df["Close"].iloc[-2]
            change_pct = ((price - prev) / prev) * 100
            vol_avg    = df["Volume"].mean()
            vol_now    = df["Volume"].iloc[-1]
            vol_ratio  = vol_now / vol_avg if vol_avg > 0 else 1
            rsi_s      = calc_rsi(df["Close"])
            rsi_v      = rsi_s.iloc[-1] if not rsi_s.isna().all() else 50

            # Score: ราคาขึ้น + Volume สูง + RSI ไม่ Overbought
            score = 0
            if change_pct > 0:    score += 2
            if vol_ratio > 1.5:   score += 2
            if 30 <= rsi_v <= 60: score += 2
            if change_pct > 2:    score += 1
            if vol_ratio > 2:     score += 1

            results.append({
                "symbol": sym, "price": round(price, 2),
                "change_pct": round(change_pct, 2),
                "rsi": round(rsi_v, 1),
                "vol_ratio": round(vol_ratio, 1),
                "score": score,
            })
        except:
            continue

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:5]

# ============================================================
# ฟังก์ชันดาว
# ============================================================
def get_zodiac(lon_deg):
    signs = [("Aries","เมษ"),("Taurus","พฤษภ"),("Gemini","เมถุน"),("Cancer","กรกฎ"),
             ("Leo","สิงห์"),("Virgo","กันย์"),("Libra","ตุลย์"),("Scorpio","พิจิก"),
             ("Sagittarius","ธนู"),("Capricorn","มกร"),("Aquarius","กุมภ์"),("Pisces","มีน")]
    return signs[int(lon_deg // 30) % 12]

def get_planets(date_utc):
    bkk = ephem.Observer()
    bkk.lat, bkk.lon, bkk.elevation = "13.75", "100.517", 0
    bkk.date = date_utc
    result = {}
    for name, obj in {"Sun": ephem.Sun(), "Moon": ephem.Moon(), "Mercury": ephem.Mercury(),
                      "Venus": ephem.Venus(), "Mars": ephem.Mars(),
                      "Jupiter": ephem.Jupiter(), "Saturn": ephem.Saturn()}.items():
        obj.compute(bkk)
        lon = math.degrees(ephem.Ecliptic(obj).lon) % 360
        en, th = get_zodiac(lon)
        result[name] = {"lon": round(lon, 1), "en": en, "th": th}
    return result

def get_astro_today():
    pos = get_planets(datetime.now() - timedelta(hours=7))
    return "\n".join([f"{n:8s} → ราศี{d['th']} / {d['en']} ({d['lon']}°)" for n, d in pos.items()]), pos

def get_birth_sign(birth_str):
    try:
        pos = get_planets(datetime.strptime(birth_str, "%d/%m/%Y") - timedelta(hours=7))
        return pos["Sun"]["en"], pos["Sun"]["th"]
    except:
        return None, None

def get_weekly():
    now = datetime.now(); monday = now - timedelta(days=now.weekday())
    days = ["จันทร์","อังคาร","พุธ","พฤหัส","ศุกร์","เสาร์","อาทิตย์"]
    fire_air = ["Aries","Leo","Sagittarius","Gemini","Libra","Aquarius"]
    result = []
    for i in range(7):
        day = monday + timedelta(days=i)
        pos = get_planets(day - timedelta(hours=7))
        score = sum([pos["Mercury"]["en"] in fire_air, pos["Moon"]["en"] in fire_air, day.weekday() in [0,3,4]])
        result.append({"date": day.strftime("%d/%m"), "day": days[i],
                       "verdict": "🟢 ดีมาก" if score>=3 else ("🟡 พอใช้" if score==2 else "🔴 ระวัง"),
                       "moon": pos["Moon"]["en"], "is_today": day.date()==now.date()})
    return result

# ============================================================
# Gemini
# ============================================================
def analyze(stock, astro_str, sign_th, sign_en, weekly, birth, tarot_cards, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    weekly_str = "\n".join([f"  {d['date']} ({d['day']}) → {d['verdict']}" for d in weekly])
    tarot_str  = "\n".join([f"  {c['emoji']} {c['role']}: {c['name']} ({c['th']}) — {c['meaning']}" for c in tarot_cards])
    asset      = "Crypto" if stock["is_crypto"] else "หุ้น"
    birth_info = f"วันเกิด: {birth} | ราศี: {sign_th} ({sign_en})" if sign_th else "ไม่ได้ระบุวันเกิด"

    prompt = f"""คุณคือ AstroTrade AI นักวิเคราะห์ที่เท่ พูดภาษาไทยเข้าใจง่าย สำหรับนักลงทุนทั่วไป (ไม่เล่น Short/Margin)

{asset}: {stock['symbol']} | ราคา: {stock['price']} ({stock['arrow']}{abs(stock['change_pct'])}%)
RSI: {stock['rsi']} ({stock['rsi_signal']}) | {stock['ma_signal']}
Elliott Wave: {stock['elliott']['wave_emoji']} {stock['elliott']['wave_pos']}
สัญญาณ: {stock['signal']} — {stock['desc']}
ราคาเป้าหมาย: TP1={stock['tp1']} | TP2={stock['tp2']} | TP3={stock['tp3']} | TP4={stock['tp4']}
ตัดขาดทุน: {stock['sl']}
แนวต้าน: {stock['resistances']} | แนวรับ: {stock['supports']}

ไพ่ยิปซี: {tarot_str}
ดาววันนี้: {astro_str}
{birth_info}
วันดี/ร้าย: {weekly_str}

วิเคราะห์:
1. 📊 ภาพรวมหุ้นตอนนี้เป็นยังไง
2. 🌊 Elliott Wave บอกอะไร ควรทำอะไร
3. 🎯 ควรซื้อที่ไหน ขายทำกำไรเป็นขั้นๆ ที่ไหนบ้าง ตัดขาดทุนที่ไหน
4. 🃏 ไพ่ยิปซี 3 ใบบอกอะไรเกี่ยวกับหุ้นนี้
5. 🪐 ดาวและดวงชะตาเข้ากับหุ้นนี้ไหม (สนุกๆ)
6. 📅 วันไหนในสัปดาห์นี้เหมาะซื้อที่สุด
7. ✨ คำคมปิดท้าย AstroTrade

ตอบภาษาไทย สนุก เข้าใจง่าย"""

    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return f"❌ Gemini error: {e}"

# ============================================================
# UI: โพล Hot Picks
# ============================================================
st.markdown("<div class='section-header'>🔥 Hot Picks — อัปเดตรายชั่วโมง</div>", unsafe_allow_html=True)
poll_cat = st.radio("เลือกกลุ่ม", ["หุ้นสหรัฐ", "Crypto", "หุ้นไทย"], horizontal=True, key="poll_cat")

with st.spinner("📡 กำลังสแกนตลาด..."):
    hot = get_hot_picks(poll_cat)

if hot:
    updated_time = datetime.now().strftime("%H:%M")
    st.caption(f"⏱ อัปเดตล่าสุด: {updated_time} น. (รีเฟรชทุก 1 ชม.)")
    for i, s in enumerate(hot):
        rank_emoji = ["🥇","🥈","🥉","4️⃣","5️⃣"][i]
        clr = "#00e676" if s["change_pct"] >= 0 else "#ff5252"
        bar_pct = min(int((s["score"] / 8) * 100), 100)
        st.markdown(f"""
        <div class="poll-card">
            <div style='display:flex;justify-content:space-between;align-items:center'>
                <div>
                    <span style='font-size:1.2em'>{rank_emoji}</span>
                    <b style='font-size:1.05em;margin-left:8px'>{s['symbol']}</b>
                    <span style='color:#888;font-size:0.85em;margin-left:8px'>RSI {s['rsi']}</span>
                </div>
                <div style='text-align:right'>
                    <b style='font-size:1.1em'>{s['price']}</b><br>
                    <span style='color:{clr};font-size:0.9em'>{'▲' if s['change_pct']>=0 else '▼'}{abs(s['change_pct'])}%</span>
                    <span style='color:#888;font-size:0.8em'> Vol×{s['vol_ratio']}</span>
                </div>
            </div>
            <div class="poll-bar-bg">
                <div style='width:{bar_pct}%;height:8px;border-radius:20px;
                    background:linear-gradient(90deg,#7c4dff,#e040fb)'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ============================================================
# UI: วิเคราะห์หุ้น
# ============================================================
st.markdown("<div class='section-header'>🔮 วิเคราะห์หุ้น</div>", unsafe_allow_html=True)

asset_type = st.radio("เลือกประเภทสินทรัพย์", ["📈 หุ้น (Stock)", "🪙 Crypto"], horizontal=True)
is_crypto  = asset_type == "🪙 Crypto"

if is_crypto:
    c1, c2 = st.columns(2)
    with c1: sel = st.selectbox("🪙 เลือก Crypto", list(CRYPTO_LIST.keys()))
    with c2: manual = st.text_input("หรือพิมพ์เอง", placeholder="เช่น SOL-USD") if CRYPTO_LIST[sel] == "CUSTOM" else st.empty()
    symbol = manual.upper().strip() if CRYPTO_LIST[sel] == "CUSTOM" else CRYPTO_LIST[sel]
else:
    c1, c2 = st.columns(2)
    with c1: sel = st.selectbox("📈 เลือกหุ้น", list(STOCK_LIST.keys()))
    with c2: manual = st.text_input("หรือพิมพ์เอง", placeholder="เช่น NVDA") if STOCK_LIST[sel] == "CUSTOM" else st.empty()
    symbol = manual.upper().strip() if STOCK_LIST[sel] == "CUSTOM" else STOCK_LIST[sel]

birth = st.text_input("🎂 วันเกิด (ไม่บังคับ)", placeholder="DD/MM/YYYY เช่น 15/06/1990")

# ============================================================
# UI: เลือกไพ่ยิปซี
# ============================================================
st.markdown("<div class='section-header'>🃏 เลือกไพ่ยิปซี 3 ใบ</div>", unsafe_allow_html=True)
st.caption("กดเลือกไพ่ที่ใจสั่ง 3 ใบ แล้วค่อยวิเคราะห์")

if "selected_tarot" not in st.session_state:
    st.session_state.selected_tarot = []

cols_per_row = 5
for row_start in range(0, len(TAROT_CARDS), cols_per_row):
    row_cards = TAROT_CARDS[row_start:row_start+cols_per_row]
    cols      = st.columns(cols_per_row)
    for col, card in zip(cols, row_cards):
        with col:
            is_sel = card["name"] in [c["name"] for c in st.session_state.selected_tarot]
            border = "2px solid #e040fb" if is_sel else "1px solid rgba(224,64,251,0.3)"
            bg     = "rgba(224,64,251,0.2)" if is_sel else "rgba(124,77,255,0.1)"
            glow   = "0 0 20px rgba(224,64,251,0.6)" if is_sel else "none"
            st.markdown(f"""
            <div style='background:{bg};border:{border};border-radius:12px;
                        padding:8px 4px;text-align:center;box-shadow:{glow}'>
                <div style='font-size:1.5em'>{card['emoji']}</div>
                <div style='font-size:0.65em;color:#ce93d8'>{card['th']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("✓" if is_sel else "＋", key=f"tarot_{card['name']}", use_container_width=True):
                if is_sel:
                    st.session_state.selected_tarot = [c for c in st.session_state.selected_tarot if c["name"] != card["name"]]
                elif len(st.session_state.selected_tarot) < 3:
                    st.session_state.selected_tarot.append(card)
                st.rerun()

# แสดงไพ่ที่เลือก
if st.session_state.selected_tarot:
    roles = ["สถานการณ์ปัจจุบัน", "แนวโน้มระยะสั้น", "คำแนะนำ"]
    sel_with_role = [{"role": roles[i], **c} for i, c in enumerate(st.session_state.selected_tarot)]
    st.markdown(f"<div style='color:#e040fb;font-size:0.9em'>✓ เลือกแล้ว {len(st.session_state.selected_tarot)}/3 ใบ</div>", unsafe_allow_html=True)
    tc = st.columns(3)
    for i, card in enumerate(sel_with_role):
        with tc[i]:
            st.markdown(f"""
            <div class="tarot-card" style='border:2px solid #e040fb;box-shadow:0 0 20px rgba(224,64,251,0.4)'>
                <div style='font-size:1.8em'>{card['emoji']}</div>
                <div style='color:#ce93d8;font-size:0.7em'>{card['role']}</div>
                <div style='font-family:Playfair Display,serif;color:#fff;font-weight:700;font-size:0.85em'>{card['th']}</div>
                <div style='color:#9e9e9e;font-size:0.7em;margin-top:4px'>{card['meaning']}</div>
            </div>
            """, unsafe_allow_html=True)

# ปุ่มวิเคราะห์
st.markdown("<br>", unsafe_allow_html=True)
run = st.button("✦ ANALYZE WITH ASTROTRADE ✦", use_container_width=True)

if run:
    if not gemini_key:
        st.warning("⚠️ ใส่ Gemini API Key ที่ sidebar ก่อนนะครับ")
    elif not symbol:
        st.warning("⚠️ เลือกหรือพิมพ์ชื่อสินทรัพย์ด้วยครับ")
    elif len(st.session_state.selected_tarot) < 3:
        st.warning(f"⚠️ เลือกไพ่ยิปซีให้ครบ 3 ใบก่อนนะครับ (เลือกแล้ว {len(st.session_state.selected_tarot)} ใบ)")
    else:
        roles = ["สถานการณ์ปัจจุบัน", "แนวโน้มระยะสั้น", "คำแนะนำ"]
        tarot_cards = [{"role": roles[i], **c} for i, c in enumerate(st.session_state.selected_tarot)]

        with st.spinner(f"✨ ดึงข้อมูล {symbol}..."):
            stock = get_stock_data(symbol, is_crypto)

        if not stock:
            st.error(f"❌ ไม่พบ '{symbol}'")
        else:
            st.markdown(f"<div class='section-header'>{'🪙' if is_crypto else '📊'} {stock['symbol']}</div>", unsafe_allow_html=True)
            st.line_chart(stock["close_series"])

            m1, m2, m3 = st.columns(3)
            m1.metric("ราคาปัจจุบัน", stock["price"], f"{stock['arrow']}{abs(stock['change_pct'])}%")
            m2.metric("RSI", stock["rsi"], stock["rsi_signal"])
            m3.metric("แนวโน้ม", stock["ma_signal"])

            # Elliott Wave
            ew = stock["elliott"]
            st.markdown(f"""
            <div class="glass-card">
                <div style='font-size:1em;color:#ce93d8;font-weight:600'>🌊 Elliott Wave Analysis</div>
                <div style='font-size:1.3em;margin:6px 0'>{ew['wave_emoji']} <b>{ew['wave_pos']}</b></div>
                <div style='color:#888;font-size:0.85em'>แนวโน้มระยะยาว: {ew['trend_long']} | ระยะสั้น: {ew['trend_short']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Signal Box + TP ขั้นบันได
            clr_map = {"BUY": "#00e676", "SELL": "#ff1744", "WAIT": "#ffa000"}
            clr = clr_map.get(stock["signal_en"], "#ffa000")
            st.markdown(f"""
            <div class="{stock['cls']}">
                <div style='font-family:Playfair Display,serif;font-size:1.8em;color:{clr};font-weight:900;margin-bottom:4px'>
                    {stock['signal']}
                </div>
                <div style='color:#aaa;font-size:0.88em;margin-bottom:14px'>{stock['desc']}</div>
                <table style='width:100%;color:#eee;font-size:0.92em'>
                    <tr><td style='padding:5px 0'>🎯 เป้าหมาย TP1 (ระยะสั้น)</td><td style='text-align:right'><b style='color:#69f0ae'>{stock['tp1']}</b></td></tr>
                    <tr><td style='padding:5px 0'>🎯 เป้าหมาย TP2</td><td style='text-align:right'><b style='color:#40c4ff'>{stock['tp2']}</b></td></tr>
                    <tr><td style='padding:5px 0'>🎯 เป้าหมาย TP3</td><td style='text-align:right'><b style='color:#e040fb'>{stock['tp3']}</b></td></tr>
                    <tr><td style='padding:5px 0'>🎯 เป้าหมาย TP4 (ระยะยาว)</td><td style='text-align:right'><b style='color:#FFD700'>{stock['tp4']}</b></td></tr>
                    <tr><td style='padding:5px 0'>🛑 ราคาตัดขาดทุน</td><td style='text-align:right'><b style='color:#ff6b6b'>{stock['sl']}</b></td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

            # แนวรับ-แนวต้านหลายระดับ
            st.markdown("<div class='section-header'>📐 แนวรับ — แนวต้าน</div>", unsafe_allow_html=True)
            lc, rc = st.columns(2)
            with lc:
                st.markdown("<div style='color:#ff5252;font-weight:600;margin-bottom:6px'>🔴 แนวต้าน (Resistance)</div>", unsafe_allow_html=True)
                for i, r in enumerate(stock["resistances"]):
                    st.markdown(f"<div style='background:rgba(255,82,82,0.1);border:1px solid rgba(255,82,82,0.3);border-radius:8px;padding:8px 12px;margin:4px 0;color:#ff8a80'>R{i+1}: <b>{r}</b></div>", unsafe_allow_html=True)
            with rc:
                st.markdown("<div style='color:#69f0ae;font-weight:600;margin-bottom:6px'>🔵 แนวรับ (Support)</div>", unsafe_allow_html=True)
                for i, s in enumerate(stock["supports"]):
                    st.markdown(f"<div style='background:rgba(105,240,174,0.1);border:1px solid rgba(105,240,174,0.3);border-radius:8px;padding:8px 12px;margin:4px 0;color:#69f0ae'>S{i+1}: <b>{s}</b></div>", unsafe_allow_html=True)

            # ดาว
            with st.spinner("🔭 คำนวณดาว..."):
                astro_str, _ = get_astro_today()
            with st.expander("🪐 ตำแหน่งดาววันนี้"):
                st.code(astro_str)

            # ดวงชะตา
            sign_en, sign_th = get_birth_sign(birth) if birth else (None, None)
            if sign_th:
                st.markdown(f"""
                <div class="glass-card" style='text-align:center'>
                    <div style='font-family:Playfair Display,serif;color:#FFD700;font-size:1.1em;font-weight:700'>♈ ราศีเกิดของคุณ</div>
                    <div style='font-size:1.8em;font-weight:900;background:linear-gradient(90deg,#FFD700,#FFA500);-webkit-background-clip:text;-webkit-text-fill-color:transparent'>{sign_th} ({sign_en})</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                sign_en, sign_th = "Unknown", "ไม่ทราบ"

            # วันดี/วันร้าย
            st.markdown("<div class='section-header'>📅 วันดี/วันร้ายสัปดาห์นี้</div>", unsafe_allow_html=True)
            weekly = get_weekly()
            cols   = st.columns(7)
            for i, d in enumerate(weekly):
                with cols[i]:
                    style = "color:#e040fb;font-weight:700" if d["is_today"] else "color:#aaa"
                    st.markdown(f"<div style='{style};font-size:0.78em;text-align:center'>{'📍' if d['is_today'] else ''}{d['day']}<br><span style='font-size:0.85em'>{d['date']}</span><br>{d['verdict']}</div>", unsafe_allow_html=True)

            # AI วิเคราะห์
            st.markdown("<div class='section-header'>✨ AstroTrade AI Analysis</div>", unsafe_allow_html=True)
            with st.spinner("✨ กำลังอ่านดวงและวิเคราะห์ตลาด..."):
                result = analyze(stock, astro_str, sign_th, sign_en, weekly, birth, tarot_cards, gemini_key)
            st.markdown(f"<div class='glass-card'>{result}</div>", unsafe_allow_html=True)

            st.divider()
            st.markdown("""
            <div class="footer-text">
                ✦ ASTROTRADE 2025 ✦ WHERE THE STARS MEET THE MARKET 🌌<br>
                <span style='font-size:0.85em'>เป็นข้อมูลประกอบการตัดสินใจเท่านั้น ไม่ใช่คำแนะนำทางการเงิน</span>
            </div>
            """, unsafe_allow_html=True)
