from django.urls import path
from inicio_sesion import views

urlpatterns = [
    path('', views.foro, name="foro"),
    path('inicio_sesion/', views.inicio_sesion, name="inicio_sesion"),
    
    path('buscar_usuario/', views.buscar_usuario, name="buscar_usuario"),
    path('panel_recuperar_credenciales/', views.panel_recuperar_credenciales, name="panel_recuperar_credenciales"),

    path('recuperar_contrasenia/', views.recuperar_contrasenia, name="recuperar_contrasenia"),

    path('recuperar_usuario/', views.recuperar_usuario, name="recuperar_usuario"),

    path('panel_registro/', views.panel_registro, name="panel_registro"),

    path('confirmar_registro_personal/', views.confirmar_registro_personal, name="confirmar_registro_personal"),
    path('pre_registro_personal/', views.pre_registro_personal, name="pre_registro_personal"),
    path('pnfs_nucleos/', views.pnfs_nucleos, name="pnfs_nucleos"),
    path('datos_registro/', views.datos_registro, name="datos_registro"),
    
    path('panel_usuario/', views.panel_usuario, name="panel_usuario"),
    path('cerrar_sesion/', views.cerrar_sesion, name="cerrar_sesion"),

    path('inscripcion_estudiante/', views.inscripcion_estudiante, name="inscripcion_estudiante"),
]