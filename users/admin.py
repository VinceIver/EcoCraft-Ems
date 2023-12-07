from django.contrib import admin
from .models import Employee, Comment, Attendance
from django.contrib.contenttypes.admin import GenericTabularInline
# Register your models here.

admin.site.site_header = "Ecocraft User Admin"
admin.site.site_title = "EcoCraft Admin Area"
admin.site.index_title = "WELCOME TO ADMIN AREA"

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

class UserAdmin(admin.ModelAdmin):
    list_display = ['image_tag', 'emp_fname', 'emp_lname', 'emp_email', 'emp_position']
    search_fields = ['emp_fname', 'emp_lname', 'emp_email', 'emp_position']
    inlines = [CommentInline]

class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'employee_id','created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comment']

    def approve_comment(self, request, queryset):
        queryset.update(active=True)

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'attended')
    list_filter = ('employee', 'attended')
    search_fields = ('employee__emp_fname', 'employee__emp_lname', 'date')
    date_hierarchy = 'date' 

admin.site.register(Employee, UserAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Attendance, AttendanceAdmin)