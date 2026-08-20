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

# ----------------------------------------------------
# Master Data Configuration
# ----------------------------------------------------
DEPARTMENTS = [
    "Hematology",
    "Biochemistry",
    "Immunology",
    "Microscopy",
    "Microbiology",
    "Blood bank"
]

TEST_LISTS = {
    "Hematology": ["CBC", "PT&INR", "DCIP", "Hematocrit", "ESR", "Reticulocyte count", "VCT", "20 WBCT"],
    "Biochemistry": ["GLUCOSE", "BUN", "CREATININE", "URIC ACID", "CHOLESTEROL", "TRIGLYCERIDE", "HDL", "LDL", "TOTAL PROTEIN", "ALBUMIN", "TOTAL BILIRUBIN", "DIRECT BILIRUBIN", "AST", "ALT", "ALP", "CALCIUM", "MAGNESIUM", "PHOSPHORUS", "Na", "K", "Cl", "CO2", "Hba1c", "Micro-bilirubin", "Troponin I", "BGM STRIP"],
    "Immunology": ["HBsAg", "HBsAb", "anti-HCV", "HIV", "Syphilis", "Leptospira antibody", "Scrub typhus antibody", "Rheumatoid factor", "melioid titer", "COVID-19 TEST", "Influenza A+B TEST", "COVID-19/Influenza A+B test", "COVID-19/Influenza A+B/RSV test", "Dengue NS1"],
    "Microbiology": ["AFB", "Gram's stain", "TB lamp", "KOH", "Indiaink preperation"],
    "Microscopy": ["UA", "Stool examination", "FOB", "UPT", "Methamphetamine screening test", "Marijuana screening test", "Fern test"],
    "Blood bank": ["ABO grouping", "Rh grouping"]
}

# Qualitative Result Options per Category
QUAL_OPTIONS = {
    "blood_bank": ["Group A", "Group B", "Group AB", "Group O", "Positive", "Negative"],
    "serology": ["Reactive", "Non-reactive", "Equivocal"],
    "pos_neg": ["Positive", "Negative"],
    "stain": ["Found", "Not Found", "Gram Positive Cocci", "Gram Negative Bacilli", "Yeasts Found", "No Organism Found"],
    "titer": ["1:2", "1:4", "1:8", "1:16", "1:32", "1:64", "1:128", "1:256", "Negative"],
    "general": ["Positive", "Negative", "Reactive", "Non-reactive", "Normal", "Abnormal"]
}

def get_qual_options_for_test(test_name):
    if test_name in ["ABO grouping", "Rh grouping"]:
        return QUAL_OPTIONS["blood_bank"]
    elif test_name in ["HBsAg", "HBsAb", "anti-HCV", "HIV", "Syphilis", "Leptospira antibody", "Scrub typhus antibody"]:
        return QUAL_OPTIONS["serology"]
    elif test_name in ["melioid titer"]:
        return QUAL_OPTIONS["titer"]
    elif test_name in ["AFB", "Gram's stain", "KOH", "Indiaink preperation"]:
        return QUAL_OPTIONS["stain"]
    elif test_name in ["UPT", "FOB", "COVID-19 TEST", "Dengue NS1", "Methamphetamine screening test", "Marijuana screening test"]:
        return QUAL_OPTIONS["pos_neg"]
    else:
        return QUAL_OPTIONS["general"]

st.title("🔬 ระบบติดตามและประเมินผลประสิทธิภาพ EQA")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📝 กรอกผล EQA", "📊 Dashboard สรุปผล", "📋 ประวัติและ Export ข้อมูล"])

