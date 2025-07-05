from django.shortcuts import render , redirect
from django.views.generic import ListView , DetailView , UpdateView , DeleteView ,CreateView , TemplateView , View
from django.urls import reverse_lazy
from .models import Konditsioner
from django.contrib import messages

# Create your views here.
def home(request):
    return render(request , 'main.html')

class CondListView(ListView):
    model = Konditsioner
    template_name = 'conditioners.html'
    context_object_name = 'conditioners'


class CondCreateView(CreateView):
    model = Konditsioner
    template_name = 'conditioner-create.html'
    fields = ('name', 'brand', 'color', 'desc', 'price', 'image')
    success_url = reverse_lazy('conditioners')


class CondDetailView(DetailView):
    model = Konditsioner
    template_name = 'conditioner-detail.html'
    context_object_name = 'conditioner'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        context['previous'] = Konditsioner.objects.filter(id__lt=pk).order_by('-id').first()
        context['next'] = Konditsioner.objects.filter(id__gt=pk).order_by('id').first()
        return context

class CondUpdateView(UpdateView):
    model = Konditsioner
    fields = ('name', 'brand', 'color', 'desc', 'price', 'image')
    template_name = 'conditioner-update.html'
    context_object_name = 'conditioner'
    success_url = reverse_lazy('conditioners')

class CondDeleteView(DeleteView):
    model = Konditsioner
    template_name = 'conditioner-delete.html'
    success_url = reverse_lazy('conditioners')


from django.views import View
from django.shortcuts import redirect

class AddToCartView(View):
    def get(self, request, pk):
        cart = request.session.get('cart', [])
        if pk not in cart:
            cart.append(pk)
            request.session['cart'] = cart
        return redirect('conditioner-detail', pk=pk)

class KorzinkaView(TemplateView):
    template_name = 'korzinka.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', [])
        context['products'] = Konditsioner.objects.filter(id__in=cart)
        return context


class AddCartView(View):
    def get(self, request, pk):
        cart = request.session.get('cart', [])
        if pk not in cart:
            cart.append(pk)
            request.session['cart'] = cart
            messages.success(request, '✅ Mahsulot korzinkaga qo‘shildi!')
        else:
            messages.info(request, 'ℹ️ Bu mahsulot allaqachon korzinkada.')
        return redirect('conditioner-detail', pk=pk)

class ContactView(View):
    template_name = 'contact.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        messages.success(request, '✅ Xabaringiz uchun rahmat!')
        return redirect('thanks')
