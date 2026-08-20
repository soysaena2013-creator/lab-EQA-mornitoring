import streamlit as st
import pandas as pd

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(
    page_title="ระบบประเมินและสรุปผลคะแนน",
    page_icon="📊",
    layout="wide"
)

# ฟังก์ชันสำหรับคำนวณผลการประเมินและสถานะตามเกณฑ์ใหม่
def evaluate_score(score):
    try:
        score = float(score)
        if score == 100:
            return "Excellent", "ผ่านเกณฑ์", "🟢"
        elif 80 <= score < 100:
            return "Good", "ผ่านเกณฑ์", "🟢"
        elif 70 <= score < 80:
            return "Satisfactory", "ยอมรับได้", "🟡"
        elif score < 70:
            return "Unacceptable", "ปรับปรุง", "🔴"
        else:
            return "Invalid", "คะแนนเกินเกณฑ์", "⚪"
    except (ValueError, TypeError):
        return "N/A", "ข้อมูลไม่ถูกต้อง", "⚪"

st.title("📊 ระบบสรุปผลการประเมินคะแนน")

# แสดงตารางเกณฑ์การประเมิน
st.subheader("📋 เกณฑ์การประเมินคะแนน")
criteria_data = {
    "ช่วงคะแนน": ["100", "80 – 99", "70 – 79", "น้อยกว่า 70"],
    "ผลการประเมิน (Rating)": ["Excellent", "Good", "Satisfactory", "Unacceptable"],
    "สถานะ (Status)": ["ผ่านเกณฑ์", "ยอมรับได้ / ผ่านเกณฑ์", "ยอมรับได้", "ปรับปรุง"]
}
st.table(pd.DataFrame(criteria_data))

st.markdown("---")

# ส่วนทดสอบประเมินรายบุคคล / รายรายการ
st.subheader("🔍 ทดสอบคำนวณผลการประเมิน")
user_score = st.number_input("กรอกคะแนน (0 - 100):", min_value=0.0, max_value=100.0, value=85.0, step=1.0)

rating, status, icon = evaluate_score(user_score)

col1, col2, col3 = st.columns(3)
col1.metric("คะแนนที่ได้", f"{user_score:.2f}")
col2.metric("ผลการประเมิน (Rating)", f"{icon} {rating}")
col3.metric("สถานะ (Status)", status)

st.markdown("---")

# ส่วนอัปโหลดไฟล์ Excel / CSV เพื่อประเมินแบบกลุ่ม
st.subheader("📁 ประเมินผลแบบกลุ่ม (Upload File)")
uploaded_file = st.file_uploader("อัปโหลดไฟล์ CSV หรือ Excel (ต้องมีคอลัมน์ 'Score')", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        if 'Score' in df.columns:
            # คำนวณผลลัพธ์ลง DataFrame
            results = df['Score'].apply(evaluate_score)
            df['Rating'] = [r[0] for r in results]
            df['Status'] = [r[1] for r in results]
            
            st.success("ประเมินผลเรียบร้อยแล้ว!")
            st.dataframe(df, use_container_width=True)
            
            # สรุปจำนวนแยกตามกลุ่ม
            st.subheader("📊 สรุปภาพรวม")
            summary = df['Rating'].value_counts().reset_index()
            summary.columns = ['Rating', 'จำนวน (คน/รายการ)']
            st.dataframe(summary)
            
        else:
            st.error("ไม่พบคอลัมน์ 'Score' ในไฟล์ กรุณาตรวจสอบชื่อคอลัมน์")
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")