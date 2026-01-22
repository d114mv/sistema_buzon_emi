from django import forms
from .models import Ticket

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['categoria', 'asunto', 'descripcion', 'imagen']
        
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'asunto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Proyector dañado en aula B-102'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detalla el problema...'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'imagen': 'Evidencia (Opcional, foto o captura)'
        }

class SolicitudAccesoForm(forms.Form):
    email = forms.EmailField(
        label="Correo Institucional",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'ejemplo@est.emi.edu.bo'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@est.emi.edu.bo'):
            raise forms.ValidationError("Solo se permiten correos institucionales (@est.emi.edu.bo)")
        return email

class ValidarCodigoForm(forms.Form):
    codigo = forms.CharField(
        label="Código de Verificación",
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center', 
            'placeholder': '123456',
            'style': 'font-size: 24px; letter-spacing: 5px;'
        })
    )