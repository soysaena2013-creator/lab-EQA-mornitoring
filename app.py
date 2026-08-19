import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

st.set_page_config(page_title="EQA Tracking System", page_icon="🔬", layout="wide")

DATA_FILE = 'eqa_data.csv'

@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            'Cycle', 'Department', 'Test_Name', 'Test_Type',
            'Lab_Result', 'Assigned_Value', 'SD', 'SDI', 'Status', 'Remark'
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

st.title("🔬 ระบบติดตามและประเมินผลประสิทธิภาพ EQA")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📝 กรอกผล EQA", "📊 Dashboard สรุปผล", "📋 ประวัติและ Export ข้อมูล"])

# TAB 1: DATA ENTRY
with tab1:
    st.header("แบบฟอร์มบันทึกผล EQA")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        cycle = st.text_input("รอบการทดสอบ (Cycle/Year)", value="1/2026")
        department = st.selectbox("สาขาห้องปฏิบัติการ", [
            "Chemical Pathology", "Hematology", "Microbiology", "Immunology"
        ])
    
    with col_c2:
        test_type = st.radio("ประเภทการทดสอบ", ["Quantitative (เชิงปริมาณ)", "Qualitative (เชิงคุณภาพ)"], horizontal=True)
        test_name = st.text_input("ชื่อรายการทดสอบ (Test Name)", placeholder="เช่น Glucose, HbA1c, Anti-HIV")

    st.markdown("### 📊 ใส่ผลการทดสอบ")
    
    if "Quantitative" in test_type:
        col_q1, col_q2, col_q3 = st.columns(3)
        with col_q1:
            lab_res = st.number_input("ผลการตรวจของแล็บ (Lab Result)", value=0.0, format="%.2f")
        with col_q2:
            assigned_val = st.number_input("ค่าจริง/ค่าอ้างอิง (Assigned Value)", value=0.0, format="%.2f")
        with col_q3:
            sd_val = st.number_input("ค่า SD ของกลุ่ม (SD)", value=1.0, format="%.2f")
        
        if sd_val > 0:
            sdi = (lab_res - assigned_val) / sd_val
            abs_sdi = abs(sdi)
            if abs_sdi <= 2.0:
                status = "Acceptable"
                st.success(f"ค่า SDI: {sdi:.2f} (สถานะ: ผ่านเกณฑ์ / Acceptable)")
            elif abs_sdi < 3.0:
                status = "Warning"
                st.warning(f"ค่า SDI: {sdi:.2f} (สถานะ: เฝ้าระวัง / Warning)")
            else:
                status = "Unacceptable"
                st.error(f"ค่า SDI: {sdi:.2f} (สถานะ: ไม่ผ่านเกณฑ์ / Unacceptable)")
        else:
            sdi = 0.0
            status = "Invalid"
            st.info("กรุณาระบุค่า SD ที่มากกว่า 0")
            
        qual_lab = str(lab_res)
        qual_assigned = str(assigned_val)
        
    else:
        col_ql1, col_ql2 = st.columns(2)
        with col_ql1:
            qual_lab = st.selectbox("ผลการตรวจของแล็บ", ["Positive", "Negative", "Reactive", "Non-reactive", "Equivocal"])
        with col_ql2:
            qual_assigned = st.selectbox("ค่าจริง/ค่าอ้างอิง", ["Positive", "Negative", "Reactive", "Non-reactive", "Equivocal"])
            
        sdi = np.nan
        sd_val = np.nan
        if qual_lab == qual_assigned:
            status = "Acceptable"
            st.success("สถานะ: ผ่านเกณฑ์ (Concordant / Agree)")
        else:
            status = "Unacceptable"
            st.error("สถานะ: ไม่ผ่านเกณฑ์ (Discordant / Disagree)")

    remark = st.text_area("บันทึกเพิ่มเติม / สาเหตุกรณีไม่ผ่าน", placeholder="เช่น เปลี่ยน Lot Reagent, สอบเทียบเครื่องใหม่")

    if st.button("💾 บันทึกผล EQA", type="primary"):
        new_row = {
            'Cycle': cycle,
            'Department': department,
            'Test_Name': test_name,
            'Test_Type': 'Quantitative' if "Quantitative" in test_type else 'Qualitative',
            'Lab_Result': qual_lab,
            'Assigned_Value': qual_assigned,
            'SD': sd_val,
            'SDI': round(sdi, 2) if not np.isnan(sdi) else np.nan,
            'Status': status,
            'Remark': remark
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df)
        st.cache_data.clear()
        st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
        st.rerun()

