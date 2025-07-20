from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import render , redirect , get_object_or_404
from django.views.generic import ListView , DetailView , UpdateView , DeleteView ,CreateView , TemplateView , View
from django.urls import reverse_lazy , reverse
from .models import Post ,  Comment , Order , OrderItem
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

# Create your views here.
def home(request):
    smart_conditioners = Post.objects.filter(category__name__iexact='Smart')[:3]
    budget_conditioners = Post.objects.filter(category__name__iexact='Budget')[:3]
    premium_conditioners = Post.objects.filter(category__name__iexact='Premium')[:3]

    context = {
        'smart_conditioners': smart_conditioners,
        'budget_conditioners': budget_conditioners,
        'premium_conditioners': premium_conditioners,
    }

    return render(request, 'main.html', context)


class CondListView(ListView):
    model = Post
    template_name = 'conditioners.html'
    context_object_name = 'conditioners'
    paginate_by = 258

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-id')
        query = self.request.GET.get('q')
        category = self.request.GET.get('category')

        if query:
            queryset = queryset.filter(name__icontains=query)

        if category:
            queryset = queryset.filter(category__name__iexact=category)

        return queryset

class CondCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'conditioner-create.html'
    fields = ('name', 'brand', 'color', 'desc', 'price', 'image', 'number', 'category')
    success_url = reverse_lazy('conditioners')
    login_url = 'login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class CondDetailView(DetailView):
    model = Post
    template_name = 'conditioner-detail.html'
    context_object_name = 'conditioner'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')

        context['previous'] = Post.objects.filter(id__lt=pk).order_by('-id').first()
        context['next'] = Post.objects.filter(id__gt=pk).order_by('id').first()
        context['related_products'] = Post.objects.exclude(id=pk).order_by('?')[:5]

        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['name', 'brand', 'color', 'number', 'image', 'price', 'desc', 'category']
    template_name = 'conditioner-create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('conditioner-detail', args=[self.object.id])

class CondUpdateView(UpdateView):
    model = Post
    fields = ('name', 'brand', 'color', 'desc', 'price', 'image')
    template_name = 'conditioner-update.html'
    context_object_name = 'conditioner'
    success_url = reverse_lazy('conditioners')

class CondDeleteView(DeleteView):
    model = Post
    template_name = 'conditioner-delete.html'
    success_url = reverse_lazy('conditioners')


class KorzinkaView(TemplateView):
    template_name = 'korzinka.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', [])
        products = Post.objects.filter(id__in=cart)
        total_price = sum(product.price for product in products)

        context.update({
            'products': products,
            'total_price': total_price
        })
        return context


def create_order(request):
    cart = request.session.get('cart', [])
    if not cart:
        messages.error(request, "Sizning savatingiz bo'sh")
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        order = Order.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email=request.POST['email'],
            address=request.POST['address'],
            phone=request.POST['phone'],
        )

        for item_id in cart:
            product = get_object_or_404(Post, id=item_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
            )

        request.session['cart'] = []
        return render(request, 'orders/created.html', {'order': order})

    return render(request, 'orders/create.html')


class PaymentView(TemplateView):
    template_name = 'payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', [])
        products = Post.objects.filter(id__in=cart)
        context['products'] = products
        context['total_price'] = sum(p.price for p in products)
        return context

def process_payment(request):
    if request.method == "POST":
        checkout_data = request.session.get('checkout_data', {})
        first_name = checkout_data.get('first_name')
        last_name = checkout_data.get('last_name')
        phone = checkout_data.get('phone')
        address = checkout_data.get('address')
        email = request.user.email if request.user.is_authenticated else 'noemail@example.com'
        payment_method = request.POST.get('payment_method')

        order = Order.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            phone=phone,
            paid=False
        )
        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            product = Post.objects.get(id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                quantity=quantity,
                total_price=product.price * quantity
            )

        request.session['cart'] = {}
        del request.session['checkout_data']
        return redirect('order_confirmation', pk=order.pk)

    return redirect('checkout')

class OrderConfirmationView(TemplateView):
    template_name = 'order_confarmation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = Order.objects.last()
        return context

class AddToCartView(View):
    def get(self, request, pk):
        cart = request.session.get('cart', [])
        if pk not in cart:
            cart.append(pk)
            request.session['cart'] = cart
            messages.success(request, 'Mahsulot savatga qo\'shildi!')
        return redirect('conditioner-detail', pk=pk)


class RemoveFromCartView(View):
    def get(self, request, pk):
        cart = request.session.get('cart', [])
        if pk in cart:
            cart.remove(pk)
            request.session['cart'] = cart
            messages.success(request, 'Mahsulot savatdan olib tashlandi!')
        return redirect('korzinka')


class CheckoutView(TemplateView):
    template_name = 'checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', [])
        products = Post.objects.filter(id__in=cart)
        total_price = sum(product.price for product in products)

        context.update({
            'products': products,
            'total_price': total_price
        })
        return context

