import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

st.set_page_config(page_title="EQA & Sigma Metric Tracking", page_icon="🔬", layout="wide")

DATA_FILE = 'eqa_data.csv'

TEA_TABLE = {
    "GLUCOSE": 10.0, "BUN": 9.0, "CREATININE": 15.0, "URIC ACID": 10.0,
    "CHOLESTEROL": 10.0, "TRIGLYCERIDE": 15.0, "HDL": 10.0, "LDL": 12.0,
    "TOTAL PROTEIN": 10.0, "ALBUMIN": 10.0, "TOTAL BILIRUBIN": 20.0,
    "AST": 15.0, "ALT": 15.0, "ALP": 15.0, "CALCIUM": 1.0, "Na": 4.0,
    "K": 0.5, "Cl": 5.0, "Hba1c": 6.0, "DEFAULT": 10.0
}

# พารามิเตอร์ย่อยสำหรับ UA 10 รายการ
UA_PARAMETERS = [
    "Specific Gravity", "pH", "Leukocytes", "Nitrite", 
    "Protein", "Glucose", "Ketone", "Urobilinogen", "Bilirubin", "Blood"
]

# Dropdown Options สำหรับ UA
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

@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            'Cycle', 'Department', 'Test_Name', 'Sample_ID', 'Test_Type',
            'Lab_Result', 'Assigned_Value', 'SD_Group', 'Z_Score', 'Interpretation',
            'Lab_SD', 'Lab_CV', 'TEa_Percent', 'Bias_Percent', 'Sigma_Metric', 'Recommended_Multirule',
            'Score_Obtained', 'Max_Score', 'Score_Percent', 'Standard_Score', 'Status', 
            'Root_Cause', 'Review_Action'
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

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
    "serology": ["Reactive", "Non-reactive", "Positive", "Negative", "Equivocal", "Inconclusive"],
    "pos_neg": ["Positive", "Negative", "Inconclusive"],
    "stain": ["Found", "Not Found", "Gram Positive Cocci", "Gram Negative Bacilli", "Yeasts Found", "No Organism Found"],
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

