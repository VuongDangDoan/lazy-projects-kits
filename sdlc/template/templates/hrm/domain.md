# HRM Domain Knowledge Template
> [TEMPLATE — split into per-module L1-domain files during /quickstart]
> Each "## Module:" section becomes knowledge/L1-domain/[slug]-domain.md
> BA Agent refines §3 Business Rules based on actual requirements.

---

## Module: employee
> Slug: employee | Status: Planned (from template)

### 1. Overview
Quản lý toàn bộ thông tin hồ sơ nhân viên trong tổ chức.

### 2. Entities

**Employee**
- id, employeeCode (unique, generated), fullName, email (unique), phone
- dateOfBirth, gender, nationalId, address
- joinDate, probationEndDate, terminationDate (nullable)
- status: ACTIVE | PROBATION | ON_LEAVE | TERMINATED
- departmentId (FK → Department), positionId (FK → Position)
- managerId (FK → Employee, nullable — CEO has no manager)
- userId (FK → User — the auth account linked to this employee)
- avatarUrl, contractType: FULLTIME | PARTTIME | CONTRACT

**Department**
- id, name, code (unique), parentId (nullable — for nested org chart)
- managerId (FK → Employee)

**Position**
- id, name, level: INTERN | JUNIOR | MID | SENIOR | LEAD | MANAGER | DIRECTOR | C_LEVEL
- departmentId (FK → Department)

### 3. Business Rules
- BR-EMP-001: employeeCode auto-generated as EMP-YYYY-NNN (year + sequence, e.g. EMP-2026-001)
- BR-EMP-002: Email must be unique across all employees (including terminated)
- BR-EMP-003: Terminated employees are soft-deleted (terminationDate set) — data retained for audit
- BR-EMP-004: An employee can only belong to one department at a time
- BR-EMP-005: Manager must belong to the same or parent department
- BR-EMP-006: Employee can only view their own profile; HR Manager and Admin can view all

### 4. RBAC
| Action | admin | hr_manager | manager | employee |
|---|---|---|---|---|
| View any employee | ✅ | ✅ | Team only | Self only |
| Create employee | ✅ | ✅ | ❌ | ❌ |
| Edit employee | ✅ | ✅ | ❌ | Self (limited fields) |
| Terminate employee | ✅ | ✅ | ❌ | ❌ |
| View org chart | ✅ | ✅ | ✅ | ✅ |

### 5. Events
- `employee.created` → triggers: onboarding checklist, account creation
- `employee.terminated` → triggers: access revocation, payroll cut-off

---

## Module: attendance
> Slug: attendance | Status: Planned (from template)

### 1. Overview
Theo dõi giờ làm việc hàng ngày của nhân viên.

### 2. Entities

**AttendanceRecord**
- id, employeeId (FK), date, checkInTime, checkOutTime (nullable)
- status: PRESENT | ABSENT | LATE | HALF_DAY | HOLIDAY | ON_LEAVE
- workingHours (computed: checkOut - checkIn), overtimeHours
- notes, source: MANUAL | SYSTEM

**WorkSchedule**
- id, name, startTime, endTime, workDays (array of weekday numbers)
- lateThresholdMinutes (default: 15)

### 3. Business Rules
- BR-ATT-001: Only one AttendanceRecord per employee per date
- BR-ATT-002: LATE status if checkInTime > (schedule.startTime + lateThresholdMinutes)
- BR-ATT-003: Overtime = workingHours > 8h on regular days, any hours on weekends
- BR-ATT-004: HR Manager can edit attendance records with mandatory notes
- BR-ATT-005: Employee can only view their own attendance; managers can view team

### 4. RBAC
| Action | admin | hr_manager | manager | employee |
|---|---|---|---|---|
| Check in/out | ✅ (any) | ✅ (any) | ✅ (self) | ✅ (self) |
| Edit record | ✅ | ✅ | ❌ | ❌ |
| View all records | ✅ | ✅ | Team only | Self only |
| Generate report | ✅ | ✅ | Team only | Self only |

