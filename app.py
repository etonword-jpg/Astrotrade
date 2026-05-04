import streamlit as st
import yfinance as yf
import google.generativeai as genai
import ephem
import math
import pandas as pd
import random
import json
from datetime import datetime, timedelta

st.set_page_config(page_title="AstroTrade", page_icon="🌟", layout="centered")

try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
except:
    GEMINI_KEY = None

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Space+Grotesk:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
    html,body,[class*="css"]{font-family:'Space Grotesk',sans-serif;background-color:#080810;color:#e8e8f0;}
    .stApp{background:radial-gradient(ellipse at top left,#1a0533 0%,#080810 50%,#001a33 100%);min-height:100vh;}
    .brand-wrap{text-align:center;padding:20px 0 8px 0;}
    .brand-title{font-family:'Playfair Display',serif;font-size:3.2em;font-weight:900;background:linear-gradient(135deg,#fff 0%,#e040fb 40%,#7c4dff 70%,#40c4ff 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:6px;text-transform:uppercase;filter:drop-shadow(0 0 20px rgba(224,64,251,0.5));}
    .brand-sub{font-weight:300;color:#b39ddb;font-size:0.9em;letter-spacing:3px;text-transform:uppercase;margin-top:-4px;}
    .brand-line{width:80px;height:2px;background:linear-gradient(90deg,transparent,#e040fb,#7c4dff,transparent);margin:12px auto;}
    .glass-card{background:rgba(255,255,255,0.04);border:1px solid rgba(224,64,251,0.2);border-radius:16px;padding:20px;margin:12px 0;}
    .signal-buy{background:rgba(0,230,118,0.08);border:1px solid rgba(0,230,118,0.4);border-radius:16px;padding:20px;}
    .signal-sell{background:rgba(255,23,68,0.08);border:1px solid rgba(255,23,68,0.4);border-radius:16px;padding:20px;}
    .signal-wait{background:rgba(255,160,0,0.08);border:1px solid rgba(255,160,0,0.4);border-radius:16px;padding:20px;}
    .card-revealed{background:linear-gradient(145deg,rgba(124,77,255,0.25),rgba(224,64,251,0.12));border:2px solid #e040fb;border-radius:12px;padding:14px 8px;text-align:center;box-shadow:0 0 25px rgba(224,64,251,0.5);}
    .section-header{font-family:'Playfair Display',serif;font-size:1.3em;font-weight:700;background:linear-gradient(90deg,#e040fb,#7c4dff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:1px;margin:20px 0 10px 0;}
    .symbol-badge{display:inline-block;background:linear-gradient(135deg,rgba(124,77,255,0.3),rgba(224,64,251,0.2));border:1px solid #e040fb;border-radius:20px;padding:6px 16px;font-size:1.1em;font-weight:700;color:#e8e8f0;margin-top:8px;letter-spacing:1px;}
    [data-testid="metric-container"]{background:rgba(255,255,255,0.04);border:1px solid rgba(124,77,255,0.2);border-radius:12px;padding:12px;}
    .stButton>button{background:linear-gradient(135deg,#7c4dff,#e040fb)!important;color:white!important;border:none!important;border-radius:50px!important;font-weight:700!important;letter-spacing:2px!important;padding:14px!important;box-shadow:0 0 25px rgba(224,64,251,0.4)!important;}
    .stTextInput>div>div>input,.stSelectbox>div>div{background:rgba(255,255,255,0.05)!important;border:1px solid rgba(124,77,255,0.3)!important;border-radius:12px!important;color:#e8e8f0!important;}
    .stRadio>div{background:rgba(255,255,255,0.03);border-radius:12px;padding:8px;}
    [data-testid="stSidebar"]{background:rgba(8,8,16,0.95)!important;border-right:1px solid rgba(124,77,255,0.2)!important;}
    hr{border-color:rgba(124,77,255,0.2)!important;}
    .poll-card{background:rgba(255,255,255,0.04);border:1px solid rgba(124,77,255,0.25);border-radius:14px;padding:14px 18px;margin:8px 0;}
    .poll-bar-bg{background:rgba(255,255,255,0.08);border-radius:20px;height:8px;margin:4px 0;}
    .footer-text{text-align:center;color:#5c5c7a;font-size:0.78em;letter-spacing:1px;padding:10px 0;}
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

with st.sidebar:
    st.markdown("<div style='font-family:Playfair Display,serif;font-size:1.3em;color:#e040fb;letter-spacing:2px'>⚙ SETTINGS</div>", unsafe_allow_html=True)
    if not GEMINI_KEY:
        manual_key = st.text_input("🔑 Gemini API Key", type="password", placeholder="AIza...")
        GEMINI_KEY = manual_key
    else:
        st.success("✅ API Key พร้อมใช้งาน")
    st.divider()
    st.markdown("<div style='color:#b39ddb;font-size:0.85em;letter-spacing:1px'>HOW TO USE</div>", unsafe_allow_html=True)
    st.markdown("1. เลือกหุ้นจาก dropdown หรือพิมพ์ชื่อ")
    st.markdown("2. กดไพ่ยิปซีที่ใจสั่ง 3 ใบ")
    st.markdown("3. กด **วิเคราะห์** ได้เลย!")
    st.divider()
    st.caption("✦ AstroTrade 2025 | ไม่ใช่คำแนะนำทางการเงิน")

STOCK_OPTIONS = {
    "🇺🇸 หุ้นสหรัฐ": {
        "NVIDIA (NVDA)":"NVDA","Apple (AAPL)":"AAPL","Tesla (TSLA)":"TSLA",
        "Microsoft (MSFT)":"MSFT","Meta (META)":"META","Amazon (AMZN)":"AMZN",
        "Google (GOOGL)":"GOOGL","AMD":"AMD","Netflix (NFLX)":"NFLX","Palantir (PLTR)":"PLTR",
    },
    "🇹🇭 หุ้นไทย": {
        "CPALL":"CPALL.BK","PTT":"PTT.BK","SCB":"SCB.BK","KBANK":"KBANK.BK",
        "AOT":"AOT.BK","MINT":"MINT.BK","ADVANC":"ADVANC.BK","TRUE":"TRUE.BK",
    },
    "🪙 Crypto": {
        "Bitcoin (BTC)":"BTC-USD","Ethereum (ETH)":"ETH-USD","Solana (SOL)":"SOL-USD",
        "XRP":"XRP-USD","BNB":"BNB-USD","Dogecoin (DOGE)":"DOGE-USD",
        "Cardano (ADA)":"ADA-USD","Avalanche (AVAX)":"AVAX-USD",
        "Shiba Inu (SHIB)":"SHIB-USD","Pepe (PEPE)":"PEPE-USD","Sui (SUI)":"SUI-USD",
    },
}
ALL_DISPLAY = {"-- เลือกจากรายการ --": ""}
for group, items in STOCK_OPTIONS.items():
    for display, ticker in items.items():
        ALL_DISPLAY[f"{group}  •  {display}"] = ticker

TAROT_CARDS = [
    {"name":"The Fool","th":"คนโง่เขลา","emoji":"🃏","meaning":"จุดเริ่มต้นใหม่ โอกาสที่ไม่คาดคิด"},
    {"name":"The Magician","th":"นักมายากล","emoji":"🎩","meaning":"มีทักษะและพลัง พร้อมลงมือทำ"},
    {"name":"The High Priestess","th":"นักบวชหญิง","emoji":"🌙","meaning":"ใช้สัญชาตญาณ รอเวลาที่เหมาะสม"},
    {"name":"The Empress","th":"จักรพรรดินี","emoji":"👑","meaning":"ความอุดมสมบูรณ์ ผลตอบแทนดี"},
    {"name":"The Emperor","th":"จักรพรรดิ","emoji":"⚔️","meaning":"ความมั่นคง โครงสร้างแข็งแกร่ง"},
    {"name":"The Lovers","th":"คู่รัก","emoji":"💕","meaning":"ต้องตัดสินใจเลือก จุดเปลี่ยนสำคัญ"},
    {"name":"The Chariot","th":"รถศึก","emoji":"🏆","meaning":"ชัยชนะ ก้าวหน้าอย่างแข็งแกร่ง"},
    {"name":"Strength","th":"ความแข็งแกร่ง","emoji":"🦁","meaning":"ใจเย็น ควบคุมสถานการณ์ได้"},
    {"name":"The Hermit","th":"ฤๅษี","emoji":"🏮","meaning":"ใคร่ครวญก่อน อย่าเร่งรีบ"},
    {"name":"Wheel of Fortune","th":"วงล้อโชคชะตา","emoji":"🎡","meaning":"โชคกำลังเปลี่ยน จังหวะกำลังมา"},
    {"name":"Justice","th":"ความยุติธรรม","emoji":"⚖️","meaning":"ผลลัพธ์สมเหตุสมผล ตลาดสมดุล"},
    {"name":"The Star","th":"ดวงดาว","emoji":"⭐","meaning":"ความหวัง สัญญาณบวกกำลังมา"},
    {"name":"The Moon","th":"ดวงจันทร์","emoji":"🌕","meaning":"ความไม่แน่นอน ระวังข้อมูลลวง"},
    {"name":"The Sun","th":"ดวงอาทิตย์","emoji":"☀️","meaning":"ความสำเร็จ ผลตอบแทนสดใส"},
    {"name":"Judgement","th":"การตัดสิน","emoji":"🎺","meaning":"ถึงเวลาตัดสินใจครั้งสำคัญ"},
    {"name":"The World","th":"โลก","emoji":"🌍","meaning":"สำเร็จครบถ้วน จบรอบสมบูรณ์"},
    {"name":"The Tower","th":"หอคอย","emoji":"⚡","meaning":"เปลี่ยนแปลงฉับพลัน ระวังความเสี่ยง"},
    {"name":"The Devil","th":"ปีศาจ","emoji":"😈","meaning":"ระวังความโลภ อย่าตกใจขายหมู"},
    {"name":"Death","th":"ความตาย","emoji":"💀","meaning":"เปลี่ยนแปลงครั้งใหญ่ ยุคใหม่มา"},
    {"name":"Temperance","th":"ความพอดี","emoji":"🏺","meaning":"สมดุล อย่า FOMO อย่า Panic"},
]

def calc_rsi(series, period=14):
    delta=series.diff(); gain=delta.clip(lower=0).rolling(period).mean(); loss=-delta.clip(upper=0).rolling(period).mean()
    return 100-(100/(1+gain/loss))

def calc_atr(high,low,close,period=14):
    tr=pd.concat([high-low,(high-close.shift()).abs(),(low-close.shift()).abs()],axis=1).max(axis=1)
    return tr.rolling(period).mean()

def calc_bollinger(series,period=20):
    ma=series.rolling(period).mean(); return ma+2*series.rolling(period).std(),ma-2*series.rolling(period).std()

def get_sr_levels(df):
    price=df["Close"].iloc[-1]; h=df["High"].tail(20).max(); l=df["Low"].tail(20).min(); p=(h+l+price)/3
    r1=round(2*p-l,2);r2=round(p+(h-l),2);r3=round(h+2*(p-l),2)
    s1=round(2*p-h,2);s2=round(p-(h-l),2);s3=round(l-2*(h-p),2)
    return sorted([r for r in [r1,r2,r3] if r>price])[:3], sorted([s for s in [s1,s2,s3] if s<price],reverse=True)[:3]

def get_elliott(df):
    close=df["Close"].tail(50); recent=close.tail(10)
    tl="ขาขึ้น" if close.iloc[-1]>close.iloc[0] else "ขาลง"
    ts="ขาขึ้น" if recent.iloc[-1]>recent.iloc[0] else "ขาลง"
    changes=close.diff().dropna(); waves=[]; cur=0
    for c in changes:
        if c>0:
            if cur<=0: waves.append(cur); cur=c
            else: cur+=c
        else:
            if cur>=0: waves.append(cur); cur=c
            else: cur+=c
    waves=[w for w in waves if w!=0][-5:]
    if len(waves)>=3:
        if waves[-1]>0 and waves[-2]<0 and waves[-3]>0: wp,we="Wave 5 — คลื่นสุดท้ายขาขึ้น ระวังพลิก","⚠️"
        elif waves[-1]<0 and waves[-2]>0: wp,we="Wave C — กำลังแก้ไขลง รอจังหวะซื้อ","🔄"
        elif waves[-1]>0 and waves[-2]<0: wp,we="Wave 3 — คลื่นแรงที่สุด โอกาสทำกำไร","🚀"
        else: wp,we="Wave 1-2 — เริ่มรอบใหม่ ช่วงสะสม","🌱"
    else: wp,we="ไม่พอข้อมูล","❓"
    return {"trend_long":tl,"trend_short":ts,"wave_pos":wp,"wave_emoji":we}

def get_stock_data(symbol):
    try:
        df=yf.Ticker(symbol).history(period="3mo")
        if df.empty: return None
        df["RSI"]=calc_rsi(df["Close"]); df["MA20"]=df["Close"].rolling(20).mean(); df["MA50"]=df["Close"].rolling(50).mean()
        df["ATR"]=calc_atr(df["High"],df["Low"],df["Close"]); df["BB_upper"],df["BB_lower"]=calc_bollinger(df["Close"])
        price=df["Close"].iloc[-1]; prev=df["Close"].iloc[-2]; rsi=df["RSI"].iloc[-1]
        ma20=df["MA20"].iloc[-1]; ma50=df["MA50"].iloc[-1]; atr=df["ATR"].iloc[-1]
        bbu=df["BB_upper"].iloc[-1]; bbl=df["BB_lower"].iloc[-1]; chg=((price-prev)/prev)*100
        res,sup=get_sr_levels(df); ew=get_elliott(df)
        is_c=symbol.endswith("-USD")
        if rsi<=40 and price<=bbl:
            sig,sen,desc,cls="🟢 ซื้อ","BUY","ราคาต่ำเกินจริง — จังหวะสะสมที่ดี","signal-buy"
            e=round(price,2);sl=round(price-atr*1.5,2);tp1=round(price+atr,2);tp2=round(price+atr*2,2);tp3=round(price+atr*3,2);tp4=round(price+atr*4.5,2)
        elif rsi>=70 and price>=bbu:
            sig,sen,desc,cls="🔴 ขาย","SELL","ราคาสูงเกินไป — ถ้าถืออยู่ควรขายทำกำไร","signal-sell"
            e=round(price,2);sl=round(price-atr*1.5,2);tp1=round(price+atr*.5,2);tp2=round(price+atr,2);tp3=round(price+atr*1.5,2);tp4=round(price+atr*2,2)
        else:
            sig,sen,desc,cls="🟡 รอดูก่อน","WAIT","ยังไม่ถึงจังหวะที่ดี — รอราคาลงมาก่อน","signal-wait"
            e=round(bbl,2);sl=round(bbl-atr*1.5,2);tp1=round(bbl+atr,2);tp2=round(bbl+atr*2,2);tp3=round(bbl+atr*3,2);tp4=round(bbu,2)
        d=6 if is_c and price<0.01 else(4 if is_c and price<1 else 2)
        return {"symbol":symbol,"price":round(price,d),"change_pct":round(chg,2),"arrow":"▲" if chg>=0 else "▼",
                "rsi":round(rsi,2),"rsi_signal":"สูงเกินไป" if rsi>=70 else("ต่ำเกินไป" if rsi<=30 else "ปกติ"),
                "ma20":round(ma20,d),"ma50":round(ma50,d),"ma_signal":"แนวโน้มขาขึ้น ☀️" if ma20>ma50 else "แนวโน้มขาลง 📉",
                "signal":sig,"signal_en":sen,"desc":desc,"cls":cls,"entry":e,"sl":sl,
                "tp1":round(tp1,d),"tp2":round(tp2,d),"tp3":round(tp3,d),"tp4":round(tp4,d),
                "resistances":res,"supports":sup,"elliott":ew,"is_crypto":is_c,"close_series":df["Close"]}
    except Exception as ex:
        st.error(f"❌ {ex}"); return None

WATCHLIST={"หุ้นสหรัฐ":["NVDA","AAPL","TSLA","META","AMD","MSFT","AMZN","GOOGL"],"Crypto":["BTC-USD","ETH-USD","SOL-USD","BNB-USD","XRP-USD"],"หุ้นไทย":["CPALL.BK","PTT.BK","SCB.BK","KBANK.BK","AOT.BK"]}

@st.cache_data(ttl=3600)
def get_hot_picks(cat):
    results=[]
    for sym in WATCHLIST.get(cat,[]):
        try:
            df=yf.Ticker(sym).history(period="5d")
            if df.empty or len(df)<2: continue
            price=df["Close"].iloc[-1];prev=df["Close"].iloc[-2];chg=((price-prev)/prev)*100
            vr=df["Volume"].iloc[-1]/df["Volume"].mean() if df["Volume"].mean()>0 else 1
            rv=calc_rsi(df["Close"]).iloc[-1]
            score=sum([chg>0,vr>1.5,30<=rv<=60,chg>2,vr>2])*2
            results.append({"symbol":sym,"price":round(price,2),"change_pct":round(chg,2),"rsi":round(rv,1),"vol_ratio":round(vr,1),"score":score})
        except: continue
    return sorted(results,key=lambda x:x["score"],reverse=True)[:5]

def get_zodiac(lon):
    s=[("Aries","เมษ"),("Taurus","พฤษภ"),("Gemini","เมถุน"),("Cancer","กรกฎ"),("Leo","สิงห์"),("Virgo","กันย์"),("Libra","ตุลย์"),("Scorpio","พิจิก"),("Sagittarius","ธนู"),("Capricorn","มกร"),("Aquarius","กุมภ์"),("Pisces","มีน")]
    return s[int(lon//30)%12]

def get_planets(du):
    bkk=ephem.Observer();bkk.lat,bkk.lon,bkk.elevation="13.75","100.517",0;bkk.date=du;res={}
    for n,o in {"Sun":ephem.Sun(),"Moon":ephem.Moon(),"Mercury":ephem.Mercury(),"Venus":ephem.Venus(),"Mars":ephem.Mars(),"Jupiter":ephem.Jupiter(),"Saturn":ephem.Saturn()}.items():
        o.compute(bkk);lon=math.degrees(ephem.Ecliptic(o).lon)%360;en,th=get_zodiac(lon);res[n]={"lon":round(lon,1),"en":en,"th":th}
    return res

def get_astro_today():
    pos=get_planets(datetime.now()-timedelta(hours=7))
    return "\n".join([f"{n:8s} → ราศี{d['th']} / {d['en']} ({d['lon']}°)" for n,d in pos.items()]),pos

def get_birth_sign(bs):
    try:
        pos=get_planets(datetime.strptime(bs,"%d/%m/%Y")-timedelta(hours=7));return pos["Sun"]["en"],pos["Sun"]["th"]
    except: return None,None

def get_weekly():
    now=datetime.now();mon=now-timedelta(days=now.weekday())
    days=["จันทร์","อังคาร","พุธ","พฤหัส","ศุกร์","เสาร์","อาทิตย์"]
    fa=["Aries","Leo","Sagittarius","Gemini","Libra","Aquarius"];res=[]
    for i in range(7):
        d=mon+timedelta(days=i);pos=get_planets(d-timedelta(hours=7))
        sc=sum([pos["Mercury"]["en"] in fa,pos["Moon"]["en"] in fa,d.weekday() in [0,3,4]])
        res.append({"date":d.strftime("%d/%m"),"day":days[i],"verdict":"🟢 ดีมาก" if sc>=3 else("🟡 พอใช้" if sc==2 else "🔴 ระวัง"),"moon":pos["Moon"]["en"],"is_today":d.date()==now.date()})
    return res

def analyze(stock,astro_str,sign_th,sign_en,weekly,birth,tarot_cards,api_key):
    genai.configure(api_key=api_key);model=genai.GenerativeModel("gemini-1.5-flash")
    ws="\n".join([f"  {d['date']} ({d['day']}) → {d['verdict']}" for d in weekly])
    ts="\n".join([f"  {c['emoji']} {c['role']}: {c['name']} ({c['th']}) — {c['meaning']}" for c in tarot_cards])
    asset="Crypto" if stock["is_crypto"] else "หุ้น"
    bi=f"วันเกิด: {birth} | ราศี: {sign_th} ({sign_en})" if sign_th else "ไม่ได้ระบุวันเกิด"
    prompt=f"""คุณคือ AstroTrade AI พูดภาษาไทยเข้าใจง่าย
{asset}: {stock['symbol']} ราคา {stock['price']} ({stock['arrow']}{abs(stock['change_pct'])}%) RSI:{stock['rsi']}({stock['rsi_signal']}) {stock['ma_signal']}
Elliott: {stock['elliott']['wave_emoji']} {stock['elliott']['wave_pos']}
สัญญาณ: {stock['signal']} — {stock['desc']}
TP1={stock['tp1']} TP2={stock['tp2']} TP3={stock['tp3']} TP4={stock['tp4']} SL={stock['sl']}
แนวต้าน:{stock['resistances']} แนวรับ:{stock['supports']}
ไพ่: {ts} | ดาว: {astro_str} | {bi} | วันดี/ร้าย: {ws}
วิเคราะห์: 1.📊ภาพรวม 2.🌊Elliott Wave 3.🎯ซื้อ/ขาย/TP/SL 4.🃏ไพ่ยิปซี 5.🪐ดาว+ดวงชะตา(สนุกๆ) 6.📅วันดีที่สุด 7.✨คำคมปิดท้าย
ตอบภาษาไทย สนุก เข้าใจง่าย"""
    try: return model.generate_content(prompt).text
    except Exception as e: return f"❌ {e}"

# Hot Picks
st.markdown("<div class='section-header'>🔥 Hot Picks — อัปเดตรายชั่วโมง</div>", unsafe_allow_html=True)
poll_cat=st.radio("เลือกกลุ่ม",["หุ้นสหรัฐ","Crypto","หุ้นไทย"],horizontal=True,key="pc")
with st.spinner("📡 สแกนตลาด..."):
    hot=get_hot_picks(poll_cat)
if hot:
    st.caption(f"⏱ อัปเดต: {datetime.now().strftime('%H:%M')} น.")
    for i,s in enumerate(hot):
        rank=["🥇","🥈","🥉","4️⃣","5️⃣"][i];clr="#00e676" if s["change_pct"]>=0 else "#ff5252";bar=min(int((s["score"]/10)*100),100)
        st.markdown(f"""<div class="poll-card"><div style='display:flex;justify-content:space-between;align-items:center'><div><span style='font-size:1.2em'>{rank}</span> <b style='margin-left:6px'>{s['symbol']}</b> <span style='color:#888;font-size:0.8em'>RSI {s['rsi']}</span></div><div style='text-align:right'><b>{s['price']}</b><br><span style='color:{clr};font-size:0.9em'>{'▲' if s['change_pct']>=0 else '▼'}{abs(s['change_pct'])}%</span></div></div><div class="poll-bar-bg"><div style='width:{bar}%;height:8px;border-radius:20px;background:linear-gradient(90deg,#7c4dff,#e040fb)'></div></div></div>""",unsafe_allow_html=True)
st.divider()

# เลือกหุ้น
st.markdown("<div class='section-header'>🔮 เลือกสินทรัพย์ที่ต้องการวิเคราะห์</div>", unsafe_allow_html=True)
if "symbol_input" not in st.session_state:
    st.session_state.symbol_input = ""

col_drop, col_type = st.columns(2)
with col_drop:
    st.markdown("<div style='color:#b39ddb;font-size:0.82em;margin-bottom:4px'>📋 เลือกจากรายการ</div>", unsafe_allow_html=True)
    dropdown_sel = st.selectbox("เลือกหุ้น/Crypto",list(ALL_DISPLAY.keys()),label_visibility="collapsed")
    if ALL_DISPLAY[dropdown_sel]:
        st.session_state.symbol_input = ALL_DISPLAY[dropdown_sel]

with col_type:
    st.markdown("<div style='color:#b39ddb;font-size:0.82em;margin-bottom:4px'>✏️ พิมพ์ชื่อเอง</div>", unsafe_allow_html=True)
    typed = st.text_input("พิมพ์ชื่อหุ้น",placeholder="เช่น NVDA, BTC-USD, SCB.BK",label_visibility="collapsed",key="typed_symbol")
    if typed.strip():
        st.session_state.symbol_input = typed.strip().upper()

symbol = st.session_state.symbol_input
if symbol:
    st.markdown(f"<div style='margin:8px 0 4px 0;color:#888;font-size:0.82em'>สินทรัพย์ที่เลือก:</div><div class='symbol-badge'>{'🪙' if symbol.endswith('-USD') else '📈'} {symbol}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='color:#555;font-size:0.85em;margin-top:8px'>⬆️ เลือกหรือพิมพ์ชื่อสินทรัพย์ด้านบน</div>", unsafe_allow_html=True)

birth = st.text_input("🎂 วันเกิด (ไม่บังคับ)", placeholder="DD/MM/YYYY เช่น 15/06/1990")

# ไพ่ยิปซี
st.markdown("<div class='section-header'>🃏 เลือกไพ่ยิปซีจากสำรับ</div>", unsafe_allow_html=True)
st.markdown("<div style='color:#b39ddb;font-size:0.88em;margin-bottom:8px'>ทำจิตใจให้สงบ แล้วกดไพ่ที่ใจสั่ง 3 ใบ 🌙</div>", unsafe_allow_html=True)

if "shuffled_deck" not in st.session_state:
    deck=TAROT_CARDS.copy(); random.shuffle(deck); st.session_state.shuffled_deck=deck
if "shuffle_count" not in st.session_state:
    st.session_state.shuffle_count=0

col_sh,_=st.columns([1,3])
with col_sh:
    if st.button("🔀 สับไพ่ใหม่"):
        deck=TAROT_CARDS.copy(); random.shuffle(deck)
        st.session_state.shuffled_deck=deck
        st.session_state.shuffle_count+=1
        st.rerun()

cards_json = json.dumps([{"name":c["name"],"th":c["th"],"emoji":c["emoji"],"meaning":c["meaning"]} for c in st.session_state.shuffled_deck])
shuffle_count = st.session_state.shuffle_count

# HTML สำรับไพ่ — ใช้ string ธรรมดา ไม่ใช่ f-string เพื่อหลีกเลี่ยง brace conflict
fan_html = (
"""
<style>
#fan-root{width:100%;box-sizing:border-box;overflow:hidden;}
#fan-svg-wrap{width:100%;aspect-ratio:2/1;position:relative;overflow:hidden;}
#fan-svg-wrap svg{width:100%;height:100%;}
@keyframes flyOut{
  0%  {opacity:1;transform:translate(0,0) rotate(0deg) scale(1);}
  30% {opacity:0.8;transform:translate(var(--dx),var(--dy)) rotate(var(--dr)) scale(1.2);}
  60% {opacity:0.5;transform:translate(calc(var(--dx)*0.5),calc(var(--dy)*0.5)) rotate(calc(var(--dr)*-0.5)) scale(1.1);}
  100%{opacity:1;transform:translate(0,0) rotate(0deg) scale(1);}
}
.card-g.shuffling{animation:flyOut 0.7s ease-in-out forwards;}
#sel-area{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;min-height:130px;margin-top:14px;align-items:flex-start;}
.sel-card{background:linear-gradient(145deg,rgba(124,77,255,0.3),rgba(224,64,251,0.15));border:2px solid #e040fb;border-radius:12px;padding:10px 8px;text-align:center;width:90px;box-shadow:0 0 16px rgba(224,64,251,0.4);color:#eee;position:relative;}
.sel-card .role{color:#ce93d8;font-size:0.6em;letter-spacing:1px;text-transform:uppercase;}
.sel-card .cemoji{font-size:1.5em;margin:3px 0;}
.sel-card .cname{font-size:0.7em;font-weight:700;color:#fff;}
.sel-card .cmeaning{font-size:0.6em;color:#999;line-height:1.3;margin-top:3px;}
.sel-card .rm{position:absolute;top:3px;right:6px;background:none;border:none;color:#888;cursor:pointer;font-size:0.75em;}
#count-lbl{text-align:center;color:#e040fb;font-size:0.88em;margin-top:6px;min-height:20px;}
#clr-btn{display:block;margin:8px auto 0;background:rgba(124,77,255,0.2);border:1px solid #7c4dff;color:#e040fb;border-radius:20px;padding:5px 18px;cursor:pointer;font-size:0.82em;}
</style>
<div id="fan-root">
  <div id="fan-svg-wrap">
    <svg id="fan-svg" viewBox="0 0 400 200" preserveAspectRatio="xMidYMax meet"></svg>
  </div>
  <div id="sel-area"><span style="color:#555;font-size:0.85em;align-self:center">กดไพ่จากสำรับด้านบน</span></div>
  <div id="count-lbl"></div>
  <button id="clr-btn" onclick="clearAll()">✕ ล้างไพ่</button>
</div>
<script>
var cards="""
+ cards_json +
""";
var selected=[];
var roles=["สถานการณ์ปัจจุบัน","แนวโน้มระยะสั้น","คำแนะนำ"];
var shuffleCount="""
+ str(shuffle_count) +
""";
var lastShuffle=parseInt(sessionStorage.getItem('astroShuffle')||'-1');
var needShuffle=(shuffleCount!==lastShuffle);

function buildFan(){
  var svg=document.getElementById('fan-svg');
  svg.innerHTML='';
  var total=cards.length;
  var cx=200,cy=215,R=175,startDeg=-170,span=160;
  var defs=document.createElementNS('http://www.w3.org/2000/svg','defs');
  var rg=document.createElementNS('http://www.w3.org/2000/svg','radialGradient');
  rg.setAttribute('id','bgG');rg.setAttribute('cx','50%');rg.setAttribute('cy','100%');rg.setAttribute('r','60%');
  var s1=document.createElementNS('http://www.w3.org/2000/svg','stop');
  s1.setAttribute('offset','0%');s1.setAttribute('stop-color','#3d0070');s1.setAttribute('stop-opacity','0.5');
  var s2=document.createElementNS('http://www.w3.org/2000/svg','stop');
  s2.setAttribute('offset','100%');s2.setAttribute('stop-color','#080810');s2.setAttribute('stop-opacity','0');
  rg.appendChild(s1);rg.appendChild(s2);defs.appendChild(rg);
  var lg=document.createElementNS('http://www.w3.org/2000/svg','linearGradient');
  lg.setAttribute('id','cG');lg.setAttribute('x1','0');lg.setAttribute('y1','0');lg.setAttribute('x2','1');lg.setAttribute('y2','1');
  var ls1=document.createElementNS('http://www.w3.org/2000/svg','stop');ls1.setAttribute('offset','0%');ls1.setAttribute('stop-color','#2d0a4e');
  var ls2=document.createElementNS('http://www.w3.org/2000/svg','stop');ls2.setAttribute('offset','100%');ls2.setAttribute('stop-color','#1a0533');
  lg.appendChild(ls1);lg.appendChild(ls2);defs.appendChild(lg);
  svg.appendChild(defs);
  var bg=document.createElementNS('http://www.w3.org/2000/svg','ellipse');
  bg.setAttribute('cx','200');bg.setAttribute('cy','210');bg.setAttribute('rx','220');bg.setAttribute('ry','180');bg.setAttribute('fill','url(#bgG)');
  svg.appendChild(bg);
  var cw=20,ch=32;
  for(var i=0;i<total;i++){
    var frac=i/(total-1);
    var angleDeg=startDeg+frac*span;
    var rad=angleDeg*Math.PI/180;
    var px=cx+R*Math.cos(rad);
    var py=cy+R*Math.sin(rad);
    var rot=angleDeg+90;
    var isPicked=selected.indexOf(i)>=0;
    var g=document.createElementNS('http://www.w3.org/2000/svg','g');
    g.setAttribute('class','card-g');
    g.setAttribute('transform','translate('+px+','+py+') rotate('+rot+')');
    g.style.cursor=isPicked?'default':'pointer';
    g.style.opacity=isPicked?'0.2':'1';
    g.dataset.idx=i;g.dataset.px=px;g.dataset.py=py;
    var rect=document.createElementNS('http://www.w3.org/2000/svg','rect');
    rect.setAttribute('x',-cw/2);rect.setAttribute('y',-ch/2);
    rect.setAttribute('width',cw);rect.setAttribute('height',ch);
    rect.setAttribute('rx','3');rect.setAttribute('ry','3');
    rect.setAttribute('fill',isPicked?'#0d0020':'url(#cG)');
    rect.setAttribute('stroke',isPicked?'rgba(100,30,150,0.3)':'#e040fb');
    rect.setAttribute('stroke-width','0.8');
    var star=document.createElementNS('http://www.w3.org/2000/svg','text');
    star.setAttribute('x','0');star.setAttribute('y','5');
    star.setAttribute('text-anchor','middle');star.setAttribute('font-size','11');
    star.setAttribute('fill',isPicked?'rgba(100,30,150,0.3)':'#e040fb');
    star.textContent='✦';
    var title=document.createElementNS('http://www.w3.org/2000/svg','title');
    title.textContent=isPicked?'เลือกแล้ว':cards[i].th;
    g.appendChild(title);g.appendChild(rect);g.appendChild(star);
    if(!isPicked){
      g.addEventListener('mouseenter',function(){
        this.querySelector('rect').setAttribute('stroke','#fff');
        this.querySelector('rect').setAttribute('stroke-width','1.5');
        this.querySelector('text').setAttribute('fill','#fff');
      });
      g.addEventListener('mouseleave',function(){
        this.querySelector('rect').setAttribute('stroke','#e040fb');
        this.querySelector('rect').setAttribute('stroke-width','0.8');
        this.querySelector('text').setAttribute('fill','#e040fb');
      });
      g.addEventListener('click',onCardClick);
    }
    svg.appendChild(g);
  }
}

function onCardClick(){
  var idx=parseInt(this.dataset.idx);
  if(selected.indexOf(idx)>=0||selected.length>=3) return;
  var self=this;
  self.style.filter='drop-shadow(0 0 10px #fff)';
  setTimeout(function(){self.style.filter='';},350);
  selected.push(idx);
  buildFan();renderSelected();
}

function renderSelected(){
  var area=document.getElementById('sel-area');
  var lbl=document.getElementById('count-lbl');
  if(selected.length===0){
    area.innerHTML='<span style="color:#555;font-size:0.85em;align-self:center">กดไพ่จากสำรับด้านบน</span>';
    lbl.textContent='';return;
  }
  area.innerHTML='';
  for(var i=0;i<selected.length;i++){
    var c=cards[selected[i]];
    var div=document.createElement('div');div.className='sel-card';
    div.innerHTML='<div class="role">'+roles[i]+'</div><div class="cemoji">'+c.emoji+'</div><div class="cname">'+c.th+'</div><div class="cmeaning">'+c.meaning+'</div><button class="rm" onclick="removeCard('+i+')">✕</button>';
    area.appendChild(div);
  }
  lbl.textContent='✨ เลือกแล้ว '+selected.length+'/3 ใบ'+(selected.length===3?' — พร้อมวิเคราะห์! 🚀':'');
}

function removeCard(si){selected.splice(si,1);buildFan();renderSelected();}
function clearAll(){selected=[];buildFan();renderSelected();}

function doShuffleAnimation(){
  var svg=document.getElementById('fan-svg');
  var groups=svg.querySelectorAll('.card-g');
  var cx=200,cy=200;
  groups.forEach(function(g,i){
    var px=parseFloat(g.dataset.px||200);
    var py=parseFloat(g.dataset.py||200);
    var dx=(px-cx)*0.8+(Math.random()-0.5)*60;
    var dy=(py-cy)*0.8+(Math.random()-0.5)*60;
    var dr=(Math.random()-0.5)*60;
    g.style.setProperty('--dx',dx+'px');
    g.style.setProperty('--dy',dy+'px');
    g.style.setProperty('--dr',dr+'deg');
    setTimeout(function(){
      g.classList.add('shuffling');
      setTimeout(function(){g.classList.remove('shuffling');},750);
    },i*25);
  });
  sessionStorage.setItem('astroShuffle',shuffleCount);
}

buildFan();
renderSelected();
if(needShuffle){ setTimeout(doShuffleAnimation,150); }
</script>
"""
)

st.components.v1.html(fan_html, height=530, scrolling=False)

# เลือกไพ่ — multiselect เป็น source หลัก
st.markdown("<div style='color:#e040fb;font-size:0.9em;font-weight:600;margin:12px 0 6px 0'>👇 เลือกไพ่ที่ใจสั่ง 3 ใบ</div>", unsafe_allow_html=True)
card_names=[f"{c['emoji']} {c['th']}" for c in TAROT_CARDS]
selected_names=st.multiselect(
    "เลือกไพ่ยิปซี 3 ใบ",
    card_names,
    max_selections=3,
    placeholder="🃏 แตะเพื่อเลือกไพ่ยิปซี 3 ใบ...",
    label_visibility="collapsed"
)
selected_cards=[]
for name in selected_names:
    for card in TAROT_CARDS:
        if f"{card['emoji']} {card['th']}"==name:
            selected_cards.append(card);break

if len(selected_cards)==3:
    roles_label=["สถานการณ์ปัจจุบัน","แนวโน้มระยะสั้น","คำแนะนำ"]
    tc=st.columns(3)
    for i,card in enumerate(selected_cards):
        with tc[i]:
            st.markdown(f"""<div class="card-revealed"><div style='font-size:1.8em'>{card['emoji']}</div><div style='color:#ce93d8;font-size:0.68em;letter-spacing:1px'>{roles_label[i]}</div><div style='font-family:Playfair Display,serif;color:#fff;font-weight:700;font-size:0.88em;margin:4px 0'>{card['th']}</div><div style='color:#9e9e9e;font-size:0.7em;line-height:1.3'>{card['meaning']}</div></div>""",unsafe_allow_html=True)
    st.success("✨ เลือกครบ 3 ใบแล้ว — กด ANALYZE ได้เลย! 🚀")
elif len(selected_cards)>0:
    st.info(f"เลือกแล้ว {len(selected_cards)}/3 ใบ — เลือกให้ครบก่อนนะครับ")

st.markdown("<br>", unsafe_allow_html=True)
run=st.button("✦ ANALYZE WITH ASTROTRADE ✦",use_container_width=True)

if run:
    if not GEMINI_KEY: st.warning("⚠️ ใส่ Gemini API Key ที่ sidebar ก่อนนะครับ")
    elif not symbol: st.warning("⚠️ เลือกหรือพิมพ์ชื่อสินทรัพย์ด้วยครับ")
    elif len(selected_cards)<3: st.warning(f"⚠️ เลือกไพ่ให้ครบ 3 ใบก่อนนะครับ (เลือกแล้ว {len(selected_cards)} ใบ)")
    else:
        roles_label=["สถานการณ์ปัจจุบัน","แนวโน้มระยะสั้น","คำแนะนำ"]
        tarot_cards=[{"role":roles_label[i],**c} for i,c in enumerate(selected_cards[:3])]
        with st.spinner(f"✨ ดึงข้อมูล {symbol}..."):
            stock=get_stock_data(symbol)
        if not stock: st.error(f"❌ ไม่พบ '{symbol}' — เช่น NVDA, BTC-USD, SCB.BK")
        else:
            st.markdown(f"<div class='section-header'>{'🪙' if stock['is_crypto'] else '📊'} {stock['symbol']}</div>",unsafe_allow_html=True)
            st.line_chart(stock["close_series"])
            m1,m2,m3=st.columns(3)
            m1.metric("ราคาปัจจุบัน",stock["price"],f"{stock['arrow']}{abs(stock['change_pct'])}%")
            m2.metric("RSI",stock["rsi"],stock["rsi_signal"])
            m3.metric("แนวโน้ม",stock["ma_signal"])
            ew=stock["elliott"]
            st.markdown(f"""<div class="glass-card"><div style='color:#ce93d8;font-weight:600'>🌊 Elliott Wave</div><div style='font-size:1.3em;margin:6px 0'>{ew['wave_emoji']} <b>{ew['wave_pos']}</b></div><div style='color:#888;font-size:0.85em'>ระยะยาว: {ew['trend_long']} | ระยะสั้น: {ew['trend_short']}</div></div>""",unsafe_allow_html=True)
            clr={"BUY":"#00e676","SELL":"#ff1744","WAIT":"#ffa000"}.get(stock["signal_en"],"#ffa000")
            st.markdown(f"""<div class="{stock['cls']}"><div style='font-family:Playfair Display,serif;font-size:1.8em;color:{clr};font-weight:900;margin-bottom:4px'>{stock['signal']}</div><div style='color:#aaa;font-size:0.88em;margin-bottom:14px'>{stock['desc']}</div><table style='width:100%;color:#eee;font-size:0.92em'><tr><td style='padding:5px 0'>🎯 TP1 (ระยะสั้น)</td><td style='text-align:right'><b style='color:#69f0ae'>{stock['tp1']}</b></td></tr><tr><td style='padding:5px 0'>🎯 TP2</td><td style='text-align:right'><b style='color:#40c4ff'>{stock['tp2']}</b></td></tr><tr><td style='padding:5px 0'>🎯 TP3</td><td style='text-align:right'><b style='color:#e040fb'>{stock['tp3']}</b></td></tr><tr><td style='padding:5px 0'>🎯 TP4 (ระยะยาว)</td><td style='text-align:right'><b style='color:#FFD700'>{stock['tp4']}</b></td></tr><tr><td style='padding:5px 0'>🛑 ตัดขาดทุน</td><td style='text-align:right'><b style='color:#ff6b6b'>{stock['sl']}</b></td></tr></table></div>""",unsafe_allow_html=True)
            st.markdown("<div class='section-header'>📐 แนวรับ — แนวต้าน</div>",unsafe_allow_html=True)
            lc,rc=st.columns(2)
            with lc:
                st.markdown("<div style='color:#ff5252;font-weight:600;margin-bottom:6px'>🔴 แนวต้าน</div>",unsafe_allow_html=True)
                for i,r in enumerate(stock["resistances"]): st.markdown(f"<div style='background:rgba(255,82,82,0.1);border:1px solid rgba(255,82,82,0.3);border-radius:8px;padding:8px 12px;margin:4px 0;color:#ff8a80'>R{i+1}: <b>{r}</b></div>",unsafe_allow_html=True)
            with rc:
                st.markdown("<div style='color:#69f0ae;font-weight:600;margin-bottom:6px'>🔵 แนวรับ</div>",unsafe_allow_html=True)
                for i,s in enumerate(stock["supports"]): st.markdown(f"<div style='background:rgba(105,240,174,0.1);border:1px solid rgba(105,240,174,0.3);border-radius:8px;padding:8px 12px;margin:4px 0;color:#69f0ae'>S{i+1}: <b>{s}</b></div>",unsafe_allow_html=True)
            with st.spinner("🔭 คำนวณดาว..."):
                astro_str,_=get_astro_today()
            with st.expander("🪐 ตำแหน่งดาววันนี้"): st.code(astro_str)
            sign_en,sign_th=get_birth_sign(birth) if birth else (None,None)
            if sign_th: st.markdown(f"""<div class="glass-card" style='text-align:center'><div style='font-family:Playfair Display,serif;color:#FFD700;font-size:1.1em;font-weight:700'>♈ ราศีเกิดของคุณ</div><div style='font-size:1.8em;font-weight:900;background:linear-gradient(90deg,#FFD700,#FFA500);-webkit-background-clip:text;-webkit-text-fill-color:transparent'>{sign_th} ({sign_en})</div></div>""",unsafe_allow_html=True)
            else: sign_en,sign_th="Unknown","ไม่ทราบ"
            st.markdown("<div class='section-header'>📅 วันดี/วันร้ายสัปดาห์นี้</div>",unsafe_allow_html=True)
            weekly=get_weekly(); cols=st.columns(7)
            for i,d in enumerate(weekly):
                with cols[i]:
                    style="color:#e040fb;font-weight:700" if d["is_today"] else "color:#aaa"
                    st.markdown(f"<div style='{style};font-size:0.78em;text-align:center'>{'📍' if d['is_today'] else ''}{d['day']}<br><span style='font-size:0.85em'>{d['date']}</span><br>{d['verdict']}</div>",unsafe_allow_html=True)
            st.markdown("<div class='section-header'>✨ AstroTrade AI Analysis</div>",unsafe_allow_html=True)
            with st.spinner("✨ กำลังวิเคราะห์..."):
                result=analyze(stock,astro_str,sign_th,sign_en,weekly,birth,tarot_cards,GEMINI_KEY)
            st.markdown(f"<div class='glass-card'>{result}</div>",unsafe_allow_html=True)
            st.divider()
            st.markdown("""<div class="footer-text">✦ ASTROTRADE 2025 ✦ WHERE THE STARS MEET THE MARKET 🌌<br><span style='font-size:0.85em'>เป็นข้อมูลประกอบการตัดสินใจเท่านั้น ไม่ใช่คำแนะนำทางการเงิน</span></div>""",unsafe_allow_html=True)
