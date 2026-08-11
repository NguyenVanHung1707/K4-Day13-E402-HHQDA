# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Group E402
- Repository URL: https://github.com/NguyenVanHung1707/K4-Day13-E402-HHQDA.git
- Commit SHA cuối: 03000d5
- Thành viên và vai trò:
  1. Nguyễn Văn Hưng - 2A202601284 (Role E: QA & Chief Investigator - Trưởng Nhóm)
  2. Phạm Tuấn Anh - 2A202601060 (Role A: API & Middleware Engineer)
  3. Phạm Công Đăng - 2A202601280 (Role B: Security & Data Protection Engineer)
  4. Đặng Minh Quang - 2A202601368 (Role C: Metrics & Dashboard Specialist)
  5. Nhữ Văn Hùng - 2A202601372 (Role D: SRE & Alerts Engineer)

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (Baseline CP0 & CP1)
- Tổng số traces: 10
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: submission/evidence/dashboard_runtime.png

## 3. Logging và tracing

- Evidence correlation ID: submission/evidence/challenge_log_lines_1.png
- Evidence PII redaction: submission/evidence/pii_redacted_sample.json
- Evidence trace waterfall: submission/evidence/traces_list.png
- Giải thích một span đáng chú ý: Span `retrieve` (tại app/mock_rag.py) thực hiện truy xuất domain documents từ CORPUS và span `generate` (tại app/mock_llm.py) thực hiện sinh câu trả lời với mô hình LLM.

## 4. Prompt versioning

- Prompt name: day13-chat
- Version/label baseline: v1 (production, baseline)
- Version/label candidate: v2 (candidate)
- Trace ID của mỗi version: Danh sách traces chi tiết tại submission/evidence/traces_list.png
- Bằng chứng đổi label hoặc rollback: submission/evidence/prompt_rollback.png (Chi tiết versions tại submission/evidence/prompt_versions.png)

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ 6/6 panel
- Evidence dashboard: submission/evidence/dashboard_runtime.png
- SLO đã chọn và lý do:
  - `latency_p95_ms` (Objective: 3000ms, Target: 99.5%): Đảm bảo trải nghiệm phản hồi mượt mà cho người dùng cuối khi truy vấn hệ thống RAG/LLM.
  - `error_rate_pct` (Objective: 2%, Target: 99.0%): Kiểm soát độ tin cậy của API, đảm bảo tỷ lệ lỗi hệ thống luôn dưới 2%.
  - `daily_cost_usd` (Objective: $2.5, Target: 100.0%): Quản lý chi phí sử dụng API token LLM trong phạm vi ngân sách cho phép.
  - `quality_score_avg` (Objective: 0.75, Target: 95.0%): Đảm bảo chất lượng câu trả lời từ mô hình AI đạt mức chấp nhận được.
- Alert rules và runbook:
  - File cấu hình Alert Rules: `config/alert_rules.yaml` gồm 3 quy tắc cảnh báo symptom-based: `HighLatencyP95` (Latency P95 > 3000ms trong 5m), `HighErrorRate` (Error Rate > 2% trong 3m), `CostSpike` (Chi phí trung bình tăng 3x trong 5m).
  - File Alert Runbook: `docs/alerts.md` định nghĩa đầy đủ quy trình 3 bước kiểm tra (Metrics -> Traces -> Logs) và giải pháp khắc phục tạm thời (Mitigation) cho từng alert.

## 6. Điều tra challenge

