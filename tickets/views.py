import random
import hashlib
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count 
from .models import Ticket
from .forms import TicketForm, SolicitudAccesoForm, ValidarCodigoForm

PALABRAS_CLAVE = ['robo', 'fuego', 'incendio', 'acoso', 'golpe', 'sangre', 'amenaza', 'urgente']


def generar_hash_anonimo(identificador):
    salt = settings.SECRET_KEY
    texto_a_hashear = f"{identificador}{salt}"
    return hashlib.sha256(texto_a_hashear.encode('utf-8')).hexdigest()

def verificar_alertas(ticket):
    texto_completo = f"{ticket.asunto} {ticket.descripcion}".lower()
    
    if any(palabra in texto_completo for palabra in PALABRAS_CLAVE):
        destinatario = ticket.categoria.email_responsable
        if not destinatario:
            destinatario = 'admin@emi.edu.bo'
            
        print(f"⚠️ ALERTA DETECTADA: Enviando correo a {destinatario}...")
        
        send_mail(
            subject=f'ALERTA URGENTE: {ticket.categoria.nombre} - {ticket.asunto}',
            message=f"""
            SE HA REPORTADO UN INCIDENTE CRÍTICO.
            
            Categoría: {ticket.categoria.nombre}
            Prioridad Detectada: MÁXIMA
            
            Descripción:
            {ticket.descripcion}
            
            -------------------------------------
            Este es un mensaje automático del Sistema de Buzón EMI.
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            fail_silently=False,
        )


def solicitar_acceso(request):
    if request.method == 'POST':
        form = SolicitudAccesoForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            codigo = str(random.randint(100000, 999999))
            
            print("="*50)
            print(f"🔑 CÓDIGO DE ACCESO GENERADO: {codigo}")
            print("="*50)

            request.session['otp_codigo'] = codigo
            request.session['otp_email'] = email
            
            try:
                send_mail(
                    'Tu Código de Acceso - Buzón EMI',
                    f'Tu código de verificación es: {codigo}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error enviando mail: {e}")
            
            return redirect('validar_codigo')

def validar_codigo(request):
    if 'otp_email' not in request.session:
        return redirect('solicitar_acceso')
        
    if request.method == 'POST':
        form = ValidarCodigoForm(request.POST)
        if form.is_valid():
            codigo_ingresado = form.cleaned_data['codigo']
            codigo_real = request.session.get('otp_codigo')
            
            if codigo_ingresado == codigo_real:
                request.session['es_estudiante_validado'] = True
                
                del request.session['otp_codigo']
                
                return redirect('crear_queja')
            else:
                messages.error(request, "Código incorrecto. Inténtalo de nuevo.")
    else:
        form = ValidarCodigoForm()
    
    return render(request, 'tickets/validar.html', {'email': request.session['otp_email'], 'form': form})

def crear_queja(request):
    if not request.session.get('es_estudiante_validado'):
        return redirect('solicitar_acceso')

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            
            email_validado = request.session.get('otp_email')
            if not email_validado: 
                email_validado = "error_sesion_perdida"

            ticket.usuario_hash = generar_hash_anonimo(email_validado)
            
            ticket.save()
            
            verificar_alertas(ticket)
            
            
            return redirect('pagina_exito')
    else:
        form = TicketForm()

    return render(request, 'tickets/crear_queja.html', {'form': form})

def pagina_exito(request):
    return render(request, 'tickets/exito.html')

def dashboard_publico(request):
    tickets_validos = Ticket.objects.exclude(estado='RECH')
    
    total = tickets_validos.count()
    resueltos = tickets_validos.filter(estado='RES').count()
    en_proceso = tickets_validos.filter(estado='PROC').count()
    pendientes = tickets_validos.filter(estado='PEND').count()
    
    ultimos_tickets = tickets_validos.order_by('-fecha_creacion')[:10]
    
    context = {
        'total': total,
        'resueltos': resueltos,
        'en_proceso': en_proceso,
        'pendientes': pendientes,
        'ultimos_tickets': ultimos_tickets,
    }
    return render(request, 'tickets/dashboard.html', context)