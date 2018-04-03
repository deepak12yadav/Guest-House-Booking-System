from django.shortcuts import get_object_or_404,render, redirect, render
from .models import *
import json
from django.views.decorators import csrf
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.core.exceptions import *
from django.utils.dateparse import parse_datetime
import datetime
from django.views.decorators.cache import never_cache

@never_cache
# Create your views here.
def home(request):
    if 'id' in request.session.keys():
        if request.session['type'] == 'student':
            studentname = Student.objects.get(email = request.session['id'])
            context = {
                'name': studentname.name
            }
            return render(request, 'studenthome.html', context)
        else:
            employeename = Employee.objects.get(email = request.session['id'])
            context = {
                'name': employeename.name
            }
            return render(request, 'employeehome.html', context)
    else:
        return render(request, 'login.html')

@never_cache
def login(request):
    if request.method == 'POST':
        email = request.POST.get('emailid')
        print(email)
        password = request.POST.get('password')
        try: 
            Student.objects.get(email = email)
            student = UserProfile.objects.get(email = email)
            if student.check_pass(password):
                request.session['id'] = email
                request.session['type'] = 'student'
            return redirect('/')
        except: 
            try: 
                Employee.objects.get(email = email)
                employee = UserProfile.objects.get(email = email)
                if employee.check_pass(password):
                    request.session['id'] = email
                    request.session['type'] = 'employee'
                return redirect('/')
            except:
                messages.error(request, 'Username and/or Password is/are incorrect!')
                return redirect('/login')
    else:
        return render(request, 'login.html')

@never_cache
def signup(request):
    if request.method == 'POST':
        email = request.POST.get('emailid')
        print(email)
        pass1 = request.POST.get('pass1')
        print(pass1)
        pass2 = request.POST.get('pass2')
        print(pass2)
        try:
            studentobj = Student.objects.get(email = email)
            try:
                UserProfile.objects.get(email = email)
                messages.error(request, 'An account with this email id already exists in the database!')
                return redirect('/signup')
            except:
                if pass1 == pass2:
                    user = UserProfile(email = email, password = pass1, name = studentobj.name, institute_id = studentobj.ID)
                    user.save()
                    print("here")
                    messages.error(request, 'User successfully created!')
                    return redirect('/signup')
                else:
                    messages.error(request, 'Passwords do not match!')
                    return redirect('/signup')
        except:
            try:
                employeeobj = Employee.objects.get(email = email)
                try:
                    UserProfile.objects.get(email = email)
                    messages.error(request, 'An account with this email id already exists in the database!')
                    return redirect('/signup')
                except:
                    if pass1 == pass2:
                        user = UserProfile(email = email, password = pass1, name = employeeobj.name, institute_id = employeeobj.ID)
                        user.save()
                        messages.error(request, 'User successfully created!')
                        return redirect('/signup')
                    else:
                        messages.error(request, 'Passwords do not match!')
                        return redirect('/signup')
            except:
                messages.error(request, 'No such email id exists in our database!')
                return redirect('/signup/')
    else:
        return render(request, 'signup.html')

