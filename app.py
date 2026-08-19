import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# 1. รายชื่อหุ้น SET100 (จัดกลุ่ม Sector ครบถ้วน เพื่อให้เห็นภาพชัดเจนว่าเงินไหลไปเซกเตอร์ไหน)
set100_by_sector = {
    'Energy & Utilities': ['PTT.BK', 'PTTEP.BK', 'BCP.BK', 'TOP.BK', 'PTTGC.BK', 'GULF.BK', 'GPSC.BK', 'BGRIM.BK', 'EA.BK', 'EGCO.BK', 'RATCH.BK', 'BANPU.BK', 'OR.BK', 'CKP.BK', 'BCPG.BK', 'SUPER.BK'],
    'Banking': ['KBANK.BK', 'SCB.BK', 'BBL.BK', 'KTB.BK', 'TTB.BK', 'TISCO.BK', 'KKP.BK'],
    'Information & Communication': ['ADVANC.BK', 'TRUE.BK', 'INTUCH.BK'],
    'Commerce (Retail)': ['CPALL.BK', 'CPAXT.BK', 'CRC.BK', 'COM7.BK', 'HMPRO.BK', 'BJC.BK', 'GLOBAL.BK', 'DOHOME.BK'],
    'Property & Construction': ['SCC.BK', 'CPN.BK', 'LH.BK', 'AP.BK', 'SPALI.BK', 'SIR.BK', 'ORI.BK', 'QH.BK', 'AMATA.BK', 'WHA.BK', 'AWC.BK', 'CENTEL.BK'],
    'Healthcare': ['BDMS.BK', 'BH.BK', 'BCH.BK', 'CHG.BK', 'MEGA.BK'],
    'Transportation & Logistics': ['AOT.BK', 'BEM.BK', 'BTS.BK', 'AAV.BK', 'PSL.BK', 'PRM.BK'],
    'Food & Beverage': ['MINT.BK', 'OSP.BK', 'CBG.BK', 'ITC.BK', 'TU.BK', 'SORKON.BK'],
    'Electronic Components': ['DELTA.BK', 'KCE.BK', 'HANA.BK', 'SVI.BK']
}

def scan_set100_2months_flow():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=65) # ย้อนหลังประมาณ 2 เดือน (65 วันปฏิทิน หรือราว 42 วันทำการ)
    
    print(f"🔍 กำลังแกะรอย Fund Flow ต่างชาติใน SET100 ย้อนหลัง 2 เดือน...\n")
    
    sector_results = []
    
    for sector, tickers in set100_by_sector.items():
        sector_price_change = []
        sector_vol_spike = []
        
        for ticker in tickers:
            try:
                data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)
                if len(data) < 30:
                    continue
                
                # คำนวณผลตอบแทนราคาย้อนหลัง 2 เดือน
                start_p = float(data['Close'].iloc[0])
                end_p = float(data['Close'].iloc[-1])
                pct_change = ((end_p - start_p) / start_p) * 100
                
                # เช็ควอลุ่มผิดปกติ (Volume Spike ในช่วง 2 เดือนนี้)
                avg_vol = float(data['Volume'].mean())
                max_vol = float(data['Volume'].max())
                vol_ratio = max_vol / avg_vol if avg_vol > 0 else 0
                
                sector_price_change.append(pct_change)
                sector_vol_spike.append(vol_ratio)
            except:
                continue
        
        # คำนวณค่าเฉลี่ยของแต่ละ Sector เพื่อดูทิศทางว่ากลุ่มไหนเงินเข้าหรือไหลออก
        if sector_price_change:
            avg_sector_return = sum(sector_price_change) / len(sector_price_change)
            avg_vol_spike = sum(sector_vol_spike) / len(sector_vol_spike)
            
            # ประเมินสถานะ Flow ตามพฤติกรรมราคาและวอลุ่ม
            if avg_sector_return >= 2.5:
                flow_status = '🔥 ต่างชาติสุมหัวซื้อสะสม (Net Inflow)'
            elif avg_sector_return <= -2.5:
                flow_status = '⚠️ โดนสาดเทขายทำกำไร (Net Outflow)'
            else:
                flow_status = '⚖️ ทรงตัว ไซด์เวย์ (Neutral)'
                
            sector_results.append({
                'Sector': sector,
                '2M Return (%)': round(avg_sector_return, 2),
                'Avg Vol Intensity': round(avg_vol_spike, 2),
                'Flow Status': flow_status
            })
            
    df_result = pd.DataFrame(sector_results)
    return df_result.sort_values(by='2M Return (%)', ascending=False)

# สั่งรันโปรแกรม
result_df = scan_set100_2months_flow()

# แสดงผลลัพธ์
print("="*80)
print("📊 รายงานวิเคราะห์ Fund Flow เซกเตอร์ SET100 ย้อนหลัง 2 เดือน")
print("="*80)
print(result_df.to_string(index=False))
print("="*80)
