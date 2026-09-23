import pandas as pd
import sys
sys.path.insert(0, "scripts")
from org_country_mapping import ORG_COUNTRY_MAP

fact = pd.read_csv("./Data/processed/fact_courses.csv")
fact["Country"] = fact["Organization"].map(ORG_COUNTRY_MAP)
fact["Country"] = fact["Country"].replace("UNKNOWN", pd.NA)
n_mapped = fact["Country"].notna().sum()
n_total = len(fact)
print(f"Số dòng đã có Country: {n_mapped}/{n_total} ({n_mapped/n_total*100:.1f}%)")
# Xuất riêng bảng Dimension để nộp kèm báo cáo (minh chứng có nhiều bảng)
dim_table = (
    pd.DataFrame(list(ORG_COUNTRY_MAP.items()), columns=["Organization", "Country"])
    .query("Country != 'UNKNOWN'")
    .reset_index(drop=True)
)
dim_table.to_csv("./Data/processed/dim_organization_country.csv", index=False)
print(f"Đã lưu bảng Dimension: ./Data/processed/dim_organization_country.csv ({len(dim_table)} tổ chức)")
fact.to_csv("./Data/processed/fact_courses_with_country.csv", index=False)
print("Đã lưu: ./Data/processed/fact_courses_with_country.csv")
print("\nTop 10 quốc gia theo số khóa học:")
print(fact["Country"].value_counts().head(10))