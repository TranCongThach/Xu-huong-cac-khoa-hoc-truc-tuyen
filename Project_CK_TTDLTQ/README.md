# Project Cuối Kỳ — Phân Tích Dữ Liệu Khóa Học Coursera

## Mô tả
Dự án phân tích dữ liệu các khóa học trên nền tảng Coursera, bao gồm:
- Làm sạch & gộp dữ liệu từ nhiều nguồn
- Map quốc gia theo tổ chức
- Tính toán các chỉ số: popularity score, review ratio, v.v.
- Join dữ liệu tỉ lệ sử dụng Internet theo quốc gia (World Bank)

## Cấu trúc dự án

```
Project_CK_TTDLTQ/
├── scripts/
│   ├── clean_join_data.py       # Bước 1: Gộp & làm sạch 3 bảng raw
│   ├── org_country_mapping.PY   # Bảng map: Tổ chức -> Quốc gia (297 tổ chức)
│   ├── country.py               # Bước 2: Gán Country vào bảng Fact
│   ├── calculated.py            # Bước 3: Tính Calculated Fields
│   └── join_internet.py         # Bước 4: Join Internet Usage (World Bank)
├── Data/
│   ├── raw/                     # 
│   └── processed/               # Output sau khi chạy pipeline
├── .gitignore
└── README.md
```

## Dữ liệu Raw (tải riêng)

Thư mục `Data/raw/` không được push lên Git vì file quá lớn.  
Tải các file sau và đặt vào `Data/raw/`:

| File | Nguồn |
|------|-------|
| `coursera_course_2024.csv` | Kaggle |
| `Coursera.csv` | Kaggle |
| `coursera_course_dataset_v3.csv` | Kaggle |
| `internet_usage.csv` | World Bank |

## Cách chạy

> Yêu cầu: Python 3.10+, đã cài các thư viện bên dưới.

```bash
# 1. Tạo virtual environment
python -m venv venv

# 2. Kích hoạt venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux

# 3. Cài thư viện
pip install pandas numpy

# 4. Chạy pipeline theo thứ tự
python scripts/clean_join_data.py
python scripts/country.py
python scripts/calculated.py
python scripts/join_internet.py
```

## Output cuối cùng

| File | Mô tả |
|------|-------|
| `Data/processed/fact_courses_FINAL_v2.csv` | Bảng Fact hoàn chỉnh (6640 dòng, 36 cột) |
| `Data/processed/dim_organization_country.csv` | Bảng Dimension: Tổ chức → Quốc gia |
| `Data/processed/dim_internet_usage.csv` | Bảng Dimension: Quốc gia → Internet Usage |

## Thống kê dữ liệu

- **Tổng số khóa học:** 6,640
- **Coverage Country:** 99.8%
- **Coverage Internet Usage:** 99.8%
- **Calculated Fields:** popularity_score, review_to_enrollment_ratio, hours_to_complete, duration_weeks, skills_combined, courses_per_organization, courses_per_country

## TODO (các bước tiếp theo)

- [x] EDA (Exploratory Data Analysis) - Chạy `python scripts/eda.py` để xem biểu đồ trong `outputs/eda/`
- [ ] Phân tích Insight
- [ ] Mô hình dự báo
- [ ] Dashboard / Visualization
