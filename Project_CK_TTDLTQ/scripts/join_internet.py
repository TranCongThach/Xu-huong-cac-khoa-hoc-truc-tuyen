"""
Bước 5b (cuối): Join dữ liệu Internet Usage theo quốc gia vào bảng Fact.
Input : data/processed/fact_courses_final.csv, data/raw/internet_usage.csv
Output: data/processed/fact_courses_FINAL_v2.csv

Quyết định xử lý (giải thích cho vấn đáp):
- File internet_usage.csv là dạng WIDE (mỗi năm 1 cột: 2000...2023).
- Cột 2023 thiếu tới 158/217 quốc gia (73%) -> không dùng cố định 1 năm.
- Giải pháp: lấy giá trị của NĂM GẦN NHẤT CÓ SỐ LIỆU cho từng quốc gia
  (VD: nước A có data đến 2022 thì lấy 2022, nước B chỉ có đến 2020 thì lấy 2020).
  Đây là kỹ thuật "last valid observation" — phổ biến khi làm việc với
  time-series có độ phủ không đồng đều giữa các nhóm.
- Ký hiệu '..', 'N/A', '-' trong file gốc là missing value của World Bank,
  không phải NaN chuẩn -> phải khai báo na_values đầy đủ khi đọc.
"""
import pandas as pd

# ============================================================
# 1) Đọc & xử lý bảng Internet Usage (wide -> lấy năm gần nhất có data)
#    na_values mở rộng: World Bank dùng '..', 'N/A', '-', '' để chỉ missing
# ============================================================
net = pd.read_csv(
    r"D:\Project_CK_TTDLTQ\Data\raw\internet_usage.csv",
    na_values=["..", "N/A", "-", ""],
    keep_default_na=True,
)

year_cols = [c for c in net.columns if c.isdigit()]
year_cols_sorted = sorted(year_cols, key=int)

# bfill từ phải sang trái theo thứ tự năm giảm dần để lấy "giá trị hợp lệ gần nhất"
net_years_desc = net[year_cols_sorted[::-1]]  # 2023, 2022, ..., 2000
net["internet_usage_pct"] = net_years_desc.bfill(axis=1).iloc[:, 0]

# Ghi lại NĂM nào được lấy, để minh bạch khi báo cáo (không giấu việc "trộn năm")
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

# ============================================================
# 2) Join vào bảng Fact theo tên quốc gia
#    Lưu ý: bảng Fact dùng tên quốc gia tiếng Anh do ta tự gán thủ công
#    (VD "United States"), cần khớp đúng chính tả với "Country Name"
#    của World Bank -> kiểm tra các trường hợp không khớp được.
#
#    Đã phát hiện các trường hợp lệch tên gọi giữa 2 nguồn, xử lý như sau:
#    - "South Korea"    -> World Bank gọi là "Korea, Rep."
#    - "Hong Kong"      -> World Bank gọi là "Hong Kong SAR, China"
#    - "Czech Republic" -> World Bank gọi là "Czechia"
#    - "Taiwan"         -> KHÔNG có trong World Bank (Đài Loan không phải
#      thành viên WB nên không được thống kê riêng) -> điền thủ công
#      từ nguồn ITU 2022 (nguồn độc lập, đáng tin cậy): 91.0%.
#      Ghi chú này cần nêu rõ trong báo cáo để minh bạch nguồn dữ liệu.
# ============================================================
COUNTRY_NAME_FIX = {
    "South Korea": "Korea, Rep.",
    "Hong Kong": "Hong Kong SAR, China",
    "Czech Republic": "Czechia",
}

# Giá trị điền thủ công cho các quốc gia không có trong World Bank
# Format: { "Tên quốc gia": (internet_usage_pct, năm, nguồn) }
MANUAL_INTERNET = {
    "Taiwan": (91.0, 2022),  # Nguồn: ITU 2022 — WB không thống kê Đài Loan
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

# ============================================================
# 3) Điền thủ công các quốc gia không có trong World Bank
#    Lý do không để NaN: các nước này vẫn xác định được giá trị từ nguồn
#    đáng tin cậy khác -> để NaN là lãng phí thông tin có thể bổ sung.
#    Cần ghi rõ nguồn bổ sung trong báo cáo để minh bạch.
# ============================================================
print()
for country, (usage_pct, usage_year) in MANUAL_INTERNET.items():
    mask = merged["Country"] == country
    n_filled = mask.sum()
    if n_filled > 0:
        merged.loc[mask, "internet_usage_pct"] = usage_pct
        merged.loc[mask, "internet_usage_year"] = usage_year
        print(f"  -> Điền thủ công '{country}': {usage_pct}% (năm {usage_year}, nguồn ITU) — {n_filled} dòng")

# ============================================================
# 4) Kiểm tra các quốc gia vẫn không khớp được (ngoài manual fill)
# ============================================================
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

# ============================================================
# 5) Tổng kết coverage & lưu file
#    Ghi chú báo cáo: internet_usage_pct bị lệch phải (right-skewed) vì
#    phần lớn khóa học đến từ US/UK/Ấn Độ — đây là đặc điểm của dữ liệu,
#    không phải lỗi xử lý. Nên đề cập điều này khi trình bày dashboard.
# ============================================================
total = len(merged)
has_internet = merged["internet_usage_pct"].notna().sum()
print(f"\nCoverage internet_usage_pct: {has_internet}/{total} ({has_internet/total*100:.1f}%)")
print(f"  - Còn thiếu: {total - has_internet} dòng (do Country = NaN, không thể map)")

merged.to_csv("data/processed/fact_courses_FINAL_v2.csv", index=False)
print(f"\nHoàn tất. Số dòng: {len(merged)} | Số cột: {len(merged.columns)}")
print(f"Đã lưu: data/processed/fact_courses_FINAL_v2.csv")