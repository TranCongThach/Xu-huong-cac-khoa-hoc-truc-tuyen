# Tóm tắt quá trình và kết quả khám phá dữ liệu (EDA) trên tập dữ liệu về các khóa học trực tuyến.

## 1. Tiền xử lý dữ liệu
- **Làm sạch các giá trị placeholder**: Các giá trị rác như `"[]"`, `"['']"`, `"not found"`, `"Organization not found"`, `"Enrollment number not found"`, và `"Rating not found"` đã được đưa về dạng `NaN` chuẩn để hệ thống có thể đếm chính xác phần trăm giá trị bị khuyết.
- **Biến `popularity_score`**: Sửa lỗi 1.322 khóa học bị gán điểm 0 không hợp lý. Những khóa học bị khuyết cả `rating_num` và `enrolled_num` đã được gán lại thành `NaN`.
- **Phân tách `skills_combined`**: Giải quyết lỗi `"[]"` không được nhận diện là `NaN`. Tính năng này cũng đã được phân tách từ chuỗi danh sách để trực quan hóa top 15 skill phổ biến nhất.
- **Loại bỏ biến hằng số**: Thuộc tính `duration_weeks` vốn chỉ chứa một hằng số duy nhất (`3.0`) đã được loại bỏ khỏi Heatmap để `tránh gây nhiễu ma trận tương quan`.
- **Tách biến gốc và biến phái sinh**: Heatmap tương quan được chia thành 2 phần là: Biến gốc (`enrolled_num`, `rating_num`, `num_reviews`, `hours_to_complete`) và Biến phái sinh (`popularity_score`, `review_to_enrollment_ratio`) và sử dụng phương pháp **Spearman** thay vì Pearson để phản ánh tương quan phi tuyến.

## 2. Tóm tắt kết quả phân tích
Các biểu đồ thể hiện những điểm chính sau:
- **Phân phối các biến số chính**: Cho thấy lượng học viên (enrollment) phân bố lệch phải rất mạnh (đã được chuyển sang Log scale để dễ quan sát). Hầu hết các khóa học có rating cao (tập trung ở mức 4.5 - 5.0) và thời gian hoàn thành chủ yếu dưới 40 giờ.
- **Số lượng khóa học theo độ khó**: Phân bố các cấp độ khóa học tập trung lớn nhất ở nhóm "Beginner", tiếp đến là "Intermediate", trong khi "Advanced" chiếm tỉ lệ nhỏ nhất.
- **Phân bố các chủ đề khóa học**: Với phần dữ liệu còn lại, "Data Science" và "Computer Science" là các nhóm chủ đề thống trị.
- **Phân bố điểm đánh giá theo mức độ khó của các khóa học**: Biểu đồ Boxplot cho thấy điểm đánh giá trung vị giữa các nhóm Beginner, Intermediate, và Advanced khá tương đồng và đều duy trì ở mức rất cao.
- **Heatmap tương quan**: Heatmap tương quan hạng Spearman cho thấy mối tương quan đồng biến mạnh giữa `enrolled_num` (số học viên) và `num_reviews` (số lượt đánh giá).
- **Top 10 tổ chức có nhiều khóa học nhất**: Liệt kê các tổ chức các trường Đại học / tập đoàn công nghệ đóng góp số lượng khóa học nhiều nhất trên nền tảng.
- **Top 10 Quốc Gia có trụ sở của nhiều tổ chức**: United States áp đảo hoàn toàn khi là Quốc Gia đặt trụ sở của phần lớn các tổ chức giáo dục cung cấp khóa học.
- **Tỷ lệ Missing value theo từng cột**: Minh họa rõ ràng tỷ lệ thiếu hụt dữ liệu ở các cột. Sau khi làm sạch placeholder, tỷ lệ missing thực tế của `Skills`, `Subject` hiện ra rất rõ.
- **Top 15 skill phổ biến nhất**: Trực quan hóa các kỹ năng xuất hiện nhiều nhất (như Machine Learning, Data Science, Python, Leadership...), được bóc tách từ các mảng kỹ năng của khóa học.

## 3. Đầu ra của mô hình
- `01_data_quality.csv`: Báo cáo chi tiết về chất lượng dữ liệu (số lượng missing, % missing, số giá trị unique và kiểu dữ liệu).
- `02_descriptive_statistics.csv`: Các chỉ số thống kê mô tả (Count, Mean, Std, Min, Max, Quartiles) cho toàn bộ các biến số học.
