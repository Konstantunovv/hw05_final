# Соцсеть Yatube

Социальная сеть блогеров. Повзоляет написание постов и публикации их в отдельных группах, подписки на посты, добавление и удаление записей и их комментирование.
Подписки на любимых блогеров.

## Инструкции по установке
***- Клонируйте репозиторий:***
```
HTTPS
https://github.com/Konstantunovv/yatube_project.git
```
```
SSH
git@github.com:Konstantunovv/yatube_project.git
```

***- Установите и активируйте виртуальное окружение:***
- для MacOS
```
python3 -m venv venv
source venv/bin/activate
```
- для Windows
```
python -m venv venv
source venv/bin/activate
source venv/Scripts/activate
```

***- Установите зависимости из файла requirements.txt:***
```
pip install -r requirements.txt
```

***- Примените миграции:***
```
python manage.py migrate
```

***- В папке с файлом manage.py выполните команду:***
```
python manage.py runserver
```
