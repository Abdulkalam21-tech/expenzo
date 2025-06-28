from django.db import models

class Signup(models.Model):
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    is_admin = models.BooleanField(default=False)  # ✅ New field

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(Signup, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    note = models.TextField(blank=True, null=True)
    is_recurring = models.BooleanField(default=False)  # ✅ inside the class

    def __str__(self):
        return f"{self.title} - ₹{self.amount}"

