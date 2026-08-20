import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

st.set_page_config(page_title="EQA & Sigma Metric Tracking", page_icon="🔬", layout="wide")

DATA_FILE = 'eqa_data.csv'

# ตารางค่า TEa (%) มาตรฐานตามเกณฑ์ CLIA / AACC สำหรับ Biochemistry
TEA_TABLE = {
    "GLUCOSE": 10.0, "BUN": 9.0, "CREATININE": 15.0, "URIC ACID": 10.0,
    "CHOLESTEROL": 10.0, "TRIGLYCERIDE": 15.0, "HDL": 10.0, "LDL": 12.0,
    "TOTAL PROTEIN": 10.0, "ALBUMIN": 10.0, "TOTAL BILIRUBIN": 20.0,
    "AST": 15.0, "ALT": 15.0, "ALP": 15.0, "CALCIUM": 1.0, "Na": 4.0,
    "K": 0.5, "Cl": 5.0, "Hba1c": 6.0, "DEFAULT": 10.0
}

@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            'Cycle', 'Department', 'Test_Name', 'Sample_ID', 'Test_Type',
            'Lab_Result', 'Assigned_Value', 'SD_Group', 'Z_Score', 'Interpretation',
            'Lab_SD', 'Lab_CV', 'TEa_Percent', 'Bias_Percent', 'Sigma_Metric', 'Recommended_Multirule',
            'Score_Obtained', 'Max_Score', 'Score_Percent', 'Status', 'Remark'
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

DEPARTMENTS = ["Biochemistry", "Immunology", "Hematology", "Microscopy", "Microbiology", "Blood bank"]

TEST_LISTS = {
    "Biochemistry": ["GLUCOSE", "BUN", "CREATININE", "URIC ACID", "CHOLESTEROL", "TRIGLYCERIDE", "HDL", "LDL", "TOTAL PROTEIN", "ALBUMIN", "TOTAL BILIRUBIN", "DIRECT BILIRUBIN", "AST", "ALT", "ALP", "CALCIUM", "MAGNESIUM", "PHOSPHORUS", "Na", "K", "Cl", "CO2", "Hba1c", "Troponin I"],
    "Hematology": ["CBC", "PT&INR", "DCIP", "Hematocrit", "ESR"],
    "Immunology": ["HBsAg", "HBsAb", "anti-HCV", "HIV", "Syphilis", "COVID-19 TEST"],
    "Microbiology": ["AFB", "Gram's stain", "KOH"],
    "Microscopy": ["UA", "Stool examination", "UPT"],
    "Blood bank": ["ABO grouping", "Rh grouping"]
}

def evaluate_westgard_rules(sigma):
    if np.isnan(sigma):
        return "N/A"
    elif sigma >= 6.0:
        return "1-3s (World Class - N=1)"
    elif sigma >= 5.0:
        return "1-3s / 2-2s / R-4s (Excellent - N=2)"
    elif sigma >= 4.0:
        return "1-3s / 2-2s / R-4s / 4-1s (Good - N=2)"
    elif sigma >= 3.0:
        return "1-3s / 2-2s / R-4s / 4-1s / 10x (Marginal - N=2 or N=4)"
    else:
        return "Unacceptable (<3.0) - ต้องแก้ไข Root Cause / Re-calibrate ก่อนเลือก Rule"

st.title("🔬 ระบบติดตามผล EQA และคำนวณ Sigma Metric / Multirules")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📝 กรอกผล EQA & Sigma Metric", "📊 Dashboard & Multirules", "📋 ประวัติข้อมูล"])

