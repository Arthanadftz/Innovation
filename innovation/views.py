"""innovation views."""
from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic import View
from rest_framework import viewsets

from innovation.models import Order


class PingView(View):
    """Test if server is up."""

    def get(self, request):  # pylint: disable=unused-argument
        """Pong response."""
        return HttpResponse('pong')


class OrderleListView(LoginRequiredMixin, ListView):
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
        'data', 'company_name', 'method', 'start_year',
        'stop_year', 'build_graphics',
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
        'stop_year', 'build_graphics'
    )
    login_url = 'login'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.data = self.request.POST['data']
        return super().form_valid(form)


# class OrderCalculateView(LoginRequiredMixin, View):
from innovation.model_components import Model
class OrderCalculateView(View):
    # login_url = 'login'

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
        print(
            f'Cluster data for {order.company_name}: '
            f'{cluster_data}\nLevel: {y}'
            f'\n{df.head()}\n{cluster_data[-1]}'
        )
        return HttpResponse(
            f'<p>Cluster data for {order.company_name}: '
            f'{cluster_data[:-1]}</p><p>Level: {y}</p>'
            f'<br><p>{list(cluster_data[-1].keys())}</p>'
            f'<p>{list(cluster_data[-1].values())}</p>'
        )