---

## Module: leave
> Slug: leave | Status: Planned (from template)

### 1. Overview
Quản lý đơn nghỉ phép và theo dõi số ngày phép còn lại của từng nhân viên.

### 2. Entities

**LeaveRequest**
- id, employeeId (FK), type: ANNUAL | SICK | MATERNITY | PATERNITY | UNPAID | OTHER
- startDate, endDate, totalDays (computed)
- reason, status: PENDING | APPROVED | REJECTED | CANCELLED
- approverId (FK → Employee), approvedAt, approverNote
- createdAt

**LeaveBalance**
- id, employeeId (FK), year, leaveType
- totalDays, usedDays, remainingDays (computed)

### 3. Business Rules
- BR-LVE-001: Annual leave accrues monthly (totalDays / 12 per month worked)
- BR-LVE-002: Cannot request leave exceeding remainingDays (except UNPAID type)
- BR-LVE-003: Sick leave requires medical certificate if > 2 consecutive days
- BR-LVE-004: Direct manager approves leave; HR Manager can override
- BR-LVE-005: Leave cannot overlap with another approved leave for the same employee
- BR-LVE-006: Employee can cancel PENDING leave; cannot cancel APPROVED leave (must ask manager)
- BR-LVE-007: Minimum notice: 1 day for sick, 3 days for annual, 30 days for maternity

### 4. RBAC
| Action | admin | hr_manager | manager | employee |
|---|---|---|---|---|
| Submit leave request | ✅ | ✅ | ✅ | ✅ |
| Approve/reject | ✅ | ✅ | Team only | ❌ |
| View all requests | ✅ | ✅ | Team only | Self only |
| Adjust balance | ✅ | ✅ | ❌ | ❌ |

---

## Module: payroll
> Slug: payroll | Status: Planned (from template)

### 1. Overview
Tính toán và quản lý bảng lương hàng tháng.

### 2. Entities

**PayrollRecord**
- id, employeeId (FK), month (YYYY-MM), status: DRAFT | CONFIRMED | PAID
- baseSalary, allowances (JSON: [{name, amount}]), deductions (JSON)
- overtimePay, leaveDeduction, taxAmount, insuranceAmount
- grossSalary (computed), netSalary (computed)
- confirmedAt, paidAt, confirmedById

**SalaryConfig** (per employee)
- id, employeeId (FK), baseSalary, effectiveDate
- allowances (JSON), taxMethod: PROGRESSIVE | FLAT

### 3. Business Rules
- BR-PAY-001: Payroll generated monthly — HR creates DRAFT, reviews, then CONFIRMED
- BR-PAY-002: Only ADMIN and HR_MANAGER can view payroll records
- BR-PAY-003: Employee can only view their own payslip (read-only, no salary amounts of others)
- BR-PAY-004: CONFIRMED payroll cannot be edited — must create an adjustment record
- BR-PAY-005: Net salary = grossSalary - taxAmount - insuranceAmount - leaveDeduction
- BR-PAY-006: Overtime pay = overtimeHours × (baseSalary / 26 / 8) × overtimeRate (1.5x weekdays, 2x weekends)

### 4. RBAC
| Action | admin | hr_manager | manager | employee |
|---|---|---|---|---|
| Generate payroll | ✅ | ✅ | ❌ | ❌ |
| View any payroll | ✅ | ✅ | ❌ | Self only |
| Confirm payroll | ✅ | ✅ | ❌ | ❌ |
| Export payslip | ✅ | ✅ | ❌ | Self only |

### 5. Sensitivity note
Salary data is highly sensitive. Row-level security is mandatory:
- Employee queries must always filter `WHERE employeeId = session.user.employeeId`
- Middleware must verify role before any payroll endpoint
- Never expose salary fields in list responses — only in detail view with explicit permission check
