from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
import datetime
    

class perfil(models.Model):
    Sexos = (
             ('M','Masculino'),
             ('F','Femenino'),
             )
    
    user = models.OneToOneField(User, related_name='perfil')
    ci = models.CharField(max_length = 10, blank=True, null=True)
    sexo = models.CharField(max_length = 1, choices = Sexos, blank=True, null=True)
    fechaNac = models.DateField(blank=True, null=True)
    tlf = models.CharField(max_length = 17,blank=True, null=True)
    foto = models.ImageField(max_length = 300,null = True, blank = True)
    
    def __str__(self):
        return self.user.first_name + " " + self.user.last_name
    
    def __unicode__(self):
        return self.user
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        perfil.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User) #Un decorador que implica el trigger (No indentar)

        
class proveedor(models.Model):
    username = models.OneToOneField(User,related_name = 'proveedor')
    nombreEmpr = models.CharField(max_length = 40)
    rif = models.CharField(max_length = 10)
    ofreceRel = models.ManyToManyField('ingrediente',through = 'ofrece')
    
class cliente(models.Model):
    username = models.OneToOneField(User,related_name = 'cliente')
    idMenu = models.ForeignKey('menu')
    
class administrador(models.Model):
    username = models.OneToOneField(User,related_name = 'administrador')
    idParam = models.ForeignKey('parametro')
    usernameP = models.ForeignKey('proveedor')
      
class ingrediente(models.Model):
    idIngr = models.AutoField(primary_key = True)
    nombre = models.CharField(max_length = 50)
    cantidad = models.PositiveIntegerField()
    # consultaRel = models.ManyToManyField(proveedor,through = 'consulta')
    def __str__(self):
        return self.nombre

class item(models.Model):
    idItem = models.AutoField(primary_key = True)
    nombre = models.CharField(max_length = 50)
    tipo = models.CharField(max_length = 1)
    precio = models.DecimalField(max_digits = 30, decimal_places = 3)
    foto = models.ImageField(max_length = 300,null = True, blank = True)
    descripcion = models.CharField(max_length = 200)
    poseeRel = models.ManyToManyField(ingrediente,through = 'posee')

    def __str__(self):
         return self.nombre

class transaccion(models.Model):
    idTrans = models.AutoField(primary_key = True)
    username = models.ForeignKey('cliente')
    monto = models.DecimalField(max_digits = 30, decimal_places = 3)
    fecha = models.DateField()

class egreso(models.Model):
    idTrans = models.AutoField(primary_key = True)
    username = models.ForeignKey(User)
    monto = models.DecimalField(max_digits = 30, decimal_places = 3)
    fecha = models.DateField(default = datetime.datetime.now)
    cantidad = models.PositiveIntegerField(default = 0)
    ingredientes = models.ForeignKey("ingrediente")

class menu(models.Model):
    idMenu = models.AutoField(primary_key = True)
    nombre = models.CharField(max_length = 50)
    contieneRel = models.ManyToManyField(item,through = 'contiene')

    def __str__(self):
        return self.nombre

class ordenActual(models.Model):
    user = models.OneToOneField(User,related_name = 'ordenActual')
    tieneRel = models.ManyToManyField(item,through = 'tieneActual')

class tieneActual(models.Model):
    orden = models.ForeignKey('ordenActual')
    item = models.ForeignKey('item')
    cantidad = models.PositiveIntegerField()
    class Meta:
        unique_together = ('orden','item')


class orden(models.Model):
    nroOrden = models.AutoField(primary_key = True)
    fecha = models.DateField()    
    user = models.ForeignKey(User)
    totalPagado = models.DecimalField(max_digits = 30, decimal_places = 3, default = 0)
    tieneRel = models.ManyToManyField(item,through = 'tiene')


class resena(models.Model):
    orden = models.OneToOneField(orden,related_name = 'resena')
    contenido = models.TextField(max_length = 1000)

class billetera(models.Model):
    idBilletera = models.AutoField(primary_key = True)
    user = models.OneToOneField(User, related_name='billetera')
    password = models.CharField(max_length = 50, default = None)
    balance = models.DecimalField(max_digits = 30, decimal_places = 3,default = 0)

    def setPassword(self, raw_password):
        self.password = make_password(raw_password)

    def verifyPassword(self, rawIntento):
        return check_password(rawIntento,self.password)


class consulta(models.Model):
    username = models.ForeignKey('proveedor')
    idIngr = models.ForeignKey('ingrediente')
    
    class Meta:
        unique_together = ('username','idIngr')        
        
class ofrece(models.Model):
    usernameP = models.ForeignKey('proveedor')
    idIngr = models.ForeignKey('ingrediente')
    precio = models.PositiveIntegerField()
    idRest = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ('usernameP','idIngr')
        
    
class pedido(models.Model):
    usernameP = models.ForeignKey('proveedor')
    usernameA = models.ForeignKey('administrador')
    idIngr = models.ForeignKey('ingrediente')
    idRest = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ('usernameP','usernameA','idIngr')    

class realiza(models.Model):
    username = models.ForeignKey('cliente')
    nroOrden = models.ForeignKey('orden')
    
    class Meta:
        unique_together = ('username','nroOrden')

class tiene(models.Model):
    orden = models.ForeignKey('orden')
    item = models.ForeignKey('item')
    cantidad = models.PositiveIntegerField()    
    class Meta:
        unique_together = ('orden','item')
        
class contiene(models.Model):
    idMenu = models.ForeignKey('MENU')
    idItem = models.ForeignKey('item')
    
    class Meta:
        unique_together = ('idMenu','idItem')
        
class posee(models.Model):
    idItem = models.ForeignKey('item')
    idIngr = models.ForeignKey('ingrediente')
    cantidad = models.PositiveIntegerField()
    class Meta:
        unique_together = ('idItem','idIngr')

    def __str__(self):
        return "{} - {}".format(self.idItem.nombre, self.idIngr.nombre)

class parametro(models.Model):
    idParam = models.PositiveIntegerField()
    horarioCierre = models.TimeField()
    horarioEntrada = models.TimeField()
    cantPuestos = models.PositiveIntegerField()
    menuActual = models.OneToOneField('menu', related_name = 'menu', null = True)
