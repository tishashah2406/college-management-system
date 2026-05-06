from datetime import timedelta

def calculate_teacher_salary(teacher):
    base_salary = teacher.salary

    # assume 30 working days in a month
    working_days = 30
    per_day_salary = base_salary / working_days

    leaves = teacher.teacherleave_set.filter(status="Approved")

    total_leave_days = 0

    for leave in leaves:
        days = (leave.end_date - leave.start_date).days + 1
        total_leave_days += days

    deduction = total_leave_days * per_day_salary
    final_salary = base_salary - deduction

    return {
        "base_salary": base_salary,
        "total_leave_days": total_leave_days,
        "deduction": deduction,
        "final_salary": final_salary
    }