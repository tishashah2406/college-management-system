# teachers/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Teacher

@receiver(post_save, sender=Teacher)
def create_teacher_user(sender, instance, created, **kwargs):
    if created and instance.user is None:
        # Create a User with the teacher's email as username
        user = User.objects.create_user(
            username=instance.email,
            password='teacher123',  # you can set a default password
            first_name=instance.name
        )
        # Assign to Teacher group
        teacher_group, _ = Group.objects.get_or_create(name='Teacher')
        user.groups.add(teacher_group)
        instance.user = user
        instance.save()