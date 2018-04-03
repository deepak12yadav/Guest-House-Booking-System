from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Student)
admin.site.register(Employee)
admin.site.register(ApprovalEntity)
admin.site.register(Bookings)
admin.site.register(ApprovedBookings)
admin.site.register(DisapprovedBookings)
admin.site.register(Rooms)
admin.site.register(Guest)
admin.site.register(GuestHouse)