from datetime import datetime

# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


class Order(models.Model):
    INTERVALS = 'Intervals'
    YEAR = 'Year'
    METHOD_CHOICES = [
        (INTERVALS, 'Intervals'), (YEAR, 'Year')
    ]
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    company_name = models.CharField(
        max_length=255, db_index=True, blank=True, null=True
    )
    data = models.FileField(blank=True, null=True)
    model_type = models.CharField(max_length=128, blank=True, null=True)
    method = models.CharField(
        max_length=15, choices=METHOD_CHOICES, blank=True, null=True
    )
    start_year = models.IntegerField(blank=True, null=True)
    stop_year = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now=True, db_index=True)
    build_graphics = models.BooleanField(default=False)

    def __str__(self):
        created = datetime.strftime(self.created, "%Y-%m-%d %H:%M:%S")
        return f"{self.company_name} from {self.user.username} at {created}"

    def get_absolute_url(self):
        return reverse('order_detail', args=[str(self.id)])

    class Meta:
        ordering = ['-created']
