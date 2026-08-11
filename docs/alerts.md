# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1: HighLatencyP95

- **Tên**: HighLatencyP95
- **Severity**: Warning
- **SLI/SLO liên quan**: Latency P95 <= 3000ms (Mục tiêu 99.5%)
- **Điều kiện và thời gian duy trì**: P95 Latency vượt quá 3000ms liên tục trong 5 phút.
- **Ảnh hưởng tới người dùng**: Người dùng gặp hiện tượng phản hồi chậm khi gửi câu hỏi chat/RAG, giao diện xoay vòng chờ đợi lâu.
- **Ba bước kiểm tra đầu tiên**:
  1. Kiểm tra Dashboard Latency (P50, P95, P99) để xác định chính xác thời điểm độ trễ tăng vọt.
  2. Mở Langfuse Console, lọc các Traces có `duration > 3000ms` và xem Waterfall view để khoanh vùng span chậm (`retrieve` ở Mock RAG hay `generate` ở Mock LLM).
  3. Trích xuất `correlation_id` từ Trace bị chậm, dùng `grep` kiểm tra log tương ứng trong `data/logs.jsonl` để xem có lỗi timeout hoặc nghẽn kết nối không.
- **Mitigation tạm thời**:
  - Tạm thời giảm tham số `top_k` của bước Retrieval hoặc tăng timeout threshold.
  - Bật caching kết quả tra cứu đối với các câu hỏi phổ biến.
- **Owner**: SRE & Alerts Engineer

## Alert 2: HighErrorRate

- **Tên**: HighErrorRate
- **Severity**: Critical
- **SLI/SLO liên quan**: Error Rate <= 2% (Mục tiêu 99.0%)
- **Điều kiện và thời gian duy trì**: Tỷ lệ lỗi (Error Rate) vượt quá 2% liên tục trong 3 phút.
- **Ảnh hưởng tới người dùng**: Người dùng bị từ chối phục vụ, nhận lỗi 500 Internal Server Error hoặc thông báo request thất bại.
- **Ba bước kiểm tra đầu tiên**:
  1. Kiểm tra Dashboard Error Breakdown để xác định loại lỗi chính (`error_type` như Exception, Timeout, Model Error...).
  2. Tra cứu các log `request_failed` trong `data/logs.jsonl` bằng lệnh `grep '"event":"request_failed"' data/logs.jsonl` để xem stacktrace lỗi chi tiết.
  3. Kiểm tra trạng thái hoạt động của các service phụ thuộc (Langfuse Cloud, LLM Provider, Database).
- **Mitigation tạm thời**:
  - Kích hoạt cơ chế Fallback (trả về thông báo mặc định thân thiện thay vì ném 500 error).
  - Thao tác Rollback ứng dụng hoặc Prompt Version về phiên bản ổn định gần nhất nếu sự cố xảy ra sau khi deploy.
- **Owner**: SRE & Alerts Engineer

## Alert 3: CostSpike

- **Tên**: CostSpike
- **Severity**: Warning
- **SLI/SLO liên quan**: Chi phí hàng ngày (Daily Cost) <= $2.5 (Mục tiêu 100%)
- **Điều kiện và thời gian duy trì**: Chi phí trung bình mỗi request tăng gấp 3 lần so với baseline liên tục trong 5 phút.
- **Ảnh hưởng tới người dùng**: Không ảnh hưởng trực tiếp tới trải nghiệm người dùng ngay lập tức, nhưng có nguy cơ làm cạn kiệt ngân sách API quota dẫn đến gián đoạn dịch vụ toàn hệ thống.
- **Ba bước kiểm tra đầu tiên**:
  1. Kiểm tra Dashboard Token & Cost panel để xem lượng `tokens_in` và `tokens_out` có tăng đột biến không.
  2. Mở Langfuse Console kiểm tra xem prompt version hoặc feature nào đang tiêu tốn nhiều token nhất (ví dụ Prompt bị phình to hoặc bị lặp lại).
  3. Tra cứu log trong `data/logs.jsonl` nhóm theo `model` và `feature` để phát hiện các request hoặc user_id có lượng token bất thường.
- **Mitigation tạm thời**:
  - Áp dụng Rate Limiting hoặc hạ `max_tokens` cho câu trả lời LLM.
  - Rollback Prompt về phiên bản gọn hơn (baseline) nếu phiên bản candidate bị quá dài.
- **Owner**: SRE & Alerts Engineer

