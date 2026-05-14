# Add Download Option in Student Notes\n\n## Steps:\n1. [ ] Edit course_notes.html to add download button next to view file.\n2. [ ] Test the download functionality.\n

from django.db.models import Avg
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Student, Submission
from courses.models import Assignment


# ================= STUDENT ANALYTICS =================
@action(
    detail=False,
    methods=['get'],
    permission_classes=[IsAuthenticated]
)
def student_analytics(self, request):

    student = Student.objects.filter(
        user=request.user
    ).first()

    if not student:
        return Response(
            {"error": "Student not found"},
            status=404
        )

    courses_data = []

    total_assignments_all = 0
    total_completed_all = 0
    total_pending_all = 0
    total_late_submissions = 0

    # ================= COURSE LOOP =================
    for course in student.courses.all():

        # total assignments
        total_assignments = Assignment.objects.filter(
            course=course
        ).count()

        # completed assignments
        completed_assignments = Submission.objects.filter(
            student=student,
            assignment__course=course
        ).count()

        # pending assignments
        pending_assignments = (
            total_assignments - completed_assignments
        )

        # progress percentage
        progress = 0

        if total_assignments > 0:
            progress = (
                completed_assignments / total_assignments
            ) * 100

        # course completed status
        is_completed = progress == 100

        # late submissions
        late_submissions = 0

        submissions = Submission.objects.filter(
            student=student,
            assignment__course=course
        )

        for submission in submissions:

            if (
                submission.assignment.due_date and
                submission.submitted_at.date() >
                submission.assignment.due_date
            ):
                late_submissions += 1

        total_late_submissions += late_submissions

        # pending assignment list
        submitted_assignment_ids = submissions.values_list(
            "assignment_id",
            flat=True
        )

        pending_assignment_list = Assignment.objects.filter(
            course=course
        ).exclude(
            id__in=submitted_assignment_ids
        )

        pending_assignment_names = [
            assignment.title
            for assignment in pending_assignment_list
        ]

        # add totals
        total_assignments_all += total_assignments
        total_completed_all += completed_assignments
        total_pending_all += pending_assignments

        # add course data
        courses_data.append({

            "course_id": course.id,

            "course_name": course.name,

            "total_assignments":
                total_assignments,

            "completed_assignments":
                completed_assignments,

            "pending_assignments":
                pending_assignments,

            "pending_assignment_list":
                pending_assignment_names,

            "late_submission_count":
                late_submissions,

            "progress_percentage":
                round(progress, 2),

            "is_completed":
                is_completed
        })

    # ================= OVERALL PROGRESS =================
    overall_progress = 0

    if total_assignments_all > 0:
        overall_progress = (
            total_completed_all / total_assignments_all
        ) * 100

    # ================= LEADERBOARD =================
    leaderboard = []

    students = Student.objects.all()

    for s in students:

        total_assignments = Assignment.objects.filter(
            course__in=s.courses.all()
        ).count()

        completed_assignments = Submission.objects.filter(
            student=s
        ).count()

        progress = 0

        if total_assignments > 0:
            progress = (
                completed_assignments / total_assignments
            ) * 100

        # average grade
        avg_grade = Submission.objects.filter(
            student=s
        ).aggregate(
            Avg("grade")
        )["grade__avg"] or 0

        # final score
        final_score = (
            progress * 0.7
        ) + (
            avg_grade * 0.3
        )

        leaderboard.append({

            "student_id": s.id,

            "student_name":
                s.user.username,

            "progress":
                round(progress, 2),

            "average_grade":
                round(avg_grade, 2),

            "score":
                round(final_score, 2)
        })

    # sort leaderboard
    leaderboard = sorted(
        leaderboard,
        key=lambda x: x["score"],
        reverse=True
    )

    # rank
    student_rank = None

    for index, item in enumerate(leaderboard, start=1):

        if item["student_id"] == student.id:
            student_rank = index
            break

    # ================= DASHBOARD CARDS =================
    dashboard_cards = {

        "total_courses":
            student.courses.count(),

        "total_assignments":
            total_assignments_all,

        "completed_assignments":
            total_completed_all,

        "pending_assignments":
            total_pending_all,

        "late_submissions":
            total_late_submissions,

        "overall_progress":
            round(overall_progress, 2)
    }

    # ================= FINAL RESPONSE =================
    return Response({

        "student_name":
            student.user.username,

        "student_rank":
            student_rank,

        "dashboard_cards":
            dashboard_cards,

        "courses":
            courses_data,

        "leaderboard":
            leaderboard[:10]
    })