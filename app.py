import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# ตั้งค่าหน้าจอเว็บแอป
st.set_page_config(page_title="SET100 Sector Flow Scanner", page_icon="📈", layout="wide")

st.title("📈 SET100 Sector Flow & Momentum Scanner (yfinance)")
st.write("ระบบสแกนทิศทางเงินทุน (Fund Flow) และผลตอบแทนรายเซกเตอร์ในตลาดหุ้นไทย ย้อนหลัง 2 เดือนเต็ม!")

# รายชื่อหุ้น SET100 จัดแบ่งตาม Sector มาตรฐานตลาดหุ้นไทย (.BK)
set100_by_sector = {
    'Energy & Utilities': ['PTT.BK', 'PTTEP.BK', 'BCP.BK', 'TOP.BK', 'PTTGC.BK', 'GULF.BK', 'GPSC.BK', 'BGRIM.BK', 'EA.BK', 'EGCO.BK', 'RATCH.BK', 'BANPU.BK', 'OR.BK', 'CKP.BK'],
    'Banking': ['KBANK.BK', 'SCB.BK', 'BBL.BK', 'KTB.BK', 'TTB.BK', 'TISCO.BK', 'KKP.BK'],
    'Information & Communication': ['ADVANC.BK', 'TRUE.BK', 'INTUCH.BK'],
    'Commerce (Retail)': ['CPALL.BK', 'CPAXT.BK', 'CRC.BK', 'COM7.BK', 'HMPRO.BK', 'BJC.BK', 'GLOBAL.BK'],
    'Property & Construction': ['SCC.BK', 'CPN.BK', 'LH.BK', 'AP.BK', 'SPALI.BK', 'ORI.BK', 'QH.BK', 'AMATA.BK', 'WHA.BK', 'AWC.BK'],
    'Healthcare': ['BDMS.BK', 'BH.BK', 'BCH.BK', 'CHG.BK', 'MEGA.BK'],
    'Transportation & Logistics': ['AOT.BK', 'BEM.BK', 'BTS.BK', 'AAV.BK', 'PRM.BK'],
    'Food & Beverage': ['MINT.BK', 'OSP.BK', 'CBG.BK', 'ITC.BK', 'TU.BK'],
    'Electronic Components': ['DELTA.BK', 'KCE.BK', 'HANA.BK', 'SVI.BK']
}

if st.button("🚀 เริ่มสแกน SET100 Sector Flow ย้อนหลัง 2 เดือน"):
    with st.spinner("กำลังดึงข้อมูลราคาและวอลุ่มหุ้นไทย SET100 ผ่าน yfinance... อดใจรอนิดเดียวนะเพื่อน!"):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=65) # กรอบเวลาประมาณ 2 เดือน
        
        sector_results = []
        
        for sector, tickers in set100_by_sector.items():
            sector_price_change = []
            sector_vol_spike = []
            
            for ticker in tickers:
                try:
                    # ดึงข้อมูลจาก yfinance แบบคลีนๆ
                    data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)
                    
                    if not data.empty and len(data) > 10:
                        # ตรวจสอบโครงสร้าง DataFrame ของ yfinance (เผื่อกรณี MultiIndex)
                        if isinstance(data.columns, pd.MultiIndex):
                            close_prices = data['Close'][ticker]
                            volumes = data['Volume'][ticker]
                        else:
                            close_prices = data['Close']
                            volumes = data['Volume']
                            
                        start_p = float(close_prices.iloc[0])
                        end_p = float(close_prices.iloc[-1])
                        pct_change = ((end_p - start_p) / start_p) * 100
                        
                        avg_vol = float(volumes.mean())
                        max_vol = float(volumes.max())
                        vol_ratio = max_vol / avg_vol if avg_vol > 0 else 1.0
                        
                        sector_price_change.append(pct_change)
                        sector_vol_spike.append(vol_ratio)
                except Exception as e:
                    continue
            
            # คำนวณค่าเฉลี่ยของแต่ละ Sector
            if sector_price_change:
                avg_sector_return = sum(sector_price_change) / len(sector_price_change)
                avg_vol_spike = sum(sector_vol_spike) / len(sector_vol_spike)
                
                if avg_sector_return >= 1.5:
                    flow_status = '🔥 ต่างชาติสุมหัวซื้อสะสม (Net Inflow)'
                elif avg_sector_return <= -1.5:
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
            
            st.success("✅ สแกนข้อมูล SET100 สำเร็จเรียบร้อย!")
            st.dataframe(df_result, use_container_width=True)
        else:
            st.error("❌ ไม่สามารถดึงข้อมูลได้ในรอบนี้ ลองกดปุ่มใหม่อีกครั้งนะเพื่อน")

st.markdown("---")
st.markdown("💡 **มุมมองเพื่อนซี้:** โค้ดนี้ถูกปรับแต่งให้รองรับโครงสร้างข้อมูลของ `yfinance` แบบสมบูรณ์ เพื่อให้มึงเห็นภาพชัดๆ ว่าเงินทุนใน SET100 กำลังโยกย้ายไปซุกตัวอยู่ที่เซกเตอร์ไหน ลุยโลดเพื่อน!")
