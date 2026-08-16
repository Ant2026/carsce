from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone

from inicio_sesion.models import GrupoActividad, Actividad, CalendarioAcademico, PeriodoCargarNotas, Bitacora