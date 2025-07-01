from django.db import models
from django.contrib.auth.models import User  # ✅ using built-in User model

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 🔄 changed from Signup to User
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    note = models.TextField(blank=True, null=True)
    is_recurring = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - ₹{self.amount}"
