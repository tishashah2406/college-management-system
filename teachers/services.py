from datetime import date

def calculate_teacher_salary(teacher):
    base_salary = float(teacher.salary)

    today = date.today()

    leaves = teacher.teacherleave_set.filter(
        status='Approved'
    )

    total_leave_days = 0

    for leave in leaves:
        total_leave_days += (
            leave.end_date - leave.start_date
        ).days + 1

    allowed_paid_leaves = 10

    paid_leave_days = min(
        total_leave_days,
        allowed_paid_leaves
    )

    unpaid_leave_days = max(
        0,
        total_leave_days - allowed_paid_leaves
    )

    per_day_salary = base_salary / 30

    deduction = unpaid_leave_days * per_day_salary

    final_salary = base_salary - deduction

    return {
        "base_salary": round(base_salary, 2),
        "total_leave_days": total_leave_days,
        "paid_leave_days": paid_leave_days,
        "unpaid_leave_days": unpaid_leave_days,
        "deduction": round(deduction, 2),
        "final_salary": round(final_salary, 2),
    }