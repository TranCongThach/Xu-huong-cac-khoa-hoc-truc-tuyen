import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import ast

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Tahoma', 'DejaVu Sans']

df = pd.read_csv("../Data/processed/fact_courses_FINAL_v2.csv")

# Chuyển đổi các placeholder thành NaN
placeholders = ['[]', "['']", 'not found', 'Not Found', 'Organization not found', 
                'Enrollment number not found', 'Rating not found', 'None', 'nan']
df.replace(placeholders, np.nan, inplace=True)

for col in ['Instructor', 'Organization', 'enrolled', 'rating']:
    if col in df.columns:
        df[col] = df[col].apply(lambda x: np.nan if pd.notna(x) and 'not found' in str(x).lower() else x)

def clean_skills(val):
    if pd.isna(val): return np.nan
    val = str(val).strip()
    if val in ["[]", "['']", "['not found']"]: return np.nan
    return val

df['skills_combined'] = df['skills_combined'].apply(clean_skills)
df.loc[(df['rating_num'].isna()) | (df['enrolled_num'].isna()), 'popularity_score'] = np.nan

out_dir = "../outputs/eda"
os.makedirs(out_dir, exist_ok=True)

dq_df = pd.DataFrame({
    'Column': df.columns,
    'Missing_Count': df.isna().sum(),
    'Missing_Percentage': (df.isna().sum() / len(df)) * 100,
    'Unique_Count': df.nunique(),
    'Data_Type': df.dtypes
}).reset_index(drop=True)
dq_df.to_csv(f"{out_dir}/01_data_quality.csv", index=False)

desc_df = df.describe(include=[np.number]).T
desc_df.to_csv(f"{out_dir}/02_descriptive_statistics.csv", index=True)

# Phân phối các biến số chính
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Phân phối các biến số chính', fontsize=12, fontweight='bold', y=0.98)

sns.histplot(df['enrolled_num'].dropna(), bins=50,
             kde=True, ax=axes[0, 0], color='blue', log_scale=True)
axes[0, 0].set_title('Phân phối số lượng học viên')
axes[0, 0].set_xlabel('Số học viên đã đăng ký')
axes[0, 0].set_ylabel('Tần suất')

sns.histplot(df['rating_num'].dropna(), bins=20,
             kde=True, ax=axes[0, 1], color='salmon')
axes[0, 1].set_title('Phân phối điểm đánh giá')
axes[0, 1].set_xlabel('Điểm đánh giá (1 - 5)')
axes[0, 1].set_ylabel('Tần suất')

sns.histplot(df[df['hours_to_complete'] < 100]
             ['hours_to_complete'].dropna(), bins=30,
             kde=True, ax=axes[1, 0], color='green')
axes[1, 0].set_title('Phân phối thời gian hoàn thành (< 100 giờ)')
axes[1, 0].set_xlabel('Số giờ')
axes[1, 0].set_ylabel('Tần suất')

sns.histplot(df['popularity_score'].dropna(), bins=30, kde=True, ax=axes[1, 1], color='orchid')
axes[1, 1].set_title('Phân phối điểm phổ biến')
axes[1, 1].set_xlabel('Điểm phổ biến (0 - 1)')
axes[1, 1].set_ylabel('Tần suất')

plt.tight_layout()
plt.savefig(f"{out_dir}/03_numeric_distributions.png", dpi=300)
plt.close()

# Số lượng khóa học theo độ khó
plt.figure(figsize=(10, 6))
sns.countplot(data=df, y='level_clean', order=df['level_clean'].value_counts().index,
              hue='level_clean', palette='pastel', legend=False)
plt.title('Số lượng khóa học theo độ khó', fontsize=12, fontweight='bold')
plt.xlabel('Số lượng khóa học')
plt.ylabel('Cấp độ')
plt.tight_layout()
plt.savefig(f"{out_dir}/04_level_distribution.png", dpi=300)
plt.close()

# Số lượng khóa học
plt.figure(figsize=(12, 6))
top_subjects = df['Subject'].value_counts().head(10)
sns.barplot(x=top_subjects.values, y=top_subjects.index,
            hue=top_subjects.index, palette='pastel', legend=False)
plt.title('Phân bố các chủ đề', fontsize=12, fontweight='bold')
plt.xlabel('Số lượng khóa học')
plt.ylabel('')
plt.tight_layout()
plt.savefig(f"{out_dir}/05_subject_distribution.png", dpi=300)
plt.close()

