# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Group E402
- Repository URL: https://github.com/NguyenVanHung1707/K4-Day13-E402-HHQDA.git
- Commit SHA cuối: e8d8346
- Thành viên và vai trò:
  1. Nguyễn Văn Hưng - 2A202601284 (Role E: QA & Chief Investigator - Trưởng Nhóm)
  2. Thành viên A (Role A: API & Middleware Engineer)
  3. Thành viên B (Role B: Security & Data Protection Engineer)
  4. Thành viên C (Role C: Metrics & Dashboard Specialist)
  5. Thành viên D (Role D: SRE & Alerts Engineer)

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (Baseline CP0)
- Tổng số traces: 10
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall: submission/evidence/traces_list.png
- Giải thích một span đáng chú ý: Span `retrieve` (tại app/mock_rag.py) thực hiện truy xuất domain documents từ CORPUS và span `generate` (tại app/mock_llm.py) thực hiện sinh câu trả lời với mô hình LLM.

## 4. Prompt versioning

- Prompt name: day13-chat
- Version/label baseline: v1 (production, baseline)
- Version/label candidate: v2 (candidate)
- Trace ID của mỗi version: Danh sách traces chi tiết tại submission/evidence/traces_list.png
- Bằng chứng đổi label hoặc rollback: submission/evidence/prompt_rollback.png (Chi tiết versions tại submission/evidence/prompt_versions.png)

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`:
- Evidence dashboard:
- SLO đã chọn và lý do:
- Alert rules và runbook:

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
| --- | --- | --- | --- |
| Nguyễn Văn Hưng (Role E - 2A202601284) | CP0: Khởi tạo môi trường, Langfuse Cloud setup, chạy baseline load test & log validation (100/100). CP2: Tích hợp @observe decorator cho sub-components RAG/LLM, tạo Prompt Versioning day13-chat (v1/v2, baseline/candidate/production), thử nghiệm Rollback và lưu đủ 3 ảnh evidence | https://github.com/NguyenVanHung1707/K4-Day13-E402-HHQDA/commit/d9381e2 | Cách cấu hình Langfuse Tracing, bọc spans sub-components, quản lý Prompt Versioning và quy trình Rollback prompt |


