from django.contrib import admin
from .models import Expense, Category

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'category', 'date']
    search_fields = ['title']
    list_filter = ['category', 'date']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
