from django.test import TestCase
from django.urls import reverse

from inicio_sesion.models import Contacto, Usuario, VerificacionCodigo


class RecuperarUsuarioTests(TestCase):
    def test_recuperar_usuario_without_credentials_redirects(self):
        usuario = Usuario.objects.create(
            nombres="Ana",
            apellidos="Pérez",
            genero="F",
            cedula_identidad="12345678",
            estado_civil="Soltera",
        )
        Contacto.objects.create(
            correo_electronico="test@example.com",
            id_usuario=usuario,
        )
        VerificacionCodigo.objects.create(
            cedula_identidad=usuario.cedula_identidad,
            token="token-123",
            codigo="123456",
            creado="2024-01-01T00:00:00Z",
            activo=0,
            descripcion="recuperacion",
        )

        session = self.client.session
        session["flujo_verificacion"] = True
        session["correo_verificado"] = True
        session["token_recuperacion"] = "token-123"
        session["CI_usuario"] = usuario.cedula_identidad
        session.save()

        response = self.client.get(reverse("recuperar_usuario"))

        self.assertRedirects(response, reverse("buscar_usuario"))
