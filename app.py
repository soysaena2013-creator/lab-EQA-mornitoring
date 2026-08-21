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

# พารามิเตอร์ย่อยสำหรับ CBC (ส่วนที่ 1) 8 รายการ
CBC_PART1_PARAMETERS = [
    "RBC count (10^6/ul)", "WBC count (10^3/ul)", "PLT count (10^3/ul)", 
    "Hemoglobin concentration (g/dl)", "Hematocrit (%)", "MCV (fl)", "MCH (pg)", "MCHC (g/dl)"
]

# พารามิเตอร์ย่อยสำหรับ Slide smear ส่วนที่ 1: WBC differential count 13 รายการ
WBC_DIFF_PARAMETERS = [
    "neutrophils", "lymphocytes", "eosinophils", "basophils", "monocytes", 
    "atypical lymphocytes", "promyelocytes", "myelocytes", "metamyelocytes", 
    "band-form neutrophils", "plasma cells", "blast cells", "NRBC/100WBC"
]

# พารามิเตอร์ย่อยสำหรับ Slide smear ส่วนที่ 2: RBC morphology 16 รายการ
RBC_MORPHOLOGY_PARAMETERS = [
    "normocytes", "microcytosis", "macrocytosis", "hypochromia", "polychromasia", 
    "target cell", "acanthocyte", "burr cell", "ovalocyte", "schistocyte", 
    "spherocyte", "stomatocyte", "tear drop cell", "rouleaux formation", 
    "agglutination", "cabot's ring", "basophilic stippling", "howell jolly bodies"
]

# พารามิเตอร์ย่อยสำหรับ Slide smear ส่วนที่ 3: Platelet estimation 3 รายการ
PLATELET_EST_PARAMETERS = [
    "decreased", "adequate", "increased"
]

# พารามิเตอร์ย่อยสำหรับ UA 10 รายการ
UA_PARAMETERS = [
    "Specific Gravity", "pH", "Leukocytes", "Nitrite", 
    "Protein", "Glucose", "Ketone", "Urobilinogen", "Bilirubin", "Blood"
]

UA_OPTIONS = {
    "Specific Gravity": ["1.000", "1.005", "1.010", "1.015", "1.020", "1.025", "1.030", "1.035"],
    "pH": ["5.0", "5.5", "6.0", "6.5", "7.0", "7.5", "8.0", "8.5", "9.0"],
    "Leukocytes": ["Negative", "Trace", "1+", "2+", "3+", "4+"],
    "Nitrite": ["Negative", "Trace", "1+", "2+", "3+", "4+"],
    "Protein": ["Negative", "Trace", "1+", "2+", "3+", "4+"],
    "Glucose": ["Negative", "Trace", "1+", "2+", "3+", "4+"],
    "Ketone": ["Negative", "Trace", "1+", "2+", "3+", "4+"],
    "Urobilinogen": ["Negative", "Trace", "1+", "2+", "3+", "4+"],
    "Bilirubin": ["Negative", "Trace", "1+", "2+", "3+", "4+"],
    "Blood": ["Negative", "Trace", "1+", "2+", "3+", "4+"]
}

# ตัวเลือกสำหรับ Gram's Stain ย่อย
GRAM_REACTION_OPTIONS = ["Gram-positive", "Gram-negative", "Gram-variable", "No organism seen"]
GRAM_MORPHOLOGY_OPTIONS = ["Cocci", "Diplococci", "Bacilli / Rods", "Coccobacilli", "Spirilla / Curved rods", "Filamentous rods", "Yeast cells / Budding yeast", "No organism seen"]

# ตัวเลือกเชื้อและระยะสำหรับ Parasite & Stool
SPECIES_OPTIONS = [
    "Plasmodium falciparum", "Plasmodium vivax", "Plasmodium malariae", "Plasmodium ovale", "Plasmodium knowlesi",
    "Entamoeba histolytica", "Entamoeba coli", "Giardia lamblia", "Ascaris lumbricoides", "Hookworm", "Strongyloides stercoralis",
    "Trichuris trichiura", "Opisthorchis viverrini", "Taenia spp.", "Not Found / Negative"
]

STAGE_OPTIONS = [
    "Ring form", "Trophozoite", "Schizont", "Gametocyte", "Cyst", "Trophozoite (Ameba)", "Egg / Ovum", "Larva", "Adult worm", "Not Found"
]

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
    "afb": [
        "Not Found / Negative",
        "1-9 AFB / 100 fields",
        "1+",
        "2+",
        "3+"
    ],
    "stain": ["Found", "Not Found", "Yeasts Found", "No Organism Found"],
    "koh": [
        "Not Found / No fungal element seen",
        "Yeast cells found",
        "Yeast cells with pseudohyphae found",
        "Septate hyphae found",
        "Non-septate / Aseptate hyphae found",
        "Arthrospores / Arthroconidia found",
        "Budding yeast cells found"
    ],
    "titer": ["1:2", "1:4", "1:8", "1:16", "1:32", "1:64", "1:128", "1:256", "Negative"],
    "general": ["Positive", "Negative", "Reactive", "Non-reactive", "Equivocal", "Inconclusive", "Normal", "Abnormal"]
}

