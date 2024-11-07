Comando para buildear y levantar el container

```
sudo docker compose build && sudo docker compose up -d
```

Comando para correr las migraciones dentro del contenedor:

```
sudo docker compose run web python manage.py migrate
```

Comando para ingresar al docker con bash

```
sudo docker compose run web bash
```
