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
            'Lab_Result', 'Assigned_Value', 'Score_Obtained', 'Max_Score', 'Score_Percent',
            'SD', 'SDI', 'Status', 'Remark'
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

for col in ['Score_Obtained', 'Max_Score', 'Score_Percent']:
    if col not in df.columns:
        df[col] = np.nan

DEPARTMENTS = [
    "Immunology",
    "Hematology",
    "Biochemistry",
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

COLOR_MAP = {
    'Excellent': '#27ae60',     # เขียวเข้ม
    'Good': '#2ecc71',          # เขียวสว่าง
    'Satisfactory': '#f1c40f',  # เหลือง
    'Unacceptable': '#e74c3c',  # แดง
    'Acceptable': '#2ecc71',    # รองรับข้อมูลเดิม
    'Warning': '#f39c12'        # รองรับข้อมูลเดิม
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
    st.header("แบบฟอร์มบันทึกผล EQA")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        cycle = st.text_input("รอบการทดสอบ (Cycle/Year)", value="1/2026")
    with col_c2:
        department = st.selectbox("สาขาห้องปฏิบัติการ", DEPARTMENTS)
    with col_c3:
        available_tests = TEST_LISTS.get(department, []) + ["อื่นๆ (ระบุเอง)"]
        selected_test = st.selectbox("รายการทดสอบ (Test Name)", available_tests)
        test_name = st.text_input("ระบุชื่อรายการทดสอบเพิ่มเติม") if selected_test == "อื่นๆ (ระบุเอง)" else selected_test

    if department == "Immunology":
        default_mode_index = 1
    elif department in ["Biochemistry", "Hematology"]:
        default_mode_index = 0
    else:
        default_mode_index = 1
    
    col_m1, col_m2 = st.columns([2, 1])
    with col_m1:
        test_type = st.radio(
            "โหมดการประเมินผล", 
            [
                "Quantitative (เชิงปริมาณ - SDI)", 
                "Qualitative with Scoring (ประเมินด้วยคะแนน & % ภาพรวม)", 
                "Qualitative Basic (เทียบ Concordance ตรงๆ)"
            ], 
            index=default_mode_index,
            horizontal=True
        )
    with col_m2:
        num_samples = st.number_input("จำนวนตัวอย่างในรอบนี้ (1-10 ตัวอย่าง)", min_value=1, max_value=10, value=2, step=1)

    st.markdown("---")
    st.subheader(f"📋 ป้อนผลการตรวจสำหรับ: **{test_name}** ({num_samples} ตัวอย่าง)")

    if "Quantitative" in test_type:
        st.info("💡 กรอกผลตรวจ ค่า Assigned Value และ SD เพื่อคำนวณ SDI")
        
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

    elif "Scoring" in test_type:
        qual_opts = get_qual_options_for_test(test_name)
        
        init_data = pd.DataFrame({
            'รหัสตัวอย่าง (Sample ID)': [f"Sample {i+1}" for i in range(num_samples)],
            'Lab Result': [qual_opts[0]] * num_samples,
            'Assigned Value': [qual_opts[0]] * num_samples,
            'คะแนนที่ได้ (Obtained)': [100.0] * num_samples,
            'คะแนนเต็ม (Max Score)': [100.0] * num_samples
        })
        
        edited_df = st.data_editor(
            init_data,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "รหัสตัวอย่าง (Sample ID)": st.column_config.TextColumn("รหัสตัวอย่าง (Sample ID)", required=True),
                "Lab Result": st.column_config.SelectboxColumn("Lab Result", options=qual_opts, required=True),
                "Assigned Value": st.column_config.SelectboxColumn("Assigned Value", options=qual_opts, required=True),
                "คะแนนที่ได้ (Obtained)": st.column_config.NumberColumn("คะแนนที่ได้", min_value=0.0, format="%.1f"),
                "คะแนนเต็ม (Max Score)": st.column_config.NumberColumn("คะแนนเต็ม", min_value=0.1, format="%.1f")
            }
        )

        # คำนวณคะแนนภาพรวมและระดับประเมินทันทีเพื่อโชว์บนหน้าจอ
        tot_obtained = edited_df['คะแนนที่ได้ (Obtained)'].sum()
        tot_max = edited_df['คะแนนเต็ม (Max Score)'].sum()
        calc_pct = (tot_obtained / tot_max * 100) if tot_max > 0 else 0.0

        if calc_pct == 100.0:
            calc_status = "Excellent"
            status_desc = "ดีเยี่ยม (100%)"
        elif 80.0 <= calc_pct < 100.0:
            calc_status = "Good"
            status_desc = "ดี (80.0% - 99.9%)"
        elif 70.0 <= calc_pct < 80.0:
            calc_status = "Satisfactory"
            status_desc = "ยอมรับได้ / ผ่านเกณฑ์ขั้นต่ำ (70.0% - 79.9%)"
        else:
            calc_status = "Unacceptable"
            status_desc = "ต้องปรับปรุง / ไม่ผ่านเกณฑ์ (< 70.0%)"

        st.markdown("#### 🎯 ผลการคำนวณคะแนนภาพรวม (Real-time Calculation)")
        sc_col1, sc_col2, sc_col3 = st.columns([1, 1, 2])
        sc_col1.metric("คะแนนรวมที่ได้ / เต็ม", f"{tot_obtained:.1f} / {tot_max:.1f}")
        sc_col2.metric("คะแนนร้อยละภาพรวม", f"{calc_pct:.2f}%")
        
        with sc_col3:
            if calc_status == "Excellent":
                st.success(f"**ระดับผลการประเมิน**: {calc_status} — {status_desc}")
            elif calc_status == "Good":
                st.info(f"**ระดับผลการประเมิน**: {calc_status} — {status_desc}")
            elif calc_status == "Satisfactory":
                st.warning(f"**ระดับผลการประเมิน**: {calc_status} — {status_desc}")
            else:
                st.error(f"**ระดับผลการประเมิน**: {calc_status} — {status_desc}")

    else:
        st.info("💡 ระบุผลตรวจเทียบกับค่าเฉลย (Concordance)")
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
            
            if "Scoring" in test_type:
                total_obtained = edited_df['คะแนนที่ได้ (Obtained)'].sum()
                total_max = edited_df['คะแนนเต็ม (Max Score)'].sum()
                overall_pct = (total_obtained / total_max * 100) if total_max > 0 else 0.0
                
                if overall_pct == 100.0:
                    overall_status = "Excellent"
                elif 80.0 <= overall_pct < 100.0:
                    overall_status = "Good"
                elif 70.0 <= overall_pct < 80.0:
                    overall_status = "Satisfactory"
                else:
                    overall_status = "Unacceptable"

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
                        'Score_Obtained': np.nan,
                        'Max_Score': np.nan,
                        'Score_Percent': np.nan,
                        'SD': sd_val,
                        'SDI': round(sdi, 2) if not np.isnan(sdi) else np.nan,
                        'Status': status,
                        'Remark': remark
                    })

                elif "Scoring" in test_type:
                    lab_res_str = str(row['Lab Result'])
                    assigned_val_str = str(row['Assigned Value'])
                    score_obtained = float(row['คะแนนที่ได้ (Obtained)'])
                    max_score = float(row['คะแนนเต็ม (Max Score)'])
                    
                    new_rows.append({
                        'Cycle': cycle,
                        'Department': department,
                        'Test_Name': test_name,
                        'Sample_ID': sample_id,
                        'Test_Type': 'Qualitative (Scoring)',
                        'Lab_Result': lab_res_str,
                        'Assigned_Value': assigned_val_str,
                        'Score_Obtained': score_obtained,
                        'Max_Score': max_score,
                        'Score_Percent': round(overall_pct, 2),
                        'SD': np.nan,
                        'SDI': np.nan,
                        'Status': overall_status,
                        'Remark': remark
                    })

                else:
                    lab_res_str = str(row['Lab Result'])
                    assigned_val_str = str(row['Assigned Value'])
                    status = "Excellent" if lab_res_str == assigned_val_str else "Unacceptable"
                    
                    new_rows.append({
                        'Cycle': cycle,
                        'Department': department,
                        'Test_Name': test_name,
                        'Sample_ID': sample_id,
                        'Test_Type': 'Qualitative',
                        'Lab_Result': lab_res_str,
                        'Assigned_Value': assigned_val_str,
                        'Score_Obtained': np.nan,
                        'Max_Score': np.nan,
                        'Score_Percent': 100.0 if status == "Excellent" else 0.0,
                        'SD': np.nan,
                        'SDI': np.nan,
                        'Status': status,
                        'Remark': remark
                    })

            df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
            save_data(df)
            st.cache_data.clear()
            st.success(f"บันทึกข้อมูล '{test_name}' เรียบร้อยแล้ว! คะแนนภาพรวม: {overall_pct:.2f}% ({overall_status})" if "Scoring" in test_type else f"บันทึกข้อมูล '{test_name}' รวม {len(new_rows)} ตัวอย่าง เรียบร้อยแล้ว!")
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
        
        excellent_cnt = len(filtered_df[filtered_df['Status'] == 'Excellent'])
        good_cnt = len(filtered_df[filtered_df['Status'] == 'Good'])
        sat_cnt = len(filtered_df[filtered_df['Status'] == 'Satisfactory'])
        unacc_cnt = len(filtered_df[filtered_df['Status'] == 'Unacceptable'])
        
        acc_legacy_cnt = len(filtered_df[filtered_df['Status'] == 'Acceptable'])
        passed_cnt = excellent_cnt + good_cnt + sat_cnt + acc_legacy_cnt
        pass_rate = (passed_cnt / total_tests * 100) if total_tests > 0 else 0.0

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("จำนวนตัวอย่างทั้งหมด", f"{total_tests} ตัวอย่าง")
        m2.metric("ผ่านเกณฑ์ภาพรวม", f"{passed_cnt}", f"{pass_rate:.1f}%")
        m3.metric("Excellent (100%)", f"{excellent_cnt}")
        m4.metric("Good / Satisfactory", f"{good_cnt + sat_cnt}")
        m5.metric("Unacceptable (<70%)", f"{unacc_cnt}")

        st.markdown("---")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.subheader("สัดส่วนผลการประเมินแยกตามสาขา")
            dept_summary = filtered_df.groupby(['Department', 'Status']).size().reset_index(name='Count')
            fig_bar = px.bar(
                dept_summary, x='Department', y='Count', color='Status',
                color_discrete_map=COLOR_MAP,
                barmode='group', text='Count'
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_g2:
            st.subheader("แนวโน้ม SDI / คะแนน % ภาพรวม")
            quant_df = filtered_df[filtered_df['Test_Type'] == 'Quantitative'].dropna(subset=['SDI'])
            scoring_df = filtered_df[filtered_df['Score_Percent'].notnull()]

            if not quant_df.empty:
                fig_sdi = px.scatter(
                    quant_df, x='Sample_ID', y='SDI', color='Status', hover_name='Test_Name',
                    color_discrete_map=COLOR_MAP,
                    hover_data=['Cycle', 'Department', 'Test_Name', 'Lab_Result', 'Assigned_Value'],
                    title="SDI Distribution (Quantitative: ±2SD ช่วงยอมรับได้)"
                )
                fig_sdi.add_hline(y=2.0, line_dash="dash", line_color="orange")
                fig_sdi.add_hline(y=-2.0, line_dash="dash", line_color="orange")
                st.plotly_chart(fig_sdi, use_container_width=True)
            
            if not scoring_df.empty:
                fig_score = px.bar(
                    scoring_df, x='Test_Name', y='Score_Percent', color='Status',
                    color_discrete_map=COLOR_MAP,
                    hover_data=['Cycle', 'Department', 'Sample_ID', 'Score_Obtained', 'Max_Score'],
                    title="คะแนนประเมินร้อยละภาพรวม (%) - Qualitative / Scoring"
                )
                fig_score.add_hline(y=100.0, line_dash="dot", line_color="green", annotation_text="Excellent (100%)")
                fig_score.add_hline(y=80.0, line_dash="dash", line_color="#2ecc71", annotation_text="Good (80%)")
                fig_score.add_hline(y=70.0, line_dash="dash", line_color="orange", annotation_text="Satisfactory (70%)")
                st.plotly_chart(fig_score, use_container_width=True)

            if quant_df.empty and scoring_df.empty:
                st.info("ไม่มีข้อมูลในการแสดงกราฟ")
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