- Challenge ID: day13-k4-observability-v1
- Triệu chứng từ metrics: Latency P95 nhảy vọt từ 152ms lên 2727ms (tăng 17.94x), vượt ngưỡng challenge 2000ms. Tập trung suy giảm độ trễ trên feature `monitoring`. Error rate giữ ở mức 0%, chi phí Cost/request chỉ tăng nhẹ 1.24x (không phải cost spike).
- Trace ID liên quan: `9a7ce47e9560704246d6cf494d47d358`, `c42e934ee86c4e541361953f2ec0fe24`, `3b462f5f8f9493ceef599cfbfba29eae` (Minh chứng chi tiết trong file `submission/evidence/challenge_events_export.csv`).
- Log line/correlation ID liên quan: `req-605c3c30` (log event `response_sent` có `latency_ms: 2650`, `feature: monitoring`, `session_id: k4-challenge-s05`, `user_id_hash: 0c04335fe098`).
  - **Chi tiết kết quả tra cứu Log (Do Role A & B thực hiện):**
    - **Lệnh đã chạy:** `grep -E "req-605c3c30|req-4649b1ae|req-ec5cf821|req-a0fca28f|req-ed27d22f" data/logs.jsonl`
    - **Dữ liệu log thô (Raw JSON):**
      ```json
      {"service": "api", "payload": {"message_preview": "Describe how to prove a slow span is the root cause."}, "event": "request_received", "user_id_hash": "0c04335fe098", "session_id": "k4-challenge-s05", "correlation_id": "req-605c3c30", "feature": "monitoring", "model": "claude-sonnet-4-5", "env": "dev", "level": "info"}
      {"service": "api", "latency_ms": 2650, "tokens_in": 35, "tokens_out": 105, "cost_usd": 0.00168, "quality_score": 0.8, "payload": {"answer_preview": "Starter answer. Teams should improve this output logic..."}, "event": "response_sent", "user_id_hash": "0c04335fe098", "session_id": "k4-challenge-s05", "correlation_id": "req-605c3c30", "feature": "monitoring", "model": "claude-sonnet-4-5", "env": "dev", "level": "info"}
      ```
