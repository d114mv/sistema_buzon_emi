import random
import hashlib
import threading
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count 
from .models import Ticket
from .forms import TicketForm, SolicitudAccesoForm, ValidarCodigoForm

class EmailThread(threading.Thread):
    def __init__(self, subject, message, from_email, recipient_list):
        self.subject = subject
        self.message = message
        self.from_email = from_email
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        try:
            print(f"--> Iniciando envío background a {self.recipient_list}...")
            send_mail(
                self.subject,
                self.message,
                self.from_email,
                self.recipient_list,
                fail_silently=False,
            )
            print("--> Correo enviado exitosamente (Background)")
        except Exception as e:
            print(f"--> ERROR ENVIANDO CORREO BACKGROUND: {e}")


PALABRAS_CLAVE = ['robo', 'fuego', 'incendio', 'acoso', 'golpe', 'sangre', 'amenaza', 'urgente']
SPAM = ['puta', 'puto', 'pt', 'pta', 'ptm', 'mierda', 'mrd', 'mrda', 'carajo', 'crj', 'coño', 'joder', 'jdr', 'culo', 'klo', 'verga', 'vrg', 'vga', 'pija', 'cabrón', 'cabron', 'cbron', 'pelotudo', 'pelotuda', 'pltd', 'imbécil', 'imbecil', 'imb', 'idiota', 'idio', 'estúpido', 'estupido', 'stpd', 'pendejo', 'pendeja', 'pndj', 'chupa', 'chupala', 'mierdero', 'mamón', 'mamon', 'mmn', 'gil', 'gilazo', 'cojudo', 'cojuda', 'kjd', 'huevón', 'huevon', 'wevon', 'wvon', 'huevada', 'webada', 'wbda', 'cagado', 'cagada', 'cgd', 'zorra', 'perra', 'maldito', 'maldita', 'asqueroso', 'asquerosa', 'hijo de puta', 'hdp', 'la puta', 'lpt']

def generar_hash_anonimo(identificador):
    salt = settings.SECRET_KEY
    texto_a_hashear = f"{identificador}{salt}"
    return hashlib.sha256(texto_a_hashear.encode('utf-8')).hexdigest()

def verificar_alertas(ticket):
    texto_completo = f"{ticket.asunto} {ticket.descripcion}".lower()
    
    if any(palabra in texto_completo for palabra in PALABRAS_CLAVE):
        destinatario = ticket.categoria.email_responsable or 'dmurielv@est.emi.edu.bo'
        
        asunto = f'ALERTA URGENTE: {ticket.categoria.nombre} - {ticket.asunto}'
        mensaje = f"""
        SE HA REPORTADO UN INCIDENTE CRÍTICO.
        Categoría: {ticket.categoria.nombre}
        Descripción: {ticket.descripcion}
        """
        EmailThread(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [destinatario]).start()

def verificar_spam(ticket):
    texto_completo = f"{ticket.asunto} {ticket.descripcion}".lower()

    if any(palabra in texto_completo for palabra in SPAM):
        destinatario = ticket.categoria.email.responsable
        if not destinatario:
            destinatario = 'dmurielv@est.emi.edu.bo'

        print(f"⚠️ SPAM DETECTADO: Enviando correo a {destinatario}...")
        
        send_mail(
            subject=f'ALERTA DE SPAM: {ticket.categoria.nombre} - {ticket.asunto}',
            message=f"""
            SE HA REPORTADO UN INTENTO DE SPAM.
            POR FAVOR INGRESE AL SISTEMA Y ELIMINE EL REPORTE MARCADO COMO SPAM.
            
            Categoría: {ticket.categoria.nombre}
            
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
            
            request.session['otp_codigo'] = codigo
            request.session['otp_email'] = email
            
            try:
                print(f"--> Intentando enviar correo a {email}...")
                send_mail(
                    'Tu Código de Acceso - Buzón EMI',
                    f'Tu código de verificación es: {codigo}\n\nÚsalo para ingresar al sistema.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                print("--> ¡Correo enviado con éxito!")
            except Exception as e:
                print(f"--> ERROR AL ENVIAR CORREO: {e}")
            
            return redirect('validar_codigo')
            
    else:
        form = SolicitudAccesoForm()
    
    return render(request, 'tickets/login.html', {'form': form})


def validar_codigo(request):
    if 'otp_email' not in request.session:
        return redirect('solicitar_acceso')
    if request.method == 'POST':
        form = ValidarCodigoForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['codigo'] == request.session.get('otp_codigo'):
                request.session['es_estudiante_validado'] = True
                del request.session['otp_codigo']
                return redirect('crear_queja')
            else:
                messages.error(request, "Código incorrecto.")
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
            email_validado = request.session.get('otp_email', "error_sesion")
            ticket.usuario_hash = generar_hash_anonimo(email_validado)
            ticket.save()
            verificar_alertas(ticket)
            verificar_spam(ticket)
            return redirect('pagina_exito')
    else:
        form = TicketForm()
    return render(request, 'tickets/crear_queja.html', {'form': form})

def pagina_exito(request):
    return render(request, 'tickets/exito.html')

def dashboard_publico(request):
    tickets = Ticket.objects.exclude(estado='RECH')
    context = {
        'total': tickets.count(),
        'resueltos': tickets.filter(estado='RES').count(),
        'en_proceso': tickets.filter(estado='PROC').count(),
        'pendientes': tickets.filter(estado='PEND').count(),
        'ultimos_tickets': tickets.order_by('-fecha_creacion')[:10],
    }
    return render(request, 'tickets/dashboard.html', context)

def cerrar_sesion(request):
    for key in ['es_estudiante_validado', 'otp_email', 'otp_codigo']:
        if key in request.session:
            del request.session[key]
    return redirect('solicitar_acceso')