# TAB 2: DASHBOARD
with tab2:
    st.header("Dashboard สรุปผลและวิเคราะห์ประสิทธิภาพ")
    
    if not df.empty:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            selected_cycle = st.multiselect("เลือกรอบการทดสอบ", options=df['Cycle'].unique(), default=df['Cycle'].unique())
        with col_f2:
            selected_dept = st.multiselect("เลือกสาขา", options=df['Department'].unique(), default=df['Department'].unique())

        filtered_df = df[(df['Cycle'].isin(selected_cycle)) & (df['Department'].isin(selected_dept))]

        total_tests = len(filtered_df)
        acceptable_tests = len(filtered_df[filtered_df['Status'] == 'Acceptable'])
        warning_tests = len(filtered_df[filtered_df['Status'] == 'Warning'])
        unacceptable_tests = len(filtered_df[filtered_df['Status'] == 'Unacceptable'])
        
        pass_rate = (acceptable_tests / total_tests * 100) if total_tests > 0 else 0

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("รายการทดสอบทั้งหมด", f"{total_tests} รายการ")
        m2.metric("ผ่านเกณฑ์ (Pass)", f"{acceptable_tests}", f"{pass_rate:.1f}%")
        m3.metric("เฝ้าระวัง (Warning)", f"{warning_tests}")
        m4.metric("ไม่ผ่าน (Unacceptable)", f"{unacceptable_tests}")
        m5.metric("อัตราความสำเร็จภาพรวม", f"{pass_rate:.1f}%")

        st.markdown("---")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.subheader("สัดส่วนผลการประเมินแยกตามสาขา")
            dept_summary = filtered_df.groupby(['Department', 'Status']).size().reset_index(name='Count')
            fig_bar = px.bar(
                dept_summary, x='Department', y='Count', color='Status',
                color_discrete_map={'Acceptable': '#2ecc71', 'Warning': '#f1c40f', 'Unacceptable': '#e74c3c'},
                barmode='group', text='Count'
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_g2:
            st.subheader("แนวโน้ม SDI Chart (Quantitative)")
            quant_df = filtered_df[filtered_df['Test_Type'] == 'Quantitative'].dropna(subset=['SDI'])
            if not quant_df.empty:
                fig_sdi = px.scatter(
                    quant_df, x='Test_Name', y='SDI', color='Status',
                    color_discrete_map={'Acceptable': '#2ecc71', 'Warning': '#f1c40f', 'Unacceptable': '#e74c3c'},
                    hover_data=['Cycle', 'Department', 'Lab_Result', 'Assigned_Value'],
                    title="SDI Distribution (+2SD ถึง -2SD คือช่วงยอมรับได้)"
                )
                fig_sdi.add_hline(y=2.0, line_dash="dash", line_color="orange")
                fig_sdi.add_hline(y=-2.0, line_dash="dash", line_color="orange")
                fig_sdi.add_hline(y=3.0, line_dash="dash", line_color="red")
                fig_sdi.add_hline(y=-3.0, line_dash="dash", line_color="red")
                st.plotly_chart(fig_sdi, use_container_width=True)
            else:
                st.info("ไม่มีข้อมูล Quantitative ในช่วงที่เลือก")
    else:
        st.info("ยังไม่มีข้อมูลในระบบ")

# TAB 3: DATA TABLE & EXPORT
with tab3:
    st.header("ตารางข้อมูลทั้งหมด")
    st.dataframe(df, use_container_width=True)
    
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv_data,
        file_name='eqa_tracking_summary.csv',
        mime='text/csv'
    )