# ====================================================
# TAB 1: DYNAMIC DATA ENTRY FORM
# ====================================================
with tab1:
    st.header("แบบฟอร์มบันทึกผล EQA (Customized Form)")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        cycle = st.text_input("รอบการทดสอบ (Cycle/Year)", value="1/2026")
        department = st.selectbox("สาขาห้องปฏิบัติการ", DEPARTMENTS)
    
    with col_c2:
        available_tests = TEST_LISTS.get(department, []) + ["อื่นๆ (ระบุเอง)"]
        selected_test = st.selectbox("รายการทดสอบ (Test Name)", available_tests)
        
        if selected_test == "อื่นๆ (ระบุเอง)":
            test_name = st.text_input("ระบุชื่อรายการทดสอบเพิ่มเติม")
        else:
            test_name = selected_test

    st.markdown("---")
    st.subheader(f"📋 ป้อนผลการตรวจ: {test_name if test_name else 'กรุณาเลือกรายการ'}")

    # Set default test mode based on Department
    default_is_quant = department in ["Biochemistry", "Hematology"]
    
    test_type = st.radio(
        "โหมดการประเมินผล", 
        ["Quantitative (เชิงปริมาณ - SDI)", "Qualitative (เชิงคุณภาพ - Concordance)"], 
        index=0 if default_is_quant else 1,
        horizontal=True
    )

    lab_res_val = ""
    assigned_val_str = ""
    sdi = np.nan
    sd_val = np.nan

    if "Quantitative" in test_type:
        st.info("💡 โหมดเชิงปริมาณ: ระบบจะคำนวณ SDI = (Lab Result - Assigned Value) / SD อัตโนมัติ")
        col_q1, col_q2, col_q3 = st.columns(3)
        with col_q1:
            lab_res = st.number_input("ผลการตรวจของแล็บ (Lab Result)", value=0.0, format="%.2f")
        with col_q2:
            assigned_val = st.number_input("ค่าจริง/ค่าอ้างอิง (Assigned Value)", value=0.0, format="%.2f")
        with col_q3:
            sd_val = st.number_input("ค่า SD ของกลุ่ม (SD)", value=1.0, format="%.2f")
        
        lab_res_val = str(lab_res)
        assigned_val_str = str(assigned_val)

        if sd_val > 0:
            sdi = (lab_res - assigned_val) / sd_val
            abs_sdi = abs(sdi)
            if abs_sdi <= 2.0:
                status = "Acceptable"
                st.success(f"✅ ค่า SDI: {sdi:.2f} | สถานะ: ผ่านเกณฑ์ (Acceptable)")
            elif abs_sdi < 3.0:
                status = "Warning"
                st.warning(f"⚠️ ค่า SDI: {sdi:.2f} | สถานะ: เฝ้าระวัง (Warning)")
            else:
                status = "Unacceptable"
                st.error(f"❌ ค่า SDI: {sdi:.2f} | สถานะ: ไม่ผ่านเกณฑ์ (Unacceptable)")
        else:
            sdi = 0.0
            status = "Invalid"
            st.warning("กรุณาระบุค่า SD ที่มากกว่า 0")

    else:
        st.info("💡 โหมดเชิงคุณภาพ: ตัวเลือกคำตอบจะปรับตามประเภทรายการตรวจโดยอัตโนมัติ")
        options = get_qual_options_for_test(test_name)
        
        col_ql1, col_ql2 = st.columns(2)
        with col_ql1:
            lab_res_val = st.selectbox("ผลการตรวจของแล็บ (Lab Result)", options, key="lab_res_qual")
        with col_ql2:
            assigned_val_str = st.selectbox("ค่าจริง/ค่าอ้างอิง (Assigned Value)", options, key="assigned_qual")

        if lab_res_val == assigned_val_str:
            status = "Acceptable"
            st.success("✅ สถานะ: ผ่านเกณฑ์ (Concordant / Agree)")
        else:
            status = "Unacceptable"
            st.error("❌ สถานะ: ไม่ผ่านเกณฑ์ (Discordant / Disagree)")

    remark = st.text_area("บันทึกเพิ่มเติม / สาเหตุกรณีไม่ผ่าน (Root Cause / Corrective Action)", placeholder="เช่น Reagent Lot No., Calibration Status, Human Error")

    if st.button("💾 บันทึกผล EQA", type="primary"):
        if not test_name:
            st.error("กรุณาระบุชื่อรายการทดสอบก่อนบันทึก")
        else:
            new_row = {
                'Cycle': cycle,
                'Department': department,
                'Test_Name': test_name,
                'Test_Type': 'Quantitative' if "Quantitative" in test_type else 'Qualitative',
                'Lab_Result': lab_res_val,
                'Assigned_Value': assigned_val_str,
                'SD': sd_val,
                'SDI': round(sdi, 2) if not np.isnan(sdi) else np.nan,
                'Status': status,
                'Remark': remark
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.cache_data.clear()
            st.success(f"บันทึกข้อมูล '{test_name}' ({department}) เรียบร้อยแล้ว!")
            st.rerun()

# ====================================================
# TAB 2: DASHBOARD ANALYTICS
# ====================================================
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

# ====================================================
# TAB 3: DATA TABLE & EXPORT
# ====================================================
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