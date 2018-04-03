from django.db import models

# Create your models here.

class UserProfile(models.Model):
    email = models.EmailField(primary_key = True)
    password = models.CharField(max_length = 30, unique = True)
    authenticated = models.BooleanField(default = False)
    institute_id = models.CharField(max_length=30, default="")
    name = models.CharField(max_length=30, default="")
    def check_pass(self, passw):
        if passw == self.password:
            return True
        else:
            return False
    
class Student(models.Model):
    ID = models.CharField(max_length = 20, unique = True)
    email = models.EmailField(primary_key = True)
    name = models.CharField(max_length = 30)
    mobile_no = models.CharField(max_length = 10)

class Employee(models.Model):
    designation_choices = (
        ('ASSP', 'Assistant Professor'),
        ('ASOP', 'Associate Professor'),
        ('PROF', 'Professor'),
        ('LABT', 'Lab Technician'),
        ('ACCO', 'Accountant'),
        ('PROJ', 'Project Officer'),
    )   

    ID = models.CharField(max_length = 20, unique = True)
    email = models.EmailField(primary_key = True)
    name = models.CharField(max_length = 30)
    mobile_no = models.CharField(max_length = 10)
    designation = models.CharField(max_length = 4, choices = designation_choices, default = 'ASSP')

class ApprovalEntity(models.Model):
    category_choices = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    )

    user_ID = models.ForeignKey(UserProfile, on_delete = models.CASCADE)
    approval_ID = models.ForeignKey(Employee, on_delete = models.CASCADE)
    category = models.CharField(max_length = 1, choices = category_choices)

    class Meta:
        unique_together = ('user_ID', 'approval_ID', 'category')

class Guest(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length = 30)

class GuestHouse(models.Model):
    name = models.CharField(max_length = 30, unique = True)
    address = models.CharField(max_length = 100, blank = True)
    PhNo = models.CharField(max_length = 10)

class Bookings(models.Model):
    category_choices = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    )
    room_choices = (
        ('ACS', 'AC Single'),
        ('NACS', 'Non AC Single'),
        ('ACD', 'AC Double'),
        ('NACD', 'Non AC Double'),
    )

    no_rooms = models.IntegerField()
    guests = models.ManyToManyField(Guest, null = True)
    category = models.CharField(max_length = 1, choices = category_choices)
    purpose = models.CharField(max_length = 50, blank = True)
    doarrival = models.DateTimeField()
    dodeparture = models.DateTimeField()
    dobooking = models.DateTimeField()
    guestHouse = models.ForeignKey(GuestHouse, on_delete = models.CASCADE)
    room_type = models.CharField(max_length = 4, choices = room_choices)
    booker = models.ForeignKey(UserProfile, on_delete = models.CASCADE, null = True)

class ApprovedBookings(models.Model):
    booking_id = models.OneToOneField(Bookings, primary_key = True, on_delete = models.CASCADE)

class DisapprovedBookings(models.Model):
    booking_id = models.OneToOneField(Bookings, primary_key = True, on_delete = models.CASCADE)
    reason = models.CharField(max_length = 100, blank = True)

class Rooms(models.Model):
    room_choices = (
        ('SIN', 'Single'),
        ('DOB', 'Double'),
        ('ACS', 'AC Single'),
        ('NACS', 'Non AC Single'),
        ('ACD', 'AC Double'),
        ('NACD', 'Non AC Double'),
        ('SUIT', 'Suit')
    )

    gID = models.ForeignKey(GuestHouse, on_delete = models.CASCADE)
    room_type = models.CharField(max_length = 4, choices = room_choices)
    no_available = models.IntegerField()
