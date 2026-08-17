from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Prefetch
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from django.utils import timezone
from django.db.models import Exists, OuterRef

from inicio_sesion.models import MateriaAsignada, PeriodoNotasMateria, Usuario, Pnf, PNFNucleo, Estudiante, EstatusEstudiante, CalendarioCargarNotas, Nucleos, PeriodoCargarNotas, Materia, Docente, DocenteAsignadoMateria

from notas_academicas.models import PlanActividadAcademica, DetallePlanActividades, HistorialTrayectoEstudiante, HistorialDetalleNota, HistorialModificacionNotas, DetallePlanEvaluacion, PromedioFinal, Calificaciones, DetalleCalificacionesUnidad

# Registrar Reparacion 

def reg_rep_not(request):
    return render(request, "registrar_reparacion.html")