st.title("🔬 ระบบติดตามและประเมินผลประสิทธิภาพ EQA & Sigma Metric")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📝 กรอกผล EQA (Multi-Sample)", "📊 Dashboard สรุปผล & Multirules", "📋 ประวัติและ Export ข้อมูล"])

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

    if test_name == "UA":
        test_type = "UA Multi-Parameter (10 Sub-tests)"
        num_samples = st.number_input("จำนวนตัวอย่างในรอบนี้ (1-10 ตัวอย่าง)", min_value=1, max_value=10, value=1, step=1)
    else:
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

    nc_items = []  # เก็บรายการที่ไม่เข้าตามข้อกำหนดเพื่อนำมาแสดงด้านล่าง

    if test_name == "UA":
        st.info("💡 กรอกผลตรวจ ค่า Assigned Value พร้อมคะแนนที่ได้ และคะแนนเต็มในแต่ละพารามิเตอร์ ระบบจะรวมคะแนนของทุก Sample มารวมกันคำนวณ Standard Score")
        
        ua_results = {}
        total_obtained_all_samples = 0.0
        total_max_all_samples = 0.0

        for s_idx in range(num_samples):
            sample_label = f"Sample {s_idx + 1}"
            st.markdown(f"##### 🧪 **{sample_label}**")
            
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
            
            # ตรวจสอบ NC ย่อย (Mismatch หรือ ได้คะแนนไม่เต็ม)
            for _, r in edited_ua.iterrows():
                l_res, a_val = str(r['Lab Result']), str(r['Assigned Value'])
                obt_sc, max_sc = float(r['คะแนนที่ได้ (Obtained)']), float(r['คะแนนเต็ม (Max Score)'])
                if l_res != a_val or obt_sc < max_sc:
                    nc_items.append({
                        "รายการ/Sample": f"{sample_label} - UA ({r['พารามิเตอร์ (Parameter)']})",
                        "ผลตรวจห้องปฏิบัติการ": l_res,
                        "ค่าเป้าหมาย (Assigned Value)": a_val,
                        "สถานะปัญหา": "Mismatch / คะแนนไม่เต็ม"
                    })

            ua_results[sample_label] = (edited_ua, sample_obt, sample_max)
            st.caption(f"คะแนนเฉพาะ {sample_label}: {sample_obt:.1f} / {sample_max:.1f}")

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

    elif "Quantitative" in test_type:
        st.info("💡 กรอกผล Lab, ค่า Peer Group (Assigned Value/SD), ค่า %CV Lab และ TEa% ระบบจะคำนวณ Z-score, Sigma Metric และแนะนำ Westgard Multirule ให้ทันที")
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

    # ==========================================
    # ส่วนทบทวนและวิเคราะห์สาเหตุ (Non-conformity & Root Cause Analysis)
    # ==========================================
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
            placeholder="เช่น Human Error, Reagent Deterioration, Calibration Failure, Pipette Out of Tolerance, Sample Storage Condition",
            height=120
        )
    with col_rc2:
        review_action = st.text_area(
            "🛠️ ผลการทบทวน / มาตรการแก้ไขและป้องกัน (Corrective & Preventive Action / Management Review)", 
            placeholder="เช่น Re-calibrate ใหม่, เปลี่ยน น้ำยา Lot ใหม่, ทำ Maintenance เครื่องมือ, จัดอบรมเจ้าหน้าที่ผู้ปฏิบัติงาน",
            height=120
        )

    if st.button("💾 บันทึกผล EQA และบันทึกการทบทวน", type="primary"):
        if not test_name:
            st.error("กรุณาระบุชื่อรายการทดสอบก่อนบันทึก")
        else:
            new_rows = []
            
            if test_name == "UA":
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

            elif "Quantitative" in test_type:
                for _, row in edited_df.iterrows():
                    sample_id = str(row['รหัสตัวอย่าง (Sample ID)'])
                    l_res = float(row['Lab Result'])
                    a_val = float(row['Assigned Value'])
                    sd_grp = float(row['SD Group'])
                    l_sd = float(row['Lab SD'])
                    l_cv = float(row['Lab %CV'])
                    tea = float(row['TEa (%)'])
                    interp = str(row['Interpretation'])
                    
                    z_score = (l_res - a_val) / sd_grp if sd_grp > 0 else np.nan
                    bias_pct = (abs(l_res - a_val) / a_val * 100) if a_val > 0 else np.nan
                    sigma = ((tea - bias_pct) / l_cv) if l_cv > 0 and not np.isnan(bias_pct) else np.nan
                    rule = evaluate_westgard_rules(sigma)
                    
                    new_rows.append({
                        'Cycle': cycle,
                        'Department': department,
                        'Test_Name': test_name,
                        'Sample_ID': sample_id,
                        'Test_Type': 'Quantitative',
                        'Lab_Result': str(l_res),
                        'Assigned_Value': str(a_val),
                        'SD_Group': sd_grp,
                        'Z_Score': round(z_score, 2) if not np.isnan(z_score) else np.nan,
                        'Interpretation': interp,
                        'Lab_SD': l_sd,
                        'Lab_CV': l_cv,
                        'TEa_Percent': tea,
                        'Bias_Percent': round(bias_pct, 2) if not np.isnan(bias_pct) else np.nan,
                        'Sigma_Metric': round(sigma, 2) if not np.isnan(sigma) else np.nan,
                        'Recommended_Multirule': rule,
                        'Score_Obtained': np.nan,
                        'Max_Score': np.nan,
                        'Score_Percent': np.nan,
                        'Standard_Score': np.nan,
                        'Status': interp,
                        'Root_Cause': root_cause,
                        'Review_Action': review_action
                    })

            elif "Scoring" in test_type:
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
                    overall_status = "Unsatisfactory"

                for _, row in edited_df.iterrows():
                    sample_id = str(row['รหัสตัวอย่าง (Sample ID)'])
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
                        'SD_Group': np.nan,
                        'Z_Score': np.nan,
                        'Interpretation': overall_status,
                        'Lab_SD': np.nan,
                        'Lab_CV': np.nan,
                        'TEa_Percent': np.nan,
                        'Bias_Percent': np.nan,
                        'Sigma_Metric': np.nan,
                        'Recommended_Multirule': 'N/A',
                        'Score_Obtained': score_obtained,
                        'Max_Score': max_score,
                        'Score_Percent': round(overall_pct, 2),
                        'Standard_Score': np.nan,
                        'Status': overall_status,
                        'Root_Cause': root_cause,
                        'Review_Action': review_action
                    })

            else:
                for _, row in edited_df.iterrows():
                    sample_id = str(row['รหัสตัวอย่าง (Sample ID)'])
                    lab_res_str = str(row['Lab Result'])
                    assigned_val_str = str(row['Assigned Value'])
                    status = "Excellent" if lab_res_str == assigned_val_str else "Unsatisfactory"
                    
                    new_rows.append({
                        'Cycle': cycle,
                        'Department': department,
                        'Test_Name': test_name,
                        'Sample_ID': sample_id,
                        'Test_Type': 'Qualitative',
                        'Lab_Result': lab_res_str,
                        'Assigned_Value': assigned_val_str,
                        'SD_Group': np.nan,
                        'Z_Score': np.nan,
                        'Interpretation': status,
                        'Lab_SD': np.nan,
                        'Lab_CV': np.nan,
                        'TEa_Percent': np.nan,
                        'Bias_Percent': np.nan,
                        'Sigma_Metric': np.nan,
                        'Recommended_Multirule': 'N/A',
                        'Score_Obtained': np.nan,
                        'Max_Score': np.nan,
                        'Score_Percent': 100.0 if status == "Excellent" else 0.0,
                        'Standard_Score': np.nan,
                        'Status': status,
                        'Root_Cause': root_cause,
                        'Review_Action': review_action
                    })

            df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
            save_data(df)
            st.cache_data.clear()
            st.success(f"บันทึกข้อมูล '{test_name}' และผลการทบทวนรวม {len(new_rows)} รายการเรียบร้อยแล้ว!")
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
        unsat_cnt = len(filtered_df[filtered_df['Status'].isin(['Unsatisfactory', 'Unacceptable'])])
        
        acc_legacy_cnt = len(filtered_df[filtered_df['Status'] == 'Acceptable'])
        passed_cnt = excellent_cnt + good_cnt + sat_cnt + acc_legacy_cnt
        pass_rate = (passed_cnt / total_tests * 100) if total_tests > 0 else 0.0

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("จำนวนรายการย่อยทั้งหมด", f"{total_tests} รายการ")
        m2.metric("ผ่านเกณฑ์ภาพรวม", f"{passed_cnt}", f"{pass_rate:.1f}%")
        m3.metric("Excellent", f"{excellent_cnt}")
        m4.metric("Good / Satisfactory", f"{good_cnt + sat_cnt}")
        m5.metric("Unsatisfactory", f"{unsat_cnt}")

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
            st.subheader("แนวโน้ม Z-Score / Standard Score / คะแนน % ภาพรวม")
            quant_df = filtered_df[filtered_df['Test_Type'] == 'Quantitative'].dropna(subset=['Z_Score'])
            scoring_df = filtered_df[filtered_df['Score_Percent'].notnull()]

            if not quant_df.empty:
                fig_sdi = px.scatter(
                    quant_df, x='Sample_ID', y='Z_Score', color='Status', hover_name='Test_Name',
                    color_discrete_map=COLOR_MAP,
                    hover_data=['Cycle', 'Department', 'Test_Name', 'Lab_Result', 'Assigned_Value', 'Sigma_Metric'],
                    title="Z-Score Distribution (Quantitative: ±2 ช่วงยอมรับได้)"
                )
                fig_sdi.add_hline(y=2.0, line_dash="dash", line_color="orange")
                fig_sdi.add_hline(y=-2.0, line_dash="dash", line_color="orange")
                st.plotly_chart(fig_sdi, use_container_width=True)
            
            if not scoring_df.empty:
                fig_score = px.bar(
                    scoring_df, x='Test_Name', y='Standard_Score', color='Status',
                    color_discrete_map=COLOR_MAP,
                    hover_data=['Cycle', 'Department', 'Sample_ID', 'Score_Obtained', 'Max_Score', 'Score_Percent'],
                    title="Standard Score Distribution (UA / Scoring)"
                )
                fig_score.add_hline(y=4.0, line_dash="dot", line_color="green", annotation_text="Excellent (4.0)")
                fig_score.add_hline(y=3.5, line_dash="dash", line_color="#2ecc71", annotation_text="Good (3.5)")
                fig_score.add_hline(y=3.0, line_dash="dash", line_color="orange", annotation_text="Satisfactory (3.0)")
                st.plotly_chart(fig_score, use_container_width=True)

            if quant_df.empty and scoring_df.empty:
                st.info("ไม่มีข้อมูลในการแสดงกราฟ")

        st.markdown("---")
        st.subheader("📋 รายงานทบทวนรายการที่ไม่ผ่านเกณฑ์ (Root Cause & Review Log)")
        nc_history = filtered_df[filtered_df['Root_Cause'].notnull() & (filtered_df['Root_Cause'] != '')]
        if not nc_history.empty:
            st.dataframe(
                nc_history[['Cycle', 'Department', 'Test_Name', 'Sample_ID', 'Status', 'Root_Cause', 'Review_Action']], 
                use_container_width=True
            )
        else:
            st.info("ยังไม่มีประวัติบันทึกการทบทวนสาเหตุที่ไม่ผ่านในสาขาที่เลือก")

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