with tab1:
    st.header("แบบฟอร์มบันทึกผล EQA")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        cycle = st.text_input("รอบการทดสอบ (Cycle/Year)", value="1/2026")
    with c2:
        department = st.selectbox("สาขาห้องปฏิบัติการ", DEPARTMENTS)
    with c3:
        available_tests = TEST_LISTS.get(department, []) + ["อื่นๆ (ระบุเอง)"]
        selected_test = st.selectbox("รายการทดสอบ (Test Name)", available_tests)
        test_name = st.text_input("ระบุชื่อรายการทดสอบเพิ่มเติม") if selected_test == "อื่นๆ (ระบุเอง)" else selected_test

    col_m1, col_m2 = st.columns([2, 1])
    with col_m1:
        test_type = st.radio(
            "โหมดการประเมินผล", 
            ["Quantitative (เชิงปริมาณ + Z-score & Sigma Metric)", "Qualitative with Scoring", "Qualitative Basic"], 
            index=0 if department == "Biochemistry" else 1, horizontal=True
        )
    with col_m2:
        num_samples = st.number_input("จำนวนตัวอย่าง (1-10)", min_value=1, max_value=10, value=1, step=1)

    st.markdown("---")

    if "Quantitative" in test_type:
        st.info("💡 กรอกผล Lab, ค่า Peer Group (Assigned Value/SD), ค่า %CV Lab และ TEa% ระบบจะคำนวณ Z-score, Sigma Metric และแนะนำ Westgard Multirule ให้ทันที")
        
        default_tea = TEA_TABLE.get(test_name, TEA_TABLE["DEFAULT"])
        
        init_data = pd.DataFrame({
            'รหัสตัวอย่าง': [f"Sample {i+1}" for i in range(num_samples)],
            'Lab Result': [100.0] * num_samples,
            'Assigned Value': [100.0] * num_samples,
            'SD Group': [3.0] * num_samples,
            'Lab SD': [2.0] * num_samples,
            'Lab %CV': [2.0] * num_samples,
            'TEa (%)': [default_tea] * num_samples,
            'Interpretation': ['Acceptable'] * num_samples
        })
        
        edited_df = st.data_editor(
            init_data, num_rows="dynamic", use_container_width=True,
            column_config={
                "Interpretation": st.column_config.SelectboxColumn("Interpretation", options=["Acceptable", "Warning", "Unacceptable", "Action Required"]),
                "TEa (%)": st.column_config.NumberColumn("TEa (%)", format="%.1f%%"),
                "Lab %CV": st.column_config.NumberColumn("Lab %CV", format="%.2f%%"),
                "Lab SD": st.column_config.NumberColumn("Lab SD", format="%.2f"),
                "SD Group": st.column_config.NumberColumn("SD Group (Peer)", format="%.2f"),
                "Lab Result": st.column_config.NumberColumn("Lab Result", format="%.2f"),
                "Assigned Value": st.column_config.NumberColumn("Assigned Value", format="%.2f")
            }
        )

        # Real-time Calculation Display
        calc_rows = []
        for _, r in edited_df.iterrows():
            l_res, a_val, sd_grp = float(r['Lab Result']), float(r['Assigned Value']), float(r['SD Group'])
            cv_lab, tea = float(r['Lab %CV']), float(r['TEa (%)'])
            
            z_score = (l_res - a_val) / sd_grp if sd_grp > 0 else np.nan
            bias_pct = (abs(l_res - a_val) / a_val * 100) if a_val > 0 else np.nan
            sigma = ((tea - bias_pct) / cv_lab) if cv_lab > 0 and not np.isnan(bias_pct) else np.nan
            rule = evaluate_westgard_rules(sigma)
            
            calc_rows.append({'Z-Score': z_score, 'Bias (%)': bias_pct, 'Sigma': sigma, 'Multirule': rule})

        res_summary = pd.DataFrame(calc_rows)
        
        st.markdown("#### 🎯 ผลการประมวลผล Sigma Metric & Westgard Rule (Real-time)")
        res_cols = st.columns(len(calc_rows))
        for idx, row_res in res_summary.iterrows():
            with res_cols[min(idx, len(res_cols)-1)]:
                st.metric(f"{edited_df.iloc[idx]['รหัสตัวอย่าง']} - Z-score", f"{row_res['Z-Score']:.2f}" if not np.isnan(row_res['Z-Score']) else "N/A")
                st.metric("Sigma Metric", f"{row_res['Sigma']:.2f}" if not np.isnan(row_res['Sigma']) else "N/A")
                st.caption(f"**Rule**: {row_res['Multirule']}")

    elif "Scoring" in test_type:
        st.info("💡 คำนวณคะแนนร้อยละภาพรวมจากทุก Sample")
        init_data = pd.DataFrame({
            'รหัสตัวอย่าง': [f"Sample {i+1}" for i in range(num_samples)],
            'Lab Result': ['Positive'] * num_samples,
            'Assigned Value': ['Positive'] * num_samples,
            'คะแนนที่ได้': [100.0] * num_samples,
            'คะแนนเต็ม': [100.0] * num_samples
        })
        edited_df = st.data_editor(init_data, num_rows="dynamic", use_container_width=True)

    remark = st.text_area("บันทึกเพิ่มเติม / สาเหตุกรณีไม่ผ่าน (Root Cause Analysis)", placeholder="ระบุเพิ่มเติม...")

    if st.button("💾 บันทึกข้อมูล EQA", type="primary"):
        new_rows = []
        for idx, row in edited_df.iterrows():
            sample_id = str(row['รหัสตัวอย่าง'])
            if "Quantitative" in test_type:
                l_res, a_val, sd_grp = float(row['Lab Result']), float(row['Assigned Value']), float(row['SD Group'])
                l_sd, l_cv, tea = float(row['Lab SD']), float(row['Lab %CV']), float(row['TEa (%)'])
                interp = str(row['Interpretation'])
                
                z_score = (l_res - a_val) / sd_grp if sd_grp > 0 else np.nan
                bias_pct = (abs(l_res - a_val) / a_val * 100) if a_val > 0 else np.nan
                sigma = ((tea - bias_pct) / l_cv) if l_cv > 0 and not np.isnan(bias_pct) else np.nan
                rule = evaluate_westgard_rules(sigma)
                
                new_rows.append({
                    'Cycle': cycle, 'Department': department, 'Test_Name': test_name, 'Sample_ID': sample_id,
                    'Test_Type': 'Quantitative', 'Lab_Result': l_res, 'Assigned_Value': a_val,
                    'SD_Group': sd_grp, 'Z_Score': round(z_score, 2), 'Interpretation': interp,
                    'Lab_SD': l_sd, 'Lab_CV': l_cv, 'TEa_Percent': tea, 'Bias_Percent': round(bias_pct, 2),
                    'Sigma_Metric': round(sigma, 2), 'Recommended_Multirule': rule,
                    'Status': interp, 'Remark': remark
                })
        
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        save_data(df)
        st.cache_data.clear()
        st.success(f"บันทึกข้อมูล {test_name} เรียบร้อยแล้ว!")
        st.rerun()

