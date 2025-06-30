from django.shortcuts import render, HttpResponse
#prueba
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .forms import RegistroUsuarioForm
from django.contrib import messages


class RegistroUsuarioView(FormView):
    template_name = 'register.html'
    form_class = RegistroUsuarioForm
    #! modificar url
    success_url = reverse_lazy('test')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        #! mensaje para test
        messages.success(self.request, f"¡Bienvenido, {user.username}!")
        
        return super().form_valid(form)



#end prueba




# Create your views here.

def home(request):
    return render(request, 'home.html')

def register(request):
    return render(request, 'register.html')

def test(request):
    return render(request,'test.html')