import streamlit as st
import pandas as pd

st.set_page_config(page_title="Napho Lab KPI Center", page_icon="🔬", layout="wide")

st.title("🔬 Executive Command Center: ตัวชี้วัดคุณภาพ 10 หัวข้อ")
st.caption("กลุ่มงานเทคนิคการแพทย์ โรงพยาบาลนาโพธิ์")

df = st.session_state.get("kpi_records", pd.DataFrame())
latest = df.iloc[-1] if not df.empty else None

st.markdown("---")

# Row 1: Top Critical Metrics
c1, c2, c3 = st.columns(3)
with c1:
    val = latest["Blood_Wrong_Person_Pct"] + latest["Blood_Wrong_Group_Pct"] if latest is not None else 0.0
    st.metric("🩸 1. จ่ายเลือดผิดคน/ผิดหมู่", f"{val:.1f}%", delta="ผ่านเกณฑ์ (0%)" if val == 0 else "🔴 ไม่ผ่านเกณฑ์", delta_color="normal" if val == 0 else "inverse")
with c2:
    val = latest["Rejection_Rate_Pct"] if latest is not None else 0.1
    st.metric("🧪 2. ปฏิเสธสิ่งส่งตรวจ", f"{val:.3f}%", delta=f"เป้าหมาย < 0.3%", delta_color="normal" if val < 0.3 else "inverse")
with c3:
    val = latest["Overall_QA_KPI_Pct"] if latest is not None else 100.0
    st.metric("🛡️ 3. การประกันคุณภาพ (QA/IQC/EQA)", f"{val:.1f}%", delta="เป้าหมาย 100%")

st.markdown("---")

# Row 2: Operational & Speed
c4, c5, c6 = st.columns(3)
with c4:
    val = latest["Downtime_Pct"] if latest is not None else 0.0
    st.metric("⚙️ 4. Downtime เครื่องมือ", f"{val:.1f}%", delta="เป้าหมาย < 1%", delta_color="normal" if val < 1.0 else "inverse")
with c5:
    val = latest["Missed_Report_Pct"] if latest is not None else 0.0
    st.metric("⚠️ 5. Missed Report", f"{val:.2f}%", delta="เป้าหมาย < 0.3%", delta_color="normal" if val < 0.3 else "inverse")
with c6:
    val = latest["Critical_Report_Pct"] if latest is not None else 100.0
    st.metric("⏱️ 6. รายงานค่าวิกฤตครบถ้วน", f"{val:.1f}%", delta="เป้าหมาย 100%")

st.markdown("---")

# Row 3: Safety, CSAT & RLU
c7, c8, c9 = st.columns(3)
with c7:
    val = latest["Staff_Safety_Avg_Pct"] if latest is not None else 100.0
    st.metric("🛡️ 7. ความปลอดภัยเจ้าหน้าที่", f"{val:.1f}%", delta="เป้าหมาย 100%")
with c8:
    val = latest["CSAT_Patient_Pct"] if latest is not None else 88.0
    st.metric("😊 8. ความพึงพอใจผู้ป่วย/ญาติ", f"{val:.1f}%", delta="เป้าหมาย > 80%")
with c9:
    val = latest["FT3_Redundant_Reduction_Pct"] if latest is not None else 95.0
    st.metric("📉 9. ลดการสั่ง FT3 ซ้ำซ้อน", f"{val:.1f}%", delta="เป้าหมาย > 90%")

st.markdown("---")
st.info("📥 สั่งการบันทึกข้อมูลประจำเดือนใหม่ หรือดาวน์โหลดรายงาน Excel ได้ที่นี่")
if st.button("📝 ไปที่แบบฟอร์มบันทึกข้อมูล 10 หัวข้อ (Data Input Form)", use_container_width=True):
    st.switch_page("pages/0_📥_Data_Input.py")