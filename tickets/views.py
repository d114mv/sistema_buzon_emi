import hashlib
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .forms import TicketForm
from django.db.models import Count 
from .models import Ticket

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

def crear_queja(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            
            if request.user.is_authenticated:
                identificador = request.user.email
            else:
                identificador = "usuario_anonimo_demo" 
            
            ticket.usuario_hash = generar_hash_anonimo(identificador)
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