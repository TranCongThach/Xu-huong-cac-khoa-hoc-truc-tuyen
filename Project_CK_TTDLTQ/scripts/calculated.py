import pandas as pd
import numpy as np
import re

df = pd.read_csv(r"D:\Project_CK_TTDLTQ\Data\processed\fact_courses_with_country.csv")
n_before = len(df)

def parse_schedule(text):
    """'13 hours to complete (3 weeks at 4 hours a week)' -> (13.0, 3.0)"""
    if pd.isna(text):
        return np.nan, np.nan
    hours_match = re.search(r"([\d.]+)\s*hours? to complete", text)
    weeks_match = re.search(r"([\d.]+)\s*weeks?", text)
    hours = float(hours_match.group(1)) if hours_match else np.nan
    weeks = float(weeks_match.group(1)) if weeks_match else np.nan
    return hours, weeks


parsed = df["Schedule"].apply(parse_schedule)
df["hours_to_complete"] = parsed.apply(lambda x: x[0])
df["duration_weeks"] = parsed.apply(lambda x: x[1])
df["level_clean"] = (
    df["Level"].str.replace(" level", "", regex=False).fillna("Not specified")
)

df["review_to_enrollment_ratio"] = np.where(
    (df["enrolled_num"].notna()) & (df["enrolled_num"] > 0),
    df["num_reviews"] / df["enrolled_num"],
    np.nan,
)

df["enrolled_percentile"] = df["enrolled_num"].rank(pct=True)
df["rating_normalized"] = df["rating_num"] / 5.0
df["popularity_score"] = (
    0.5 * df["rating_normalized"].fillna(0) + 0.5 * df["enrolled_percentile"].fillna(0)
)

df["skills_combined"] = df["Skills"].fillna(df["gained_skills_sup1"])
df["courses_per_organization"] = df.groupby("Organization")["title"].transform("count")
df["courses_per_country"] = df.groupby("Country")["title"].transform("count")
assert len(df) == n_before, "LỖI: số dòng bị thay đổi, kiểm tra lại các bước merge/groupby!"
df.to_csv("data/processed/fact_courses_final.csv", index=False)
print(f"Hoàn tất. Số dòng: {len(df)} | Số cột: {len(df.columns)}")
print(f"Đã lưu: data/processed/fact_courses_final.csv")
print()
print("Thống kê nhanh các trường mới:")
print(df[["hours_to_complete", "duration_weeks", "review_to_enrollment_ratio", "popularity_score"]].describe())
