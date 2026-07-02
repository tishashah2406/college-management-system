from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db import transaction

from students.models import Student
from teachers.models import Teacher
from notifications.models import Notification


# ================= BASE AUTH MIXIN =================
class AuthMixin:

    def redirect_user(self, request, user):

        if user.is_superuser:
            return redirect('admin:index')

        if user.groups.filter(name='Teacher').exists():
            return redirect('teacher_dashboard')

        if user.groups.filter(name='Student').exists():
            return redirect('student_dashboard')

        return redirect('home')


# ================= LOGIN VIEW =================
class LoginView(AuthMixin, View):

    template_name = 'registration/login.html'

    def get(self, request):

        if request.user.is_authenticated:
            return self.redirect_user(
                request,
                request.user
            )

        return render(
            request,
            self.template_name
        )

    def post(self, request):

        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:

            messages.error(
                request,
                "All fields are required"
            )

            return render(
                request,
                self.template_name
            )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:

            messages.error(
                request,
                "Invalid username or password"
            )

            return render(
                request,
                self.template_name
            )

        # Teacher Approval Check
        if user.groups.filter(name="Teacher").exists():

            teacher = Teacher.objects.get(
                user=user
            )

            if not teacher.is_approved:

                messages.error(
                    request,
                    "Your teacher account is waiting for administrator approval."
                )

                return render(
                    request,
                    self.template_name
                )

        login(request, user)

        return self.redirect_user(
            request,
            user
        )


# ================= REGISTER VIEW =================
class RegisterView(AuthMixin, View):

    template_name = 'registration/register.html'

    def get(self, request):

        if request.user.is_authenticated:
            return self.redirect_user(
                request,
                request.user
            )

        return render(
            request,
            self.template_name
        )

    def post(self, request):

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        age = request.POST.get("age")
        user_type = request.POST.get("user_type")
        salary = request.POST.get("salary")

        # Validation
        if not username or not email or not password or not user_type:

            messages.error(
                request,
                "Please fill all required fields"
            )

            return render(
                request,
                self.template_name
            )

        if len(password) < 6:

            messages.error(
                request,
                "Password must be at least 6 characters"
            )

            return render(
                request,
                self.template_name
            )

        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "Username already exists"
            )

            return render(
                request,
                self.template_name
            )

        if User.objects.filter(email=email).exists():

            messages.error(
                request,
                "Email already exists"
            )

            return render(
                request,
                self.template_name
            )

        try:
            age = int(age) if age else 0

        except ValueError:

            messages.error(
                request,
                "Age must be a number"
            )

            return render(
                request,
                self.template_name
            )

        try:
            salary = float(salary) if salary else 0

        except ValueError:

            messages.error(
                request,
                "Salary must be a number"
            )

            return render(
                request,
                self.template_name
            )

        try:

            with transaction.atomic():

                # Create User
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                # ================= STUDENT =================
                if user_type == "student":

                    group, created = Group.objects.get_or_create(
                        name="Student"
                    )

                    user.groups.add(group)

                    Student.objects.create(
                        user=user,
                        name=username,
                        email=email,
                        age=age
                    )

                    Notification.objects.create(
                        user=user,
                        message="Welcome to College Management System"
                    )

                    admins = User.objects.filter(
                        is_superuser=True
                    )

                    for admin in admins:

                        Notification.objects.create(
                            user=admin,
                            message=f"New student joined: {username}"
                        )

                # ================= TEACHER =================
                elif user_type == "teacher":

                    group, created = Group.objects.get_or_create(
                        name="Teacher"
                    )

                    user.groups.add(group)

                    Teacher.objects.create(
                        user=user,
                        name=username,
                        email=email,
                        salary=salary,
                        is_approved=False
                    )

                    admins = User.objects.filter(
                        is_superuser=True
                    )

                    for admin in admins:

                        Notification.objects.create(
                            user=admin,
                            message=f"New teacher registration: {username}"
                        )

                    Notification.objects.create(
                        user=user,
                        message="Your account has been created and is waiting for admin approval."
                    )

                                    # ================= INVALID ROLE =================
                else:

                    messages.error(
                        request,
                        "Invalid user type"
                    )

                    return render(
                        request,
                        self.template_name
                    )

                # ================= ADMIN NOTIFICATION =================
                admins = User.objects.filter(
                    is_superuser=True
                )

                for admin in admins:

                    Notification.objects.create(
                        user=admin,
                        message=f"New {user_type}: {username}"
                    )

        except Exception as e:

            print(e)

            messages.error(
                request,
                "Something went wrong"
            )

            return render(
                request,
                self.template_name
            )

        # ================= REDIRECT AFTER REGISTRATION =================

        # Teacher should NOT login until approved
        if user_type == "teacher":

            messages.success(
                request,
                "Teacher account created successfully. Please wait for administrator approval."
            )

            return redirect("login")

        # Student logs in immediately
        login(
            request,
            user
        )

        messages.success(
            request,
            "Account created successfully"
        )

        return self.redirect_user(
            request,
            user
        )