@never_cache
def make_booking(request):
    if request.method == 'POST':
        try:  
            email = request.session['id']
            guesthouse = request.POST.get('guesthouse')
            category = request.POST.get('category')
            purpose = request.POST.get('purpose')
            doarrival = request.POST.get('doa') 
            dodeparture = request.POST.get('dod')
            dobooking = datetime.datetime.now()
            room_type = request.POST.get('room_type')
            no_rooms = request.POST.get('no_rooms')
            guests = []

            booking = list(Bookings.objects.all())

            date_in = doarrival
            date_processing = date_in.replace('T', '-').replace(':', '-').split('-')
            date_processing = [int(v) for v in date_processing]
            date_out1 = datetime.datetime(*date_processing)


            date_in = dodeparture
            date_processing = date_in.replace('T', '-').replace(':', '-').split('-')
            date_processing = [int(v) for v in date_processing]
            date_out2 = datetime.datetime(*date_processing)
            cou=0;

            if  (date_out1 > date_out2 or date_out1 < datetime.datetime.now()):
                messages.error(request, 'Please enter valid dates!')
                return redirect('/makebookings/')

            list_disapprovals = list(DisapprovedBookings.objects.all())
            list_approvals = list(ApprovedBookings.objects.all())
            ll=[]
            la=[]
            for l in list_disapprovals:
                ll.append(l.booking_id)
            
            for l in list_approvals:
                la.append(l.booking_id)

            for book in booking:
                if( (book not in ll)  and   not(book.doarrival < date_out1 and book.dodeparture < date_out1) and not(book.doarrival > date_out2 and book.dodeparture > date_out2) and (book.guestHouse.name == guesthouse)):
                    cou += book.no_rooms  

             
            guesthouse_obj = GuestHouse.objects.get(name = guesthouse)
            guesthouse_max_occ = Rooms.objects.get(gID = guesthouse_obj, room_type = room_type).no_available

            if cou+int(no_rooms) > guesthouse_max_occ:
                if category == 'A' or category == 'B':
                    cdcat = 0
                    for book in booking:
                        if( (book not in ll) and (book not in la) and not(book.doarrival < date_out1 and book.dodeparture < date_out1) and not(book.doarrival > date_out2 and book.dodeparture > date_out2) and (book.guestHouse.name == guesthouse) and book.category < category):
                            cdcat += book.no_rooms
                    if int(no_rooms) >= cdcat:
                        messages.error(request, 'Guesthouse full! Either select other category or change the GuestHouse')
                        return redirect('/makebookings/')
                    else:
                        rooms_to_del = cdcat - int(no_rooms)
                        for book in booking:
                            if( (book not in ll) and (book not in la) and not(book.doarrival < date_out1 and book.dodeparture < date_out1) and not(book.doarrival > date_out2 and book.dodeparture > date_out2) and (book.guestHouse.name == guesthouse) and book.category < category):
                                rooms_to_del -= book.no_rooms
                                disapp = DisapprovedBookings(booking_id=book, reason="Priority not high enough!")
                                disapp.save()
                                if rooms_to_del <= 0:
                                    break
                else:
                    messages.error(request, 'Guesthouse full! Either select other category or change the GuestHouse')
                    return redirect('/makebookings/') 

            print("debug2")

            for i in range(int(request.POST.get('no_guests'))):
                guest = Guest(email = request.POST.get('guest' + str(i+1)), name = request.POST.get('name' + str(i+1)))
                guests += [guest]
                guest.save()

            
            booking = Bookings(
                category = category, 
                purpose = purpose, 
                doarrival = doarrival,
                dodeparture = dodeparture,
                dobooking = dobooking,
                room_type = room_type,
                no_rooms = no_rooms
            )
            print("debug3")
            print(booking)
            print(guests)
            booking.booker = UserProfile.objects.get(email = email)
            booking.guestHouse = GuestHouse.objects.get(name = guesthouse)
            print("debug5")
            print(booking.id)
            booking.save()
            print(booking.id)
            for guest in guests:
                booking.guests.add(guest)
            #for guest in guests:
           
            return redirect('/')
        except:
            return redirect('/') 
    else:
        return render(request, 'makebookings.html')


@never_cache
def viewbookings(request):
    try:
        email = request.session['id']
        booking_ids = []
        bookings = []
        approve = []
        disapprove = []
        pending = []



        for booking in list(Bookings.objects.all()):
            if booking.booker.email == email:
                booking_ids.append(booking.id)
                bookings.append(booking)

        for booking in list(ApprovedBookings.objects.all()):
            if booking.booking_id.id in booking_ids:
                approve.append(booking.booking_id)

        for booking in list(DisapprovedBookings.objects.all()):
            if booking.booking_id.id in booking_ids:
                disapprove.append(booking)
        
        for booking in bookings:
            if booking not in approve and booking not in disapprove:
                pending.append(booking)

       
        context = {
            'approve': approve,
            'disapprove' : disapprove,
            'pending' : pending
        }
        
        return render(request, 'viewbookings.html', context)
    except:
        return redirect('/')


@never_cache
def approve(request):
    booking_id = request.POST['id']
    booking = Bookings.objects.get(id = booking_id)
    app_booking = ApprovedBookings(booking_id = booking)
    app_booking.save()
    return redirect('/approvebookings')

@never_cache
def disapprove(request):
    booking_id = request.POST['id']
    reason = request.POST['reason']
    print(booking_id)
    booking = Bookings.objects.get(id = booking_id)
    disapp_booking = DisapprovedBookings(booking_id = booking, reason = reason)
    disapp_booking.save()
    return redirect('/approvebookings')

def logout(request):
    del request.session['id']
    del request.session['type']
    request.session.modified = True
    return render(request, 'logout.html')

@never_cache
def bookings_for_approval(request):
    d = []
    try:
        print("Hello1")
        employee = Employee.objects.get(email = request.session['id'])
        approval_entity = list(ApprovalEntity.objects.all())
        bookings = list(Bookings.objects.all())
        for approval_e in approval_entity:
            print(approval_e.approval_ID)
            if approval_e.approval_ID.email == employee.email:
                print(str(approval_e.approval_ID) + "Debug")
                for book in bookings:
                    print(book.doarrival.date)
                    print(datetime.date.today())
                    if approval_e.user_ID == book.booker and book.doarrival.date() > datetime.date.today():
                        try:
                            temp = ApprovedBookings.objects.get(booking_id = book)
                        except:
                            try:
                                temp = DisapprovedBookings.objects.get(booking_id = book)
                            except:
                                #print(book)
                                d.append(book)
        context = {
            'list' : d
        }
        return render(request, 'bookings_to_approve.html', context)
    except:
        context = {
            'list' : d
        }
        return render(request, 'bookings_to_approve.html', context)
