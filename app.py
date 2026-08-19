import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Global Patent & Tech Momentum Scanner", page_icon="🔬", layout="wide")

st.title("🔬 Global Patent & Tech Momentum Scanner")
st.write("ระบบสแกนหุ้นนวัตกรรม สิทธิบัตรล้ำสมัย และหุ้นเทคฯ โลก ยิงตรงผ่าน FMP API ส่วนตัวของมึง!")

# ฝัง FMP API Key ของมึง
FMP_API_KEY = "JccLhsHLrNMeQSphHit6kKv4sSw9aKiK"

# จัดกลุ่มหุ้นนวัตกรรม / สิทธิบัตรระดับโลกตามธีม
tech_innovation_tickers = {
    'AI & Custom Silicon (ชิปประมวลผลขั้นสูง)': ['NVDA', 'AVGO', 'AMD', 'TSM', 'QCOM'],
    'Semiconductor Equipment (เครื่องมือผลิตชิป/สิทธิบัตรนาโน)': ['ASML', 'KLAC', 'AMAT', 'LRCX'],
    'Cloud & Enterprise Moat (โครงสร้างพื้นฐานดิจิทัล)': ['MSFT', 'GOOGL', 'AMZN', 'META'],
    'Biotech & Gene Editing (นวัตกรรมการแพทย์/ยีน)': ['CRSP', 'EDIT', 'REGN', 'VRTX']
}

if st.button("🚀 เริ่มสแกนหุ้นนวัตกรรมและสิทธิบัตรย้อนหลัง 2 เดือน"):
    with st.spinner("กำลังดึงข้อมูลขุมทรัพย์สิทธิบัตรและราคาหุ้นผ่าน FMP API... รอแป๊บเดียวเพื่อน!"):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=65)
        
        results = []
        
        for theme, tickers in tech_innovation_tickers.items():
            for ticker in tickers:
                try:
                    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?from={start_date.strftime('%Y-%m-%d')}&to={end_date.strftime('%Y-%m-%d')}&apikey={FMP_API_KEY}"
                    response = requests.get(url, timeout=10)
                    data = response.json()
                    
                    if 'historical' in data and len(data['historical']) > 5:
                        hist = data['historical']
                        start_p = float(hist[-1]['close'])
                        end_p = float(hist[0]['close'])
                        pct_change = ((end_p - start_p) / start_p) * 100
                        
                        volumes = [float(day['volume']) for day in hist]
                        avg_vol = sum(volumes) / len(volumes) if volumes else 1
                        max_vol = max(volumes) if volumes else 1
                        vol_ratio = max_vol / avg_vol if avg_vol > 0 else 1.0
                        
                        # คัดกรองตัวที่โมเมนตัมกำลังมาหรือวอลุ่มเข้าพุ่ง
                        status = '🔥 สตอรี่เด่น / โมเมนตัมพุ่ง' if pct_change > 0 else '📉 พักฐานสะสมกำลัง'
                        
                        results.append({
                            'Theme / Sector': theme,
                            'Ticker': ticker,
                            'Current Price ($)': round(end_p, 2),
                            '2M Return (%)': round(pct_change, 2),
                            'Vol Spike (x)': round(vol_ratio, 2),
                            'Status': status
                        })
                except Exception as e:
                    continue
                    
        if results:
            df_result = pd.DataFrame(results)
            df_result = df_result.sort_values(by='2M Return (%)', ascending=False)
            
            st.success("✅ สแกนพอร์ตหุ้นนวัตกรรมและสิทธิบัตรระดับโลกสำเร็จเรียบร้อย!")
            st.dataframe(df_result, use_container_width=True)
        else:
            st.error("❌ เกิดข้อผิดพลาดในการดึงข้อมูล ลองกดใหม่อีกครั้งนะเพื่อน")

st.markdown("---")
st.markdown("💡 **มุมมองเพื่อนซี้:** หุ้นกลุ่มนี้แหละเพื่อนที่ขับเคลื่อนด้วย **'คูเมืองสิทธิบัตร (Patent Moats)'** ของจริง เวลาข่าวเทคโนโลยีหรือชิป AI ใหม่ๆ ออกมา ตัวพวกนี้จะวิ่งตอบสนองไวมาก มึงลองเอาไปรันดู แล้วบอกกูนะว่าอยากเจาะงบการเงินตัวไหนเป็นพิเศษ เดี๋ยวจัดให้เต็มสูบเว้ย!")
