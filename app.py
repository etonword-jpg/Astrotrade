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
# CSS: Neon Dark + Glassmorphism + Google Fonts (Glam)
# ============================================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Space+Grotesk:wght@300;400;600;700&display=swap" rel="stylesheet">

<style>
    /* Base */
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        background-color: #080810;
        color: #e8e8f0;
    }

    /* Background gradient */
    .stApp {
        background: radial-gradient(ellipse at top left, #1a0533 0%, #080810 50%, #001a33 100%);
        min-height: 100vh;
    }

    /* Brand */
    .brand-wrap {
        text-align: center;
        padding: 20px 0 8px 0;
    }
    .brand-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.2em;
        font-weight: 900;
        background: linear-gradient(135deg, #fff 0%, #e040fb 40%, #7c4dff 70%, #40c4ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 6px;
        text-transform: uppercase;
        filter: drop-shadow(0 0 20px rgba(224, 64, 251, 0.5));
    }
    .brand-sub {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 300;
        color: #b39ddb;
        font-size: 0.9em;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-top: -4px;
    }
    .brand-line {
        width: 80px; height: 2px;
        background: linear-gradient(90deg, transparent, #e040fb, #7c4dff, transparent);
        margin: 12px auto;
    }

    /* Glass card */
    .glass-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(224,64,251,0.2);
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 30px rgba(124,77,255,0.1), inset 0 0 30px rgba(255,255,255,0.02);
    }

    /* Signal box */
    .signal-buy {
        background: rgba(0,230,118,0.08);
        border: 1px solid rgba(0,230,118,0.4);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 0 20px rgba(0,230,118,0.15);
    }
    .signal-sell {
        background: rgba(255,23,68,0.08);
        border: 1px solid rgba(255,23,68,0.4);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 0 20px rgba(255,23,68,0.15);
    }
    .signal-wait {
        background: rgba(255,160,0,0.08);
        border: 1px solid rgba(255,160,0,0.4);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 0 20px rgba(255,160,0,0.15);
    }

    /* Tarot card */
    .tarot-card {
        background: linear-gradient(145deg, rgba(124,77,255,0.15), rgba(224,64,251,0.08));
        border: 1px solid rgba(224,64,251,0.3);
        border-radius: 16px;
        padding: 16px 10px;
        text-align: center;
        box-shadow: 0 0 20px rgba(124,77,255,0.2);
        transition: transform 0.2s;
    }

    /* Section header */
    .section-header {
        font-family: 'Playfair Display', serif;
        font-size: 1.3em;
        font-weight: 700;
        background: linear-gradient(90deg, #e040fb, #7c4dff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
        margin: 20px 0 10px 0;
    }

    /* Metric override */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(124,77,255,0.2);
        border-radius: 12px;
        padding: 12px;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #7c4dff, #e040fb) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1em !important;
        letter-spacing: 2px !important;
        padding: 14px !important;
        box-shadow: 0 0 25px rgba(224,64,251,0.4) !important;
        transition: all 0.3s !important;
    }
    .stButton > button:hover {
        box-shadow: 0 0 40px rgba(224,64,251,0.7) !important;
        transform: translateY(-2px) !important;
    }

    /* Input */
    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(124,77,255,0.3) !important;
        border-radius: 12px !important;
        color: #e8e8f0 !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    /* Radio */
    .stRadio > div {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 8px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(8,8,16,0.95) !important;
        border-right: 1px solid rgba(124,77,255,0.2) !important;
    }

    /* Divider */
    hr { border-color: rgba(124,77,255,0.2) !important; }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 12px !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    /* Footer */
    .footer-text {
        text-align: center;
        color: #5c5c7a;
        font-size: 0.78em;
        letter-spacing: 1px;
        padding: 10px 0;
    }

    /* Neon glow tag */
    .neon-tag {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.75em;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .neon-green { background: rgba(0,230,118,0.15); color: #00e676; border: 1px solid #00e676; }
    .neon-red   { background: rgba(255,23,68,0.15);  color: #ff1744; border: 1px solid #ff1744; }
    .neon-gold  { background: rgba(255,214,0,0.15);  color: #ffd600; border: 1px solid #ffd600; }
    .neon-purple{ background: rgba(124,77,255,0.15); color: #7c4dff; border: 1px solid #7c4dff; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="brand-wrap">
    <div class="brand-title">✦ AstroTrade</div>
    <div class="brand-line"></div>
    <div class="brand-sub">Where the Stars Meet the Market</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.markdown("<div style='font-family:Playfair Display,serif;font-size:1.3em;color:#e040fb;letter-spacing:2px'>⚙ SETTINGS</div>", unsafe_allow_html=True)
    gemini_key = st.text_input("🔑 Gemini API Key", type="password", placeholder="AIza...")
    st.divider()
    st.markdown("<div style='color:#b39ddb;font-size:0.85em;letter-spacing:1px'>HOW TO USE</div>", unsafe_allow_html=True)
    st.markdown("1. ใส่ Gemini API Key")
    st.markdown("2. เลือกประเภท: หุ้น / Crypto")
    st.markdown("3. เลือกหรือพิมพ์ชื่อ")
    st.markdown("4. ใส่วันเกิด")
    st.markdown("5. กด **วิเคราะห์**")
    st.divider()
    st.markdown("<div style='color:#5c5c7a;font-size:0.75em;text-align:center'>✦ AstroTrade 2025<br>ไม่ใช่คำแนะนำทางการเงิน</div>", unsafe_allow_html=True)

# ============================================================
# รายการ Crypto และหุ้น
# ============================================================
CRYPTO_LIST = {
    "-- พิมพ์เอง --": "", "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD", "Solana (SOL)": "SOL-USD",
    "XRP": "XRP-USD", "BNB": "BNB-USD", "Dogecoin (DOGE)": "DOGE-USD",
    "Cardano (ADA)": "ADA-USD", "Avalanche (AVAX)": "AVAX-USD",
    "Chainlink (LINK)": "LINK-USD", "Polkadot (DOT)": "DOT-USD",
    "Shiba Inu (SHIB)": "SHIB-USD", "Pepe (PEPE)": "PEPE-USD",
    "Sui (SUI)": "SUI-USD",
}

STOCK_LIST = {
    "-- พิมพ์เอง --": "", "NVIDIA": "NVDA", "Apple": "AAPL",
    "Tesla": "TSLA", "Microsoft": "MSFT", "Meta": "META",
    "Amazon": "AMZN", "Google": "GOOGL", "AMD": "AMD",
    "CPALL (ไทย)": "CPALL.BK", "PTT (ไทย)": "PTT.BK",
    "SCB (ไทย)": "SCB.BK", "KBANK (ไทย)": "KBANK.BK",
}

# ============================================================
# ไพ่ Tarot
# ============================================================
TAROT_CARDS = [
    {"name": "The Fool", "th": "คนโง่เขลา", "emoji": "🃏", "meaning": "จุดเริ่มต้นใหม่ โอกาสที่ไม่คาดคิด"},
    {"name": "The Magician", "th": "นักมายากล", "emoji": "🎩", "meaning": "มีทักษะและพลัง พร้อมลงมือทำ"},
    {"name": "The High Priestess", "th": "นักบวชหญิง", "emoji": "🌙", "meaning": "ใช้สัญชาตญาณ รอเวลาที่เหมาะสม"},
    {"name": "The Empress", "th": "จักรพรรดินี", "emoji": "👑", "meaning": "ความอุดมสมบูรณ์ ผลตอบแทนดี"},
    {"name": "The Emperor", "th": "จักรพรรดิ", "emoji": "⚔️", "meaning": "ความมั่นคง มีโครงสร้างที่แข็งแกร่ง"},
    {"name": "The Lovers", "th": "คู่รัก", "emoji": "💕", "meaning": "ต้องตัดสินใจเลือก จุดเปลี่ยนสำคัญ"},
    {"name": "The Chariot", "th": "รถศึก", "emoji": "🏆", "meaning": "ชัยชนะ ก้าวหน้าอย่างแข็งแกร่ง"},
    {"name": "Strength", "th": "ความแข็งแกร่ง", "emoji": "🦁", "meaning": "ใจเย็น ควบคุมสถานการณ์ได้"},
    {"name": "The Hermit", "th": "ฤๅษี", "emoji": "🏮", "meaning": "ใคร่ครวญก่อน อย่าเร่งรีบ"},
    {"name": "Wheel of Fortune", "th": "วงล้อโชคชะตา", "emoji": "🎡", "meaning": "โชคกำลังเปลี่ยน จังหวะกำลังมา"},
    {"name": "Justice", "th": "ความยุติธรรม", "emoji": "⚖️", "meaning": "ผลลัพธ์สมเหตุสมผล ตลาดสมดุล"},
    {"name": "The Star", "th": "ดวงดาว", "emoji": "⭐", "meaning": "ความหวัง สัญญาณบวกกำลังมา"},
    {"name": "The Moon", "th": "ดวงจันทร์", "emoji": "🌕", "meaning": "ความไม่แน่นอน ระวังข้อมูลลวง"},
    {"name": "The Sun", "th": "ดวงอาทิตย์", "emoji": "☀️", "meaning": "ความสำเร็จ ผลตอบแทนสดใส"},
    {"name": "Judgement", "th": "การตัดสิน", "emoji": "🎺", "meaning": "ถึงเวลาตัดสินใจครั้งสำคัญ"},
    {"name": "The World", "th": "โลก", "emoji": "🌍", "meaning": "สำเร็จครบถ้วน จบรอบอย่างสมบูรณ์"},
    {"name": "The Tower", "th": "หอคอย", "emoji": "⚡", "meaning": "การเปลี่ยนแปลงฉับพลัน ระวังความเสี่ยง"},
    {"name": "The Devil", "th": "ปีศาจ", "emoji": "😈", "meaning": "ระวังความโลภ อย่าตกใจขายหมู"},
    {"name": "Death", "th": "ความตาย", "emoji": "💀", "meaning": "การเปลี่ยนแปลงครั้งใหญ่ ยุคใหม่กำลังมา"},
    {"name": "Temperance", "th": "ความพอดี", "emoji": "🏺", "meaning": "สมดุล อย่า FOMO อย่า Panic"},
]

def draw_tarot():
    cards = random.sample(TAROT_CARDS, 3)
    roles = ["สถานการณ์ปัจจุบัน", "แนวโน้มระยะสั้น", "คำแนะนำ"]
    return [{"role": roles[i], **cards[i]} for i in range(3)]

# ============================================================
# ฟังก์ชันดึงข้อมูลหุ้น
# ============================================================
def calc_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = -delta.clip(upper=0).rolling(period).mean()
    rs    = gain / loss
    return 100 - (100 / (1 + rs))

def calc_atr(high, low, close, period=14):
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low  - close.shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def calc_bollinger(series, period=20):
    ma  = series.rolling(period).mean()
    std = series.rolling(period).std()
    return ma + 2*std, ma - 2*std

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
        change     = price - prev_price
        change_pct = (change / prev_price) * 100
        support    = df["Low"].tail(20).min()
        resistance = df["High"].tail(20).max()

        if rsi <= 40 and price <= bb_lower:
            signal      = "🟢 ซื้อ"
            signal_en   = "BUY"
            entry       = round(price, 2)
            stop_loss   = round(price - atr * 1.5, 2)
            take_profit = round(price + atr * 3,   2)
            signal_desc = "ราคาต่ำเกินจริง — จังหวะสะสมที่ดี"
            signal_cls  = "signal-buy"
        elif rsi >= 70 and price >= bb_upper:
            signal      = "🔴 ขาย"
            signal_en   = "SELL"
            entry       = round(price, 2)
            stop_loss   = round(price - atr * 1.5, 2)
            take_profit = round(price + atr * 1.5, 2)
            signal_desc = "ราคาสูงเกินไปแล้ว — ถ้าถืออยู่ควรขายทำกำไร"
            signal_cls  = "signal-sell"
        else:
            signal      = "🟡 รอดูก่อน"
            signal_en   = "WAIT"
            entry       = round(bb_lower, 2)
            stop_loss   = round(bb_lower - atr * 1.5, 2)
            take_profit = round(bb_upper, 2)
            signal_desc = "ยังไม่ถึงจังหวะที่ดี — รอราคาลงมาก่อน"
            signal_cls  = "signal-wait"

        rr = round(abs(take_profit - entry) / abs(entry - stop_loss), 2) if entry != stop_loss else 0
        d  = 6 if is_crypto and price < 0.01 else (4 if is_crypto and price < 1 else 2)

        return {
            "symbol": symbol, "price": round(price, d),
            "change_pct": round(change_pct, 2), "arrow": "▲" if change >= 0 else "▼",
            "rsi": round(rsi, 2),
            "rsi_signal": "สูงเกินไป" if rsi >= 70 else ("ต่ำเกินไป" if rsi <= 30 else "ปกติ"),
            "ma20": round(ma20, d), "ma50": round(ma50, d),
            "ma_signal": "แนวโน้มขาขึ้น ☀️" if ma20 > ma50 else "แนวโน้มขาลง 📉",
            "support": round(support, d), "resistance": round(resistance, d),
            "signal": signal, "signal_en": signal_en,
            "signal_desc": signal_desc, "signal_cls": signal_cls,
            "entry": round(entry, d), "stop_loss": round(stop_loss, d),
            "take_profit": round(take_profit, d), "rr_ratio": rr,
            "is_crypto": is_crypto, "close_series": df["Close"],
        }
    except Exception as e:
        st.error(f"❌ ดึงข้อมูลไม่ได้: {e}")
        return None

# ============================================================
# ฟังก์ชันดาว
# ============================================================
def get_zodiac(lon_deg):
    signs = [
        ("Aries","เมษ"), ("Taurus","พฤษภ"), ("Gemini","เมถุน"),
        ("Cancer","กรกฎ"), ("Leo","สิงห์"), ("Virgo","กันย์"),
        ("Libra","ตุลย์"), ("Scorpio","พิจิก"), ("Sagittarius","ธนู"),
        ("Capricorn","มกร"), ("Aquarius","กุมภ์"), ("Pisces","มีน"),
    ]
    return signs[int(lon_deg // 30) % 12]

def get_planets(date_utc):
    bkk = ephem.Observer()
    bkk.lat, bkk.lon, bkk.elevation = "13.75", "100.517", 0
    bkk.date = date_utc
    result = {}
    for name, obj in {
        "Sun": ephem.Sun(), "Moon": ephem.Moon(),
        "Mercury": ephem.Mercury(), "Venus": ephem.Venus(),
        "Mars": ephem.Mars(), "Jupiter": ephem.Jupiter(),
        "Saturn": ephem.Saturn()
    }.items():
        obj.compute(bkk)
        lon = math.degrees(ephem.Ecliptic(obj).lon) % 360
        en, th = get_zodiac(lon)
        result[name] = {"lon": round(lon, 1), "en": en, "th": th}
    return result

def get_astro_today():
    pos   = get_planets(datetime.now() - timedelta(hours=7))
    lines = [f"{n:8s} → ราศี{d['th']} / {d['en']} ({d['lon']}°)" for n, d in pos.items()]
    return "\n".join(lines), pos

def get_birth_sign(birth_str):
    try:
        pos = get_planets(datetime.strptime(birth_str, "%d/%m/%Y") - timedelta(hours=7))
        return pos["Sun"]["en"], pos["Sun"]["th"]
    except:
        return None, None

def get_weekly():
    now      = datetime.now()
    monday   = now - timedelta(days=now.weekday())
    days     = ["จันทร์","อังคาร","พุธ","พฤหัส","ศุกร์","เสาร์","อาทิตย์"]
    fire_air = ["Aries","Leo","Sagittarius","Gemini","Libra","Aquarius"]
    result   = []
    for i in range(7):
        day = monday + timedelta(days=i)
        pos = get_planets(day - timedelta(hours=7))
        score = sum([
            pos["Mercury"]["en"] in fire_air,
            pos["Moon"]["en"]    in fire_air,
            day.weekday() in [0, 3, 4],
        ])
        verdict = "🟢 ดีมาก" if score >= 3 else ("🟡 พอใช้" if score == 2 else "🔴 ระวัง")
        result.append({
            "date": day.strftime("%d/%m"), "day": days[i],
            "verdict": verdict, "moon": pos["Moon"]["en"],
            "is_today": day.date() == now.date(),
        })
    return result

# ============================================================
# Gemini
# ============================================================
def analyze(stock, astro_str, sign_th, sign_en, weekly, birth, tarot_cards, api_key):
    genai.configure(api_key=api_key)
    model      = genai.GenerativeModel("gemini-1.5-flash")
    weekly_str = "\n".join([f"  {d['date']} ({d['day']}) → {d['verdict']}" for d in weekly])
    tarot_str  = "\n".join([f"  {c['emoji']} {c['role']}: {c['name']} ({c['th']}) — {c['meaning']}" for c in tarot_cards])
    asset      = "Crypto" if stock["is_crypto"] else "หุ้น"

    prompt = f"""คุณคือ AstroTrade AI — นักวิเคราะห์ที่เท่ห์ มีสไตล์ พูดภาษาไทยเข้าใจง่าย
เหมาะสำหรับคนที่ซื้อขายหุ้นปกติ (ไม่ได้เล่น Short/Margin)

=== {asset}: {stock['symbol']} ===
ราคา: {stock['price']} ({stock['arrow']}{abs(stock['change_pct'])}%)
RSI: {stock['rsi']} ({stock['rsi_signal']}) | {stock['ma_signal']}
สัญญาณ: {stock['signal']} — {stock['signal_desc']}
ราคาเป้าหมายทำกำไร: {stock['take_profit']}
ราคาตัดขาดทุน: {stock['stop_loss']}
แนวรับ: {stock['support']} | แนวต้าน: {stock['resistance']}

=== ไพ่ยิปซีวันนี้ 🃏 ===
{tarot_str}

=== ดาววันนี้ ===
{astro_str}

=== ดวงชะตา ===
วันเกิด: {birth} | ราศี: {sign_th} ({sign_en})

=== วันดี/วันร้ายสัปดาห์นี้ ===
{weekly_str}

วิเคราะห์ให้ครบ เขียนสนุก อ่านง่าย มีพลังงาน Gen-Z:
1. 📊 ตอนนี้หุ้นเป็นยังไง ควรทำอะไร
2. 🎯 ซื้อที่ราคาไหน ขายทำกำไรที่ไหน ตัดขาดทุนที่ไหน
3. 🃏 ไพ่ยิปซี 3 ใบบอกอะไรเกี่ยวกับหุ้นนี้
4. 🪐 ดาวและดวงชะตาราศี{sign_th}เข้ากับหุ้นนี้ไหม (สนุกๆ เฮฮา)
5. 📅 วันไหนในสัปดาห์นี้เหมาะซื้อที่สุด
6. ✨ คำคมปิดท้ายสไตล์ AstroTrade

ตอบภาษาไทย สนุก เข้าใจง่าย ไม่ใช้ศัพท์เทคนิคเยอะ"""

    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return f"❌ Gemini error: {e}"

# ============================================================
# UI หลัก
# ============================================================
asset_type = st.radio("เลือกประเภทสินทรัพย์", ["📈 หุ้น (Stock)", "🪙 Crypto"], horizontal=True)
is_crypto  = asset_type == "🪙 Crypto"

if is_crypto:
    c1, c2 = st.columns(2)
    with c1: sel    = st.selectbox("🪙 เลือก Crypto", list(CRYPTO_LIST.keys()))
    with c2: manual = st.text_input("หรือพิมพ์เอง", placeholder="เช่น SOL-USD")
    symbol = CRYPTO_LIST[sel] if CRYPTO_LIST[sel] else manual.upper().strip()
else:
    c1, c2 = st.columns(2)
    with c1: sel    = st.selectbox("📈 เลือกหุ้น", list(STOCK_LIST.keys()))
    with c2: manual = st.text_input("หรือพิมพ์เอง", placeholder="เช่น NVDA หรือ CPALL.BK")
    symbol = STOCK_LIST[sel] if STOCK_LIST[sel] else manual.upper().strip()

birth = st.text_input("🎂 วันเกิดของคุณ", placeholder="DD/MM/YYYY เช่น 15/06/1990")
run   = st.button("✦ ANALYZE WITH ASTROTRADE ✦", use_container_width=True)

if run:
    if not gemini_key:
        st.warning("⚠️ ใส่ Gemini API Key ที่ sidebar ก่อนนะครับ")
    elif not symbol:
        st.warning("⚠️ เลือกหรือพิมพ์ชื่อสินทรัพย์ด้วยครับ")
    elif not birth:
        st.warning("⚠️ ใส่วันเกิดด้วยนะครับ")
    else:
        with st.spinner(f"✨ กำลังดึงข้อมูล {symbol}..."):
            stock = get_stock_data(symbol, is_crypto)

        if not stock:
            st.error(f"❌ ไม่พบ '{symbol}'")
        else:
            # Header หุ้น
            st.markdown(f"<div class='section-header'>{'🪙' if is_crypto else '📊'} {stock['symbol']}</div>", unsafe_allow_html=True)
            st.line_chart(stock["close_series"])

            # Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("ราคาปัจจุบัน", stock["price"], f"{stock['arrow']}{abs(stock['change_pct'])}%")
            m2.metric("RSI", stock["rsi"], stock["rsi_signal"])
            m3.metric("แนวโน้ม", stock["ma_signal"])

            # Signal Box
            clr_map = {"BUY": "#00e676", "SELL": "#ff1744", "WAIT": "#ffa000"}
            clr = clr_map.get(stock["signal_en"], "#ffa000")
            st.markdown(f"""
            <div class="{stock['signal_cls']}">
                <div style='font-family:Playfair Display,serif;font-size:1.8em;color:{clr};font-weight:900;margin-bottom:4px'>
                    {stock['signal']} <span style='font-size:0.5em;color:#888'>{stock['signal_en']}</span>
                </div>
                <div style='color:#aaa;font-size:0.88em;margin-bottom:14px'>{stock['signal_desc']}</div>
                <table style='width:100%;color:#eee;font-family:Space Grotesk,sans-serif;font-size:0.92em'>
                    <tr>
                        <td style='padding:6px 0'>🎯 ราคาเป้าหมายทำกำไร</td>
                        <td style='text-align:right'><b style='color:#00e676;font-size:1.1em'>{stock['take_profit']}</b></td>
                    </tr>
                    <tr>
                        <td style='padding:6px 0'>🛑 ราคาตัดขาดทุน</td>
                        <td style='text-align:right'><b style='color:#ff6b6b;font-size:1.1em'>{stock['stop_loss']}</b></td>
                    </tr>
                    <tr>
                        <td style='padding:6px 0'>⚖️ อัตราความคุ้มค่า</td>
                        <td style='text-align:right'><b style='color:#ffd600'>1 : {stock['rr_ratio']}</b></td>
                    </tr>
                    <tr>
                        <td style='padding:6px 0;color:#888'>🔵 แนวรับ</td>
                        <td style='text-align:right;color:#888'>{stock['support']}</td>
                    </tr>
                    <tr>
                        <td style='padding:6px 0;color:#888'>🔴 แนวต้าน</td>
                        <td style='text-align:right;color:#888'>{stock['resistance']}</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

            # ไพ่ยิปซี
            st.markdown("<div class='section-header'>🃏 ไพ่ยิปซีวันนี้</div>", unsafe_allow_html=True)
            tarot_cards = draw_tarot()
            tc1, tc2, tc3 = st.columns(3)
            for col, card in zip([tc1, tc2, tc3], tarot_cards):
                with col:
                    st.markdown(f"""
                    <div class="tarot-card">
                        <div style='font-size:2.2em;margin-bottom:4px'>{card['emoji']}</div>
                        <div style='color:#ce93d8;font-size:0.7em;letter-spacing:1px;text-transform:uppercase'>{card['role']}</div>
                        <div style='font-family:Playfair Display,serif;color:#fff;font-weight:700;font-size:0.95em;margin:4px 0'>{card['th']}</div>
                        <div style='color:#9e9e9e;font-size:0.72em;line-height:1.4'>{card['meaning']}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # ดาว
            with st.spinner("🔭 คำนวณดาว..."):
                astro_str, _ = get_astro_today()
            with st.expander("🪐 ตำแหน่งดาววันนี้"):
                st.code(astro_str)

            # ดวงชะตา
            sign_en, sign_th = get_birth_sign(birth)
            if sign_th:
                st.markdown(f"""
                <div class="glass-card" style='text-align:center'>
                    <div style='font-size:1.5em'>♈</div>
                    <div style='font-family:Playfair Display,serif;color:#FFD700;font-size:1.2em;font-weight:700'>
                        ราศีเกิดของคุณ
                    </div>
                    <div style='font-size:1.8em;font-weight:900;
                        background:linear-gradient(90deg,#FFD700,#FFA500);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent'>
                        {sign_th} ({sign_en})
                    </div>
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
                    today_style = "color:#e040fb;font-weight:700" if d["is_today"] else "color:#aaa"
                    st.markdown(f"<div style='{today_style};font-size:0.8em;text-align:center'>{'📍' if d['is_today'] else ''}{d['day']}<br><span style='font-size:0.85em'>{d['date']}</span></div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:center;font-size:0.9em'>{d['verdict']}</div>", unsafe_allow_html=True)

            # AI
            st.markdown("<div class='section-header'>✨ AstroTrade AI Analysis</div>", unsafe_allow_html=True)
            with st.spinner("✨ กำลังอ่านดวงและวิเคราะห์ตลาด..."):
                result = analyze(stock, astro_str, sign_th, sign_en, weekly, birth, tarot_cards, gemini_key)
            st.markdown(f"<div class='glass-card'>{result}</div>", unsafe_allow_html=True)

            # Footer
            st.divider()
            st.markdown("""
            <div class="footer-text">
                ✦ ASTROTRADE 2025 ✦<br>
                WHERE THE STARS MEET THE MARKET 🌌<br>
                <span style='font-size:0.85em'>เป็นข้อมูลประกอบการตัดสินใจเท่านั้น ไม่ใช่คำแนะนำทางการเงิน</span>
            </div>
            """, unsafe_allow_html=True)
