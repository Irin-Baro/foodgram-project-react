[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)
<br>

# Cервис Foodgram - продуктовый помощник

- [Описание](#description)
- [Установка](#run)
- [Создание Docker-образов](#docker)
- [Деплой на сервере](#deploy)
- [Автор](#author)


## Описание <a id=description></a>

Проект Foodgram позволяет пользователям:
  - регистрироваться;
  - создавать свои рецепты, редактировать и удалять их;
  - просматривать рецепты других пользователей;
  - добавлять рецепты других пользователей в "Избранное" и в "Корзину покупок";
  - скачивать список ингредиентов для рецептов, добавленных в "Корзину"
  - подписываться на других пользователей;

Проект доступен по адресу [https://foodgram-baro.hopto.org/](https://foodgram-baro.hopto.org/)
email: 
```sh
admin-email@ya.ru
```
password:
```sh
1
```

## Установка <a id=run></a>

1. Клонируйте репозиторий:

    ```sh
    git clone https://github.com/Irin-Baro/foodgram-project-react
    ```
    ```sh
    cd foodgram-project-react
    ```
2. Создайте файл .env и заполните его своими данными. (Пример в корневой директории проекта в файле .env.example)

### Создание Docker-образов <a id=docker></a>

1.  Замените username на ваш логин на DockerHub:

    ```sh
    cd frontend
    docker build -t username/foodgram_frontend .
    cd ../backend
    docker build -t username/foodgram_backend . 
    ```

2. Загрузите образы на DockerHub:

    ```sh
    docker push username/foodgram_frontend
    docker push username/foodgram_backend
    ```

### Деплой на сервере <a id=deploy></a>

1. Подключитесь к удаленному серверу:

    ```sh
    ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера 
    ```

2. Создайте на сервере директорию foodgram через терминал:

    ```sh
    mkdir foodgram
    ```

3. В директории foodgram/ разместите файл .env со своими данными:

    ```sh
    touch .env
    nano .env
    ```

4. Изменение настройки location в секции server:

    ```sh
    sudo nano /etc/nginx/sites-enabled/default
    ```

    ```sh
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8000;
    }
    ```

5. Проверка и перезапуск Nginx:

    ```sh
    sudo nginx -t
    sudo service nginx reload
    ```

6. Установка docker compose на сервер:

    ```sh
    sudo apt update
    sudo apt install curl
    curl -fSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo apt-get install docker-compose-plugin
    ```

7. Запуск docker compose:

    ```sh
    sudo docker compose -f docker-compose.production.yml up -d
    ```

## Автор <a id=author></a>
 
- [Ирина Баронская](https://github.com/Irin-Baro)

