# MiBilletera — Wallet estilo Nequi

App de billetera digital (registro, login, saldo, recargas y transferencias entre usuarios)
construida con **Flask + PostgreSQL**, lista para desplegar en **Render**.

## Estructura del proyecto

```
wallet-app/
├── app.py                 # App factory principal
├── config.py               # Configuración (lee variables de entorno)
├── extensions.py           # Instancias: db, login_manager, bcrypt
├── models.py                # Modelos: User, Wallet, Transaction
├── requirements.txt
├── render.yaml              # Blueprint de despliegue en Render
├── .env.example
├── routes/
│   ├── auth.py               # /login /registro /logout
│   └── wallet.py             # /dashboard + API (/api/balance, /api/history, /api/deposit, /api/transfer)
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
└── static/
    ├── css/style.css        # Estilos visuales (tipo app móvil)
    └── js/
        ├── main.js           # Comportamiento global (flash messages)
        └── dashboard.js       # Lógica de saldo, recarga y transferencias
```

## Cómo funciona

- **Autenticación:** Flask-Login + contraseñas hasheadas con bcrypt.
- **PIN de transferencias:** cada usuario define un PIN de 4 dígitos al registrarse; se
  exige para confirmar cualquier transferencia (como en Nequi).
- **Saldo y movimientos:** se guardan en las tablas `wallets` y `transactions`; el frontend
  los consulta vía una pequeña API JSON (`/api/balance`, `/api/history`).
- **Transferencias:** se buscan por número de celular del destinatario; se valida saldo
  suficiente y PIN antes de mover el dinero.

## Instalación local

1. Crea un entorno virtual e instala dependencias:
   ```bash
   python -m venv venv
   source venv/bin/activate   # en Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Crea una base de datos PostgreSQL local (o usa Docker):
   ```bash
   createdb wallet_db
   ```

3. Copia `.env.example` a `.env` y ajusta `DATABASE_URL` y `SECRET_KEY`.

4. Corre la app:
   ```bash
   python app.py
   ```
   Abre `http://localhost:5000`.

   Las tablas se crean automáticamente al iniciar (`db.create_all()`). Para proyectos
   reales, reemplaza esto por migraciones con `flask db migrate` / `flask db upgrade`
   (Flask-Migrate ya está incluido).

## Despliegue en Render

**Opción A — Blueprint automático (recomendado):**
1. Sube este proyecto a un repositorio en GitHub.
2. En Render, ve a **New → Blueprint** y selecciona el repo.
3. Render leerá `render.yaml` y creará automáticamente:
   - Una base de datos PostgreSQL (`wallet-db`)
   - Un servicio web (`wallet-app`) con `SECRET_KEY` autogenerada y `DATABASE_URL`
     conectada a la base de datos.
4. Espera el build y listo — tu app queda en una URL tipo `https://wallet-app.onrender.com`.

**Opción B — Manual:**
1. Crea un **PostgreSQL** en Render y copia su "Internal Connection String".
2. Crea un **Web Service** apuntando a tu repo:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
3. En **Environment**, agrega:
   - `DATABASE_URL` = la cadena de conexión copiada
   - `SECRET_KEY` = cualquier cadena aleatoria segura

## Próximos pasos sugeridos

- Reemplazar `db.create_all()` por migraciones con Flask-Migrate en producción.
- Agregar límite de intentos de PIN fallidos.
- Añadir verificación de correo/celular al registrarse.
- Mostrar el historial paginado en vez de solo los últimos 30 movimientos.
