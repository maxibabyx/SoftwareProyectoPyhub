from django.conf.urls import url
from Inventario import views


'''
	Permite redireccionar todos los path que comienzan con URL:
	http://servidor/inventario/

'''

urlpatterns = [
     url(r'^mostrar/$', views.mostrarInventario),
]