@never_cache
def check_availability(request):
    c1 = {
        'ACS' : 0,
        'NACS' : 0,
        'ACD' : 0,
        'NACD' : 0
    }
    c2 = {
        'ACS' : 0,
        'NACS' : 0,
        'ACD' : 0,
        'NACD' : 0
    }
    c3 = {
        'ACS' : 0,
        'NACS' : 0,
        'ACD' : 0,
        'NACD' : 0
    } 
    context = {
        'list1' : c1,
        'list2' : c2,
        'list3' : c3
    }


    try:
        guesthouse_obj = GuestHouse.objects.get(name = "Technology Guest House")
        try:
            rooms = Rooms.objects.get(gID = guesthouse_obj, room_type = 'ACS')
            context['list1']['ACS'] = rooms.no_available
        except:
            pass
        try:
            rooms = Rooms.objects.get(gID = guesthouse_obj, room_type = 'NACS')
            context['list1']['NACS'] = rooms.no_available
        except:
            pass
        try:
            rooms = Rooms.objects.get(gID = guesthouse_obj, room_type = 'ACD')
            context['list1']['ACD'] = rooms.no_available
        except:
            pass
        
        try:
            rooms = Rooms.objects.get(gID = guesthouse_obj, room_type = 'NACD')
            context['list1']['NACD'] = rooms.no_available
        except:
            pass
        
    except:
        pass
        
    try:
        guesthouse_obj = GuestHouse.objects.get(name = "Visveswaraya Guest House")
        try:
            rooms = Rooms.objects.get(gID = guesthouse_obj, room_type = 'ACS')
            context['list2']['ACS'] = rooms.no_available
        except:
            pass
        try:
            rooms = Rooms.objects.get(gID = guesthouse_obj, room_type = 'NACS')
            context['list2']['NACS'] = rooms.no_available
        except:
            pass
        try:
            rooms = Rooms.objects.get(gID = guesthouse_obj, room_type = 'ACD')
            context['list2']['ACD'] = rooms.no_available
        except:
            pass
        try:
            rooms = Rooms.objects.get(gID = guesthouse_obj, room_type = 'NACD')
            context['list2']['NACD'] = rooms.no_available
        except:
            pass
    except:
        pass
    try:
        guesthouse_obj = GuestHouse.objects.get(name = "Salt Lake Guest House")
        try:
            rooms = Rooms.objects.get(gID = guesthouse_obj, room_type = 'ACS')
            context['list3']['ACS'] = rooms.no_available
        except:
            pass
        try:
            rooms = Rooms.objects.get(gID = guesthouse_obj, room_type = 'NACS')
            context['list3']['NACS'] = rooms.no_available
        except:
            pass
        try:
            rooms = Rooms.objects.get(gID = guesthouse_obj, room_type = 'ACD')
            context['list3']['ACD'] = rooms.no_available
        except:
            pass
        try:
            rooms = Rooms.objects.get(gID = guesthouse_obj, room_type = 'NACD')
            context['list3']['NACD'] = rooms.no_available
        except:
            pass
    except:
        pass
    if request.method == 'GET':
        booking = list(Bookings.objects.all())
        for book in booking:
            if( not(book.doarrival < datetime.datetime.now() and book.dodeparture < datetime.datetime.now()) and not(book.doarrival > datetime.datetime.now() and book.dodeparture > datetime.datetime.now())):
                if(book.guestHouse.name == "Technology Guest House"):
                    context['list1'][book.room_type] -= book.no_rooms
                elif(book.guestHouse.name == "Visveswaraya Guest House"):
                    context['list2'][book.room_type] -= book.no_rooms
                elif(book.guestHouse.name == "Salt Lake Guest House"):
                    context['list3'][book.room_type] -= book.no_rooms

        return render(request, 'checkavailability.html',context)
    if request.method == 'POST':
        booking = list(Bookings.objects.all())
        doarrival = request.POST.get('doa') 
        dodeparture = request.POST.get('dod')

        date_in = doarrival
        date_processing = date_in.replace('T', '-').replace(':', '-').split('-')
        date_processing = [int(v) for v in date_processing]
        date_out1 = datetime.datetime(*date_processing)


        date_in = dodeparture
        date_processing = date_in.replace('T', '-').replace(':', '-').split('-')
        date_processing = [int(v) for v in date_processing]
        date_out2 = datetime.datetime(*date_processing)
        for book in booking:
            if( not(book.doarrival < date_out1 and book.dodeparture < date_out1) and not(book.doarrival > date_out2 and book.dodeparture > date_out2)):
                if(book.guestHouse.name == "Technology Guest House"):
                    context['list1'][book.room_type] -= book.no_rooms
                elif(book.guestHouse.name == "Visveswaraya Guest House"):
                    context['list2'][book.room_type] -= book.no_rooms
                elif(book.guestHouse.name == "Salt Lake Guest House"):
                    context['list3'][book.room_type] -= book.no_rooms

        return render(request, 'checkavailability.html',context)