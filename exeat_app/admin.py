from django.contrib import admin
from django.utils.html import format_html
from .models import Student, Exeat, HouseMistress, House, School, SubAdmin, SecurityPerson


# ==================== SCHOOL ADMIN ====================

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'email', 'phone', 'created_at')
    search_fields = ('name', 'code', 'email')
    list_filter = ('created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('address',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


# ==================== SUB-ADMIN ADMIN ====================

@admin.register(SubAdmin)
class SubAdminAdmin(admin.ModelAdmin):
    list_display = ('get_user_name', 'school', 'phone', 'created_at')
    search_fields = ('user__username', 'user__email', 'school__name')
    list_filter = ('school', 'created_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'school', 'phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'user')

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_user_name.short_description = 'Name'


# ==================== HOUSE ADMIN ====================

@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'description', 'created_at')
    search_fields = ('name', 'school__name')
    list_filter = ('school', 'created_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('school', 'name', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


# ==================== STUDENT ADMIN ====================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'school', 'house', 'email', 'phone')
    search_fields = ('student_id', 'name', 'email', 'school__name')
    list_filter = ('school', 'house', 'created_at')
    fieldsets = (
        ('User', {
            'fields': ('user', 'school')
        }),
        ('Personal Information', {
            'fields': ('student_id', 'name', 'email', 'phone', 'photo')
        }),
        ('House', {
            'fields': ('house',)
        }),
        ('Guardian Information', {
            'fields': ('guardian_name', 'guardian_phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'user')


# ==================== HOUSE MISTRESS ADMIN ====================

@admin.register(HouseMistress)
class HouseMistressAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'house', 'email', 'phone')
    search_fields = ('name', 'email', 'house__name', 'school__name')
    list_filter = ('school', 'house', 'created_at')
    fieldsets = (
        ('User', {
            'fields': ('user', 'school')
        }),
        ('Personal Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('House', {
            'fields': ('house',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'user')


# ==================== SECURITY PERSON ADMIN ====================

@admin.register(SecurityPerson)
class SecurityPersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'email', 'employee_id', 'phone')
    search_fields = ('name', 'email', 'employee_id', 'school__name')
    list_filter = ('school', 'created_at')
    fieldsets = (
        ('User', {
            'fields': ('user', 'school')
        }),
        ('Personal Information', {
            'fields': ('name', 'email', 'phone', 'employee_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'user')


# ==================== EXEAT ADMIN ====================

@admin.register(Exeat)
class ExeatAdmin(admin.ModelAdmin):
    list_display = ('student', 'school', 'status', 'start_date', 'end_date', 'created_at')
    search_fields = ('student__name', 'student__student_id', 'school__name')
    list_filter = ('school', 'status', 'created_at')
    fieldsets = (
        ('School & Student', {
            'fields': ('school', 'student')
        }),
        ('Exeat Details', {
            'fields': ('reason', 'start_date', 'end_date', 'status')
        }),
        ('Approvals', {
            'fields': ('approved_by',)
        }),
        ('Sign Out', {
            'fields': ('signed_out_by', 'signed_out_time')
        }),
        ('Sign In', {
            'fields': ('signed_in_by', 'signed_in_time')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    actions = ['approve_exeats', 'reject_exeats']

    def approve_exeats(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f'Approved {queryset.count()} exeats.')
    approve_exeats.short_description = 'Approve selected exeats'

    def reject_exeats(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f'Rejected {queryset.count()} exeats.')
    reject_exeats.short_description = 'Reject selected exeats'