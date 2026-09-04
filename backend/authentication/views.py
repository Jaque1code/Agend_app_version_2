from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError
from .models import Usuario


class RegistroClienteView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        nombre = request.data.get('nombre', '').strip()
        apellido = request.data.get('apellido', '').strip()
        correo = request.data.get('correo', '').strip().lower()
        telefono = request.data.get('telefono', '').strip()
        clave = request.data.get('password') or request.data.get('clave', '')

        if not nombre or not apellido or not correo or not clave:
            return Response(
                {"error": "Nombre, apellido, correo y contraseña son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Usuario.objects.filter(correo=correo).exists():
            return Response(
                {"error": "Ya existe una cuenta registrada con este correo electrónico."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Instanciar el usuario
            usuario = Usuario(
                nombre=nombre,
                apellido=apellido,
                correo=correo,
                telefono=telefono,
                activo=True
            )

            # Asignar rol (FK o campo entero)
            if hasattr(usuario, 'id_rol_id'):
                usuario.id_rol_id = 3
            elif hasattr(usuario, 'id_rol'):
                usuario.id_rol = 3

            # Asignar contraseña según la definición del modelo
            if hasattr(usuario, 'set_password'):
                usuario.set_password(clave)
            elif hasattr(usuario, 'password'):
                usuario.password = make_password(clave)
            elif hasattr(usuario, 'clave_hash'):
                usuario.clave_hash = make_password(clave)
            elif hasattr(usuario, 'clave'):
                usuario.clave = make_password(clave)

            usuario.save()

            # Obtener ID de rol
            rol_id_val = getattr(usuario, 'id_rol_id', getattr(usuario, 'id_rol', 3))
            if hasattr(rol_id_val, 'id_rol'):
                rol_id_val = rol_id_val.id_rol

            return Response({
                "mensaje": "Cliente registrado exitosamente.",
                "usuario": {
                    "id_usuario": getattr(usuario, 'id_usuario', getattr(usuario, 'id', None)),
                    "nombre": usuario.nombre,
                    "apellido": usuario.apellido,
                    "correo": usuario.correo,
                    "id_rol": rol_id_val,
                    "rol": "CLIENTE"
                }
            }, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            return Response(
                {"error": f"Error de integridad en BD: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Error interno del servidor: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        correo = request.data.get('correo', '').strip().lower()
        clave = request.data.get('clave') or request.data.get('password', '')

        print(f"\n--- [DEBUG LOGIN] ---")
        print(f"Buscando correo recibido: '{correo}'")
        print(f"Clave recibida (len={len(clave)}): '{clave}'")

        if not correo or not clave:
            return Response({"error": "Debe ingresar correo y contraseña."}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar usuario insensible a mayúsculas/minúsculas
        usuario = Usuario.objects.filter(correo__iexact=correo).first()

        if not usuario:
            print(f"[DEBUG LOGIN] ERROR: Usuario con correo '{correo}' NO existe en la base de datos.")
            return Response({"error": "Credenciales inválidas o cuenta inactiva."}, status=status.HTTP_401_UNAUTHORIZED)

        print(f"[DEBUG LOGIN] Usuario encontrado: ID={usuario.id_usuario if hasattr(usuario, 'id_usuario') else usuario.id}")
        print(f"[DEBUG LOGIN] Atributos disponibles: {dir(usuario)}")

        # Extraer hash o clave guardada
        hash_almacenado = (
            getattr(usuario, 'clave_hash', None) or 
            getattr(usuario, 'password', None) or 
            getattr(usuario, 'clave', None) or 
            ''
        )
        print(f"[DEBUG LOGIN] Hash guardado en BD: '{hash_almacenado}'")

        # Comparaciones posibles
        coincide_directo = (clave == hash_almacenado)
        coincide_django = check_password(clave, hash_almacenado)
        
        print(f"[DEBUG LOGIN] ¿Coincidencia texto plano?: {coincide_directo}")
        print(f"[DEBUG LOGIN] ¿Coincidencia check_password?: {coincide_django}")

        valido = coincide_directo or coincide_django

        if not valido:
            print("[DEBUG LOGIN] Rechazado por contraseña incorrecta.")
            return Response({"error": "Credenciales inválidas."}, status=status.HTTP_401_UNAUTHORIZED)

        # Determinar rol
        rol_id_val = getattr(usuario, 'id_rol_id', getattr(usuario, 'id_rol', 3))
        if hasattr(rol_id_val, 'id_rol'):
            rol_id_val = rol_id_val.id_rol

        roles_map = {1: 'ADMINISTRADOR', 2: 'PROFESIONAL', 3: 'CLIENTE'}
        rol_nombre = roles_map.get(int(rol_id_val or 3), 'CLIENTE')

        print(f"[DEBUG LOGIN] ¡ÉXITO! Usuario autenticado con rol: {rol_nombre}\n")

        return Response({
            "mensaje": "Inicio de sesión exitoso",
            "usuario": {
                "id_usuario": getattr(usuario, 'id_usuario', getattr(usuario, 'id', None)),
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "correo": usuario.correo,
                "telefono": getattr(usuario, 'telefono', '') or '',
                "id_rol": int(rol_id_val or 3),
                "rol": rol_nombre
            }
        }, status=status.HTTP_200_OK)