with tab2:
    st.header("Dashboard วิเคราะห์ Sigma Metric และ แนะนำ Westgard Multirule")
    if not df.empty and 'Sigma_Metric' in df.columns:
        biochem_df = df[df['Sigma_Metric'].notnull()]
        if not biochem_df.empty:
            fig_sigma = px.bar(
                biochem_df, x='Test_Name', y='Sigma_Metric', color='Interpretation',
                title="ระดับ Sigma Metric แยกตามรายการทดสอบ Biochemistry",
                hover_data=['Cycle', 'Sample_ID', 'Bias_Percent', 'Lab_CV', 'Recommended_Multirule']
            )
            fig_sigma.add_hline(y=6.0, line_dash="dot", line_color="green", annotation_text="World Class (6σ)")
            fig_sigma.add_hline(y=3.0, line_dash="dash", line_color="red", annotation_text="Minimum Acceptable (3σ)")
            st.plotly_chart(fig_sigma, use_container_width=True)
            
            st.subheader("📋 ตารางแนะนำการเลือกใช้ QC Multirules ตามค่า Sigma")
            st.dataframe(biochem_df[['Cycle', 'Test_Name', 'Sample_ID', 'Z_Score', 'Bias_Percent', 'Lab_CV', 'Sigma_Metric', 'Recommended_Multirule', 'Interpretation']], use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูล Quantitative / Sigma Metric")
    else:
        st.info("ยังไม่มีข้อมูลในระบบ")

with tab3:
    st.header("ตารางข้อมูลประวัติทั้งหมด")
    st.dataframe(df, use_container_width=True)