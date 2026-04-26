import streamlit as st
import yfinance as yf
import google.generativeai as genai
import ephem
import math
import pandas as pd
import random
from datetime import datetime, timedelta

st.set_page_config(page_title="AstroTrade", page_icon="🌟", layout="centered")

st.markdown("""
<style>
.brand-title {
    font-size: 2.8em; font-weight: 900;
    background: linear-gradient(90deg, #FFD700, #FFA500);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; letter-spacing: 3px;
}
.brand-sub { text-align: center; color: #aaaacc; font-size: 0.95em; margin-top: -10px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="brand-title">✦ AstroTrade</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-sub">Where the Stars Meet the Market 🌌📈🪙</div>', unsafe_allow_html=True)
st.divider()

with st.sidebar:
    st.markdown("### ⚙️ ตั้งค่า")
    gemini_key = st.text_input("🔑 Gemini API Key", type="password", placeholder="AIza...")
    st.divider()
    st.markdown("**📌 วิธีใช้**")
    st.markdown("1. ใส่ Gemini API Key")
    st.markdown("2. เลือกประเภท: หุ้น / Crypto")
    st.markdown("3. เลือกหรือพิมพ์ชื่อ")
    st.markdown("4. ใส่วันเกิด")
    st.markdown("5. กด **วิเคราะห์**")
    st.divider()
    st.caption("⚠️ ไม่ใช่คำแนะนำทางการเงิน")

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
    {"name": "Wheel of Fortune", "th": "วงล้อแห่งโชคชะตา", "emoji": "🎡", "meaning": "โชคกำลังเปลี่ยน จังหวะกำลังมา"},
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
    """สุ่มไพ่ Tarot 3 ใบ"""
    cards = random.sample(TAROT_CARDS, 3)
    roles = ["สถานการณ์ปัจจุบัน", "แนวโน้มระยะสั้น", "คำแนะนำ"]
    return [{"role": roles[i], **cards[i]} for i in range(3)]

# ============================================================
# ฟังก์ชันดึงข้อมูลหุ้น (ปรับเป็น BUY-only logic)
# ============================================================
def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calc_atr(high, low, close, period=14):
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def calc_bollinger(series, period=20):
    ma = series.rolling(period).mean()
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

        # ปรับ logic เป็น BUY/WAIT/SELL สำหรับการซื้อขายปกติ
        # SELL = ถืออยู่แล้วควรขาย, BUY = ควรซื้อเพิ่ม, WAIT = รอดูก่อน
        if rsi <= 40 and price <= bb_lower:
            signal = "🟢 ซื้อ (BUY)"
            entry  = round(price, 2)
            # SL ต่ำกว่าราคาเข้าเสมอ
            stop_loss   = round(price - (atr * 1.5), 2)
            # TP สูงกว่าราคาเข้าเสมอ
            take_profit = round(price + (atr * 3), 2)
            signal_desc = "ราคาต่ำเกินจริง น่าซื้อสะสม"
        elif rsi >= 70 and price >= bb_upper:
            signal = "🔴 ขาย (SELL)"
            entry  = round(price, 2)
            # ถือหุ้นอยู่แล้ว TP คือราคาที่ขายแล้วได้กำไร (สูงกว่าต้นทุนเฉลี่ย)
            # SL คือราคาที่ยอมขายตัดขาดทุน (ต่ำกว่าราคาปัจจุบัน)
            stop_loss   = round(price - (atr * 1.5), 2)
            take_profit = round(price + (atr * 1.5), 2)
            signal_desc = "ราคาสูงเกินไปแล้ว ถ้าถืออยู่ควรขายทำกำไร"
        else:
            signal = "🟡 รอดูก่อน (WAIT)"
            entry  = round(bb_lower, 2)
            stop_loss   = round(bb_lower - (atr * 1.5), 2)
            take_profit = round(bb_upper, 2)
            signal_desc = "ยังไม่ถึงจังหวะที่ดี รอราคาลงมาก่อน"

        rr = round(abs(take_profit - entry) / abs(entry - stop_loss), 2) if entry != stop_loss else 0
        d  = 6 if is_crypto and price < 0.01 else (4 if is_crypto and price < 1 else 2)

        return {
            "symbol"     : symbol,
            "price"      : round(price, d),
            "change_pct" : round(change_pct, 2),
            "arrow"      : "▲" if change >= 0 else "▼",
            "rsi"        : round(rsi, 2),
            "rsi_signal" : "สูงเกินไป (Overbought)" if rsi >= 70 else ("ต่ำเกินไป (Oversold)" if rsi <= 30 else "ปกติ (Neutral)"),
            "ma20"       : round(ma20, d),
            "ma50"       : round(ma50, d),
            "ma_signal"  : "แนวโน้มขาขึ้น ☀️" if ma20 > ma50 else "แนวโน้มขาลง 📉",
            "support"    : round(support, d),
            "resistance" : round(resistance, d),
            "signal"     : signal,
            "signal_desc": signal_desc,
            "entry"      : round(entry, d),
            "stop_loss"  : round(stop_loss, d),
            "take_profit": round(take_profit, d),
            "rr_ratio"   : rr,
            "is_crypto"  : is_crypto,
            "close_series": df["Close"],
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
    pos = get_planets(datetime.now() - timedelta(hours=7))
    lines = [f"{n:8s} → ราศี{d['th']} / {d['en']} ({d['lon']}°)" for n, d in pos.items()]
    return "\n".join(lines), pos

def get_birth_sign(birth_str):
    try:
        pos = get_planets(datetime.strptime(birth_str, "%d/%m/%Y") - timedelta(hours=7))
        return pos["Sun"]["en"], pos["Sun"]["th"]
    except:
        return None, None

def get_weekly():
    now    = datetime.now()
    monday = now - timedelta(days=now.weekday())
    days   = ["จันทร์","อังคาร","พุธ","พฤหัส","ศุกร์","เสาร์","อาทิตย์"]
    fire_air = ["Aries","Leo","Sagittarius","Gemini","Libra","Aquarius"]
    result = []
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
# ฟังก์ชัน Gemini
# ============================================================
def analyze(stock, astro_str, sign_th, sign_en, weekly, birth, tarot_cards, api_key):
    genai.configure(api_key=api_key)
    model      = genai.GenerativeModel("gemini-1.5-flash")
    weekly_str = "\n".join([f"  {d['date']} ({d['day']}) → {d['verdict']}" for d in weekly])
    tarot_str  = "\n".join([f"  {c['emoji']} {c['role']}: {c['name']} ({c['th']}) — {c['meaning']}" for c in tarot_cards])
    asset      = "Crypto" if stock["is_crypto"] else "หุ้น"

    prompt = f"""คุณคือ AstroTrade AI ผู้เชี่ยวชาญด้านกราฟเทคนิค โหราศาสตร์ และไพ่ยิปซี
พูดภาษาไทย เข้าใจง่าย เหมาะสำหรับคนที่ซื้อขายหุ้นปกติ (ไม่ได้เล่น Short/Margin)

=== {asset}: {stock['symbol']} ===
ราคาปัจจุบัน: {stock['price']} ({stock['arrow']}{abs(stock['change_pct'])}%)
RSI: {stock['rsi']} → {stock['rsi_signal']}
แนวโน้ม: {stock['ma_signal']}
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

วิเคราะห์ให้ครบ อธิบายแบบเข้าใจง่าย:
1. 📊 ตอนนี้หุ้นเป็นยังไง ควรทำอะไร
2. 🎯 ถ้าจะซื้อ ควรซื้อที่ราคาไหน และควรขายทำกำไรที่ไหน
3. 🛑 ถ้าราคาลงมาถึงเท่าไหร่ควรยอมขายตัดขาดทุนออก
4. 🃏 ไพ่ยิปซี 3 ใบบอกอะไรเกี่ยวกับหุ้นตัวนี้
5. 🪐 ดาวและดวงชะตาราศี{sign_th}เข้ากับหุ้นนี้ไหม (สนุกๆ)
6. 📅 วันไหนในสัปดาห์นี้เหมาะซื้อที่สุด
7. 💬 คำคมปิดท้าย

ตอบภาษาไทย เข้าใจง่าย ไม่ใช้ศัพท์เทคนิคเยอะ"""

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
run   = st.button("✦ วิเคราะห์ด้วย AstroTrade", use_container_width=True, type="primary")

if run:
    if not gemini_key:
        st.warning("⚠️ ใส่ Gemini API Key ที่ sidebar ก่อนครับ")
    elif not symbol:
        st.warning("⚠️ เลือกหรือพิมพ์ชื่อสินทรัพย์")
    elif not birth:
        st.warning("⚠️ ใส่วันเกิดด้วยครับ")
    else:
        with st.spinner(f"⏳ ดึงข้อมูล {symbol}..."):
            stock = get_stock_data(symbol, is_crypto)

        if not stock:
            st.error(f"❌ ไม่พบ '{symbol}'")
        else:
            # กราฟ
            st.subheader(f"{'🪙' if is_crypto else '📊'} {stock['symbol']}")
            st.line_chart(stock["close_series"])

            # เมตริก
            m1, m2, m3 = st.columns(3)
            m1.metric("ราคาปัจจุบัน", stock["price"], f"{stock['arrow']}{abs(stock['change_pct'])}%")
            m2.metric("RSI", stock["rsi"], stock["rsi_signal"])
            m3.metric("สัญญาณ", stock["signal"])

            # Signal Box (SL ต่ำกว่าราคาเสมอ, TP สูงกว่าราคาเสมอ สำหรับ BUY/WAIT)
            clr = "#00c853" if "ซื้อ" in stock["signal"] else ("#ff1744" if "ขาย" in stock["signal"] else "#ffa000")
            st.markdown(f"""
            <div style='background:#111133;border-left:5px solid {clr};padding:18px;border-radius:10px;margin:12px 0'>
                <h3 style='color:{clr};margin:0 0 6px 0'>{stock['signal']}</h3>
                <p style='color:#aaa;margin:0 0 12px 0;font-size:0.9em'>{stock['signal_desc']}</p>
                <table style='color:#eee;font-size:0.95em;width:100%'>
                    <tr><td>🎯 ราคาเป้าหมายทำกำไร</td><td><b style='color:#69f0ae'>{stock['take_profit']}</b></td></tr>
                    <tr><td>🛑 ราคาตัดขาดทุน</td><td><b style='color:#ff6b6b'>{stock['stop_loss']}</b></td></tr>
                    <tr><td>⚖️ อัตราความคุ้มค่า</td><td><b>1:{stock['rr_ratio']}</b></td></tr>
                    <tr><td>🔵 แนวรับ</td><td>{stock['support']}</td></tr>
                    <tr><td>🔴 แนวต้าน</td><td>{stock['resistance']}</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

            # ไพ่ยิปซี
            st.subheader("🃏 ไพ่ยิปซีวันนี้")
            tarot_cards = draw_tarot()
            tc1, tc2, tc3 = st.columns(3)
            for col, card in zip([tc1, tc2, tc3], tarot_cards):
                with col:
                    st.markdown(f"""
                    <div style='background:#1a1a2e;border:1px solid #9c27b0;
                                padding:12px;border-radius:10px;text-align:center'>
                        <div style='font-size:2em'>{card['emoji']}</div>
                        <div style='color:#ce93d8;font-size:0.75em'>{card['role']}</div>
                        <div style='color:#fff;font-weight:bold;font-size:0.9em'>{card['th']}</div>
                        <div style='color:#aaa;font-size:0.75em;margin-top:4px'>{card['meaning']}</div>
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
                <div style='background:#1a1a2e;border:1px solid #FFD700;
                            padding:12px;border-radius:10px;text-align:center'>
                    <b style='color:#FFD700'>♈ ราศีเกิดของคุณ: {sign_th} ({sign_en})</b>
                </div>
                """, unsafe_allow_html=True)
            else:
                sign_en, sign_th = "Unknown", "ไม่ทราบ"

            # วันดี/วันร้าย
            st.subheader("📅 วันดี/วันร้ายสัปดาห์นี้")
            weekly = get_weekly()
            cols   = st.columns(7)
            for i, d in enumerate(weekly):
                with cols[i]:
                    st.markdown(f"**{'📍' if d['is_today'] else ''}{d['day']}**")
                    st.caption(d["date"])
                    st.markdown(d["verdict"])

            # AI วิเคราะห์
            st.subheader("🤖 AstroTrade AI Analysis")
            with st.spinner("✨ กำลังวิเคราะห์..."):
                result = analyze(stock, astro_str, sign_th, sign_en, weekly, birth, tarot_cards, gemini_key)
            st.markdown(result)

            st.divider()
            st.markdown(
                "<div style='text-align:center;color:#666;font-size:0.8em'>"
                "✦ AstroTrade — Where the Stars Meet the Market 🌌<br>"
                "⚠️ เป็นข้อมูลประกอบการตัดสินใจเท่านั้น ไม่ใช่คำแนะนำทางการเงิน"
                "</div>", unsafe_allow_html=True
            )
