"""bookeasy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from mainapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login, name = 'login'),
    path('', views.home, name = 'home'),
    path('signup/', views.signup, name="signup"),
    path('logout/', views.logout, name="logout"),
    path('approvebookings/', views.bookings_for_approval, name="approvebookings"),
    path('disapprove/', views.disapprove, name = 'disapprove'),
    path('approve/', views.approve, name = 'approve'),
    path('viewbookings/', views.viewbookings, name = 'viewbookings'),
    path('makebookings/', views.make_booking, name = 'makebookings'),
    path('checkavailability/', views.check_availability, name="checkavailability")
]
