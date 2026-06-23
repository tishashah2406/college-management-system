from django.shortcuts import render


from .models import Contact

def contact(request):

    success = False

    if request.method == "POST":

        name = request.POST.get("name")

        email = request.POST.get("email")

        subject = request.POST.get("subject")

        message = request.POST.get("message")

        Contact.objects.create(

            name=name,
            email=email,
            subject=subject,
            message=message
        )

        success = True

    return render(

        request,
        
        'contact.html',

        {
            'success': success
        }
    )


def admin_complaints(request):


    complaints = complaints.objects.filter(
        assigned_admin=request.user
    )


    return render(
        request,
        "admin/complaints.html",
        {
        "complaints":complaints
        }
    )
