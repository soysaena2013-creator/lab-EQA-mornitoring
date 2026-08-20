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
            'Cycle', 'Department', 'Test_Name', 'Sample_ID', 'Test_Type',
            'Lab_Result', 'Assigned_Value', 'SD', 'SDI', 'Status', 'Remark'
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

if 'Sample_ID' not in df.columns:
    df['Sample_ID'] = "Sample 1"

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

tab1, tab2, tab3 = st.tabs(["📝 กรอกผล EQA (Multi-Sample)", "📊 Dashboard สรุปผล", "📋 ประวัติและ Export ข้อมูล"])

with tab1:
    st.header("แบบฟอร์มบันทึกผล EQA (รองรับหลาย Sample ต่อรอบ)")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        cycle = st.text_input("รอบการทดสอบ (Cycle/Year)", value="1/2026")
    with col_c2:
        department = st.selectbox("สาขาห้องปฏิบัติการ", DEPARTMENTS)
    with col_c3:
        available_tests = TEST_LISTS.get(department, []) + ["อื่นๆ (ระบุเอง)"]
        selected_test = st.selectbox("รายการทดสอบ (Test Name)", available_tests)
        test_name = st.text_input("ระบุชื่อรายการทดสอบเพิ่มเติม") if selected_test == "อื่นๆ (ระบุเอง)" else selected_test

    default_is_quant = department in ["Biochemistry", "Hematology"]
    
    col_m1, col_m2 = st.columns([2, 1])
    with col_m1:
        test_type = st.radio(
            "โหมดการประเมินผล", 
            ["Quantitative (เชิงปริมาณ - SDI)", "Qualitative (เชิงคุณภาพ - Concordance)"], 
            index=0 if default_is_quant else 1,
            horizontal=True
        )
    with col_m2:
        num_samples = st.number_input("จำนวนตัวอย่างในรอบนี้ (2-6 ตัวอย่าง)", min_value=1, max_value=10, value=2, step=1)

    st.markdown("---")
    st.subheader(f"📋 ป้อนผลการตรวจสำหรับ: **{test_name}** ({num_samples} ตัวอย่าง)")

    if "Quantitative" in test_type:
        st.info("💡 ท่านสามารถดับเบิ้ลคลิกเพื่อแก้ไข **รหัสตัวอย่าง (Sample ID)**, ผลตรวจ, ค่า Assigned Value และ SD ในตารางได้ตามต้องการ")
        
        init_data = pd.DataFrame({
            'รหัสตัวอย่าง (Sample ID)': [f"Sample {i+1}" for i in range(num_samples)],
            'Lab Result': [0.0] * num_samples,
            'Assigned Value': [0.0] * num_samples,
            'SD': [1.0] * num_samples
        })
        
        edited_df = st.data_editor(
            init_data, 
            num_rows="dynamic", 
            use_container_width=True,
            column_config={
                "รหัสตัวอย่าง (Sample ID)": st.column_config.TextColumn("รหัสตัวอย่าง (Sample ID)", required=True),
                "Lab Result": st.column_config.NumberColumn("Lab Result", format="%.2f"),
                "Assigned Value": st.column_config.NumberColumn("Assigned Value", format="%.2f"),
                "SD": st.column_config.NumberColumn("SD", format="%.2f", min_value=0.01)
            }
        )

    else:
        st.info("💡 ท่านสามารถดับเบิ้ลคลิกเพื่อแก้ไข **รหัสตัวอย่าง (Sample ID)** และเลือกผลตรวจเชิงคุณภาพในตารางได้ตามต้องการ")
        qual_opts = get_qual_options_for_test(test_name)
        
        init_data = pd.DataFrame({
            'รหัสตัวอย่าง (Sample ID)': [f"Sample {i+1}" for i in range(num_samples)],
            'Lab Result': [qual_opts[0]] * num_samples,
            'Assigned Value': [qual_opts[0]] * num_samples
        })
        
        edited_df = st.data_editor(
            init_data,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "รหัสตัวอย่าง (Sample ID)": st.column_config.TextColumn("รหัสตัวอย่าง (Sample ID)", required=True),
                "Lab Result": st.column_config.SelectboxColumn("Lab Result", options=qual_opts, required=True),
                "Assigned Value": st.column_config.SelectboxColumn("Assigned Value", options=qual_opts, required=True)
            }
        )

    remark = st.text_area("บันทึกเพิ่มเติม / สาเหตุกรณีไม่ผ่าน (Root Cause / Corrective Action)", placeholder="เช่น Reagent Lot No., Calibration Status, Human Error")

    if st.button("💾 บันทึกผล EQA ทั้งหมด", type="primary"):
        if not test_name:
            st.error("กรุณาระบุชื่อรายการทดสอบก่อนบันทึก")
        else:
            new_rows = []
            for _, row in edited_df.iterrows():
                sample_id = str(row['รหัสตัวอย่าง (Sample ID)'])
                
                if "Quantitative" in test_type:
                    lab_res = float(row['Lab Result'])
                    assigned_val = float(row['Assigned Value'])
                    sd_val = float(row['SD'])
                    
                    if sd_val > 0:
                        sdi = (lab_res - assigned_val) / sd_val
                        abs_sdi = abs(sdi)
                        if abs_sdi <= 2.0:
                            status = "Acceptable"
                        elif abs_sdi < 3.0:
                            status = "Warning"
                        else:
                            status = "Unacceptable"
                    else:
                        sdi = np.nan
                        status = "Invalid"
                        
                    new_rows.append({
                        'Cycle': cycle,
                        'Department': department,
                        'Test_Name': test_name,
                        'Sample_ID': sample_id,
                        'Test_Type': 'Quantitative',
                        'Lab_Result': str(lab_res),
                        'Assigned_Value': str(assigned_val),
                        'SD': sd_val,
                        'SDI': round(sdi, 2) if not np.isnan(sdi) else np.nan,
                        'Status': status,
                        'Remark': remark
                    })
                else:
                    lab_res_str = str(row['Lab Result'])
                    assigned_val_str = str(row['Assigned Value'])
                    status = "Acceptable" if lab_res_str == assigned_val_str else "Unacceptable"
                    
                    new_rows.append({
                        'Cycle': cycle,
                        'Department': department,
                        'Test_Name': test_name,
                        'Sample_ID': sample_id,
                        'Test_Type': 'Qualitative',
                        'Lab_Result': lab_res_str,
                        'Assigned_Value': assigned_val_str,
                        'SD': np.nan,
                        'SDI': np.nan,
                        'Status': status,
                        'Remark': remark
                    })

            df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
            save_data(df)
            st.cache_data.clear()
            st.success(f"บันทึกข้อมูล '{test_name}' รวม {len(new_rows)} ตัวอย่าง เรียบร้อยแล้ว!")
            st.rerun()

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
        m1.metric("จำนวนตัวอย่างทั้งหมด", f"{total_tests} ตัวอย่าง")
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
                    quant_df, x='Sample_ID', y='SDI', color='Status', hover_name='Test_Name',
                    color_discrete_map={'Acceptable': '#2ecc71', 'Warning': '#f1c40f', 'Unacceptable': '#e74c3c'},
                    hover_data=['Cycle', 'Department', 'Test_Name', 'Lab_Result', 'Assigned_Value'],
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