# Mức độ khó của các khóa học
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='level_clean', y='rating_num', hue='level_clean', palette='Set2', 
            order=['Beginner', 'Intermediate', 'Advanced', 'Not specified'], legend=False)
plt.title('Phân bố điểm đánh giá theo mức độ khó', fontsize=12, fontweight='bold')
plt.xlabel('Cấp độ')
plt.ylabel('Điểm đánh giá')
plt.tight_layout()
plt.savefig(f"{out_dir}/06_rating_by_level.png", dpi=300)
plt.close()

# Heatmap
fig, axes = plt.subplots(1, 2, figsize=(18, 8))
cols_raw = ['enrolled_num', 'rating_num', 'num_reviews', 'hours_to_complete']
cols_derived = ['popularity_score', 'review_to_enrollment_ratio']

sns.heatmap(df[cols_raw].corr(method='spearman'), ax=axes[0], annot=True, cmap='coolwarm', fmt=".2f",
            xticklabels=['Học viên', 'Rating', 'Số Reviews', 'Số giờ'],
            yticklabels=['Học viên', 'Rating', 'Số Reviews', 'Số giờ'])
axes[0].set_title('Tương quan Spearman (Biến Gốc)', fontsize=12, fontweight='bold', pad=15)

sns.heatmap(df[cols_derived].corr(method='spearman'), ax=axes[1], annot=True, cmap='coolwarm', fmt=".2f",
            xticklabels=['Độ phổ biến', 'Tỉ lệ Rev/Enr'],
            yticklabels=['Độ phổ biến', 'Tỉ lệ Rev/Enr'])
axes[1].set_title('Tương quan Spearman (Biến Phái Sinh)', fontsize=12, fontweight='bold', pad=15)

plt.tight_layout()
plt.savefig(f"{out_dir}/07_correlation_spearman.png", dpi=300)
plt.close()

# Top 10 tổ chức có nhiều khóa học nhất
plt.figure(figsize=(12, 6))
top_orgs = df['Organization'].value_counts().head(10)
sns.barplot(x=top_orgs.values, y=top_orgs.index,
            hue=top_orgs.index, palette='viridis', legend=False)
plt.title('Top 10 tổ chức có nhiều khóa học nhất', fontsize=12, fontweight='bold')
plt.xlabel('Số lượng khóa học')
plt.ylabel('')
plt.tight_layout()
plt.savefig(f"{out_dir}/08_top_organizations.png", dpi=300)
plt.close()

# Top 10 QG
plt.figure(figsize=(12, 6))
top_countries = df['Country'].value_counts().head(10)
sns.barplot(x=top_countries.values, y=top_countries.index,
            hue=top_countries.index, palette='magma', legend=False)
plt.title('Top 10 Quốc Gia trụ sở tổ chức', fontsize=12, fontweight='bold')
plt.xlabel('Số lượng khóa học')
plt.ylabel('')
plt.tight_layout()
plt.savefig(f"{out_dir}/09_organization_hq_countries.png", dpi=300)
plt.close()

# Tỷ lệ Missing value
missing_pct = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
missing_pct = missing_pct[missing_pct > 0] 

plt.figure(figsize=(12, 10))
sns.barplot(x=missing_pct.values, y=missing_pct.index,
            hue=missing_pct.index, palette='Reds_r', legend=False)
plt.title('Tỷ lệ Missing value theo từng cột (%)', fontsize=12, fontweight='bold')
plt.xlabel('Phần trăm thiếu (%)')
plt.ylabel('Tên cột')
for i, v in enumerate(missing_pct.values):
    plt.text(v + 0.5, i, f"{v:.1f}%", va='center')
plt.xlim(0, 105)
plt.tight_layout()
plt.savefig(f"{out_dir}/10_missing_values.png", dpi=300)
plt.close()

# Top các skill phổ biến nhất
skills_list = []
for item in df['skills_combined'].dropna():
    try:
        if item.startswith('['):
            skills = ast.literal_eval(item)
            if isinstance(skills, list):
                skills_list.extend(skills)
        else:
            skills_list.append(item)
    except:
        pass

skills_series = pd.Series(skills_list)
top_skills = skills_series.value_counts().head(15)

plt.figure(figsize=(12, 8))
sns.barplot(x=top_skills.values, y=top_skills.index,
            hue=top_skills.index, palette='mako', legend=False)
plt.title('Top 15 skill phổ biến nhất', fontsize=12, fontweight='bold')
plt.xlabel('Tần suất xuất hiện')
plt.ylabel('')
plt.tight_layout()
plt.savefig(f"{out_dir}/11_top_skills.png", dpi=300)
plt.close()
