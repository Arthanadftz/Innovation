from django.db import models
from django.urls import reverse


class OrderResult(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    recommendation = models.TextField()
    y_value = models.DecimalField(max_digits=18, decimal_places=2)
    p_percent = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    graph_image = models.FileField(null=True, blank=True)

    def __str__(self):
        return self.order.company_name

    def get_absolute_url(self):
        return reverse('order_result_detail', args=[str(self.id)])
