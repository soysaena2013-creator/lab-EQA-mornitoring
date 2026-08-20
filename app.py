import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="EQA & Sigma Metric Tracking", page_icon="🔬", layout="wide")

DATA_FILE = 'eqa_data.csv'

# ค่า TEa อ้างอิง
TEA_TABLE = {
    "GLUCOSE": 10.0, "BUN": 9.0, "CREATININE": 15.0, "URIC ACID": 10.0,
    "CHOLESTEROL": 10.0, "TRIGLYCERIDE": 15.0, "HDL": 10.0, "LDL": 12.0,
    "TOTAL PROTEIN": 10.0, "ALBUMIN": 10.0, "TOTAL BILIRUBIN": 20.0,
    "AST": 15.0, "ALT": 15.0, "ALP": 15.0, "CALCIUM": 1.0, "Na": 4.0,
    "K": 0.5, "Cl": 5.0, "Hba1c": 6.0, "DEFAULT": 10.0
}

# รายการย่อยสำหรับ CBC (ส่วนที่ 1)
CBC_PART1_PARAMS = [
    "RBC count (10^6/ul)", "WBC count (10^3/ul)", "PLT count (10^3/ul)",
    "Hemoglobin concentration (g/dl)", "Hematocrit (%)", "MCV (fl)", "MCH (pg)", "MCHC (g/dl)"
]

# รายการย่อยสำหรับ Slide Smear (ส่วนที่ 2.1: WBC differential count)
CBC_SLIDE_WBC_PARAMS = [
    "neutrophils", "lymphocytes", "eosinophils", "basophils", "monocytes",
    "atypical lymphocytes", "promyelocytes", "myelocytes", "metamyelocytes",
    "band-form neutrophils", "plasma cells", "blast cells", "NRBC/100WBC"
]

# รายการย่อยสำหรับ Slide Smear (ส่วนที่ 2.2: RBC morphology)
CBC_SLIDE_RBC_PARAMS = [
    "normocytes", "microcytosis", "macrocytosis", "hypochromia", "polychromasia",
    "target cell", "acanthocyte", "burr cell", "ovalocyte", "schistocyte",
    "spherocyte", "stomatocyte", "tear drop cell", "rouleaux formation",
    "agglutination", "cabot's ring", "basophilic stippling", "howell jolly bodies"
]

# รายการย่อยสำหรับ Slide Smear (ส่วนที่ 2.3: Platelet estimation)
CBC_SLIDE_PLT_PARAMS = ["decreased", "adequate", "increased"]

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
    "Microscopy": ["UA", "Blood parasite", "Blood parasite (digital slide)", "Urine sediment by photo observation", "Stool examination", "FOB", "UPT", "Methamphetamine screening test", "Marijuana screening test", "Fern test"],
    "Blood bank": ["ABO grouping", "Rh grouping"]
}

