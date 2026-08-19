import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.title("📊 SET100 Sector Flow Scanner (by FMP API)")
st.write("ระบบสแกนทิศทางตลาดและผลตอบแทนรายเซกเตอร์ ดึงข้อมูลทรงพลังผ่าน FMP API ของมึงเอง!")

# ฝัง FMP API Key ของมึงไว้เรียบร้อย ไม่ต้องกรอกเองแล้วเว้ยเพื่อน!
FMP_API_KEY = "JccLhsHLrNMeQSphHit6kKv4sSw9aKiK"

# รายชื่อหุ้น SET100 จัดตาม Sector
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

if st.button("🚀 เริ่มสแกนข้อมูลผ่าน FMP API"):
    with st.spinner("กำลังต่อสายตรงดึงข้อมูลจาก FMP API... รอแป๊บเดียวรู้เรื่อง!"):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=65) # ย้อนหลัง 2 เดือน
        
        sector_results = []
        
        for sector, tickers in set100_by_sector.items():
            sector_price_change = []
            sector_vol_spike = []
            
            for ticker in tickers:
                try:
                    # ดึงข้อมูลราคา Historical Daily ผ่าน FMP API
                    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?from={start_date.strftime('%Y-%m-%d')}&to={end_date.strftime('%Y-%m-%d')}&apikey={FMP_API_KEY}"
                    response = requests.get(url)
                    data = response.json()
                    
                    if 'historical' in data and len(data['historical']) > 5:
                        hist = data['historical']
                        start_p = float(hist[-1]['close']) # วันเก่าสุด
                        end_p = float(hist[0]['close'])     # วันล่าสุด
                        pct_change = ((end_p - start_p) / start_p) * 100
                        
                        # คำนวณความหนาแน่นของ Volume
                        volumes = [float(day['volume']) for day in hist]
                        avg_vol = sum(volumes) / len(volumes) if volumes else 1
                        max_vol = max(volumes) if volumes else 1
                        vol_ratio = max_vol / avg_vol if avg_vol > 0 else 1.0
                        
                        sector_price_change.append(pct_change)
                        sector_vol_spike.append(vol_ratio)
                except Exception as e:
                    continue
            
            if sector_price_change:
                avg_sector_return = sum(sector_price_change) / len(sector_price_change)
                avg_vol_spike = sum(sector_vol_spike) / len(sector_vol_spike)
                
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
                
        if sector_results:
            df_result = pd.DataFrame(sector_results)
            if 'Return_2M (%)' in df_result.columns:
                df_result = df_result.sort_values(by='Return_2M (%)', ascending=False)
            
            st.success("✅ ดึงข้อมูลผ่าน FMP API สำเร็จเรียบร้อย!")
            st.dataframe(df_result, use_container_width=True)
        else:
            st.error("❌ ไม่พบข้อมูล ลองเช็คการเชื่อมต่อหรือ API Key อีกทีนะเพื่อน")
            
