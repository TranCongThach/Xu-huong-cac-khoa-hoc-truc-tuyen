import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Tahoma', 'DejaVu Sans']

df = pd.read_csv("../Data/processed/fact_courses_FINAL_v2.csv")

# 1. Phân phối dữ liệu số
fig1, axes1 = plt.subplots(2, 2, figsize=(16, 12))
fig1.suptitle('Phân Phối Các Biến Số Chính', fontsize=18, fontweight='bold', y=0.98)

sns.histplot(df['enrolled_num'].dropna(), bins=50, kde=True, ax=axes1[0, 0], color='skyblue', log_scale=True)
axes1[0, 0].set_title('Phân phối Số lượng Học viên (Log Scale)')
axes1[0, 0].set_xlabel('Số học viên đã đăng ký')
axes1[0, 0].set_ylabel('Tần suất')

sns.histplot(df['rating_num'].dropna(), bins=20, kde=True, ax=axes1[0, 1], color='salmon')
axes1[0, 1].set_title('Phân phối Điểm Đánh Giá (Rating)')
axes1[0, 1].set_xlabel('Điểm đánh giá (1-5)')
axes1[0, 1].set_ylabel('Tần suất')

sns.histplot(df[df['hours_to_complete'] < 100]['hours_to_complete'].dropna(), bins=30, kde=True, ax=axes1[1, 0], color='lightgreen')
axes1[1, 0].set_title('Phân phối Thời Gian Hoàn Thành (< 100 giờ)')
axes1[1, 0].set_xlabel('Số giờ')
axes1[1, 0].set_ylabel('Tần suất')

sns.histplot(df['popularity_score'].dropna(), bins=30, kde=True, ax=axes1[1, 1], color='orchid')
axes1[1, 1].set_title('Phân phối Điểm Phổ Biến (Popularity Score)')
axes1[1, 1].set_xlabel('Điểm phổ biến (0-1)')
axes1[1, 1].set_ylabel('Tần suất')

fig1.tight_layout()

# 2. Phân phối biến phân loại
fig2, axes2 = plt.subplots(1, 2, figsize=(16, 6))
fig2.suptitle('Phân Phối Dữ Liệu Phân Loại', fontsize=18, fontweight='bold')

sns.countplot(data=df, y='level_clean', order=df['level_clean'].value_counts().index, ax=axes2[0], hue='level_clean', palette='pastel', legend=False)
axes2[0].set_title('Số lượng khóa học theo Độ Khó')
axes2[0].set_xlabel('Số lượng khóa học')
axes2[0].set_ylabel('Cấp độ')

top_subjects = df['Subject'].value_counts().head(10)
sns.barplot(x=top_subjects.values, y=top_subjects.index, ax=axes2[1], hue=top_subjects.index, palette='pastel', legend=False)
axes2[1].set_title('Top 10 Chủ Đề (Subject) Phổ Biến Nhất')
axes2[1].set_xlabel('Số lượng khóa học')
axes2[1].set_ylabel('')

fig2.tight_layout()

# 3. Rating theo độ khó
fig3 = plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='level_clean', y='rating_num', hue='level_clean', palette='Set2', 
            order=['Beginner', 'Intermediate', 'Advanced', 'Not specified'], legend=False)
plt.title('Phân Bố Điểm Đánh Giá Theo Mức Độ Khó', fontsize=16, fontweight='bold')
plt.xlabel('Cấp độ (Level)')
plt.ylabel('Điểm đánh giá')
fig3.tight_layout()

# 4. Heatmap
cols_for_corr = ['enrolled_num', 'rating_num', 'num_reviews', 'hours_to_complete', 
                 'duration_weeks', 'popularity_score', 'review_to_enrollment_ratio']
corr_matrix = df[cols_for_corr].corr()

fig4 = plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5,
            xticklabels=['Học viên', 'Rating', 'Số Reviews', 'Số giờ', 'Số tuần', 'Độ phổ biến', 'Tỉ lệ Rev/Enr'],
            yticklabels=['Học viên', 'Rating', 'Số Reviews', 'Số giờ', 'Số tuần', 'Độ phổ biến', 'Tỉ lệ Rev/Enr'])
plt.title('Ma Trận Tương Quan Giữa Các Biến Số Chính', fontsize=16, fontweight='bold', pad=20)
fig4.tight_layout()

# 5. Top tổ chức & Quốc gia
fig5, axes5 = plt.subplots(1, 2, figsize=(18, 7))
fig5.suptitle('Phân Tích Theo Tổ Chức Và Quốc Gia', fontsize=18, fontweight='bold')

top_orgs = df['Organization'].value_counts().head(10)
sns.barplot(x=top_orgs.values, y=top_orgs.index, ax=axes5[0], hue=top_orgs.index, palette='viridis', legend=False)
axes5[0].set_title('Top 10 Tổ Chức Có Nhiều Khóa Học Nhất')
axes5[0].set_xlabel('Số lượng khóa học')
axes5[0].set_ylabel('')

top_countries = df['Country'].value_counts().head(10)
sns.barplot(x=top_countries.values, y=top_countries.index, ax=axes5[1], hue=top_countries.index, palette='magma', legend=False)
axes5[1].set_title('Top 10 Quốc Gia Cung Cấp Khóa Học')
axes5[1].set_xlabel('Số lượng khóa học')
axes5[1].set_ylabel('')

fig5.tight_layout()

# 6. Tỷ lệ các missing value
missing_pct = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
missing_pct = missing_pct[missing_pct > 0] 

fig6 = plt.figure(figsize=(12, 8))
sns.barplot(x=missing_pct.values, y=missing_pct.index, hue=missing_pct.index, palette='Reds_r', legend=False)
plt.title('Tỉ Lệ Missing Value Theo Từng Cột (%)', fontsize=16, fontweight='bold')
plt.xlabel('Phần trăm thiếu (%)')
plt.ylabel('Tên cột')
for i, v in enumerate(missing_pct.values):
    plt.text(v + 0.5, i, f"{v:.1f}%", va='center')
plt.xlim(0, 105)
fig6.tight_layout()

plt.show()
