# Proyecto Backend de Edukar

## Crear el virtual environment

Corremos el siguiente comando para crear el virtual environment del proyecto con el nombre **venv**
```bash
python -m venv venv
```

Posteriormente procedemos a instalar las dependencias **(Linux)**
```bash
source venv/bin/activate
```

Para **Windows** correr el siguiente comando:
```powershell
venv/Script/activate
```

## Instalación de librerías
```bash
pip install -r requirements.txt
```

## Aplicando creación de tablas y contenido básico
Aplicar las migraciones para crear las tablas
```bash
python manage.py migrate
```

Procedemos a crear nuestro superusuario
```bash
python manage.py createsuperuser
```
La línea de comando te pedirá rellenar la siguiente información para tu superusuario: **username**, **email**, **contraseña** y **confirmar contraseña**. Una vez realizado esos pasos tendrás disponible tu superusuario.

A continuación, creamos la sección **Curso** con las subsecciones por defecto:
```bash
python manage.py setsections
```

## Correr el servidor
```bash
python manage.py runserver
```
