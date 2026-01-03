from django.contrib import admin
from django.utils.html import format_html
from .models import Student, Exeat, HouseMistress, House

class StudentInline(admin.TabularInline):
    model = Student
    extra = 0
    fields = ('student_id', 'name', 'email')
    readonly_fields = ('student_id', 'name', 'email')

class HouseMistressInline(admin.TabularInline):
    model = HouseMistress
    extra = 0
    fields = ('name', 'email', 'phone')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'email', 'phone', 'house', 'guardian_name', 'guardian_phone', 'photo_thumbnail')
    search_fields = ('student_id', 'name', 'email')
    list_filter = ('house',)
    ordering = ('name',)
    readonly_fields = ('photo_thumbnail',)

    def photo_thumbnail(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" />', obj.photo.url)
        return 'No photo'
    photo_thumbnail.short_description = 'Photo'

@admin.register(Exeat)
class ExeatAdmin(admin.ModelAdmin):
    list_display = ('student', 'reason', 'start_date', 'end_date', 'status', 'approved_by', 'signed_out_by', 'signed_in_by', 'is_overdue')
    search_fields = ('student__name', 'reason')
    list_filter = ('status', 'start_date', 'end_date', 'approved_by')
    ordering = ('-start_date',)
    date_hierarchy = 'start_date'
    list_editable = ('status',)
    readonly_fields = ('signed_out_time', 'signed_in_time')
    actions = ['approve_exeats', 'reject_exeats', 'mark_completed']

    def approve_exeats(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f'Approved {queryset.count()} exeats.')
    approve_exeats.short_description = 'Approve selected exeats'

    def reject_exeats(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f'Rejected {queryset.count()} exeats.')
    reject_exeats.short_description = 'Reject selected exeats'

    def mark_completed(self, request, queryset):
        queryset.filter(status='signed_out').update(status='completed')
        self.message_user(request, f'Marked {queryset.count()} exeats as completed.')
    mark_completed.short_description = 'Mark signed-out exeats as completed'

@admin.register(HouseMistress)
class HouseMistressAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'house')
    search_fields = ('name', 'email')
    list_filter = ('house',)
    ordering = ('name',)

@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'student_count', 'house_mistress_count')
    search_fields = ('name',)
    ordering = ('name',)
    inlines = [StudentInline, HouseMistressInline]

    def student_count(self, obj):
        return obj.student_set.count()
    student_count.short_description = 'Students'

    def house_mistress_count(self, obj):
        return obj.housemistress_set.count()
    house_mistress_count.short_description = 'House Mistresses'