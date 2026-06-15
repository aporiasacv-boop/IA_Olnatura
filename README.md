# Asistente de Inteligencia Empresarial Olnatura

API backend construida con **FastAPI** y **Python 3.12** para el sistema de inteligencia empresarial de Olnatura.

## Descripción

Este proyecto implementa una arquitectura por capas (layered architecture) que separa responsabilidades en:

| Capa | Carpeta | Responsabilidad |
|------|---------|-----------------|
| **Presentación** | `app/api/` | Endpoints HTTP, routers, dependencias |
| **Servicios** | `app/services/` | Lógica de aplicación y orquestación |
| **Repositorios** | `app/repositories/` | Acceso a datos (CRUD, consultas) |
| **Modelos** | `app/models/` | Entidades ORM (SQLAlchemy) |
| **Schemas** | `app/schemas/` | DTOs Pydantic (entrada/salida API) |
| **Infraestructura** | `app/db/` | Conexión PostgreSQL, sesiones |
| **Core** | `app/core/` | Configuración, excepciones transversales |

## Requisitos

- Python 3.12+
- PostgreSQL 14+

## Instalación

```bash
# Clonar el repositorio y entrar al directorio del proyecto
cd IA_Olnatura

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/macOS
# Editar .env con los valores de tu entorno
```

## Ejecución local

### 1. Preparar entorno

```powershell
# Windows PowerShell — desde la raíz del proyecto
cd IA_Olnatura
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

```bash
# Linux / macOS
cd IA_Olnatura
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` si necesitas cambiar `APP_NAME`, `PORT` o `LOG_LEVEL`.

### 2. Levantar el servidor

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

O usando las variables del `.env`:

```bash
uvicorn app.main:app --reload --host %HOST% --port %PORT%   # Windows cmd
uvicorn app.main:app --reload --host $env:HOST --port $env:PORT   # PowerShell
```

### 3. Probar los endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | http://localhost:8000/ | Información de bienvenida |
| GET | http://localhost:8000/health | Estado del servicio |
| GET | http://localhost:8000/docs | Swagger UI |

Ejemplo con curl:

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

La documentación interactiva estará disponible en:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Pruebas

```bash
pytest
```

Ejecutar con más detalle:

```bash
pytest -v
```

## Estructura del proyecto

```
IA_Olnatura/
├── app/
│   ├── main.py              # Punto de entrada FastAPI
│   ├── core/                # Configuración y excepciones
│   ├── api/                 # Capa de presentación (REST)
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   ├── services/            # Capa de lógica de aplicación
│   ├── repositories/        # Capa de acceso a datos
│   ├── models/              # Entidades SQLAlchemy
│   ├── schemas/             # Schemas Pydantic
│   └── db/                  # Sesión y engine PostgreSQL
├── tests/                   # Pruebas automatizadas
├── .env.example             # Plantilla de variables de entorno
├── requirements.txt
└── README.md
```

## Variables de entorno

Consultar `.env.example` para la lista completa de variables. Las principales son:

| Variable | Descripción |
|----------|-------------|
| `APP_ENV` | Entorno: `development`, `staging`, `production` |
| `LOG_LEVEL` | Nivel de logs: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `DATABASE_URL` | URL de conexión PostgreSQL |
| `DEBUG` | Activa modo debug de FastAPI |

## Estado del proyecto

Aplicación FastAPI mínima operativa con endpoints `/` y `/health`, configuración centralizada y logging básico.

## Configuración de GitHub

El proyecto ya tiene Git inicializado con un commit en la rama `main`. Para publicarlo en GitHub y poder hacer commits libremente:

### 1. Autenticarse en GitHub CLI

```powershell
gh auth login
```

Sigue el asistente (GitHub.com → HTTPS → Login con navegador).

### 2. Crear el repositorio remoto y subir el código

```powershell
cd "C:\Users\BecarioQR\OneDrive - OLNATURA, S.A. DE CV\Escritorio\IA_Olnatura"

# Crear repo privado en tu cuenta (cambia --public si lo prefieres público)
gh repo create IA_Olnatura --private --source=. --remote=origin --push
```

Si el repositorio ya existe en GitHub, solo conecta y sube:

```powershell
git remote add origin https://github.com/TU_USUARIO/IA_Olnatura.git
git push -u origin main
```

### 3. Trabajar con commits

```powershell
git add .
git commit -m "Descripcion del cambio"
git push
```

## Licencia

Uso interno — Olnatura, S.A. de C.V.
