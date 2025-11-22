from django import forms
from django.contrib.auth.models import User
from . import models


class PerfilForm(forms.ModelForm):
    class Meta:
        model = models.Perfil
        filds = "__all__"
        exclude = ('usuario',)


class UserForm(forms.ModelForm):
    
    password= forms.CharField(
        required = False, widget = forms.PasswordInput(),
        label='Senha'
    )   
    
    password2= forms.CharField(
        required = False, widget = forms.PasswordInput(),
        label='Confirmar Senha'
    )   

    def __init__(self,usuario=None,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario


    class Meta:
        model = User
        fields = ('first_name','last_name','username', 'password',
                  'password2','email')

    def clean(self,*args,**kwargs):
        data = self.data
        cleaned = self.cleaned_data
        validation_errors_msg={}

        usuario_data = cleaned.get('username')
        password_data =  cleaned.get('password')
        password2_data = cleaned.get('passoword2')
        email_data = cleaned.get('email')

        usuario_db = User.objects.filter(username=usuario_data).first()
        email_db = User.objects.filter(email=email_data).first()

        error_msg_user_exists = "Usuário já existe."
        error_msg_email_exists = "E-mail já existe."
        error_msg_password_match = "As senhas não coincidem."
        password_short_msg = "A senha precisa de pelo ao menos 6 caracteres."
        # Usuarios Logados - Atualização
        if self.usuario:
            if usuario_data != usuario_db:
                if usuario_db:
                    validation_errors_msg["username"] = error_msg_user_exists
            
            if password_data:
                if password_data != password2_data:
                    validation_errors_msg["password"] = error_msg_password_match
                    validation_errors_msg["password2"] = error_msg_password_match
                if len(password_data) < 6:
                    validation_errors_msg["password"] = password_short_msg

            if email_data != email_db:
                validation_errors_msg["email"] = error_msg_email_exists

        #Usuarios não Logados - Cadastro
        else:
            pass
        if validation_errors_msg:
            raise (forms.ValidationError(validation_errors_msg))