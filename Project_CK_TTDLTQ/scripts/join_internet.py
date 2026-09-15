import pandas as pd
net = pd.read_csv(
    r"D:\Project_CK_TTDLTQ\Data\raw\internet_usage.csv",
    na_values=["..", "N/A", "-", ""],
    keep_default_na=True,
)

year_cols = [c for c in net.columns if c.isdigit()]
year_cols_sorted = sorted(year_cols, key=int)
net_years_desc = net[year_cols_sorted[::-1]]  
net["internet_usage_pct"] = net_years_desc.bfill(axis=1).iloc[:, 0]

def get_latest_year(row):
    for y in year_cols_sorted[::-1]:
        if pd.notna(row[y]):
            return int(y)
    return None

net["internet_usage_year"] = net.apply(get_latest_year, axis=1)
net_clean = net[["Country Name", "Country Code", "internet_usage_pct", "internet_usage_year"]]
n_missing_all = net_clean["internet_usage_pct"].isna().sum()
print(f"Quốc gia hoàn toàn không có dữ liệu (mọi năm đều thiếu): {n_missing_all}/{len(net_clean)}")
net_clean.to_csv("data/processed/dim_internet_usage.csv", index=False)
print("Đã lưu bảng Dimension: data/processed/dim_internet_usage.csv")

COUNTRY_NAME_FIX = {
    "South Korea": "Korea, Rep.",
    "Hong Kong": "Hong Kong SAR, China",
    "Czech Republic": "Czechia",
}

MANUAL_INTERNET = {
    "Taiwan": (91.0, 2022),  
}

fact = pd.read_csv(r"D:\Project_CK_TTDLTQ\Data\processed\fact_courses_final.csv")
n_before = len(fact)
fact["_country_for_join"] = fact["Country"].replace(COUNTRY_NAME_FIX)
merged = fact.merge(
    net_clean[["Country Name", "internet_usage_pct", "internet_usage_year"]],
    left_on="_country_for_join",
    right_on="Country Name",
    how="left",
).drop(columns=["Country Name", "_country_for_join"])
assert len(merged) == n_before, "LỖI: số dòng thay đổi sau khi join!"
print()
for country, (usage_pct, usage_year) in MANUAL_INTERNET.items():
    mask = merged["Country"] == country
    n_filled = mask.sum()
    if n_filled > 0:
        merged.loc[mask, "internet_usage_pct"] = usage_pct
        merged.loc[mask, "internet_usage_year"] = usage_year
        print(f"  -> Điền thủ công '{country}': {usage_pct}% (năm {usage_year}, nguồn ITU) — {n_filled} dòng")

unmatched_countries = (
    merged.loc[merged["Country"].notna() & merged["internet_usage_pct"].isna(), "Country"]
    .unique()
)
if len(unmatched_countries) > 0:
    print(f"\n{len(unmatched_countries)} quốc gia có trong Fact nhưng KHÔNG khớp tên với World Bank:")
    print(list(unmatched_countries))
    print("   -> Cần sửa tên trong org_country_mapping.py hoặc thêm bảng ánh xạ tên quốc gia.")
else:
    print("Tất cả quốc gia có Country đã được map internet_usage_pct thành công! ✓")
total = len(merged)
has_internet = merged["internet_usage_pct"].notna().sum()
print(f"\nCoverage internet_usage_pct: {has_internet}/{total} ({has_internet/total*100:.1f}%)")
print(f"  - Còn thiếu: {total - has_internet} dòng (do Country = NaN, không thể map)")
merged.to_csv("data/processed/fact_courses_FINAL_v2.csv", index=False)
print(f"\nHoàn tất. Số dòng: {len(merged)} | Số cột: {len(merged.columns)}")
print(f"Đã lưu: data/processed/fact_courses_FINAL_v2.csv")
