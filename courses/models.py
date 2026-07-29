from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    duration = models.IntegerField(help_text="Duration in months")
    fees = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.code})"
        
#  Notes 
class Note(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='notes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

#  Assignment 
class Assignment(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    course = models.ForeignKey(
    Course,
    on_delete=models.CASCADE,
    related_name="assignments"
)

    due_date = models.DateField()


    attachment = models.FileField(
        upload_to='assignments/',
        blank=True,
        null=True
    )


    def __str__(self):
        return self.title
