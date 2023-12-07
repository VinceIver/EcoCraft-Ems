from django.db import models
from datetime import datetime
import os
import random
from django.utils import timezone
from django.utils.html import mark_safe


now = timezone.now()

def image_path(instance, filename):
    basefilename, file_extension = os.path.splitext(filename)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    randomstr = ''.join((random.choice(chars)) for x in range(10))
    _now = datetime.now()

    return 'profile_pic/{year}-{month}-{imageid}-{basename}-{randomstring}{ext}'.format(imageid = instance, basename=basefilename, 
    randomstring = randomstr, ext=file_extension, year=_now.strftime('%Y'), month=_now.strftime('%m'), day=_now.strftime('%d'))



class Employee(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
    ]

    emp_fname = models.CharField(max_length=200, verbose_name='First Name',)
    emp_lname = models.CharField(max_length=200, verbose_name='Last Name')
    emp_email = models.EmailField(unique=True, max_length=200, verbose_name='Email')
    emp_position = models.CharField(max_length=200, verbose_name='Position')
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    emp_image = models.ImageField(upload_to=image_path, default='profile_pic/image.jpg')
    pub_date = models.DateField(default=now)
    contact_number = models.CharField(max_length=15, verbose_name='Contact Number', blank=True, null=True)
    birthday = models.DateField(null=True, blank=True, verbose_name='Birthday')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name='Status')  # New field

    def __str__(self):
        return self.emp_fname + ' ' + self.emp_lname

    def image_tag(self):
        return mark_safe('<img src="/users/media/%s" width="50" height="50" />' % self.emp_image)

    def __str__(self):
        return self.emp_email
    
    def get_status_display(self):
        return self.status.capitalize()

class EmployeeAddress(models.Model):
    employee = models.OneToOneField('Employee', on_delete=models.CASCADE, related_name='address')
    street_address = models.CharField(max_length=255, verbose_name='Street Address', default='')
    city = models.CharField(max_length=100, verbose_name='City', default='')
    state = models.CharField(max_length=100, verbose_name='State', default='')
    zip_code = models.CharField(max_length=20, verbose_name='ZIP Code', default='')

    def __str__(self):
        return f'{self.employee.emp_fname} {self.employee.emp_lname} Address'
    
class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    attended = models.BooleanField(default=False)

    
class Comment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField(default='null')
    body = models.TextField(default='null')
    created_on = models.DateTimeField(default=now)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.name)