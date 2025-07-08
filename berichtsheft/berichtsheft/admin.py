from django.contrib import admin
from .models import Logbook, Year, Week, Task


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1
    fields = ("category", "name", "hours")
    verbose_name_plural = "Tasks"


class WeekInline(admin.TabularInline):
    model = Week
    extra = 1
    fields = ("week_number",)
    verbose_name_plural = "Weeks"
    show_change_link = True


class YearInline(admin.TabularInline):
    model = Year
    extra = 1
    fields = ("year_number",)
    verbose_name_plural = "Years"
    show_change_link = True


@admin.register(Logbook)
class LogbookAdmin(admin.ModelAdmin):
    list_display = ("student_name", "start_year")
    search_fields = ("student_name",)
    inlines = [YearInline]


@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ("logbook", "year_number")
    list_filter = ("logbook",)
    search_fields = ("logbook__student_name",)
    inlines = [WeekInline]


@admin.register(Week)
class WeekAdmin(admin.ModelAdmin):
    list_display = ("year", "week_number")
    list_filter = ("year__logbook", "year__year_number")
    search_fields = ("entries__name",)
    inlines = [TaskInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("week", "category", "name", "hours")
    list_filter = ("category", "week__year__logbook")
    search_fields = ("name",)
