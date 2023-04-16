from django.contrib.auth.views import LoginView, LogoutView

from users.forms import UserLoginForm


class UserLogin(LoginView):
    form_class = UserLoginForm
    template_name = 'user/login.html'
    redirect_authenticated_user = ''



class UserLogout(LogoutView):
    template_name = 'user/login.html'
