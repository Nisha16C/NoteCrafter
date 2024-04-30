from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required 
from .models import Signup, Notes


# Create your views here.

def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')

def register(request):
    error = ""
    if request.method == 'POST':
        fn = request.POST.get('firstName')
        ln = request.POST.get('lastName')
        e = request.POST.get('email')
        p = request.POST.get('password')
        c = request.POST.get('ContactNo')
        ab = request.POST.get('About')
        role = "ROLE_USER"

        try:
            # Create a new user
            user = User.objects.create_user(username=e, password=p, first_name=fn, last_name=ln)
            # Create a corresponding Signup object
            Signup.objects.create(user=user, ContactNo=c, About=ab, Role=role)
            # If successful, set error flag to "no"
            error = "no"
        except:
            # If an error occurs during user creation, set error flag to "yes"
            error = "yes"

    # Redirect to user_login page if registration is successful
    if error == "no":
        return redirect('user_login')

    # Render the registration page with the error flag
    return render(request, 'register.html', {'error': error, 'success_message': "Registration Successfully."})
# user_login view
def user_login(request):
    error = ""
    success_message = ""
    if request.method == 'POST':
        u = request.POST.get('email')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            success_message = "You Login Successfully"
            # Update user's profile if it exists
            update_profile(user)
            return redirect('dashboard')  # Assuming you have a URL pattern named 'dashboard'
        else:
            error = "Invalid Credential, Try Again"
    return render(request, 'user_login.html', {'error': error, 'success_message': success_message})

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    
    user = request.user
    signup, created = Signup.objects.get_or_create(user=user)
    totalnotes = Notes.objects.filter(signup=signup).count()
    first_name = user.first_name
    last_name = user.last_name

    return render(request, 'dashboard.html', {'first_name': first_name, 'last_name': last_name, 'totalnotes': totalnotes})

# Update user's profile
def update_profile(user):
    signup, created = Signup.objects.get_or_create(user=user)
    # Update the 'About' and 'ContactNo' fields if they are empty
    if not signup.About:
        signup.About = ""  # Set a default value if 'About' field is empty
    if not signup.ContactNo:
        signup.ContactNo = ""  # Set a default value if 'ContactNo' field is empty
    signup.save()

@login_required
def profile(request):
    user = request.user
    signup, created = Signup.objects.get_or_create(user=user)
    error = ""
    success_message = ""  # Initialize success_message variable

    if request.method == "POST":
        fname = request.POST.get('firstName')
        lname = request.POST.get('lastName')
        contactNo = request.POST.get('ContactNo')
        about = request.POST.get('About')

        # Update user's first name and last name
        user.first_name = fname
        user.last_name = lname

        # Update Signup object fields
        signup.ContactNo = contactNo
        signup.About = about

        try:
            user.save()  # Save user object
            signup.save()  # Save Signup object
            success_message = "Profile has been updated."
        except:
            error = "yes"

    # Pass user and signup objects to the template
    return render(request, 'profile.html', {'user': user, 'signup': signup, 'error': error, 'success_message': success_message})

@login_required
def addNotes(request):
    user = User.objects.get(id=request.user.id)
    signup = Signup.objects.get(user=user)
    error = ""
    success_message = None  # Define success_message with a default value of None

    # Check if the request method is POST
    if request.method == "POST":
        # Get the title and content of the note from the POST data
        title = request.POST.get('Title')
        content = request.POST.get('Content')

        try:
            # Attempt to create a new note object
            Notes.objects.create(signup=signup, Title=title, Content=content)
            # If successful, set the success message
            success_message = "New Notes Added Successfully."
        except:
            # If an error occurs, set the error flag
            error = "yes"

    # Render the addNotes.html template with the necessary variables
    return render(request, 'addNotes.html', {'error': error, 'success_message': success_message})

def viewNotes(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    user = User.objects.get(id=request.user.id)
    signup = Signup.objects.get(user=user)
    notes = Notes.objects.filter(signup=signup)
    return render(request, 'viewNotes.html', locals())

@login_required
def editNotes(request, pid):
    if not request.user.is_authenticated:
        return redirect('user_login')

    notes = Notes.objects.get(id=pid)
    error = ""  # Initialize error variable

    if request.method == "POST":
        title = request.POST.get('Title')
        content = request.POST.get('Content')

        notes.Title = title
        notes.Content = content

        try:
            notes.save()
            error = "no"  # Set error to "no" if update is successful
        except:
            error = "yes"  # Set error to "yes" if an exception occurs

    return render(request, 'editNotes.html', {'notes': notes, 'error': error})

def deleteNotes(request,pid):
    if not request.user.is_authenticated:
        return redirect('user_login')
    notes = Notes.objects.get(id=pid)
    notes.delete()
    return redirect('viewNotes')

def changePassword(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    error = ""
    user = request.user
    if request.method == "POST":
        o = request.POST['oldpassword']
        n = request.POST['newpassword']
        try:
            u = User.objects.get(id=request.user.id)
            if user.check_password(o):
                u.set_password(n)
                u.save()
                error = "no"
            else:
                error = 'not'
        except:
            error = "yes"
    return render(request, 'changePassword.html', locals())

def Logout(request):
    logout(request)
    return redirect('index')
