"""innovation views."""
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
# import io
import os

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.files import File
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import redirect
import matplotlib.pyplot as plt
from rest_framework import viewsets

from innovation.models import Order, OrderResult
from innovation.model_components import Model
from minio_utils import get_file_from_minio


class PingView(View):
    """Test if server is up."""

    def get(self, request):  # pylint: disable=unused-argument
        """Pong response."""
        return HttpResponse('pong')


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order_list.html'
    login_url = 'login'

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order_detail.html'
    login_url = 'login'

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user


class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Order
    fields = (
        'data', 'company_name', 'model_type', 'method', 'start_year',
        'stop_year', 'build_graphics', 'attribute_name',
    )
    template_name = 'order_edit.html'
    login_url = 'login'

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.data = self.request.POST['data']
        return super().form_valid(form)

    # def dispatch(self, request, *args, **kwargs):
    #     obj = self.get_object()
    #     if obj.author != self.request.user:
    #         raise PermissionDenied
    #     return super().dispatch(request, *args, **kwargs)


class OrderDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Order
    template_name = 'order_delete.html'
    success_url = reverse_lazy('order_list')
    login_url = 'login'

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user

    # def dispatch(self, request, *args, **kwargs):
    #     obj = self.get_object()
    #     if obj.author != self.request.user:
    #         raise PermissionDenied
    #     return super().dispatch(request, *args, **kwargs)


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    template_name = 'order_new.html'
    fields = (
        'data', 'company_name', 'model_type', 'method', 'start_year',
        'stop_year', 'build_graphics', 'attribute_name',
    )
    login_url = 'login'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.data = self.request.POST['data']
        return super().form_valid(form)


class OrderResultDetailView(LoginRequiredMixin, DetailView):
    model = OrderResult
    template_name = 'order_result_detail.html'
    login_url = 'login'

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user


class OrderCalculateView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        order = Order.objects.get(pk=kwargs['pk'])
        model = Model(order.data.name)
        df = model.get_dataframe()
        cluster_data = model.get_cluster(
            method=order.method,
            year_start=order.start_year,
            year_stop=order.stop_year
        )
        y = model.calculate_y().quantize(Decimal('0.00'), ROUND_HALF_UP)
        rec = model.get_recommendation(cluster_data[0])
        p_percent = model.get_p_value(df) * 100
        order_result = OrderResult.objects.create(
            order=order, recommendation=rec, y_value=y, p_percent=p_percent
        )
        df_clean = df.fillna('None')
        x_vals = list(df_clean['Год'].values)
        y_vals = list(df_clean[order.attribute_name].values)
        x_vals = [el for i, el in enumerate(x_vals) if y_vals[i] != 'None']
        y_vals = [el for el in y_vals if el != 'None']
        # Build graph
        f, ax = plt.subplots(figsize=(11, 9))
        stat = f'{order.attribute_name}\nСреднее:' \
               f' {round(sum(y_vals)/len(y_vals), 2)}' \
               f'\nMax: {round(max(y_vals), 2)}'
        plt.plot(x_vals, y_vals, label=stat)
        plt.xlabel('Год')
        plt.ylabel(order.attribute_name)
        # bytes_image = io.BytesIO()
        plt.title(
            f"Тренд показателя *{order.attribute_name}* {order.company_name}"
        )
        plt.legend(loc='best')
        fname = f'{order_result.id}_{order.company_name}_{datetime.now()}.png'
        plt.savefig(fname, format='png')
        # plt.savefig(bytes_image, format='png')
        # bytes_image.seek(0)
        with open(fname, 'rb') as image_file:
            order_result.graph_image = File(image_file)
            order_result.save()

        os.remove(fname)
        # return HttpResponse(f'<img src="{order_result.graph_image.url}" alt="test">')
        return redirect(order_result)
        # return HttpResponse(
        #     f'<p>Cluster data for {order.company_name}: '
        #     f'{cluster_data[:-1]}</p><p>Level: {y}</p>'
        #     f'<br><p>{list(cluster_data[-1].keys())}</p>'
        #     f'<p>{list(cluster_data[-1].values())}</p>'
        # )
