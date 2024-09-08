from django.shortcuts import render
from app.models import Accountuser, Records, Feedback
from BOB_bank import settings
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.cache import cache_control
from django.contrib import messages
from django.core.mail import send_mail
# Create your views here.

def home(request):
    return render(request, 'home.html', )

def register(request):
    if request.method=='POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        date = request.POST['date']
        aadhar = request.POST['aadhar']
        mobile = request.POST['mobile']
        acc_type = request.POST['type']
        gen = request.POST['gender']
        deposite = request.POST['deposite']
        password = request.POST['password']

        if fname=='':
            messages.error(request, 'First name field cannot be empty')
            return HttpResponseRedirect('/register')
        elif lname=='':
            messages.error(request, 'Last name field cannot be empty')
            return HttpResponseRedirect('/register')
        elif mobile=='':
            messages.error(request, 'Phone number field cannot be empty')
            return HttpResponseRedirect('/register')
        elif email=='':
            messages.error(request, 'Email field cannot be empty')
            return HttpResponseRedirect('/register')
        elif User.objects.filter(email=email):
            messages.error(request, 'Email already used !')
            return HttpResponseRedirect('/register')
        elif date=='':
            messages.error(request, 'Date of birth field cannot be empty')
            return HttpResponseRedirect('/register')
        
        elif gen=='':
            messages.error(request, 'Gender field cannot be empty')
            return HttpResponseRedirect('/register')
        elif password=='':
            messages.error(request, 'Password field cannot be empty')
            return HttpResponseRedirect('/register')
        elif len(password) < 8:
            messages.error(request, 'Password must contain atleast 8 characters')
            return HttpResponseRedirect('/register')
        elif not any(x.islower() for x in password):
            messages.error(request, 'Password must contain atleast 1 lowercase character')
            return HttpResponseRedirect('/register')
        elif not any(x.isupper() for x in password):
            messages.error(request, 'Password must contain atleast 1 uppercase character')
            return HttpResponseRedirect('/register')
        elif not any(x.isdigit() for x in password):
            messages.error(request, 'Password must contain atleast 1 digit')
            return HttpResponseRedirect('/register')
        else:
            user = User.objects.create_user(fname, email, password)
            user.first_name = fname 
            user.last_name = lname 
            user.save()

            data = Accountuser(user=user, dob=date, aadhar_number=aadhar, phone=mobile, account_type=acc_type, gender=gen, balance=deposite)
            data.save()
            record = f'Congratulation! Account is created'
            
            messages.success(request, record)
            return render(request, 'home.html')

    return render(request, 'registration.html')




def user_login(request):
    if request.method=='POST':
        nm = request.POST.get('name')
        dt = request.POST.get('date')
        password = request.POST.get('password')

        user = authenticate(username=nm, password=password)
        if user:
            required_user = Accountuser.objects.get(user=user)
            if str(required_user.dob) == str(dt):
                messages.success(request, 'Successfully logged in.')
                login(request, user)
                return render(request, 'home.html')
            else:
                print(dt)
                messages.error(request, 'Wrong date')
                return render(request, 'home.html')
        else:
            messages.error(request, 'No user found')
            return render(request, 'registration.html')
    return render(request, 'login.html')



@cache_control(no_cache=True, must_revalidade=True, no_store=True)
@login_required(login_url='user_login')
def profile(request):
    # users_list = list(User.objects.values_list('username',flat=True))
    current = Accountuser.objects.get(user=request.user)
    return render(request, 'profile.html', {'current' : current})


@cache_control(no_cache=True, must_revalidade=True, no_store=True)
def withdrawal(request):
    if request.method=='POST':
        money = request.POST['amount']
        password = request.POST['password']

        current = Accountuser.objects.get(user=request.user)
        user = authenticate(username=current, password=password)
        if user:
            if current.balance >= int(money):
                current.balance -= int(money)
                current.save()
                data = Records(user=current, transaction='withdrawal', amount=int(money))
                data.save()
                statement = f'Dear {current}, collect the cash'
                messages.success(request, statement)
                return HttpResponseRedirect('/profile')
            else:
                statement = f'Dear {current}, you do not have enough balance to proceed this request'
                messages.info(request, statement)
                return HttpResponseRedirect('/profile')
        else:
            statement = 'Wrong password'
            messages.error(request, statement)
            return HttpResponseRedirect('/profile')
    return HttpResponseRedirect('/profile')
    

@cache_control(no_cache=True, must_revalidade=True, no_store=True)
def send(request):
    if request.method=='POST':
        money = request.POST['amount']
        receiver = request.POST['mobile']
        password = request.POST['password']

        current = Accountuser.objects.get(user=request.user)
        user = authenticate(username=current, password=password)
        receiver = Accountuser.objects.get(phone=receiver)
        print(receiver)
        if user and receiver:
            if current.balance >= int(money):
                current.balance -= int(money)
                receiver.balance += int(money)
                current.save()
                receiver.save()
                data = Records(user=current, transaction=f'sent money to {receiver}', amount=int(money))
                data.save()
                statement = f'Dear {current}, amount is sent successfully'
                messages.success(request, statement)
                return HttpResponseRedirect('/profile')
            else:
                statement = f'Dear {current}, you do not have enough balance to proceed this request'
                messages.info(request, statement)
                return HttpResponseRedirect('/profile')
        else:
            statement = 'Wrong data'
            messages.error(request, statement)
            return HttpResponseRedirect('/profile')

    return HttpResponseRedirect('/profile')

    

@cache_control(no_cache=True, must_revalidade=True, no_store=True)
def balance_check(request):
    current = Accountuser.objects.get(user = request.user)
    base = current.balance
    message = f'Your balance is {base}'
    messages.success(request, message)
    return HttpResponseRedirect('/profile')

@cache_control(no_cache=True, must_revalidade=True, no_store=True)
def deposite(request):
    if request.method=='POST':
        am = request.POST['amount']
        mobile = request.POST['mobile']
        sender = Accountuser.objects.get(user = request.user)
        receiver = Accountuser.objects.get(phone=mobile)
        
        if receiver:
            receiver.balance += int(am)
            receiver.save()
            data = Records(user=receiver, transaction=f'Credited by {sender}', amount=int(am))
            data.save()
            statement = f"Money is deposited in {receiver} account successfully."
            messages.success(request, statement)
            return HttpResponseRedirect('/profile')
        else:
            statement = 'No user detected'
            messages.error(request, statement)
            return HttpResponseRedirect('/profile')
        
    return HttpResponseRedirect('/profile')
    
        
@cache_control(no_cache=True, must_revalidade=True, no_store=True)
def display_records(request):
    current = Accountuser.objects.get(user = request.user)
    data = Records.objects.filter(user = current)
    return render(request, 'transactions.html', {'records' : data})

@cache_control(no_cache=True, must_revalidade=True, no_store=True)
def feedback(request):
    if request.method == 'POST':
        name = request.POST['name']
        phone = request.POST['phone']
        feedback = request.POST['feedback']

        data = Feedback(name=name, phone=phone, feedback=feedback)
        data.save()
        messages.success(request, 'Thank you for your feedback.')
        return HttpResponseRedirect('/')

    return render(request, 'feedback.html')

@cache_control(no_cache=True, must_revalidade=True, no_store=True)
def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return HttpResponseRedirect('/')
