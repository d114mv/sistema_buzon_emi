import uuid
from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    email_responsable = models.EmailField(help_text="Correo del administrativo a cargo")
    
    prioridad_base = models.IntegerField(default=1)

    def __str__(self):
        return self.nombre

class Ticket(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'PEND', 'Pendiente'
        EN_PROCESO = 'PROC', 'En Proceso'
        RESUELTO = 'RES', 'Resuelto'
        RECHAZADO = 'RECH', 'Rechazado/Spam'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    usuario_hash = models.CharField(max_length=64, db_index=True)
    
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    asunto = models.CharField(max_length=200)
    descripcion = models.TextField()
    
    imagen = models.ImageField(upload_to='evidencias/%Y/%m/', blank=True, null=True)
    
    estado = models.CharField(
        max_length=4, 
        choices=Estado.choices, 
        default=Estado.PENDIENTE
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    comentario_admin = models.TextField(blank=True, help_text="Notas internas de la resolución")

    def __str__(self):
        return f"{self.categoria} - {self.asunto} ({self.get_estado_display()})"