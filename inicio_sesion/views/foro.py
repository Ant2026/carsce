from django.shortcuts import render

def foro(request):
    return render(request, 'Foro/foro.html')

def Historia(request):
    return render(request, 'Foro/Historia.html')

def mision_vision(request):
    return render(request, 'Foro/mision_vision.html')

def psc(request):
    return render(request, 'Foro/psc.html')

def pst(request):
    return render(request, 'Foro/pst.html')

def trayectoria(request):
    return render(request, 'Foro/trayectoria.html')

def carreras_impartidas(request):
    return render(request, 'Foro/carreras_impartidas.html')

def Planificacion_Docente(request):
    return render(request, 'Foro/Planificacion_Docente.html')

def barra_lateral(request):
    return render(request, 'Estructura/Barra_Lateral.html')