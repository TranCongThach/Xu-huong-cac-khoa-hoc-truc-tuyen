import pandas as pd
import re
import numpy as np

pd.set_option('display.max_columns', None)
def normalize_key(s: pd.Series) -> pd.Series:
    """Chuẩn hóa chuỗi để làm khóa join: lowercase, bỏ khoảng trắng thừa, bỏ ký tự đặc biệt.
    Giữ nguyên NaN (không biến thành chuỗi "nan") để tránh ghép nhầm các dòng
    thực sự thiếu dữ liệu vào chung một nhóm."""
    is_na = s.isna()
    result = (
        s.astype(str)
        .str.lower()
        .str.strip()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.replace(r"\s+", " ", regex=True)
    )
    result[is_na] = pd.NA
    return result


def parse_enrolled(val):
    """'170,608' -> 170608 ; 'Enrollment number not found' -> NaN"""
    if pd.isna(val):
        return np.nan
    val = str(val).strip()
    if "not found" in val.lower():
        return np.nan
    val = val.replace(",", "")
    try:
        return float(val)
    except ValueError:
        return np.nan


def parse_rating(val):
    """'4.6' -> 4.6 ; 'Rating not found' -> NaN"""
    if pd.isna(val):
        return np.nan
    val = str(val).strip()
    if "not found" in val.lower():
        return np.nan
    try:
        return float(val)
    except ValueError:
        return np.nan


def parse_percent(val):
    """'98%' -> 98.0"""
    if pd.isna(val):
        return np.nan
    val = str(val).strip().replace("%", "")
    try:
        return float(val)
    except ValueError:
        return np.nan


# ============================================================
# BANG 1 (FACT): coursera_course_2024.csv
# ============================================================
print("Đang xử lý bảng chính: coursera_course_2024.csv ...")
fact = pd.read_csv(r"D:\Project_CK_TTDLTQ\Data\raw\coursera_course_2024.csv", on_bad_lines="skip")
fact = fact.drop(columns=["Unnamed: 0"], errors="ignore")

fact["enrolled_num"] = fact["enrolled"].apply(parse_enrolled)
fact["rating_num"] = fact["rating"].apply(parse_rating)
fact["satisfaction_rate_num"] = fact["Satisfaction Rate"].apply(parse_percent)
fact["num_reviews"] = pd.to_numeric(fact["num_reviews"], errors="coerce")

# Sửa lỗi: "Organization not found" là placeholder giống "Rating not found",
# phải chuyển thành NaN thật (phát hiện muộn khi rà soát mở rộng mapping quốc gia
# lên top 300 tổ chức — 10 dòng bị ảnh hưởng).
fact["Organization"] = fact["Organization"].replace("Organization not found", pd.NA)

# Khóa join kép: Title + Organization (tránh ghép nhầm 41 khóa học trùng tên khác tổ chức)
fact["_title_key"] = normalize_key(fact["title"])
fact["_org_key"] = normalize_key(fact["Organization"])

# Dedupe: 4 dòng trùng thật (cùng Title + cùng Organization) -> giữ dòng có nhiều dữ liệu hơn
fact["_completeness"] = fact.notna().sum(axis=1)
fact = (
    fact.sort_values("_completeness", ascending=False)
    .drop_duplicates(subset=["_title_key", "_org_key"], keep="first")
    .drop(columns=["_completeness"])
)

print(f"  -> Sau khi làm sạch: {len(fact)} dòng (gốc 6645)")

# ============================================================
# BANG 2: Coursera.csv (bổ sung Subject, Duration, Gained Skills)
# ============================================================
print("Đang xử lý bảng bổ sung: Coursera.csv ...")
sup1 = pd.read_csv(r"D:\Project_CK_TTDLTQ\Data\raw\Coursera.csv", on_bad_lines="skip", skipinitialspace=True)

sup1["_title_key"] = normalize_key(sup1["Title"])
sup1["_org_key"] = normalize_key(sup1["Institution"])
sup1 = sup1.drop_duplicates(subset=["_title_key", "_org_key"], keep="first")

sup1_renamed = sup1[
    ["_title_key", "_org_key", "Subject", "Duration", "Gained Skills"]
].rename(columns={"Duration": "duration_sup1", "Gained Skills": "gained_skills_sup1"})

print(f"  -> {len(sup1)} dòng sau dedupe (gốc 3404)")

# ============================================================
# BANG 3: coursera_course_dataset_v3.csv (bổ sung Difficulty, Type, course_url)
# ============================================================
print("Đang xử lý bảng bổ sung: coursera_course_dataset_v3.csv ...")
sup2 = pd.read_csv(r"D:\Project_CK_TTDLTQ\Data\raw\coursera_course_dataset_v3.csv", on_bad_lines="skip")

sup2["_title_key"] = normalize_key(sup2["Title"])
sup2["_org_key"] = normalize_key(sup2["Organization"])
sup2 = sup2.drop_duplicates(subset=["_title_key", "_org_key"], keep="first")

sup2_renamed = sup2[
    ["_title_key", "_org_key", "Difficulty", "Type", "course_url", "Duration"]
].rename(columns={"Duration": "duration_sup2"})

print(f"  -> {len(sup2)} dòng sau dedupe (gốc 623)")

# ============================================================
# JOIN: left-join giữ nguyên số dòng của bảng Fact chính
# ============================================================
print("\nĐang Join 3 bảng theo khóa (Title + Organization) ...")
merged = fact.merge(sup1_renamed, on=["_title_key", "_org_key"], how="left")
merged = merged.merge(sup2_renamed, on=["_title_key", "_org_key"], how="left")

match1 = merged["Subject"].notna().sum()
match2 = merged["Difficulty"].notna().sum()
print(f"  -> Khớp với Coursera.csv: {match1} dòng")
print(f"  -> Khớp với v3.csv: {match2} dòng")
print(f"  -> Tổng số dòng sau Join: {len(merged)} (phải vẫn = {len(fact)})")

merged = merged.drop(columns=["_title_key", "_org_key"])
merged.to_csv("data/processed/fact_courses.csv", index=False)
print("\nĐã lưu: data/processed/fact_courses.csv")