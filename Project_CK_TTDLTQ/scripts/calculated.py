"""
Bước 6: Tạo Calculated Fields và xuất bảng Fact hoàn chỉnh.
Input : data/processed/fact_courses_with_country.csv
Output: data/processed/fact_courses_final.csv

Lưu ý cho Terry khi bảo vệ đồ án (vấn đáp):
- Mọi quyết định xử lý ở đây đều có LÝ DO cụ thể, ghi rõ trong comment.
- Nếu giảng viên hỏi "tại sao chọn cách này mà không phải cách khác",
  câu trả lời nằm ngay trong docstring/comment bên dưới từng hàm.
"""
import pandas as pd
import numpy as np
import re

df = pd.read_csv(r"D:\Project_CK_TTDLTQ\Data\processed\fact_courses_with_country.csv")
n_before = len(df)

# ============================================================
# 1) Parse cột 'Schedule' -> số giờ học & số tuần học (dạng số)
#    Lý do: cột Schedule là text tự do "13 hours to complete (3 weeks
#    at 4 hours a week)" -> không dùng được để lọc/so sánh trên dashboard.
#    Ưu tiên dùng Schedule thay vì duration_sup1/sup2 vì Schedule có
#    độ phủ dữ liệu tốt hơn (chỉ ~28% thiếu so với >70% thiếu của 2 cột kia,
#    do 2 cột đó chỉ có giá trị ở phần dữ liệu được Join thêm).
# ============================================================
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

# ============================================================
# 2) Chuẩn hóa cột 'Level' (độ khó)
#    Lý do: bỏ chữ " level" thừa cho gọn ("Beginner level" -> "Beginner"),
#    và fillna("Not specified") thay vì để NaN — vì đây là cột dùng để
#    LỌC (filter) trên dashboard, để NaN sẽ gây lỗi hiển thị dropdown.
# ============================================================
df["level_clean"] = (
    df["Level"].str.replace(" level", "", regex=False).fillna("Not specified")
)

# ============================================================
# 3) review_to_enrollment_ratio: tỉ lệ người review / người đăng ký
#    Ý nghĩa: proxy đo mức độ "tương tác" của học viên với khóa học.
#    Không dùng khi enrolled_num = 0 hoặc NaN -> kết quả NaN (không suy diễn số liệu).
# ============================================================
df["review_to_enrollment_ratio"] = np.where(
    (df["enrolled_num"].notna()) & (df["enrolled_num"] > 0),
    df["num_reviews"] / df["enrolled_num"],
    np.nan,
)

# ============================================================
# 4) popularity_score: điểm phổ biến tổng hợp (0-1), kết hợp rating + enrolled
#    Lý do cần chuẩn hóa (normalize) trước khi cộng gộp:
#    - rating_num: thang 0-5
#    - enrolled_num: thang từ vài chục đến hàng triệu (lệch cực mạnh)
#    => Nếu cộng trực tiếp, enrolled sẽ át hoàn toàn rating.
#    Giải pháp: đưa enrolled về percentile rank (0-1), rating về (rating/5),
#    rồi lấy trung bình có trọng số 50-50. Trọng số này là lựa chọn hợp lý,
#    có thể điều chỉnh và giải thích rõ trong báo cáo (không phải "chân lý").
# ============================================================
df["enrolled_percentile"] = df["enrolled_num"].rank(pct=True)
df["rating_normalized"] = df["rating_num"] / 5.0
df["popularity_score"] = (
    0.5 * df["rating_normalized"].fillna(0) + 0.5 * df["enrolled_percentile"].fillna(0)
)

# ============================================================
# 4b) Gộp 'Skills' (từ bảng chính) và 'gained_skills_sup1' (từ Coursera.csv)
#     Lý do: 2 cột cùng ý nghĩa (kỹ năng đạt được sau khóa học) nhưng khác tên
#     do đến từ 2 nguồn khác nhau -> để riêng dễ gây nhầm cho người làm EDA
#     (không biết dùng cột nào). Ưu tiên 'Skills' (độ phủ tốt hơn, từ bảng
#     chính 6.640 dòng), chỉ lấy 'gained_skills_sup1' để lấp chỗ trống.
# ============================================================
df["skills_combined"] = df["Skills"].fillna(df["gained_skills_sup1"])

# ============================================================
# 5) Các trường tổng hợp theo nhóm (hữu ích cho Dashboard: bar chart Top N)
# ============================================================
df["courses_per_organization"] = df.groupby("Organization")["title"].transform("count")
df["courses_per_country"] = df.groupby("Country")["title"].transform("count")

# ============================================================
# KIỂM TRA CUỐI: đảm bảo không làm mất dòng nào trong toàn bộ quá trình
# ============================================================
assert len(df) == n_before, "LỖI: số dòng bị thay đổi, kiểm tra lại các bước merge/groupby!"

df.to_csv("data/processed/fact_courses_final.csv", index=False)

print(f"Hoàn tất. Số dòng: {len(df)} | Số cột: {len(df.columns)}")
print(f"Đã lưu: data/processed/fact_courses_final.csv")
print()
print("Thống kê nhanh các trường mới:")
print(df[["hours_to_complete", "duration_weeks", "review_to_enrollment_ratio", "popularity_score"]].describe())