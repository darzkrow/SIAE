# Guía de Configuración y Despliegue 🛠️

## 📋 Requisitos Previos
- Docker & Docker Compose
- Python 3.10+ (si se corre localmente)
- Redis Server (para notificaciones)

---

## 🚀 Inicio Rápido con Docker

La forma más eficiente de levantar el proyecto es utilizando los perfiles de Docker Compose.

```bash
# Levantar todo el stack (Backend + Frontend + DB + Redis)
docker-compose up --build
```

---

## 🔧 Configuración Local (Entorno de Desarrollo)

### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate en Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## ⚙️ Variables de Entorno (.env)
Asegúrate de configurar los siguientes valores:
- `DEBUG`: `True` para desarrollo.
- `DATABASE_URL`: Conexión a PostgreSQL.
- `REDIS_URL`: Conexión a Redis para Channels/Notificaciones.
- `SECRET_KEY`: Llave secreta de Django.

---

## 🧪 Pruebas
Para ejecutar el set de pruebas completo del sistema modularizado:
```bash
cd backend
pytest  # O python manage.py test
```