class DecreaseQuantityView(View):
    def get(self, request, pk):
        cart = request.session.get('cart', [])
        if pk in cart:
            cart.remove(pk)
            request.session['cart'] = cart
            messages.info(request, "📦 Mahsulot miqdori kamaytirildi!")
        return redirect('korzinka')

class IncreaseQuantityView(View):
    def get(self, request, pk):
        cart = request.session.get('cart', {})

        if isinstance(cart, list):
            cart = {str(i): 1 for i in cart}  # Eski listdan dict ga o'tish
        else:
            cart = {str(k): int(v) for k, v in cart.items()}

        pk = str(pk)
        if pk in cart:
            cart[pk] += 1
        else:
            cart[pk] = 1

        request.session['cart'] = cart
        messages.success(request, "Mahsulot soni oshirildi.")
        return redirect('korzinka')

class ProcessCheckoutView(View):
    def post(self, request):
        cart = request.session.get('cart', [])
        if not cart:
            messages.error(request, 'Savat bo\'sh!')
            return redirect('korzinka')
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            notes=request.POST.get('notes'),
            total_price=sum(p.price for p in Post.objects.filter(id__in=cart))
        )
        for product_id in cart:
            product = get_object_or_404(Post, id=product_id)
            order.products.add(product)
        request.session['cart'] = []
        messages.success(request, 'Buyurtmangiz qabul qilindi!')
        return redirect('order-confirmation', pk=order.pk)


class CheckoutView(TemplateView):
    template_name = 'checkout.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', [])
        products = Post.objects.filter(id__in=cart)
        total_price = sum(product.price for product in products)

        context.update({
            'products': products,
            'total_price': total_price
        })
        return context

    def post(self, request):
        request.session['checkout_data'] = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'phone': request.POST.get('phone'),
            'address': request.POST.get('address'),
            'notes': request.POST.get('notes'),
        }
        return redirect('payment')

class AddCartView(View):
    def get(self, request, pk):
        cart = request.session.get('cart', {})

        if isinstance(cart, list):
            cart = {str(i): 1 for i in cart}

        pk = str(pk)
        if pk not in cart:
            cart[pk] = 1
            request.session['cart'] = cart
            messages.success(request, '✅ Mahsulot korzinkaga qo‘shildi!')
        else:
            messages.info(request, 'ℹ️ Bu mahsulot allaqachon korzinkada.')

        return redirect('conditioner-detail', pk=pk)

from .models import ContactMessage

class ContactView(View):
    template_name = 'contact.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        ContactMessage.objects.create(name=name, email=email, message=message)
        messages.success(request, '✅ Xabaringiz uchun rahmat!')
        return redirect('thanks')


@login_required
def add_comment(request, pk):
    conditioner = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Comment.objects.create(
                post=conditioner,
                author=request.user,
                text=text
            )
            messages.success(request, "Komment qo‘shildi!")
        else:
            messages.warning(request, "Komment bo‘sh bo‘lmasligi kerak.")

        return redirect('conditioner-detail', pk=pk)

    return redirect('conditioner-detail', pk=pk)


@login_required
def update_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if request.user != comment.author:
        raise PermissionDenied

    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            comment.text = text
            comment.save()
            messages.success(request, "Komment muvaffaqiyatli tahrirlandi!")
        else:
            messages.warning(request, "Komment bo'sh bo'lmasligi kerak.")

    return redirect('conditioner-detail', pk=comment.post.id)


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if request.user != comment.author:
        raise PermissionDenied

    post_id = comment.post.id
    comment.delete()
    messages.success(request, "Komment muvaffaqiyatli o'chirildi!")

    return redirect('conditioner-detail', pk=post_id)

@login_required(login_url='login')
def profile_view(request):
    return render(request, 'account/profile.html', {'user': request.user})

@login_required(login_url='login')
def update_profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        image = request.FILES.get('image')

        if User.objects.filter(username=username).exclude(pk=user.pk).exists():
            messages.error(request, "Bu username allaqachon band.")
            return redirect('update-profile')

        user.username = username
        user.email = email
        user.save()

        if image:
            profile.image = image
            profile.save()

        messages.success(request, "Profil muvaffaqiyatli yangilandi.")
        return redirect('profile')

    return render(request, 'account/edit_profile.html', {
        'user': user,
        'profile': profile
    })

@login_required(login_url='login')
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Parolingiz muvaffaqiyatli o'zgartirildi!")
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if 'old_password' in field:
                        messages.error(request, "Hozirgi parolingiz xato kiritildi!")
                    elif 'new_password2' in field:
                        messages.error(request, "Yangi parollar mos kelmadi!")
                    else:
                        messages.error(request, f"Xato: {error}")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'account/change_password.html')
def about(request):
    return render(request , 'account/about.html')