- Root cause: Phân tích Waterfall Trace từ Langfuse cho thấy span `retrieve` (truy xuất Vector Store tại `app/mock_rag.py`) chiếm 2502ms (94.3% tổng latency request), trong khi span `generate` (sinh câu trả lời LLM tại `app/mock_llm.py`) chỉ tốn 151ms. Sự cố `rag_slow` đã chèn độ trễ nhân tạo `time.sleep(2.5)` vào luồng RAG retrieval.
- Fix Action: Tắt sự cố `rag_slow` bằng `python scripts/inject_incident.py --scenario rag_slow --disable`. Bổ sung cơ chế timeout 1.0s cho hàm `retrieve()` kèm fallback domain context để đảm bảo SLA response time < 1500ms ngay cả khi Vector Store bị nghẽn.
- Preventive Measure: Bổ sung chỉ số Metric & Alert Rule riêng cho độ trễ của sub-component Retrieval (`span_name == retrieve` > 1500ms) thay vì chỉ đo độ trễ API tổng thể; tích hợp Circuit Breaker cho module RAG để tự động chuyển sang fallback answer khi Vector Store quá tải.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
| --- | --- | --- | --- |
| Nguyễn Văn Hưng (Role E - 2A202601284) | CP0: Khởi tạo môi trường, Langfuse Cloud setup, chạy baseline load test & log validation (100/100). CP2: Tích hợp @observe decorator cho sub-components RAG/LLM, tạo Prompt Versioning day13-chat (v1/v2, baseline/candidate/production), thử nghiệm sự cố practice (rag_slow), kiểm thử Rollback và lưu đủ 3 ảnh evidence. CP3: Dẫn dắt điều tra Challenge chính thức (day13-k4-observability-v1), kích hoạt challenge load test, mở Trace Waterfall xác định span retrieve bị trễ 2502ms, kết nối Metrics -> Traces -> Logs để chẩn đoán Root Cause và đề xuất Fix/Preventive Action | https://github.com/NguyenVanHung1707/K4-Day13-E402-HHQDA/commit/d9381e2 | Quy trình điều tra incident chuẩn theo 3 lớp Metrics -> Traces -> Logs, kỹ năng phân tích Waterfall Trace để khoanh vùng slow span và kết nối Correlation ID giữa Langfuse với JSON logs |
| Phạm Công Đăng (Role B - 2A202601280) | CP0: Kiểm tra danh sách PII mẫu trong `data/sample_queries.jsonl`. CP1: Bổ sung đầy đủ 6 regex pattern PII (email, phone_vn, cccd, credit_card, passport, address_vn) trong `app/pii.py`; viết lại `scrub_event` quét đệ quy mọi trường string trong `app/logging_config.py`; phối hợp cùng Role A chạy `load_test.py` và tự chạy `validate_logs.py`, đạt 100/100 (0 PII leak, correlation ID propagation 100%). CP3: Cùng Role A grep `data/logs.jsonl` theo `correlation_id` để trích log line phục vụ điều tra root cause | https://github.com/NguyenVanHung1707/K4-Day13-E402-HHQDA/commit/d9381e2 | Cách viết processor `scrub_event` cho `structlog`, thiết kế regex PII tránh false positive/overlap, và quy trình kiểm chứng log bằng `validate_logs.py` |
| Nhữ Văn Hùng (Role D - 2A202601372) | CP2: Cấu hình mục tiêu SLO trong `config/slo.yaml` (Latency P95 <= 3000ms, Error rate <= 2%, Cost <= $2.5, Quality >= 0.75); Xây dựng 3 Alert Rules dựa trên triệu chứng người dùng (`HighLatencyP95`, `HighErrorRate`, `CostSpike`) trong `config/alert_rules.yaml`; Soạn thảo Alert Runbook chi tiết tại `docs/alerts.md`. CP3: Đối chiếu các chỉ số bất thường trên Dashboard với Alert Rules & SLO, xác nhận alert `HighLatencyP95` kích hoạt (firing) khi độ trễ P95 tăng vọt do sự cố `rag_slow`, hỗ trợ Trưởng nhóm khoanh vùng nguyên nhân sự cố | https://github.com/NguyenVanHung1707/K4-Day13-E402-HHQDA/commit/b2ea177 | Cách thiết lập SLO/SLI chuẩn cho hệ thống AI, viết Alert Rules theo nguyên tắc symptom-based và xây dựng Alert Runbook giúp đội ngũ SRE ứng cứu sự cố theo luồng Metrics -> Traces -> Logs |
| Đặng Minh Quang (Role C - 2A202601368) | CP2: Dựng Dashboard 6 panel runtime theo đúng contract kiểm định bằng `validate_dashboard.py` (hợp lệ 6/6 panel), chụp và lưu minh chứng `submission/evidence/dashboard_runtime.png`. CP3: Theo dõi chỉ số Latency P95 trên Dashboard, phát hiện độ trễ tăng từ 152ms lên 2727ms (tăng 17.94x) trên tính năng `monitoring`, bàn giao chỉ số đo đếm cho Role E và D | https://github.com/NguyenVanHung1707/K4-Day13-E402-HHQDA/commit/b4381e2 | Thiết kế Dashboard quan sát hệ thống AI, quản lý các mốc thời gian P50/P95/P99 và cách kết nối Dashboard runtime với log data sạch |
| Phạm Tuấn Anh (Role A - 2A202601060) | CP0: Khởi chạy API server và kiểm tra health check. CP1: Thiết lập `CorrelationIdMiddleware` để quản lý context và sinh `req-xxxx`; cấu hình contextvars ở route `/chat` để log tự động nhặt bối cảnh; bổ sung Global Exception Handler trả về chuẩn lỗi kèm `correlation_id`. CP3: Dùng `grep` tra cứu trong `data/logs.jsonl` dựa trên Correlation ID trích xuất từ Trace do Role E cung cấp, trích xuất raw JSON log line xác nhận Root Cause | https://github.com/NguyenVanHung1707/K4-Day13-E402-HHQDA/commit/a21a0d1 | Tầm quan trọng của Correlation ID trong việc theo vết (traceability) xuyên suốt hệ thống, và cách structlog truyền tải Context Variables bất đồng bộ |
