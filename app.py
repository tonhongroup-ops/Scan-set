import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# ตั้งค่าหน้าจอ Streamlit
st.set_page_config(page_title="SET100 Sector Flow Scanner", page_icon="📊", layout="wide")

st.title("📊 SET100 Sector Flow & Fund Flow Scanner")
st.write("ระบบสแกนทิศทางเงินทุนและผลตอบแทนรายเซกเตอร์ตลาดหุ้นไทย ขับเคลื่อนด้วยพลัง FMP API ส่วนตัวของมึง!")

# ฝัง FMP API Key ของมึงไว้เรียบร้อย เบ็ดเสร็จในตัว
FMP_API_KEY = "JccLhsHLrNMeQSphHit6kKv4sSw9aKiK"

# จัดกลุ่มหุ้น SET100 ตามเซกเตอร์หลัก (ใช้สัญลักษณ์ตามมาตรฐาน FMP)
set100_by_sector = {
    'Energy & Utilities': ['PTT.BK', 'PTTEP.BK', 'BCP.BK', 'TOP.BK', 'PTTGC.BK', 'GULF.BK', 'GPSC.BK'],
    'Banking': ['KBANK.BK', 'SCB.BK', 'BBL.BK', 'KTB.BK', 'TTB.BK'],
    'Information & Communication': ['ADVANC.BK', 'TRUE.BK', 'INTUCH.BK'],
    'Commerce (Retail)': ['CPALL.BK', 'CRC.BK', 'COM7.BK', 'HMPRO.BK'],
    'Property & Construction': ['SCC.BK', 'CPN.BK', 'LH.BK', 'AP.BK', 'AMATA.BK', 'WHA.BK'],
    'Healthcare': ['BDMS.BK', 'BH.BK', 'BCH.BK'],
    'Transportation & Logistics': ['AOT.BK', 'BEM.BK', 'BTS.BK'],
    'Food & Beverage': ['MINT.BK', 'OSP.BK', 'CBG.BK', 'TU.BK'],
    'Electronic Components': ['DELTA.BK', 'KCE.BK', 'HANA.BK']
}

# ปุ่มกดเริ่มรันระบบสแกน
if st.button("🚀 เริ่มสแกน Fund Flow ย้อนหลัง 2 เดือน"):
    with st.spinner("กำลังเชื่อมต่อ FMP API เพื่อดึงข้อมูลราคาและคำนวณวอลุ่ม... รอแป๊บเดียวรู้เรื่องเพื่อน!"):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=65) # กรอบเวลา 2 เดือน
        
        sector_results = []
        
        for sector, tickers in set100_by_sector.items():
            sector_price_change = []
            sector_vol_spike = []
            
            for ticker in tickers:
                try:
                    # ดึงข้อมูล Historical Price จาก FMP API
                    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?from={start_date.strftime('%Y-%m-%d')}&to={end_date.strftime('%Y-%m-%d')}&apikey={FMP_API_KEY}"
                    response = requests.get(url, timeout=10)
                    data = response.json()
                    
                    if 'historical' in data and len(data['historical']) > 5:
                        hist = data['historical']
                        start_p = float(hist[-1]['close']) # ราคาเริ่มต้นช่วงย้อนหลัง
                        end_p = float(hist[0]['close'])     # ราคาปัจจุบันล่าสุด
                        pct_change = ((end_p - start_p) / start_p) * 100
                        
                        # คำนวณความหนาแน่นของ Volume ซื้อขาย
                        volumes = [float(day['volume']) for day in hist]
                        avg_vol = sum(volumes) / len(volumes) if volumes else 1
                        max_vol = max(volumes) if volumes else 1
                        vol_ratio = max_vol / avg_vol if avg_vol > 0 else 1.0
                        
                        sector_price_change.append(pct_change)
                        sector_vol_spike.append(vol_ratio)
                except Exception as e:
                    continue
            
            # คำนวณค่าเฉลี่ยรายเซกเตอร์เมื่อมีหุ้นรอดในกลุ่ม
            if sector_price_change:
                avg_sector_return = sum(sector_price_change) / len(sector_price_change)
                avg_vol_spike = sum(sector_vol_spike) / len(sector_vol_spike)
                
                # กำหนดสถานะกระแสเงินทุน (Fund Flow Status)
                if avg_sector_return >= 1.0:
                    flow_status = '🔥 ต่างชาติสุมหัวซื้อสะสม (Net Inflow)'
                elif avg_sector_return <= -1.0:
                    flow_status = '⚠️ โดนสาดเทขายทำกำไร (Net Outflow)'
                else:
                    flow_status = '⚖️ ทรงตัว ไซด์เวย์ (Neutral)'
                    
                sector_results.append({
                    'Sector': sector,
                    'Return_2M (%)': round(avg_sector_return, 2),
                    'Vol_Intensity': round(avg_vol_spike, 2),
                    'Flow_Status': flow_status
                })
                
        # แสดงผลลัพธ์ในรูปแบบตาราง Streamlit
        if sector_results:
            df_result = pd.DataFrame(sector_results)
            if 'Return_2M (%)' in df_result.columns:
                df_result = df_result.sort_values(by='Return_2M (%)', ascending=False)
            
            st.success("✅ สแกนข้อมูลสำเร็จเรียบร้อย ลุยวิเคราะห์หุ้นเล่นรอบต่อได้เลย!")
            st.dataframe(df_result, use_container_width=True)
        else:
            st.error("❌ ไม่สามารถดึงข้อมูลชุดนี้ได้ ลองตรวจสอบการเชื่อมต่อหรือชื่อหุ้นใน FMP อีกครั้งนะเพื่อน")

st.markdown("---")
st.markdown("💡 **มุมมองเพื่อนซี้:** โค้ดนี้ถูกออกแบบมาเพื่อให้มึงต่อยอดดึงงบการเงินรายไตรมาส หรือสแกนหุ้นเติบโตสายเทคโนโลยี นวัตกรรมใหม่ๆ ผ่าน FMP ได้ทันที มีอะไรให้กูเขียนฟังก์ชันเสริมบอกได้เลยเว้ย!")
                
