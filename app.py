import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

st.title("📊 SET100 Sector Flow Scanner (ย้อนหลัง 2 เดือน)")
st.write("ระบบสแกนทิศทางเงินทุน (Fund Flow) และค่าเฉลี่ยผลตอบแทนรายเซกเตอร์ในตลาดหุ้นไทย")

# รายชื่อหุ้น SET100 จัดตาม Sector
set100_by_sector = {
    'Energy & Utilities': ['PTT.BK', 'PTTEP.BK', 'BCP.BK', 'TOP.BK', 'PTTGC.BK', 'GULF.BK', 'GPSC.BK', 'BGRIM.BK', 'EA.BK', 'EGCO.BK', 'RATCH.BK', 'BANPU.BK', 'OR.BK', 'CKP.BK', 'BCPG.BK'],
    'Banking': ['KBANK.BK', 'SCB.BK', 'BBL.BK', 'KTB.BK', 'TTB.BK', 'TISCO.BK', 'KKP.BK'],
    'Information & Communication': ['ADVANC.BK', 'TRUE.BK', 'INTUCH.BK'],
    'Commerce (Retail)': ['CPALL.BK', 'CPAXT.BK', 'CRC.BK', 'COM7.BK', 'HMPRO.BK', 'BJC.BK', 'GLOBAL.BK', 'DOHOME.BK'],
    'Property & Construction': ['SCC.BK', 'CPN.BK', 'LH.BK', 'AP.BK', 'SPALI.BK', 'ORI.BK', 'QH.BK', 'AMATA.BK', 'WHA.BK', 'AWC.BK', 'CENTEL.BK'],
    'Healthcare': ['BDMS.BK', 'BH.BK', 'BCH.BK', 'CHG.BK', 'MEGA.BK'],
    'Transportation & Logistics': ['AOT.BK', 'BEM.BK', 'BTS.BK', 'AAV.BK', 'PRM.BK'],
    'Food & Beverage': ['MINT.BK', 'OSP.BK', 'CBG.BK', 'ITC.BK', 'TU.BK'],
    'Electronic Components': ['DELTA.BK', 'KCE.BK', 'HANA.BK', 'SVI.BK']
}

if st.button("🚀 เริ่มสแกนข้อมูล Fund Flow ย้อนหลัง 2 เดือน"):
    with st.spinner("กำลังดึงข้อมูลราคาและคำนวณเซกเตอร์... รอแป๊บเดียวนะเพื่อน!"):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=65) # ย้อนหลัง 2 เดือน
        
        sector_results = []
        
        for sector, tickers in set100_by_sector.items():
            sector_price_change = []
            sector_vol_spike = []
            
            for ticker in tickers:
                try:
                    data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)
                    if len(data) < 20:
                        continue
                    
                    start_p = float(data['Close'].iloc[0])
                    end_p = float(data['Close'].iloc[-1])
                    pct_change = ((end_p - start_p) / start_p) * 100
                    
                    avg_vol = float(data['Volume'].mean())
                    max_vol = float(data['Volume'].max())
                    vol_ratio = max_vol / avg_vol if avg_vol > 0 else 0
                    
                    sector_price_change.append(pct_change)
                    sector_vol_spike.append(vol_ratio)
                except Exception as e:
                    continue
            
            if sector_price_change:
                avg_sector_return = sum(sector_price_change) / len(sector_price_change)
                avg_vol_spike = sum(sector_vol_spike) / len(sector_vol_spike)
                
                if avg_sector_return >= 2.0:
                    flow_status = '🔥 ต่างชาติสุมหัวซื้อสะสม (Net Inflow)'
                elif avg_sector_return <= -2.0:
                    flow_status = '⚠️ โดนสาดเทขายทำกำไร (Net Outflow)'
                else:
                    flow_status = '⚖️ ทรงตัว ไซด์เวย์ (Neutral)'
                    
                sector_results.append({
                    'Sector': sector,
                    'Return_2M': round(avg_sector_return, 2),
                    'Vol_Intensity': round(avg_vol_spike, 2),
                    'Flow_Status': flow_status
                })
                
        if sector_results:
            df_result = pd.DataFrame(sector_results)
            # เช็คความปลอดภัยก่อนสั่ง Sort ป้องกัน KeyError
            if 'Return_2M' in df_result.columns:
                df_result = df_result.sort_values(by='Return_2M', ascending=False)
            
            st.success("✅ สแกนข้อมูลสำเร็จเรียบร้อย!")
            st.dataframe(df_result, use_container_width=True)
        else:
            st.warning("⚠️ ไม่พบข้อมูลการประมวลผล กรุณาลองใหม่อีกครั้ง")
            
