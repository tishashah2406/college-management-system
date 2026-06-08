from datetime import date, timedelta
from .models import Holiday

def calculate_teacher_salary(teacher):
    base_salary = float(teacher.salary)

    today = date.today()

    # Current month
    start_month = date(today.year, today.month, 1)

    if today.month == 12:
        end_month = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end_month = date(today.year, today.month + 1, 1) - timedelta(days=1)

    total_days = (end_month - start_month).days + 1

    # Sundays
    sunday_count = 0
    current = start_month

    while current <= end_month:
        if current.weekday() == 6:  # Sunday
            sunday_count += 1
        current += timedelta(days=1)

    # Public Holidays
    public_holidays = Holiday.objects.filter(
        date__range=[start_month, end_month]
    ).count()

    # Approved Leaves
    leaves = teacher.teacherleave_set.filter(status='Approved')

    total_leave_days = 0

    for leave in leaves:
        total_leave_days += (
            leave.end_date - leave.start_date
        ).days + 1

    allowed_paid_leaves = 3

    paid_leave_days = min(
        total_leave_days,
        allowed_paid_leaves
    )

    unpaid_leave_days = max(
        0,
        total_leave_days - allowed_paid_leaves
    )

    # Working days
    working_days = total_days - sunday_count - public_holidays

    per_day_salary = (
        base_salary / working_days
        if working_days > 0 else 0
    )

    deduction = unpaid_leave_days * per_day_salary

    final_salary = base_salary - deduction

    return {
        "base_salary": round(base_salary, 2),

        "total_days": total_days,
        "working_days": working_days,

        "sundays": sunday_count,
        "public_holidays": public_holidays,

        "total_leave_days": total_leave_days,
        "paid_leave_days": paid_leave_days,
        "unpaid_leave_days": unpaid_leave_days,

        "deduction": round(deduction, 2),
        "final_salary": round(final_salary, 2),
    }