import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="แบบฟอร์มบันทึก KPI-QI", page_icon="📥", layout="wide")

# แก้ไขปุ่มย้อนกลับให้เป็น st.page_link เพื่อความเสถียร
st.page_link("app.py", label="กลับสู่หน้า Command Center", icon="⬅️")

st.title("📥 แบบฟอร์มบันทึกตัวชี้วัดคุณภาพ (KPI-QI 10 หัวข้อ)")
st.caption("กลุ่มงานเทคนิคการแพทย์ โรงพยาบาลนาโพธิ์")

# โครงสร้างรายการตรวจแยกตามสาขาสำหรับหัวข้อที่ 2
LAB_TESTS = {
    "Hematology": ["CBC", "Hematocrit", "ESR", "DCIP", "Reticulocyte count", "VCT", "20WBCT", "PT&INR", "Wright stain"],
    "Biochemistry": [
        "Glucose", "BUN", "Creatinine", "Uric acid", "Cholesterol", "Triglyceride", "HDL", "LDL", 
        "Total protein", "Albumin", "Total bilirubin", "Direct bilirubin", "AST", "ALT", "ALP", 
        "Calcium", "Magnesium", "Phosphorus", "Na", "K", "Cl", "CO2", "HbA1c", "Troponin I", "Micro-bilirubin"
    ],
    "Immunology": [
        "HBsAg", "HBsAb", "Anti-HCV", "HIV", "RPR", "RF", "Leptospira Ab", "Scrub typhus Ab", 
        "COVID-19 Ag test", "Influenza A+B test", "COVID-19 + Influenza A+B test", 
        "COVID-19 + Influenza A+B test+RSV test", "Melioid titer"
    ],
    "Microbiology": ["AFB", "Gram's stain", "KOH", "TB lamp"],
    "Microscopy": ["UA", "Stool exam", "FOB", "UPT", "Methamphetamine screening test", "Marijuana screening test"],
    "Blood Bank": ["ABO grouping", "Rh grouping"]
}

BRANCHES = list(LAB_TESTS.keys())

# Initialize Session State
if "kpi_records" not in st.session_state:
    st.session_state["kpi_records"] = pd.DataFrame()

