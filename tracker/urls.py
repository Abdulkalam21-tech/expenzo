from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),

    # 🔐 Auth
    path('signup/', views.register_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 🧠 Main & Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('main/', views.main_page_view, name='main_page'),

    # 💰 Expenses
    path('add/', views.add_expense, name='add_expense'),
    path('expenses/', views.view_expenses, name='view_expenses'),
    path('edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),

    # 📁 Categories
    path('add-category/', views.add_category_view, name='add_category'),

    # 📊 Summary
    path('summary/', views.summary_view, name='summary'),
    path('profile/', views.profile_view, name='profile'),
    path('export/', views.export_expenses_csv, name='export_expenses'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),


]