COLOR_MAP = {
    'Excellent': '#27ae60',
    'Good': '#2ecc71',
    'Satisfactory': '#f1c40f',
    'Unsatisfactory': '#e74c3c',
    'Unacceptable': '#e74c3c',
    'Acceptable': '#2ecc71',
    'Warning': '#f39c12'
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

def get_qual_options_for_test(test_name):
    if test_name in ["ABO grouping", "Rh grouping"]:
        return QUAL_OPTIONS["blood_bank"]
    elif test_name == "Syphilis":
        return QUAL_OPTIONS["syphilis"]
    elif test_name in ["HBsAg", "HBsAb", "anti-HCV", "HIV", "Leptospira antibody", "Scrub typhus antibody"]:
        return QUAL_OPTIONS["serology"]
    elif test_name in ["melioid titer"]:
        return QUAL_OPTIONS["titer"]
    elif test_name == "AFB":
        return QUAL_OPTIONS["afb"]
    elif test_name == "KOH":
        return QUAL_OPTIONS["koh"]
    elif test_name in ["Indiaink preperation"]:
        return QUAL_OPTIONS["stain"]
    elif test_name in ["UPT", "FOB", "COVID-19 TEST", "Dengue NS1", "Methamphetamine screening test", "Marijuana screening test"]:
        return QUAL_OPTIONS["pos_neg"]
    else:
        return QUAL_OPTIONS["general"]

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

def evaluate_di_performance(di):
    if di <= 0.5:
        return "excellent"
    elif 0.5 < di <= 1.0:
        return "Good"
    elif 1.0 < di <= 2.0:
        return "satisfactory"
    elif 2.0 < di <= 3.0:
        return "unsatisfactory"
    else:
        return "serious problem"

def evaluate_score_performance(score):
    if score >= 3.5:
        return "excellent"
    elif 3.0 <= score < 3.5:
        return "good"
    elif 2.5 <= score < 3.0:
        return "satisfactory"
    elif 1.5 <= score < 2.5:
        return "unsatisfactory"
    else:
        return "serious problem"

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
        department = st.selectbox("สาขาห้องปฏิบัติการ", DEPARTMENTS, index=DEPARTMENTS.index("Immunology") if "Immunology" in DEPARTMENTS else 0)
    with col_c3:
        available_tests = TEST_LISTS.get(department, []) + ["อื่นๆ (ระบุเอง)"]
        selected_test = st.selectbox("รายการทดสอบ (Test Name)", available_tests)
        test_name = st.text_input("ระบุชื่อรายการทดสอบเพิ่มเติม") if selected_test == "อื่นๆ (ระบุเอง)" else selected_test

    # เพิ่มช่องเลือกวิธีทดสอบเฉพาะรายการ Syphilis
    test_method = "N/A"
    if test_name == "Syphilis":
        test_method = st.selectbox("วิธีที่ใช้ทดสอบ (Test Method)", QUAL_OPTIONS["syphilis_methods"])

    # ตรวจสอบประเภทรายการ Multi-Parameter
    if test_name in ["CBC", "UA", "Blood parasite", "Blood parasite (digital slide)", "Stool examination", "Gram's stain"]:
        test_type = f"{test_name} Multi-Parameter Scoring"
        num_samples = st.number_input("จำนวนตัวอย่างในรอบนี้ (1-10 ตัวอย่าง)", min_value=1, max_value=10, value=1, step=1)
    else:
        default_mode_index = 1 if department in ["Immunology", "Microscopy", "Microbiology"] else 0
        col_m1, col_m2 = st.columns([2, 1])
        with col_m1:
            test_type = st.radio(
                "โหมดการประเมินผล", 
                [
                    "Quantitative (เชิงปริมาณ + Z-score & Sigma Metric)", 
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

    nc_items = []

    # 1. กรณี CBC (Complete Blood Count แยก 2 ส่วนตามโจทย์ใหม่)
    if test_name == "CBC":
        st.info("💡 ป้อนข้อมูลสำหรับ CBC (ส่วนที่ 1) และ Slide smear (ส่วนที่ 2: WBC differential count, RBC morphology และ Platelet estimation)")
        
        cbc_results = {}
        
        for s_idx in range(num_samples):
            st.markdown(f"##### 🩸 **ตัวอย่างที่ {s_idx + 1}**")
            sample_id_input = st.text_input(f"ชื่อ/รหัสตัวอย่าง (Sample ID)", value=f"Sample {s_idx + 1}", key=f"cbc_sid_key_{s_idx}")
            
            # --- ส่วนที่ 1: CBC ---
            st.markdown("###### **ส่วนที่ 1: CBC**")
            cbc_part1_data = []
            for param in CBC_PART1_PARAMETERS:
                cbc_part1_data.append({
                    "รายการย่อย": param,
                    "Lab Result": 0.0,
                    "Lab DI": 0.0
                })
            
            cbc_p1_df = pd.DataFrame(cbc_part1_data)
            edited_cbc_p1 = st.data_editor(
                cbc_p1_df,
                key=f"cbc_p1_editor_{s_idx}",
                use_container_width=True,
                column_config={
                    "รายการย่อย": st.column_config.TextColumn("รายการย่อย", disabled=True),
                    "Lab Result": st.column_config.NumberColumn("Lab Result", format="%.2f", required=True),
                    "Lab DI": st.column_config.NumberColumn("Lab DI", format="%.2f", required=True)
                }
            )
            
            # ประเมิน performance จาก lab DI สำหรับส่วนที่ 1
            cbc_p1_rows_eval = []
            for _, r in edited_cbc_p1.iterrows():
                p_name = r['รายการย่อย']
                l_res = float(r['Lab Result'])
                di = float(r['Lab DI'])
                perf = evaluate_di_performance(di)
                cbc_p1_rows_eval.append({"Parameter": p_name, "Lab Result": l_res, "Lab DI": di, "Performance": perf})
                
                if di > 1.0:
                    nc_items.append({
                        "รายการ/Sample": f"{sample_id_input} - CBC P.1 ({p_name})",
                        "ผลตรวจห้องปฏิบัติการ": str(l_res),
                        "ค่าเป้าหมาย (Lab DI)": str(di),
                        "สถานะปัญหา": f"Performance: {perf}"
                    })

            # --- ส่วนที่ 2: Slide smear ---
            st.markdown("###### **ส่วนที่ 2: Slide smear**")
            
            # ส่วนย่อยที่ 1: WBC differential count
            st.markdown("**1. WBC differential count**")
            wbc_diff_data = []
            for param in WBC_DIFF_PARAMETERS:
                wbc_diff_data.append({
                    "รายการย่อย": param,
                    "Lab Result": 0.0,
                    "Lab DI": 0.0,
                    "Mean": 0.0,
                    "SD": 0.0
                })
            
            wbc_diff_df = pd.DataFrame(wbc_diff_data)
            edited_wbc_diff = st.data_editor(
                wbc_diff_df,
                key=f"wbc_diff_editor_{s_idx}",
                use_container_width=True,
                column_config={
                    "รายการย่อย": st.column_config.TextColumn("รายการย่อย", disabled=True),
                    "Lab Result": st.column_config.NumberColumn("Lab Result", format="%.2f", required=True),
                    "Lab DI": st.column_config.NumberColumn("Lab DI", format="%.2f", required=True),
                    "Mean": st.column_config.NumberColumn("Mean", format="%.2f", required=True),
                    "SD": st.column_config.NumberColumn("SD", format="%.2f", required=True)
                }
            )
            
            wbc_diff_rows_eval = []
            for _, r in edited_wbc_diff.iterrows():
                p_name = r['รายการย่อย']
                l_res = float(r['Lab Result'])
                di = float(r['Lab DI'])
                mean_val = float(r['Mean'])
                sd_val = float(r['SD'])
                perf = evaluate_di_performance(di)
                wbc_diff_rows_eval.append({"Parameter": p_name, "Lab Result": l_res, "Lab DI": di, "Mean": mean_val, "SD": sd_val, "Performance": perf})
                
                if di > 1.0:
                    nc_items.append({
                        "รายการ/Sample": f"{sample_id_input} - WBC diff ({p_name})",
                        "ผลตรวจห้องปฏิบัติการ": str(l_res),
                        "ค่าเป้าหมาย (Lab DI)": str(di),
                        "สถานะปัญหา": f"Performance: {perf}"
                    })

            # ส่วนย่อยที่ 2: RBC morphology
            st.markdown("**2. RBC morphology**")
            rbc_morph_data = []
            for param in RBC_MORPHOLOGY_PARAMETERS:
                rbc_morph_data.append({
                    "รายการย่อย": param,
                    "Lab Result": "normocytes",
                    "Assigned Value": "normocytes"
                })
            
            rbc_morph_df = pd.DataFrame(rbc_morph_data)
            edited_rbc_morph = st.data_editor(
                rbc_morph_df,
                key=f"rbc_morph_editor_{s_idx}",
                use_container_width=True,
                column_config={
                    "รายการย่อย": st.column_config.TextColumn("รายการย่อย", disabled=True),
                    "Lab Result": st.column_config.TextColumn("Lab Result", required=True),
                    "Assigned Value": st.column_config.TextColumn("Assigned Value", required=True)
                }
            )
            
            rbc_score = st.number_input(f"Score รวม RBC morphology ({sample_id_input})", min_value=0.0, max_value=4.0, value=3.5, step=0.1, key=f"rbc_score_{s_idx}")
            rbc_perf = evaluate_score_performance(rbc_score)
            st.caption(f"ระดับ Performance ของ RBC morphology: **{rbc_perf}**")

            # ส่วนย่อยที่ 3: Platelet estimation
            st.markdown("**3. Platelet estimation**")
            plt_est_data = []
            for param in PLATELET_EST_PARAMETERS:
                plt_est_data.append({
                    "รายการย่อย": param,
                    "Lab Result": "adequate",
                    "Assigned Value": "adequate"
                })
            
            plt_est_df = pd.DataFrame(plt_est_data)
            edited_plt_est = st.data_editor(
                plt_est_df,
                key=f"plt_est_editor_{s_idx}",
                use_container_width=True,
                column_config={
                    "รายการย่อย": st.column_config.TextColumn("รายการย่อย", disabled=True),
                    "Lab Result": st.column_config.TextColumn("Lab Result", required=True),
                    "Assigned Value": st.column_config.TextColumn("Assigned Value", required=True)
                }
            )
            
            plt_score = st.number_input(f"Score รวม Platelet estimation ({sample_id_input})", min_value=0.0, max_value=4.0, value=3.5, step=0.1, key=f"plt_score_{s_idx}")
            plt_perf = evaluate_score_performance(plt_score)
            st.caption(f"ระดับ Performance ของ Platelet estimation: **{plt_perf}**")

            cbc_results[sample_id_input] = {
                "p1": cbc_p1_rows_eval,
                "wbc_diff": wbc_diff_rows_eval,
                "rbc_score": rbc_score,
                "rbc_perf": rbc_perf,
                "plt_score": plt_score,
                "plt_perf": plt_perf
            }

        st.markdown("---")
        st.markdown("#### 🎯 ผลการสรุปภาพรวม CBC")
        st.success("บันทึกข้อมูลโครงสร้าง CBC 2 ส่วนเรียบร้อยแล้ว")

    # 2. กรณี Gram's stain
    elif test_name == "Gram's stain":
        st.info("💡 **Gram's stain**: กรอกผลแยกตาม 2 หัวข้อย่อย ได้แก่ การติดสี (Gram Reaction) และ รูปร่างของแบคทีเรีย (Morphology)")
        
        gram_results = {}
        total_obtained_all_samples = 0.0
        total_max_all_samples = 0.0

        for s_idx in range(num_samples):
            st.markdown(f"##### 🧫 **ตัวอย่างที่ {s_idx + 1}**")
            sample_id_input = st.text_input(f"ชื่อ/รหัสตัวอย่าง (Sample ID)", value=f"Sample {s_idx + 1}", key=f"gram_sid_key_{s_idx}")
            
            categories = ["การติดสี (Gram Reaction)", "รูปร่างของแบคทีเรีย (Morphology)"]
            sample_obtained = 0.0
            sample_max = 0.0
            sample_details = []

            with st.expander(f"📌 กรอกผล Gram's stain สำหรับ {sample_id_input}", expanded=True):
                for cat in categories:
                    st.markdown(f"**🔹 {cat}**")
                    col_res1, col_res2, col_sc1, col_sc2 = st.columns([3, 3, 1, 1])
                    
                    opts = GRAM_REACTION_OPTIONS if cat == "การติดสี (Gram Reaction)" else GRAM_MORPHOLOGY_OPTIONS
                    
                    with col_res1:
                        lab_ans = st.selectbox(f"Lab Result ({cat})", options=opts, key=f"lab_gram_{s_idx}_{cat}")
                    with col_res2:
                        assign_ans = st.selectbox(f"Assigned Value ({cat})", options=opts, key=f"ass_gram_{s_idx}_{cat}")

                    with col_sc1:
                        obt_score = st.number_input("คะแนนได้", min_value=0.0, value=1.0, step=0.5, key=f"obt_gram_{s_idx}_{cat}")
                    with col_sc2:
                        max_score = st.number_input("คะแนนเต็ม", min_value=0.1, value=1.0, step=0.5, key=f"max_gram_{s_idx}_{cat}")

                    sample_obtained += obt_score
                    sample_max += max_score

                    sample_details.append({
                        "หัวข้อย่อย": cat,
                        "Lab Result": lab_ans,
                        "Assigned Value": assign_ans,
                        "คะแนนที่ได้": obt_score,
                        "คะแนนเต็ม": max_score
                    })

                    if lab_ans != assign_ans or obt_score < max_score:
                        nc_items.append({
                            "รายการ/Sample": f"{sample_id_input} - Gram's stain ({cat})",
                            "ผลตรวจห้องปฏิบัติการ": lab_ans,
                            "ค่าเป้าหมาย (Assigned Value)": assign_ans,
                            "สถานะปัญหา": f"Mismatch / คะแนนได้ {obt_score}/{max_score}"
                        })

            total_obtained_all_samples += sample_obtained
            total_max_all_samples += sample_max
            gram_results[sample_id_input] = (pd.DataFrame(sample_details), sample_obtained, sample_max)
            st.caption(f"คะแนนรวมเฉพาะ {sample_id_input}: **{sample_obtained:.1f} / {sample_max:.1f}**")

        overall_std_score = round((total_obtained_all_samples * 4.0) / total_max_all_samples, 2) if total_max_all_samples > 0 else 0.0
        overall_score_pct = (total_obtained_all_samples / total_max_all_samples * 100.0) if total_max_all_samples > 0 else 0.0

        if overall_std_score >= 4.0:
            eval_status = "Excellent"
        elif 3.50 <= overall_std_score < 4.0:
            eval_status = "Good"
        elif 3.00 <= overall_std_score < 3.50:
            eval_status = "Satisfactory"
        else:
            eval_status = "Unsatisfactory"

        st.markdown("---")
        st.markdown("#### 🎯 ผลการสรุปคะแนนภาพรวม Gram's stain (รวมทุก Sample)")
        sc_c1, sc_c2, sc_c3 = st.columns(3)
        sc_c1.metric("คะแนนรวมทุก Sample", f"{total_obtained_all_samples:.1f} / {total_max_all_samples:.1f}")
        sc_c2.metric("Overall Standard Score", f"{overall_std_score:.2f}")
        sc_c3.metric("Scoring Evaluation", eval_status)

    # 3. กรณี Blood parasite & Stool examination
    elif test_name in ["Blood parasite", "Blood parasite (digital slide)", "Stool examination"]:
        st.info(f"💡 **{test_name}**: หัวข้อย่อยถูกล็อกไว้ตามมาตรฐาน — ท่านสามารถเลือก/พิมพ์คำตอบได้มากกว่า 1 รายการ (Multi-select) ในช่อง Lab Result และ Assigned Value")
        
        bp_results = {}
        total_obtained_all_samples = 0.0
        total_max_all_samples = 0.0

        for s_idx in range(num_samples):
            st.markdown(f"##### 🔬 **ตัวอย่างที่ {s_idx + 1}**")
            sample_id_input = st.text_input(f"ชื่อ/รหัสตัวอย่าง (Sample ID)", value=f"Sample {s_idx + 1}", key=f"bp_sid_key_{s_idx}")
            
            categories = ["ตระกูลและสายพันธุ์ (Species)", "ระยะที่พบ (Stage)"]
            if test_name != "Stool examination":
                categories.append("% Parasitemia")

            sample_obtained = 0.0
            sample_max = 0.0
            sample_details = []

            with st.expander(f"📌 กรอกผลตรวจสำหรับ {sample_id_input}", expanded=True):
                for cat in categories:
                    st.markdown(f"**🔹 {cat}**")
                    col_res1, col_res2, col_sc1, col_sc2 = st.columns([3, 3, 1, 1])
                    
                    if cat == "ตระกูลและสายพันธุ์ (Species)":
                        with col_res1:
                            lab_ans = st.multiselect(
                                f"Lab Result ({cat})", 
                                options=SPECIES_OPTIONS, 
                                default=["Plasmodium falciparum"] if "Blood parasite" in test_name else ["Entamoeba histolytica"],
                                key=f"lab_{s_idx}_{cat}"
                            )
                        with col_res2:
                            assign_ans = st.multiselect(
                                f"Assigned Value ({cat})", 
                                options=SPECIES_OPTIONS, 
                                default=["Plasmodium falciparum"] if "Blood parasite" in test_name else ["Entamoeba histolytica"],
                                key=f"ass_{s_idx}_{cat}"
                            )
                    elif cat == "ระยะที่พบ (Stage)":
                        with col_res1:
                            lab_ans = st.multiselect(
                                f"Lab Result ({cat})", 
                                options=STAGE_OPTIONS, 
                                default=["Ring form"] if "Blood parasite" in test_name else ["Cyst"],
                                key=f"lab_{s_idx}_{cat}"
                            )
                        with col_res2:
                            assign_ans = st.multiselect(
                                f"Assigned Value ({cat})", 
                                options=STAGE_OPTIONS, 
                                default=["Ring form"] if "Blood parasite" in test_name else ["Cyst"],
                                key=f"ass_{s_idx}_{cat}"
                            )
                    else: # % Parasitemia
                        with col_res1:
                            lab_ans = st.text_input(f"Lab Result ({cat})", value="1.5%", key=f"lab_{s_idx}_{cat}")
                        with col_res2:
                            assign_ans = st.text_input(f"Assigned Value ({cat})", value="1.5%", key=f"ass_{s_idx}_{cat}")

                    with col_sc1:
                        obt_score = st.number_input("คะแนนได้", min_value=0.0, value=1.0, step=0.5, key=f"obt_{s_idx}_{cat}")
                    with col_sc2:
                        max_score = st.number_input("คะแนนเต็ม", min_value=0.1, value=1.0, step=0.5, key=f"max_{s_idx}_{cat}")

                    lab_str = ", ".join(lab_ans) if isinstance(lab_ans, list) else str(lab_ans)
                    assign_str = ", ".join(assign_ans) if isinstance(assign_ans, list) else str(assign_ans)

                    sample_obtained += obt_score
                    sample_max += max_score

                    sample_details.append({
                        "หัวข้อย่อย": cat,
                        "Lab Result": lab_str,
                        "Assigned Value": assign_str,
                        "คะแนนที่ได้": obt_score,
                        "คะแนนเต็ม": max_score
                    })

                    is_mismatch = set(lab_ans) != set(assign_ans) if isinstance(lab_ans, list) else lab_str != assign_str
                    if is_mismatch or obt_score < max_score:
                        nc_items.append({
                            "รายการ/Sample": f"{sample_id_input} - {test_name} ({cat})",
                            "ผลตรวจห้องปฏิบัติการ": lab_str,
                            "ค่าเป้าหมาย (Assigned Value)": assign_str,
                            "สถานะปัญหา": f"Mismatch / คะแนนได้ {obt_score}/{max_score}"
                        })

            total_obtained_all_samples += sample_obtained
            total_max_all_samples += sample_max
            bp_results[sample_id_input] = (pd.DataFrame(sample_details), sample_obtained, sample_max)
            st.caption(f"คะแนนรวมเฉพาะ {sample_id_input}: **{sample_obtained:.1f} / {sample_max:.1f}**")

        overall_std_score = round((total_obtained_all_samples * 4.0) / total_max_all_samples, 2) if total_max_all_samples > 0 else 0.0
        overall_score_pct = (total_obtained_all_samples / total_max_all_samples * 100.0) if total_max_all_samples > 0 else 0.0

        if overall_std_score >= 4.0:
            eval_status = "Excellent"
        elif 3.50 <= overall_std_score < 4.0:
            eval_status = "Good"
        elif 3.00 <= overall_std_score < 3.50:
            eval_status = "Satisfactory"
        else:
            eval_status = "Unsatisfactory"

        st.markdown("---")
        st.markdown(f"#### 🎯 ผลการสรุปคะแนนภาพรวม {test_name} (รวมทุก Sample)")
        sc_c1, sc_c2, sc_c3 = st.columns(3)
        sc_c1.metric("คะแนนรวมทุก Sample", f"{total_obtained_all_samples:.1f} / {total_max_all_samples:.1f}")
        sc_c2.metric("Overall Standard Score", f"{overall_std_score:.2f}")
        sc_c3.metric("Scoring Evaluation", eval_status)

    # 4. กรณี UA (Urinalysis)
    elif test_name == "UA":
        st.info("💡 ป้อนค่า Assigned Value และคะแนนในแต่ละพารามิเตอร์ เพื่อคำนวณ Standard Score รวม")
        
        ua_results = {}
        total_obtained_all_samples = 0.0
        total_max_all_samples = 0.0

        for s_idx in range(num_samples):
            st.markdown(f"##### 🧪 **ตัวอย่างที่ {s_idx + 1}**")
            sample_id_input = st.text_input(f"ชื่อ/รหัสตัวอย่าง (Sample ID)", value=f"Sample {s_idx + 1}", key=f"ua_sid_key_{s_idx}")
            
            ua_data = []
            for param in UA_PARAMETERS:
                opts = UA_OPTIONS[param]
                ua_data.append({
                    "พารามิเตอร์ (Parameter)": param,
                    "Lab Result": opts[0],
                    "Assigned Value": opts[0],
                    "คะแนนที่ได้ (Obtained)": 1.0,
                    "คะแนนเต็ม (Max Score)": 1.0
                })
            
            ua_df = pd.DataFrame(ua_data)
            edited_ua = st.data_editor(
                ua_df,
                key=f"ua_editor_{s_idx}",
                use_container_width=True,
                column_config={
                    "พารามิเตอร์ (Parameter)": st.column_config.TextColumn("พารามิเตอร์", disabled=True),
                    "Lab Result": st.column_config.SelectboxColumn("Lab Result", options=list(set(sum(UA_OPTIONS.values(), []))), required=True),
                    "Assigned Value": st.column_config.SelectboxColumn("Assigned Value", options=list(set(sum(UA_OPTIONS.values(), []))), required=True),
                    "คะแนนที่ได้ (Obtained)": st.column_config.NumberColumn("คะแนนที่ได้", min_value=0.0, format="%.1f"),
                    "คะแนนเต็ม (Max Score)": st.column_config.NumberColumn("คะแนนเต็ม", min_value=0.1, format="%.1f")
                }
            )
            
            sample_obt = edited_ua['คะแนนที่ได้ (Obtained)'].sum()
            sample_max = edited_ua['คะแนนเต็ม (Max Score)'].sum()
            
            total_obtained_all_samples += sample_obt
            total_max_all_samples += sample_max
            
            for _, r in edited_ua.iterrows():
                l_res, a_val = str(r['Lab Result']), str(r['Assigned Value'])
                obt_sc, max_sc = float(r['คะแนนที่ได้ (Obtained)']), float(r['คะแนนเต็ม (Max Score)'])
                if l_res != a_val or obt_sc < max_sc:
                    nc_items.append({
                        "รายการ/Sample": f"{sample_id_input} - UA ({r['พารามิเตอร์ (Parameter)']})",
                        "ผลตรวจห้องปฏิบัติการ": l_res,
                        "ค่าเป้าหมาย (Assigned Value)": a_val,
                        "สถานะปัญหา": "Mismatch / คะแนนไม่เต็ม"
                    })

            ua_results[sample_id_input] = (edited_ua, sample_obt, sample_max)
            st.caption(f"คะแนนเฉพาะ {sample_id_input}: {sample_obt:.1f} / {sample_max:.1f}")

        overall_std_score = round((total_obtained_all_samples * 4.0) / total_max_all_samples, 2) if total_max_all_samples > 0 else 0.0
        overall_score_pct = (total_obtained_all_samples / total_max_all_samples * 100.0) if total_max_all_samples > 0 else 0.0

        if overall_std_score >= 4.0:
            eval_status = "Excellent"
        elif 3.50 <= overall_std_score < 4.0:
            eval_status = "Good"
        elif 3.00 <= overall_std_score < 3.50:
            eval_status = "Satisfactory"
        else:
            eval_status = "Unsatisfactory"

        st.markdown("---")
        st.markdown("#### 🎯 ผลการสรุปคะแนนภาพรวม UA (รวมทุก Sample)")
        sc_c1, sc_c2, sc_c3 = st.columns(3)
        sc_c1.metric("คะแนนรวมทุก Sample", f"{total_obtained_all_samples:.1f} / {total_max_all_samples:.1f}")
        sc_c2.metric("Overall Standard Score", f"{overall_std_score:.2f}")
        sc_c3.metric("Scoring Evaluation", eval_status)

    # 5. กรณี Quantitative
    elif "Quantitative" in test_type:
        st.info("💡 สามารถปรับแต่งชื่อ Sample ID และกรอกผล Lab, ค่า Peer Group (Assigned Value/SD), ค่า %CV Lab และ TEa% ได้ในตาราง")
        default_tea = TEA_TABLE.get(test_name, TEA_TABLE["DEFAULT"])
        
        init_data = pd.DataFrame({
            'รหัสตัวอย่าง (Sample ID)': [f"Sample {i+1}" for i in range(num_samples)],
            'Lab Result': [100.0] * num_samples,
            'Assigned Value': [100.0] * num_samples,
            'SD Group': [3.0] * num_samples,
            'Lab SD': [2.0] * num_samples,
            'Lab %CV': [2.0] * num_samples,
            'TEa (%)': [default_tea] * num_samples,
            'Interpretation': ['Acceptable'] * num_samples
        })
        
        edited_df = st.data_editor(
            init_data, 
            num_rows="dynamic", 
            use_container_width=True,
            column_config={
                "รหัสตัวอย่าง (Sample ID)": st.column_config.TextColumn("รหัสตัวอย่าง (Sample ID)", required=True),
                "Lab Result": st.column_config.NumberColumn("Lab Result", format="%.2f"),
                "Assigned Value": st.column_config.NumberColumn("Assigned Value", format="%.2f"),
                "SD Group": st.column_config.NumberColumn("SD Group (Peer)", format="%.2f"),
                "Lab SD": st.column_config.NumberColumn("Lab SD", format="%.2f"),
                "Lab %CV": st.column_config.NumberColumn("Lab %CV", format="%.2f%%"),
                "TEa (%)": st.column_config.NumberColumn("TEa (%)", format="%.1f%%"),
                "Interpretation": st.column_config.SelectboxColumn("Interpretation", options=["Acceptable", "Warning", "Unacceptable", "Action Required"])
            }
        )

        calc_rows = []
        for _, r in edited_df.iterrows():
            l_res, a_val, sd_grp = float(r['Lab Result']), float(r['Assigned Value']), float(r['SD Group'])
            cv_lab, tea = float(r['Lab %CV']), float(r['TEa (%)'])
            s_id, interp = str(r['รหัสตัวอย่าง (Sample ID)']), str(r['Interpretation'])
            
            z_score = (l_res - a_val) / sd_grp if sd_grp > 0 else np.nan
            bias_pct = (abs(l_res - a_val) / a_val * 100) if a_val > 0 else np.nan
            sigma = ((tea - bias_pct) / cv_lab) if cv_lab > 0 and not np.isnan(bias_pct) else np.nan
            rule = evaluate_westgard_rules(sigma)
            
            calc_rows.append({'Z-Score': z_score, 'Bias (%)': bias_pct, 'Sigma': sigma, 'Multirule': rule})

            if interp in ["Unacceptable", "Warning", "Action Required"] or (not np.isnan(z_score) and abs(z_score) > 2.0):
                nc_items.append({
                    "รายการ/Sample": f"{test_name} ({s_id})",
                    "ผลตรวจห้องปฏิบัติการ": str(l_res),
                    "ค่าเป้าหมาย (Assigned Value)": str(a_val),
                    "สถานะปัญหา": f"{interp} (Z-score: {z_score:.2f})"
                })

        res_summary = pd.DataFrame(calc_rows)
        
        st.markdown("#### 🎯 ผลการประมวลผล Sigma Metric & Westgard Rule (Real-time)")
        res_cols = st.columns(min(len(calc_rows), 5))
        for idx, row_res in res_summary.iterrows():
            with res_cols[idx % len(res_cols)]:
                st.metric(f"{edited_df.iloc[idx]['รหัสตัวอย่าง (Sample ID)']} - Z-score", f"{row_res['Z-Score']:.2f}" if not np.isnan(row_res['Z-Score']) else "N/A")
                st.metric("Sigma Metric", f"{row_res['Sigma']:.2f}" if not np.isnan(row_res['Sigma']) else "N/A")
                st.caption(f"**Rule**: {row_res['Multirule']}")

    # 6. กรณี Qualitative with Scoring
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
            calc_status = "Unsatisfactory"
            status_desc = "ต้องปรับปรุง / ไม่ผ่านเกณฑ์ (< 70.0%)"

        for _, r in edited_df.iterrows():
            l_res, a_val = str(r['Lab Result']), str(r['Assigned Value'])
            s_id = str(r['รหัสตัวอย่าง (Sample ID)'])
            obt_sc, max_sc = float(r['คะแนนที่ได้ (Obtained)']), float(r['คะแนนเต็ม (Max Score)'])
            if l_res != a_val or obt_sc < max_sc:
                nc_items.append({
                    "รายการ/Sample": f"{test_name} ({s_id})",
                    "ผลตรวจห้องปฏิบัติการ": l_res,
                    "ค่าเป้าหมาย (Assigned Value)": a_val,
                    "สถานะปัญหา": "Mismatch / คะแนนไม่เต็ม"
                })

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

    # 7. กรณี Qualitative Basic
    else:
        st.info("💡 กรอกผลตรวจและค่าเป้าหมายเพื่อเทียบความสอดคล้อง (Concordance)")
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
                "Lab Result": st.column_config.TextColumn("Lab Result", required=True) if test_name == "Urine sediment by photo observation" else st.column_config.SelectboxColumn("Lab Result", options=qual_opts, required=True),
                "Assigned Value": st.column_config.TextColumn("Assigned Value", required=True) if test_name == "Urine sediment by photo observation" else st.column_config.SelectboxColumn("Assigned Value", options=qual_opts, required=True)
            }
        )

        for _, r in edited_df.iterrows():
            l_res, a_val = str(r['Lab Result']), str(r['Assigned Value'])
            s_id = str(r['รหัสตัวอย่าง (Sample ID)'])
            if l_res != a_val:
                nc_items.append({
                    "รายการ/Sample": f"{test_name} ({s_id})",
                    "ผลตรวจห้องปฏิบัติการ": l_res,
                    "ค่าเป้าหมาย (Assigned Value)": a_val,
                    "สถานะปัญหา": "Mismatch"
                })

    # ส่วนทบทวนและวิเคราะห์สาเหตุ (Non-conformity)
    st.markdown("---")
    st.subheader("🔍 สรุปรายการที่ไม่เป็นไปตามข้อกำหนด & การทบทวนทางเทคนิค (ISO 15189)")
    
    if nc_items:
        st.warning(f"⚠️ พบ {len(nc_items)} รายการที่ไม่เป็นไปตามข้อกำหนด/ไม่ผ่านเกณฑ์ กรุณาระบุสาเหตุและผลการทบทวนเพื่อแก้ไข")
        nc_df = pd.DataFrame(nc_items)
        st.dataframe(nc_df, use_container_width=True)
    else:
        st.success("✅ ผลการทดสอบทุกรายการผ่านเกณฑ์ตามข้อกำหนดทั้งหมด")

    col_rc1, col_rc2 = st.columns(2)
    with col_rc1:
        root_cause = st.text_area(
            "📌 สาเหตุที่ไม่ผ่าน / สิ่งที่ไม่เป็นไปตามข้อกำหนด (Root Cause Analysis)", 
            placeholder="เช่น Identification Error, Over-decolorization, Human Error",
            height=120
        )
    with col_rc2:
        review_action = st.text_area(
            "🛠️ ผลการทบทวน / มาตรการแก้ไขและป้องกัน (Corrective & Preventive Action / Management Review)", 
            placeholder="เช่น ปรับปรุงเทคนิคการย้อม Gram, จัด Training การอ่านลักษณะ Morphology, สอบทานสไลด์ร่วมกับผู้เชี่ยวชาญ",
            height=120
        )

    # ปุ่มบันทึกข้อมูล
    if st.button("💾 บันทึกผล EQA และบันทึกการทบทวน", type="primary"):
        if not test_name:
            st.error("กรุณาระบุชื่อรายการทดสอบก่อนบันทึก")
        else:
            new_rows = []
            
            # บันทึก CBC (ตามโครงสร้างใหม่ 2 ส่วน)
            if test_name == "CBC":
                for s_label, sub_data in cbc_results.items():
                    # ส่วนที่ 1
                    for item in sub_data["p1"]:
                        new_rows.append({
                            'Cycle': cycle,
                            'Department': department,
                            'Test_Name': f"CBC P.1 ({item['Parameter']})",
                            'Test_Method': test_method,
                            'Sample_ID': s_label,
                            'Test_Type': 'Quantitative (CBC Part 1)',
                            'Lab_Result': item['Lab Result'],
                            'Assigned_Value': np.nan,
                            'SD_Group': np.nan,
                            'Z_Score': np.nan,
                            'Interpretation': item['Performance'],
                            'Lab_SD': np.nan,
                            'Lab_CV': np.nan,
                            'TEa_Percent': np.nan,
                            'Bias_Percent': np.nan,
                            'Sigma_Metric': np.nan,
                            'Recommended_Multirule': 'N/A',
                            'Score_Obtained': np.nan,
                            'Max_Score': np.nan,
                            'Score_Percent': np.nan,
                            'Standard_Score': np.nan,
                            'Status': item['Performance'],
                            'Root_Cause': root_cause,
                            'Review_Action': review_action
                        })
                    # ส่วนที่ 2: WBC diff
                    for item in sub_data["wbc_diff"]:
                        new_rows.append({
                            'Cycle': cycle,
                            'Department': department,
                            'Test_Name': f"Slide smear - WBC diff ({item['Parameter']})",
                            'Test_Method': test_method,
                            'Sample_ID': s_label,
                            'Test_Type': 'Slide Smear (WBC Diff)',
                            'Lab_Result': item['Lab Result'],
                            'Assigned_Value': item['Mean'],
                            'SD_Group': item['SD'],
                            'Z_Score': np.nan,
                            'Interpretation': item['Performance'],
                            'Lab_SD': np.nan,
                            'Lab_CV': np.nan,
                            'TEa_Percent': np.nan,
                            'Bias_Percent': np.nan,
                            'Sigma_Metric': np.nan,
                            'Recommended_Multirule': 'N/A',
                            'Score_Obtained': np.nan,
                            'Max_Score': np.nan,
                            'Score_Percent': np.nan,
                            'Standard_Score': np.nan,
                            'Status': item['Performance'],
                            'Root_Cause': root_cause,
                            'Review_Action': review_action
                        })
                    # ส่วนที่ 2: RBC morphology
                    new_rows.append({
                        'Cycle': cycle,
                        'Department': department,
                        'Test_Name': "Slide smear - RBC morphology",
                        'Test_Method': test_method,
                        'Sample_ID': s_label,
                        'Test_Type': 'Slide Smear (RBC Morphology)',
                        'Lab_Result': sub_data["rbc_score"],
                        'Assigned_Value': 4.0,
                        'SD_Group': np.nan,
                        'Z_Score': np.nan,
                        'Interpretation': sub_data["rbc_perf"],
                        'Lab_SD': np.nan,
                        'Lab_CV': np.nan,
                        'TEa_Percent': np.nan,
                        'Bias_Percent': np.nan,
                        'Sigma_Metric': np.nan,
                        'Recommended_Multirule': 'N/A',
                        'Score_Obtained': sub_data["rbc_score"],
                        'Max_Score': 4.0,
                        'Score_Percent': (sub_data["rbc_score"]/4.0)*100,
                        'Standard_Score': sub_data["rbc_score"],
                        'Status': sub_data["rbc_perf"],
                        'Root_Cause': root_cause,
                        'Review_Action': review_action
                    })
                    # ส่วนที่ 2: Platelet estimation
                    new_rows.append({
                        'Cycle': cycle,
                        'Department': department,
                        'Test_Name': "Slide smear - Platelet estimation",
                        'Test_Method': test_method,
                        'Sample_ID': s_label,
                        'Test_Type': 'Slide Smear (Platelet Est)',
                        'Lab_Result': sub_data["plt_score"],
                        'Assigned_Value': 4.0,
                        'SD_Group': np.nan,
                        'Z_Score': np.nan,
                        'Interpretation': sub_data["plt_perf"],
                        'Lab_SD': np.nan,
                        'Lab_CV': np.nan,
                        'TEa_Percent': np.nan,
                        'Bias_Percent': np.nan,
                        'Sigma_Metric': np.nan,
                        'Recommended_Multirule': 'N/A',
                        'Score_Obtained': sub_data["plt_score"],
                        'Max_Score': 4.0,
                        'Score_Percent': (sub_data["plt_score"]/4.0)*100,
                        'Standard_Score': sub_data["plt_score"],
                        'Status': sub_data["plt_perf"],
                        'Root_Cause': root_cause,
                        'Review_Action': review_action
                    })

            # บันทึก Gram's stain
            elif test_name == "Gram's stain":
                for s_label, (sub_df, sub_tot_obt, sub_tot_m) in gram_results.items():
                    for _, r in sub_df.iterrows():
                        cat_name = str(r['หัวข้อย่อย'])
                        l_val = str(r['Lab Result'])
                        a_val = str(r['Assigned Value'])
                        sub_obt = float(r['คะแนนที่ได้'])
                        sub_max = float(r['คะแนนเต็ม'])
                        
                        new_rows.append({
                            'Cycle': cycle,
                            'Department': department,
                            'Test_Name': f"Gram's stain ({cat_name})",
                            'Test_Method': test_method,
                            'Sample_ID': s_label,
                            'Test_Type': 'Qualitative (Gram\'s stain Sub-parameter)',
                            'Lab_Result': l_val,
                            'Assigned_Value': a_val,
                            'SD_Group': np.nan,
                            'Z_Score': np.nan,
                            'Interpretation': "Match" if l_val == a_val else "Mismatch",
                            'Lab_SD': np.nan,
                            'Lab_CV': np.nan,
                            'TEa_Percent': np.nan,
                            'Bias_Percent': np.nan,
                            'Sigma_Metric': np.nan,
                            'Recommended_Multirule': 'N/A',
                            'Score_Obtained': sub_obt,
                            'Max_Score': sub_max,
                            'Score_Percent': round(overall_score_pct, 2),
                            'Standard_Score': round(overall_std_score, 2),
                            'Status': eval_status,
                            'Root_Cause': root_cause,
                            'Review_Action': review_action
                        })

            # บันทึกกลุ่ม Blood parasite / Stool
            elif test_name in ["Blood parasite", "Blood parasite (digital slide)", "Stool examination"]:
                for s_label, (sub_df, sub_tot_obt, sub_tot_m) in bp_results.items():
                    for _, r in sub_df.iterrows():
                        cat_name = str(r['หัวข้อย่อย'])
                        l_val = str(r['Lab Result'])
                        a_val = str(r['Assigned Value'])
                        sub_obt = float(r['คะแนนที่ได้'])
                        sub_max = float(r['คะแนนเต็ม'])
                        
                        new_rows.append({
                            'Cycle': cycle,
                            'Department': department,
                            'Test_Name': f"{test_name} ({cat_name})",
                            'Test_Method': test_method,
                            'Sample_ID': s_label,
                            'Test_Type': f'Qualitative ({test_name} Sub-parameter)',
                            'Lab_Result': l_val,
                            'Assigned_Value': a_val,
                            'SD_Group': np.nan,
                            'Z_Score': np.nan,
                            'Interpretation': "Match" if l_val == a_val else "Mismatch",
                            'Lab_SD': np.nan,
                            'Lab_CV': np.nan,
                            'TEa_Percent': np.nan,
                            'Bias_Percent': np.nan,
                            'Sigma_Metric': np.nan,
                            'Recommended_Multirule': 'N/A',
                            'Score_Obtained': sub_obt,
                            'Max_Score': sub_max,
                            'Score_Percent': round(overall_score_pct, 2),
                            'Standard_Score': round(overall_std_score, 2),
                            'Status': eval_status,
                            'Root_Cause': root_cause,
                            'Review_Action': review_action
                        })

            # บันทึกกลุ่ม UA
            elif test_name == "UA":
                for s_label, (sub_df, sub_tot_obt, sub_tot_m) in ua_results.items():
                    for _, r in sub_df.iterrows():
                        p_name = r['พารามิเตอร์ (Parameter)']
                        l_val = str(r['Lab Result'])
                        a_val = str(r['Assigned Value'])
                        sub_obt = float(r['คะแนนที่ได้ (Obtained)'])
                        sub_max = float(r['คะแนนเต็ม (Max Score)'])
                        
                        new_rows.append({
                            'Cycle': cycle,
                            'Department': department,
                            'Test_Name': f"UA ({p_name})",
                            'Test_Method': test_method,
                            'Sample_ID': s_label,
                            'Test_Type': 'Qualitative (UA Sub-parameter)',
                            'Lab_Result': l_val,
                            'Assigned_Value': a_val,
                            'SD_Group': np.nan,
                            'Z_Score': np.nan,
                            'Interpretation': "Match" if l_val == a_val else "Mismatch",
                            'Lab_SD': np.nan,
                            'Lab_CV': np.nan,
                            'TEa_Percent': np.nan,
                            'Bias_Percent': np.nan,
                            'Sigma_Metric': np.nan,
                            'Recommended_Multirule': 'N/A',
                            'Score_Obtained': sub_obt,
                            'Max_Score': sub_max,
                            'Score_Percent': round(overall_score_pct, 2),
                            'Standard_Score': round(overall_std_score, 2),
                            'Status': eval_status,
                            'Root_Cause': root_cause,
                            'Review_Action': review_action
                        })

            # บันทึกกลุ่ม Quantitative
            elif "Quantitative" in test_type:
                for idx, r in edited_df.iterrows():
                    l_res, a_val, sd_grp = float(r['Lab Result']), float(r['Assigned Value']), float(r['SD Group'])
                    l_sd, cv_lab, tea = float(r['Lab SD']), float(r['Lab %CV']), float(r['TEa (%)'])
                    s_id, interp = str(r['รหัสตัวอย่าง (Sample ID)']), str(r['Interpretation'])
                    
                    row_calc = calc_rows[idx]
                    
                    new_rows.append({
                        'Cycle': cycle,
                        'Department': department,
                        'Test_Name': test_name,
                        'Test_Method': test_method,
                        'Sample_ID': s_id,
                        'Test_Type': test_type,
                        'Lab_Result': l_res,
                        'Assigned_Value': a_val,
                        'SD_Group': sd_grp,
                        'Z_Score': row_calc['Z-Score'],
                        'Interpretation': interp,
                        'Lab_SD': l_sd,
                        'Lab_CV': cv_lab,
                        'TEa_Percent': tea,
                        'Bias_Percent': row_calc['Bias (%)'],
                        'Sigma_Metric': row_calc['Sigma'],
                        'Recommended_Multirule': row_calc['Multirule'],
                        'Score_Obtained': np.nan,
                        'Max_Score': np.nan,
                        'Score_Percent': np.nan,
                        'Standard_Score': np.nan,
                        'Status': interp,
                        'Root_Cause': root_cause,
                        'Review_Action': review_action
                    })

            # บันทึกกลุ่ม Qualitative with Scoring
            elif "Scoring" in test_type:
                for _, r in edited_df.iterrows():
                    s_id = str(r['รหัสตัวอย่าง (Sample ID)'])
                    l_res, a_val = str(r['Lab Result']), str(r['Assigned Value'])
                    obt_sc, max_sc = float(r['คะแนนที่ได้ (Obtained)']), float(r['คะแนนเต็ม (Max Score)'])
                    
                    new_rows.append({
                        'Cycle': cycle,
                        'Department': department,
                        'Test_Name': test_name,
                        'Test_Method': test_method,
                        'Sample_ID': s_id,
                        'Test_Type': test_type,
                        'Lab_Result': l_res,
                        'Assigned_Value': a_val,
                        'SD_Group': np.nan,
                        'Z_Score': np.nan,
                        'Interpretation': "Match" if l_res == a_val else "Mismatch",
                        'Lab_SD': np.nan,
                        'Lab_CV': np.nan,
                        'TEa_Percent': np.nan,
                        'Bias_Percent': np.nan,
                        'Sigma_Metric': np.nan,
                        'Recommended_Multirule': 'N/A',
                        'Score_Obtained': obt_sc,
                        'Max_Score': max_sc,
                        'Score_Percent': round(calc_pct, 2),
                        'Standard_Score': np.nan,
                        'Status': calc_status,
                        'Root_Cause': root_cause,
                        'Review_Action': review_action
                    })

            # บันทึกกลุ่ม Qualitative Basic
            else:
                for _, r in edited_df.iterrows():
                    s_id = str(r['รหัสตัวอย่าง (Sample ID)'])
                    l_res, a_val = str(r['Lab Result']), str(r['Assigned Value'])
                    is_match = (l_res == a_val)
                    
                    new_rows.append({
                        'Cycle': cycle,
                        'Department': department,
                        'Test_Name': test_name,
                        'Test_Method': test_method,
                        'Sample_ID': s_id,
                        'Test_Type': test_type,
                        'Lab_Result': l_res,
                        'Assigned_Value': a_val,
                        'SD_Group': np.nan,
                        'Z_Score': np.nan,
                        'Interpretation': "Match" if is_match else "Mismatch",
                        'Lab_SD': np.nan,
                        'Lab_CV': np.nan,
                        'TEa_Percent': np.nan,
                        'Bias_Percent': np.nan,
                        'Sigma_Metric': np.nan,
                        'Recommended_Multirule': 'N/A',
                        'Score_Obtained': 1.0 if is_match else 0.0,
                        'Max_Score': 1.0,
                        'Score_Percent': 100.0 if is_match else 0.0,
                        'Standard_Score': 4.0 if is_match else 0.0,
                        'Status': "Acceptable" if is_match else "Unsatisfactory",
                        'Root_Cause': root_cause,
                        'Review_Action': review_action
                    })

            # เพิ่มข้อมูลลง DataFrame และบันทึกลงไฟล์ CSV
            new_df = pd.DataFrame(new_rows)
            df = pd.concat([df, new_df], ignore_index=True)
            save_data(df)
            st.success("✅ บันทึกข้อมูล EQA เรียบร้อยแล้ว!")
            st.rerun()

# =========================================================
# TAB 2: Dashboard สรุปผล & Multirules
# =========================================================
with tab2:
    st.header("📊 Dashboard สรุปผล & คำแนะนำ Westgard Multirules")
    
    if df.empty:
        st.info("ยังไม่มีข้อมูลในระบบ กรุณากรอกข้อมูลใน Tab 'กรอกผล EQA'")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            selected_dept = st.selectbox("เลือกสาขาห้องปฏิบัติการ", ["ทั้งหมด"] + list(df['Department'].unique()))
        with col_f2:
            filtered_df = df if selected_dept == "ทั้งหมด" else df[df['Department'] == selected_dept]
            selected_cycle = st.selectbox("เลือกรอบการทดสอบ (Cycle)", ["ทั้งหมด"] + list(filtered_df['Cycle'].unique()))
            
        if selected_cycle != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df['Cycle'] == selected_cycle]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("จำนวนรายการทั้งหมด", len(filtered_df))
        
        quant_df = filtered_df[filtered_df['Sigma_Metric'].notna()]
        avg_sigma = quant_df['Sigma_Metric'].mean() if not quant_df.empty else 0.0
        m2.metric("ค่าเฉลี่ย Sigma Metric", f"{avg_sigma:.2f}" if not quant_df.empty else "N/A")
        
        pass_count = len(filtered_df[filtered_df['Status'].isin(['Acceptable', 'Excellent', 'Good', 'Satisfactory', 'excellet'])])
        pass_rate = (pass_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0.0
        m3.metric("อัตราการผ่านเกณฑ์ (%)", f"{pass_rate:.1f}%")
        
        nc_count = len(filtered_df) - pass_count
        m4.metric("รายการที่ไม่ผ่าน/ต้องทบทวน", f"{nc_count}")

        st.markdown("---")
        
        if not quant_df.empty:
            st.subheader("📈 Performance Metrics (Sigma Metric)")
            fig_sigma = px.bar(
                quant_df, 
                x='Test_Name', 
                y='Sigma_Metric', 
                color='Status',
                color_discrete_map=COLOR_MAP,
                title="Sigma Metric แยกตามรายการทดสอบ",
                hover_data=['Cycle', 'Sample_ID', 'Bias_Percent', 'Lab_CV']
            )
            fig_sigma.add_hline(y=6.0, line_dash="dash", line_color="green", annotation_text="6 Sigma (World Class)")
            fig_sigma.add_hline(y=3.0, line_dash="dash", line_color="red", annotation_text="3 Sigma (Minimum Performance)")
            st.plotly_chart(fig_sigma, use_container_width=True)

        st.subheader("🎯 ตารางแนะนำการเลือก Westgard Rules ตามค่า Sigma Metric")
        if not quant_df.empty:
            summary_rules = quant_df[['Test_Name', 'Sample_ID', 'Sigma_Metric', 'Recommended_Multirule']].drop_duplicates()
            st.dataframe(summary_rules, use_container_width=True)
        else:
            st.caption("ไม่มีข้อมูล Quantitative สำหรับคำนวณ Sigma Metric")

# =========================================================
# TAB 3: ประวัติและ Export ข้อมูล
# =========================================================
with tab3:
    st.header("📋 ประวัติข้อมูล EQA ทั้งหมด และการ Export")
    
    if df.empty:
        st.info("ยังไม่มีข้อมูลบันทึกในระบบ")
    else:
        st.dataframe(df, use_container_width=True)
        
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลดข้อมูลเป็น CSV",
                data=csv_data,
                file_name="eqa_sigma_tracking_data.csv",
                mime="text/csv",
                type="primary"
            )
        
        with col_ex2:
            if st.button("🗑️ ล้างข้อมูลทั้งหมดในระบบ", type="secondary"):
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                st.cache_data.clear()
                st.success("ลบข้อมูลสำเร็จแล้ว!")
                st.rerun()