QUAL_OPTIONS = {
    "blood_bank": ["Group A", "Group B", "Group AB", "Group O", "Positive", "Negative"],
    "serology": ["Reactive", "Non-reactive", "Positive", "Negative", "Equivocal", "Inconclusive"],
    "syphilis": [
        "Reactive", "Non-reactive", "Positive", "Negative", "Equivocal", "Inconclusive",
        "Reactive 1:2", "Reactive 1:4", "Reactive 1:8", "Reactive 1:16", 
        "Reactive 1:32", "Reactive 1:64", "Reactive 1:128", "Reactive 1:256", "Reactive 1:512"
    ],
    "syphilis_methods": ["RPR", "VDRL", "Syphilis Ab", "TPHA"],
    "pos_neg": ["Positive", "Negative", "Inconclusive"],
    "afb": ["Not Found / Negative", "1-9 AFB / 100 fields", "1+", "2+", "3+"],
    "stain": ["Found", "Not Found", "Yeasts Found", "No Organism Found"],
    "koh": [
        "Not Found / No fungal element seen", "Yeast cells found", "Yeast cells with pseudohyphae found",
        "Septate hyphae found", "Non-septate / Aseptate hyphae found", "Arthrospores / Arthroconidia found", "Budding yeast cells found"
    ],
    "titer": ["1:2", "1:4", "1:8", "1:16", "1:32", "1:64", "1:128", "1:256", "Negative"],
    "general": ["Positive", "Negative", "Reactive", "Non-reactive", "Equivocal", "Inconclusive", "Normal", "Abnormal"]
}

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        df_loaded = pd.read_csv(DATA_FILE)
        if 'Test_Method' not in df_loaded.columns:
            df_loaded['Test_Method'] = 'N/A'
        return df_loaded
    else:
        return pd.DataFrame(columns=[
            'Cycle', 'Department', 'Test_Name', 'Test_Method', 'Sample_ID', 'Test_Type',
            'Lab_Result', 'Assigned_Value', 'SD_Group', 'Z_Score', 'Interpretation',
            'Lab_SD', 'Lab_CV', 'TEa_Percent', 'Bias_Percent', 'Sigma_Metric', 'Recommended_Multirule',
            'Score_Obtained', 'Max_Score', 'Score_Percent', 'Standard_Score', 'Status', 
            'Root_Cause', 'Review_Action'
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)
    st.cache_data.clear()

def evaluate_di_performance(di):
    if np.isnan(di):
        return "N/A"
    di_abs = abs(di)
    if di_abs <= 0.5:
        return "Excellent"
    elif 0.5 < di_abs <= 1.0:
        return "Good"
    elif 1.0 < di_abs <= 2.0:
        return "Satisfactory"
    elif 2.0 < di_abs <= 3.0:
        return "Unsatisfactory"
    else:
        return "Serious problem"

def evaluate_score_performance(score):
    if np.isnan(score):
        return "N/A"
    if score >= 3.5:
        return "Excellent"
    elif 3.0 <= score < 3.5:
        return "Good"
    elif 2.5 <= score < 3.0:
        return "Satisfactory"
    elif 1.5 <= score < 2.5:
        return "Unsatisfactory"
    else:
        return "Serious problem"

# ---------------------------------------------------------
# Main Application Layout
# ---------------------------------------------------------
df = load_data()

st.title("🔬 ระบบติดตามและประเมินผลประสิทธิภาพ EQA & Sigma Metric")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📝 กรอกผล EQA (Multi-Sample)", "📊 Dashboard สรุปผล & Multirules", "📋 ประวัติและ Export ข้อมูล"])

# =========================================================
# TAB 1: กรอกผล EQA (Multi-Sample)
# =========================================================
with tab1:
    st.header("แบบฟอร์มบันทึกผล EQA")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        cycle = st.text_input("รอบการทดสอบ (Cycle/Year)", value="1/2026")
    with col_c2:
        department = st.selectbox("สาขาห้องปฏิบัติการ", DEPARTMENTS, index=DEPARTMENTS.index("Hematology") if "Hematology" in DEPARTMENTS else 0)
    with col_c3:
        available_tests = TEST_LISTS.get(department, []) + ["อื่นๆ (ระบุเอง)"]
        selected_test = st.selectbox("รายการทดสอบ (Test Name)", available_tests)
        test_name = st.text_input("ระบุชื่อรายการทดสอบเพิ่มเติม") if selected_test == "อื่นๆ (ระบุเอง)" else selected_test

    test_method = "N/A"
    if test_name == "Syphilis":
        test_method = st.selectbox("วิธีที่ใช้ทดสอบ (Test Method)", QUAL_OPTIONS["syphilis_methods"])

    if test_name == "CBC":
        test_type = "CBC Multi-Part Scoring"
        num_samples = st.number_input("จำนวนตัวอย่างในรอบนี้ (1-10 ตัวอย่าง)", min_value=1, max_value=10, value=1, step=1)
    else:
        num_samples = st.number_input("จำนวนตัวอย่างในรอบนี้ (1-10 ตัวอย่าง)", min_value=1, max_value=10, value=1, step=1)

    st.markdown("---")
    st.subheader(f"📋 ป้อนผลการตรวจสำหรับ: **{test_name}** ({num_samples} ตัวอย่าง)")

    nc_items = []
    cbc_results_store = []

    # กรณี CBC
    if test_name == "CBC":
        st.info("💡 **CBC**: แบ่งการบันทึกเป็น 2 ส่วนหลัก ได้แก่ ส่วนที่ 1 CBC (อัตโนมัติ 8 รายการ พร้อม Lab Performance คิดจาก Lab DI อัตโนมัติ) และ ส่วนที่ 2 Slide Smear")
        
        for s_idx in range(num_samples):
            st.markdown(f"##### 🩸 **ตัวอย่างที่ {s_idx + 1}**")
            sample_id_input = st.text_input(f"ชื่อ/รหัสตัวอย่าง (Sample ID)", value=f"Sample {s_idx + 1}", key=f"cbc_sid_{s_idx}")
            
            # --- ส่วนที่ 1: CBC ---
            st.markdown("---")
            st.markdown("###### **ส่วนที่ 1: CBC (8 รายการ)**")
            part1_data = []
            for param in CBC_PART1_PARAMS:
                part1_data.append({
                    "Parameter": param,
                    "Lab Result": 0.0,
                    "Lab DI": 0.0,
                    "Lab Performance": "Excellent"
                })
            df_part1 = pd.DataFrame(part1_data)
            
            # ใช้ data_editor เพียงตารางเดียว และคำนวณ Lab Performance ทันทีแบบ Real-time
            edited_part1 = st.data_editor(
                df_part1,
                key=f"cbc_p1_editor_{s_idx}",
                use_container_width=True,
                column_config={
                    "Parameter": st.column_config.TextColumn("Parameter", disabled=True),
                    "Lab Result": st.column_config.NumberColumn("Lab Result", format="%.2f"),
                    "Lab DI": st.column_config.NumberColumn("Lab DI (Deviation Index)", format="%.2f"),
                    "Lab Performance": st.column_config.TextColumn("Lab Performance", disabled=True)
                }
            )
            
            # อัปเดตช่อง Lab Performance ตาม Lab DI ที่ผู้ใช้กรอกเข้ามาสดๆ
            for i in range(len(edited_part1)):
                di_val = float(edited_part1.loc[i, "Lab DI"])
                edited_part1.loc[i, "Lab Performance"] = evaluate_di_performance(di_val)
            
            for _, r in edited_part1.iterrows():
                p_name = r["Parameter"]
                l_res = float(r["Lab Result"])
                di_val = float(r["Lab DI"])
                perf = str(r["Lab Performance"])
                
                cbc_results_store.append({
                    'Sample_ID': sample_id_input,
                    'Section': 'Part 1: CBC',
                    'Item_Name': p_name,
                    'Lab_Result': str(l_res),
                    'Assigned_Value': 'N/A',
                    'Lab_DI': di_val,
                    'Mean': np.nan,
                    'SD': np.nan,
                    'Performance': perf
                })
                
                if perf in ["Unsatisfactory", "Serious problem"]:
                    nc_items.append({
                        "รายการ/Sample": f"{sample_id_input} - CBC ({p_name})",
                        "ผลตรวจห้องปฏิบัติการ": str(l_res),
                        "ค่าเป้าหมาย (Assigned Value)": f"DI: {di_val:.2f}",
                        "สถานะปัญหา": f"Performance: {perf}"
                    })

            # --- ส่วนที่ 2: Slide smear ---
            st.markdown("---")
            st.markdown("###### **ส่วนที่ 2: Slide Smear**")
            
            # ส่วนที่ 2.1 WBC differential count
            st.markdown("**2.1 WBC differential count** (กรอก Lab Result, Lab DI, Mean, SD)")
            p21_data = []
            for param in CBC_SLIDE_WBC_PARAMS:
                p21_data.append({
                    "Parameter": param,
                    "Lab Result": 0.0,
                    "Lab DI": 0.0,
                    "Mean": 0.0,
                    "SD": 0.0
                })
            df_p21 = pd.DataFrame(p21_data)
            
            edited_p21 = st.data_editor(
                df_p21,
                key=f"cbc_p21_editor_{s_idx}",
                use_container_width=True,
                column_config={
                    "Parameter": st.column_config.TextColumn("Parameter", disabled=True),
                    "Lab Result": st.column_config.NumberColumn("Lab Result", format="%.2f"),
                    "Lab DI": st.column_config.NumberColumn("Lab DI", format="%.2f"),
                    "Mean": st.column_config.NumberColumn("Mean", format="%.2f"),
                    "SD": st.column_config.NumberColumn("SD", format="%.2f")
                }
            )
            
            for _, r in edited_p21.iterrows():
                p_name = r["Parameter"]
                l_res = float(r["Lab Result"])
                di_val = float(r["Lab DI"])
                mean_val = float(r["Mean"])
                sd_val = float(r["SD"])
                perf = evaluate_di_performance(di_val)
                
                cbc_results_store.append({
                    'Sample_ID': sample_id_input,
                    'Section': 'Part 2.1: WBC diff',
                    'Item_Name': p_name,
                    'Lab_Result': str(l_res),
                    'Assigned_Value': 'N/A',
                    'Lab_DI': di_val,
                    'Mean': mean_val,
                    'SD': sd_val,
                    'Performance': perf
                })

            # ส่วนที่ 2.2 RBC morphology
            st.markdown("**2.2 RBC morphology**")
            p22_data = []
            for param in CBC_SLIDE_RBC_PARAMS:
                p22_data.append({
                    "Parameter": param,
                    "Lab Result": "Normal",
                    "Assigned Value": "Normal",
                    "Score (0-4)": 4.0
                })
            df_p22 = pd.DataFrame(p22_data)
            
            edited_p22 = st.data_editor(
                df_p22,
                key=f"cbc_p22_editor_{s_idx}",
                use_container_width=True,
                column_config={
                    "Parameter": st.column_config.TextColumn("Parameter", disabled=True),
                    "Lab Result": st.column_config.TextColumn("Lab Result"),
                    "Assigned Value": st.column_config.TextColumn("Assigned Value"),
                    "Score (0-4)": st.column_config.NumberColumn("Score", min_value=0.0, max_value=4.0, format="%.1f")
                }
            )
            
            p22_avg_score = edited_p22["Score (0-4)"].mean() if not edited_p22.empty else 0.0
            p22_perf = evaluate_score_performance(p22_avg_score)
            st.info(f"📊 คะแนนเฉลี่ย RBC morphology ของ {sample_id_input}: **{p22_avg_score:.2f}** | Performance: **{p22_perf}**")
            
            for _, r in edited_p22.iterrows():
                cbc_results_store.append({
                    'Sample_ID': sample_id_input,
                    'Section': 'Part 2.2: RBC morphology',
                    'Item_Name': r["Parameter"],
                    'Lab_Result': str(r["Lab Result"]),
                    'Assigned_Value': str(r["Assigned Value"]),
                    'Lab_DI': np.nan,
                    'Mean': np.nan,
                    'SD': np.nan,
                    'Performance': p22_perf
                })

            # ส่วนที่ 2.3 Platelet estimation
            st.markdown("**2.3 Platelet estimation**")
            p23_data = []
            for param in CBC_SLIDE_PLT_PARAMS:
                p23_data.append({
                    "Parameter": param,
                    "Lab Result": "adequate",
                    "Assigned Value": "adequate",
                    "Score (0-4)": 4.0
                })
            df_p23 = pd.DataFrame(p23_data)
            
            edited_p23 = st.data_editor(
                df_p23,
                key=f"cbc_p23_editor_{s_idx}",
                use_container_width=True,
                column_config={
                    "Parameter": st.column_config.TextColumn("Parameter", disabled=True),
                    "Lab Result": st.column_config.TextColumn("Lab Result"),
                    "Assigned Value": st.column_config.TextColumn("Assigned Value"),
                    "Score (0-4)": st.column_config.NumberColumn("Score", min_value=0.0, max_value=4.0, format="%.1f")
                }
            )
            
            p23_avg_score = edited_p23["Score (0-4)"].mean() if not edited_p23.empty else 0.0
            p23_perf = evaluate_score_performance(p23_avg_score)
            st.info(f"📊 คะแนนเฉลี่ย Platelet estimation ของ {sample_id_input}: **{p23_avg_score:.2f}** | Performance: **{p23_perf}**")
            
            for _, r in edited_p23.iterrows():
                cbc_results_store.append({
                    'Sample_ID': sample_id_input,
                    'Section': 'Part 2.3: Platelet estimation',
                    'Item_Name': r["Parameter"],
                    'Lab_Result': str(r["Lab Result"]),
                    'Assigned_Value': str(r["Assigned Value"]),
                    'Lab_DI': np.nan,
                    'Mean': np.nan,
                    'SD': np.nan,
                    'Performance': p23_perf
                })

    # ส่วนทบทวนและวิเคราะห์สาเหตุ (Non-conformity)
    st.markdown("---")
    st.subheader("🔍 สรุปรายการที่ไม่เป็นไปตามข้อกำหนด & การทบทวนทางเทคนิค (ISO 15189)")
    
    if nc_items:
        st.warning(f"⚠️ พบ {len(nc_items)} รายการที่ไม่ผ่านเกณฑ์ กรุณาระบุสาเหตุและแนวทางแก้ไข")
        st.dataframe(pd.DataFrame(nc_items), use_container_width=True)
    else:
        st.success("✅ ผลการทดสอบทุกรายการผ่านเกณฑ์ตามข้อกำหนดทั้งหมด")

    col_rc1, col_rc2 = st.columns(2)
    with col_rc1:
        root_cause = st.text_area("📌 สาเหตุที่ไม่ผ่าน (Root Cause Analysis)", height=120)
    with col_rc2:
        review_action = st.text_area("🛠️ ผลการทบทวน / มาตรการแก้ไข (Corrective & Preventive Action)", height=120)

    # ปุ่มบันทึกข้อมูล
    if st.button("💾 บันทึกผล EQA และบันทึกการทบทวน", type="primary"):
        if not test_name:
            st.error("กรุณาระบุชื่อรายการทดสอบก่อนบันทึก")
        else:
            new_rows = []
            if test_name == "CBC":
                for item in cbc_results_store:
                    new_rows.append({
                        'Cycle': cycle,
                        'Department': department,
                        'Test_Name': f"CBC - {item['Section']} ({item['Item_Name']})",
                        'Test_Method': test_method,
                        'Sample_ID': item['Sample_ID'],
                        'Test_Type': 'CBC Detailed Breakdown',
                        'Lab_Result': item['Lab_Result'],
                        'Assigned_Value': item['Assigned_Value'],
                        'SD_Group': np.nan,
                        'Z_Score': np.nan,
                        'Interpretation': item['Performance'],
                        'Lab_SD': item['SD'] if not np.isnan(item['SD']) else np.nan,
                        'Lab_CV': np.nan,
                        'TEa_Percent': np.nan,
                        'Bias_Percent': np.nan,
                        'Sigma_Metric': np.nan,
                        'Recommended_Multirule': 'N/A',
                        'Score_Obtained': item['Lab_DI'] if not np.isnan(item['Lab_DI']) else np.nan,
                        'Max_Score': np.nan,
                        'Score_Percent': np.nan,
                        'Standard_Score': np.nan,
                        'Status': item['Performance'],
                        'Root_Cause': root_cause,
                        'Review_Action': review_action
                    })

            new_df = pd.DataFrame(new_rows)
            df = pd.concat([df, new_df], ignore_index=True)
            save_data(df)
            st.success("✅ บันทึกข้อมูล EQA เรียบร้อยแล้ว!")
            st.rerun()

# =========================================================
# TAB 2 & TAB 3
# =========================================================
with tab2:
    st.header("📊 Dashboard สรุปผล & คำแนะนำ Westgard Multirules")
    if df.empty:
        st.info("ยังไม่มีข้อมูลในระบบ")
    else:
        st.dataframe(df, use_container_width=True)

with tab3:
    st.header("📋 ประวัติข้อมูล EQA ทั้งหมด และการ Export")
    if df.empty:
        st.info("ยังไม่มีข้อมูลบันทึกในระบบ")
    else:
        st.dataframe(df, use_container_width=True)
        csv_data = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 ดาวน์โหลดข้อมูลเป็น CSV", data=csv_data, file_name="eqa_tracking_data.csv", mime="text/csv", type="primary")