with st.form("kpi_10_topics_form", clear_on_submit=False):
    st.subheader("🗓️ ข้อมูลช่วงเวลา")
    c_m, c_y = st.columns(2)
    with c_m:
        month = st.selectbox("ประจำเดือน", [
            "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
            "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
        ])
    with c_y:
        year = st.number_input("ปี พ.ศ.", value=2569, step=1)

    st.markdown("---")

    # --- 1. สิ่งส่งตรวจมีคุณภาพ ---
    st.header("1. สิ่งส่งตรวจมีคุณภาพ (เป้าหมาย < 0.3%)")
    c1_1, c1_2 = st.columns(2)
    with c1_1:
        rejected_specimens = st.number_input("1. จำนวนสิ่งส่งตรวจที่ถูกปฏิเสธ (รายการ)", min_value=0, value=0)
        total_specimens = st.number_input("2. จำนวนการเก็บสิ่งส่งตรวจทั้งหมด (ใบนำส่งที่คีย์ในระบบ)", min_value=1, value=1)
    with c1_2:
        rejection_reasons = st.multiselect(
            "3. สาเหตุของการปฏิเสธสิ่งส่งตรวจ",
            options=[
                "hemolysis", "clotted", "ปริมาณน้อยเกินไป", "ปริมาณมากเกินไป", 
                "ไม่ระบุตัวผู้ป่วย", "ระบุตัวผู้ป่วยผิดคน/สลับคน", "เจาะเลือดผิดคน", 
                "หกเลอะเทอะ", "เจาะเก็บผิดตำแหน่ง", "เจาะเก็บผิดเวลา", 
                "เจาะเก็บข้างที่ให้สารน้ำ", "ใช้หลอดเก็บไม่ถูกประเภท", "อื่นๆ"
            ]
        )
    
    # คำนวณ % การปฏิเสธสิ่งส่งตรวจ
    rej_pct = (rejected_specimens / total_specimens) * 100 if total_specimens > 0 else 0.0
    st.info(f"📊 ร้อยละการเก็บสิ่งส่งตรวจไม่ถูกต้อง: **{rej_pct:.3f}%** (เกณฑ์เป้าหมาย < 0.3%)")

    st.markdown("---")

    # --- 2. การประกันคุณภาพทางห้องปฏิบัติการ ---
    st.header("2. การประกันคุณภาพทางห้องปฏิบัติการ (IQC / EQA)")
    st.caption("ประเมินรายรายการตรวจและสรุปผลตามสาขา")

    qa_results = []
    
    for branch, tests in LAB_TESTS.items():
        with st.expander(f"📁 สาขา {branch} ({len(tests)} รายการตรวจ)", expanded=False):
            for test in tests:
                tc1, tc2, tc3 = st.columns([2, 2, 2])
                with tc1:
                    iqc_ans = st.radio(f"[{test}] IQC", ["ดำเนินการแล้ว", "ยังไม่ดำเนินการ"], key=f"iqc_{branch}_{test}")
                with tc2:
                    eqa_ans = st.radio(f"[{test}] EQA", ["ดำเนินการแล้ว", "ยังไม่ดำเนินการ"], key=f"eqa_{branch}_{test}")
                with tc3:
                    eqa_acc = st.number_input(f"[{test}] % ความถูกต้อง EQA", min_value=0.0, max_value=100.0, value=100.0, key=f"acc_{branch}_{test}")
                
                qa_results.append({
                    "Branch": branch,
                    "Test": test,
                    "IQC_Done": 1 if iqc_ans == "ดำเนินการแล้ว" else 0,
                    "EQA_Done": 1 if eqa_ans == "ดำเนินการแล้ว" else 0,
                    "EQA_Acc": eqa_acc
                })

    # คำนวณ QA สรุป
    qa_df = pd.DataFrame(qa_results)
    total_tests_count = len(qa_df)
    total_iqc_pct = (qa_df["IQC_Done"].sum() / total_tests_count) * 100 if total_tests_count > 0 else 0.0
    total_eqa_pct = (qa_df["EQA_Done"].sum() / total_tests_count) * 100 if total_tests_count > 0 else 0.0
    avg_eqa_acc = qa_df["EQA_Acc"].mean() if total_tests_count > 0 else 0.0
    overall_qa_kpi = (total_iqc_pct + total_eqa_pct + avg_eqa_acc) / 3

    st.success(f"📈 สรุปภาพรวม QA: IQC = {total_iqc_pct:.1f}% | EQA = {total_eqa_pct:.1f}% | ความถูกต้อง EQA = {avg_eqa_acc:.1f}% -> KPI รวม = {overall_qa_kpi:.1f}%")

    st.markdown("---")

    # --- 3. เครื่องมือมีความปลอดภัย พร้อมใช้งาน ---
    st.header("3. เครื่องมือมีความปลอดภัย พร้อมใช้งานอย่างมีประสิทธิภาพ")
    c3_1, c3_2, c3_3 = st.columns(3)
    with c3_1:
        calib_pct = st.number_input("1. ร้อยละการสอบเทียบเครื่องมือหลักครบถ้วน (เป้าหมาย 100%)", min_value=0.0, max_value=100.0, value=100.0)
    with c3_2:
        pm_pct = st.number_input("2. ร้อยละการบำรุงรักษา PM ครบถ้วน (เป้าหมาย 100%)", min_value=0.0, max_value=100.0, value=100.0)
    with c3_3:
        downtime_pct = st.number_input("3. ร้อยละ Downtime เครื่องมือ (เป้าหมาย < 1%)", min_value=0.0, max_value=100.0, value=0.0)

    st.markdown("---")

    # --- 4. ผลการตรวจมีความถูกต้อง ---
    st.header("4. ผลการตรวจมีความถูกต้อง")
    c4_1, c4_2, c4_3 = st.columns(3)
    with c4_1:
        miss_pct = st.number_input("1. ร้อยละอุบัติการณ์ Missed Report (เป้าหมาย < 0.3%)", min_value=0.0, max_value=100.0, value=0.0)
    with c4_2:
        near_miss_pct = st.number_input("2. ร้อยละอุบัติการณ์ Near Miss (เป้าหมาย < 0.3%)", min_value=0.0, max_value=100.0, value=0.0)
    with c4_3:
        send_ext_pct = st.number_input("3. ร้อยละการส่งต่อสิ่งส่งตรวจภายนอกถูกต้อง ครบถ้วน (เป้าหมาย 100%)", min_value=0.0, max_value=100.0, value=100.0)

    st.markdown("---")

    # --- 5. รวดเร็ว ทันเวลา ---
    st.header("5. รวดเร็ว ทันเวลา (รายงานผลทันเวลา OPD รายสาขา)")
    opd_tat_branches = {}
    cols_opd = st.columns(3)
    for idx, b_name in enumerate(BRANCHES):
        with cols_opd[idx % 3]:
            opd_tat_branches[f"OPD_TAT_{b_name}"] = st.number_input(f"รายงานผลทันเวลา OPD สาขา {b_name} (%)", min_value=0.0, max_value=100.0, value=85.0)

    c5_1, c5_2 = st.columns(2)
    with c5_1:
        crit_resp_pct = st.number_input("การตอบสนองรายงานค่าวิกฤติ ครบถ้วน ทันเวลา (%) (เป้าหมาย 80%)", min_value=0.0, max_value=100.0, value=100.0)
    with c5_2:
        crit_rpt_pct = st.number_input("LAB รายงานค่าวิกฤตครบถ้วน (%) (เป้าหมาย 100%)", min_value=0.0, max_value=100.0, value=100.0)

    st.markdown("---")

    # --- 6. ปลอดภัย ---
    st.header("6. ความปลอดภัย (ผู้ป่วยและเจ้าหน้าที่)")
    st.subheader("6.1 การจ่ายเลือดและการแพ้เลือด")
    c6_1, c6_2, c6_3, c6_4 = st.columns(4)
    with c6_1:
        total_blood_issued = st.number_input("จำนวนที่จ่ายเลือดทั้งหมด (ยูนิต/เคส)", min_value=0, value=100)
    with c6_2:
        blood_wrong_person_cases = st.number_input("จำนวนจ่ายเลือดผิดคน (เคส)", min_value=0, value=0)
    with c6_3:
        blood_wrong_grp_cases = st.number_input("จำนวนจ่ายเลือดผิดหมู่ (เคส)", min_value=0, value=0)
    with c6_4:
        blood_adverse_cases = st.number_input("จำนวนที่เกิดปฏิกิริยาจากการได้รับเลือด (เคส)", min_value=0, value=0)

    bw_person_pct = (blood_wrong_person_cases / total_blood_issued * 100) if total_blood_issued > 0 else 0.0
    bw_grp_pct = (blood_wrong_grp_cases / total_blood_issued * 100) if total_blood_issued > 0 else 0.0
    b_adv_pct = (blood_adverse_cases / total_blood_issued * 100) if total_blood_issued > 0 else 0.0

    st.subheader("6.2 ความปลอดภัยของเจ้าหน้าที่ (เป้าหมายรวม 100%)")
    cs1, cs2, cs3 = st.columns(3)
    with cs1:
        staff_health_pct = st.number_input("1. ร้อยละการตรวจสุขภาพประจำปี (%)", min_value=0.0, max_value=100.0, value=100.0)
    with cs2:
        staff_flu_pct = st.number_input("2. ร้อยละได้รับวัคซีนไข้หวัดใหญ่ (%)", min_value=0.0, max_value=100.0, value=100.0)
    with cs3:
        staff_no_accident_pct = st.number_input("3. ร้อยละไม่เกิดอุบัติเหตุ/ติดเชื้อจากการทำงาน (%)", min_value=0.0, max_value=100.0, value=100.0)
    
    staff_safety_avg = (staff_health_pct + staff_flu_pct + staff_no_accident_pct) / 3
    st.info(f"🛡️ ค่าเฉลี่ยความปลอดภัยเจ้าหน้าที่: **{staff_safety_avg:.1f}%**")

    st.markdown("---")

    # --- 7. โลหิตเพียงพอ ---
    st.header("7. โลหิตเพียงพอ (เป้าหมาย > 80%)")
    c7_1, c7_2 = st.columns(2)
    with c7_1:
        blood_req_total = st.number_input("1. จำนวนที่ขอเลือดทั้งหมด (ยูนิต)", min_value=0, value=100)
    with c7_2:
        blood_supplied_total = st.number_input("2. จำนวนที่จัดหาเลือดได้ทั้งหมด (ยูนิต)", min_value=0, value=95)
    
    blood_fulfillment_pct = (blood_supplied_total / blood_req_total * 100) if blood_req_total > 0 else 0.0
    st.info(f"🩸 ร้อยละที่ผู้ป่วยได้รับเลือดตามที่ขอ: **{blood_fulfillment_pct:.1f}%**")

    st.markdown("---")

    # --- 8. ผู้รับบริการพึงพอใจ ---
    st.header("8. ความพึงพอใจของผู้รับบริการ (เป้าหมายทุกกลุ่ม > 80%)")
    csat_cols = st.columns(5)
    with csat_cols[0]:
        csat_patient = st.number_input("1. ผู้ป่วยและญาติ (%)", min_value=0.0, max_value=100.0, value=88.0)
    with csat_cols[1]:
        csat_nurse = st.number_input("2. พยาบาล/สหวิชาชีพ (%)", min_value=0.0, max_value=100.0, value=90.0)
    with csat_cols[2]:
        csat_doctor = st.number_input("3. แพทย์ (%)", min_value=0.0, max_value=100.0, value=90.0)
    with csat_cols[3]:
        csat_pcu = st.number_input("4. รพ.สต. (%)", min_value=0.0, max_value=100.0, value=85.0)
    with csat_cols[4]:
        csat_helper = st.number_input("5. ผู้ช่วยเหลือ/เวรเปล (%)", min_value=0.0, max_value=100.0, value=88.0)

    st.markdown("---")

    # --- 9. Rational Laboratory Use (RLU) ---
    st.header("9. Rational Laboratory Use (RLU)")
    st.subheader("9.1 ตรวจซ้ำภายใน 90 วัน (Overutilization: เป้าหมาย < 5%)")
    o1, o2, o3, o4 = st.columns(4)
    with o1:
        over_hba1c = st.number_input("1. HbA1c ซ้ำ 90 วัน (%)", min_value=0.0, max_value=100.0, value=2.0)
    with o2:
        over_ldl = st.number_input("2. LDL ซ้ำ 90 วัน (%)", min_value=0.0, max_value=100.0, value=1.5)
    with o3:
        over_chol = st.number_input("3. Cholesterol ซ้ำ 90 วัน (%)", min_value=0.0, max_value=100.0, value=1.0)
    with o4:
        over_tri = st.number_input("4. Triglyceride ซ้ำ 90 วัน (%)", min_value=0.0, max_value=100.0, value=1.0)

    st.subheader("9.2 ผู้ป่วย DM ได้รับการตรวจอย่างน้อยปีละ 1 ครั้ง (Underutilization: เป้าหมาย > 70%)")
    u1, u2, u3, u4, u5 = st.columns(5)
    with u1:
        under_hba1c = st.number_input("1. DM ตรวจ HbA1c/ปี (%)", min_value=0.0, max_value=100.0, value=85.0)
    with u2:
        under_ldl = st.number_input("2. DM ตรวจ LDL/ปี (%)", min_value=0.0, max_value=100.0, value=80.0)
    with u3:
        under_cr = st.number_input("3. DM ตรวจ Creatinine/ปี (%)", min_value=0.0, max_value=100.0, value=85.0)
    with u4:
        under_chol = st.number_input("4. DM ตรวจ Cholesterol/ปี (%)", min_value=0.0, max_value=100.0, value=80.0)
    with u5:
        under_tri = st.number_input("5. DM ตรวจ Triglycerides/ปี (%)", min_value=0.0, max_value=100.0, value=80.0)

    st.markdown("---")

    # --- 10. ลดค่าใช้จ่ายการสั่ง Lab โดยไม่จำเป็น ---
    st.header("10. ลดค่าใช้จ่ายการสั่ง Lab เป็น Test โดยไม่จำเป็น (เป้าหมาย > 90%)")
    redu_ft3_pct = st.number_input("ร้อยละลดการสั่งตรวจ FT3 คู่กับ (FT4, TSH) (%)", min_value=0.0, max_value=100.0, value=95.0)

    st.markdown("---")

    btn_submit = st.form_submit_button("💾 บันทึกข้อมูลตัวชี้วัดทั้งหมด", use_container_width=True)

    if btn_submit:
        record = {
            "Month": month,
            "Year": year,
            "Period": f"{month} {year}",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            # Topic 1
            "Rejection_Rate_Pct": rej_pct,
            "Rejected_Count": rejected_specimens,
            "Total_Specimens": total_specimens,
            "Rejection_Reasons": ", ".join(rejection_reasons),
            # Topic 2
            "IQC_Total_Pct": total_iqc_pct,
            "EQA_Total_Pct": total_eqa_pct,
            "EQA_Acc_Avg_Pct": avg_eqa_acc,
            "Overall_QA_KPI_Pct": overall_qa_kpi,
            # Topic 3
            "Calib_Pct": calib_pct,
            "PM_Pct": pm_pct,
            "Downtime_Pct": downtime_pct,
            # Topic 4
            "Missed_Report_Pct": miss_pct,
            "Near_Miss_Pct": near_miss_pct,
            "Send_External_Acc_Pct": send_ext_pct,
            # Topic 5
            **opd_tat_branches,
            "Critical_Response_Pct": crit_resp_pct,
            "Critical_Report_Pct": crit_rpt_pct,
            # Topic 6
            "Total_Blood_Issued": total_blood_issued,
            "Blood_Wrong_Person_Pct": bw_person_pct,
            "Blood_Wrong_Group_Pct": bw_grp_pct,
            "Blood_Adverse_React_Pct": b_adv_pct,
            "Staff_Health_Check_Pct": staff_health_pct,
            "Staff_Flu_Vaccine_Pct": staff_flu_pct,
            "Staff_No_Accident_Pct": staff_no_accident_pct,
            "Staff_Safety_Avg_Pct": staff_safety_avg,
            # Topic 7
            "Blood_Fulfillment_Pct": blood_fulfillment_pct,
            # Topic 8
            "CSAT_Patient_Pct": csat_patient,
            "CSAT_Nurse_Pct": csat_nurse,
            "CSAT_Doctor_Pct": csat_doctor,
            "CSAT_PCU_Pct": csat_pcu,
            "CSAT_Helper_Pct": csat_helper,
            # Topic 9
            "Over_HbA1c_Pct": over_hba1c,
            "Over_LDL_Pct": over_ldl,
            "Over_Chol_Pct": over_chol,
            "Over_Tri_Pct": over_tri,
            "Under_HbA1c_Pct": under_hba1c,
            "Under_LDL_Pct": under_ldl,
            "Under_Cr_Pct": under_cr,
            "Under_Chol_Pct": under_chol,
            "Under_Tri_Pct": under_tri,
            # Topic 10
            "FT3_Redundant_Reduction_Pct": redu_ft3_pct
        }

        new_df = pd.DataFrame([record])
        st.session_state["kpi_records"] = pd.concat([st.session_state["kpi_records"], new_df], ignore_index=True)
        st.success(f"✅ บันทึกข้อมูลประจำเดือน {month} {year} สำเร็จเรียบร้อยแล้ว!")

# --- Export Section ---
st.markdown("---")
st.subheader("📊 ข้อมูลที่บันทึกไว้ และการส่งออก (Export Data)")
df_records = st.session_state["kpi_records"]

if not df_records.empty:
    st.dataframe(df_records, use_container_width=True)

    b_excel = io.BytesIO()
    with pd.ExcelWriter(b_excel, engine="openpyxl") as writer:
        df_records.to_excel(writer, index=False, sheet_name="KPI_10_Topics")

    c_ex, c_csv = st.columns(2)
    with c_ex:
        st.download_button(
            label="📥 ดาวน์โหลดข้อมูลทั้งหมดเป็น Excel (.xlsx)",
            data=b_excel.getvalue(),
            file_name=f"Napho_Lab_KPI_10Topics_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with c_csv:
        csv_bytes = df_records.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📄 ดาวน์โหลดข้อมูลทั้งหมดเป็น CSV (.csv)",
            data=csv_bytes,
            file_name=f"Napho_Lab_KPI_10Topics_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
else:
    st.info("ยังไม่มีรายการข้อมูลในระบบ กรุณากรอกแบบฟอร์มด้านบนเพื่อบันทึก")