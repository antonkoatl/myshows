# Каталог сериалов
Хобби-проект каталога сериалов. Сайт можно посмотреть [тут](http://94.41.86.239:8000/myshows/).
## Ключевые особенности
### Список сериалов
- [Список сериалов](http://94.41.86.239:8000/myshows/all/). Возможность поиска по различным параметрам (жанр, тэги, год, страна, категория, тип, актёрский состав).

### Викторина
- [Викторина](http://94.41.86.239:8000/myshows/trivia/). Сыграть в викторину по имеющейся базе сериалов. Доступно 3 типа вопросов:
1. Назвать сериал по скриншоту
![Trivia Example 1](https://github.com/antonkoatl/myshows/blob/master/example/trivia_example_1.png?raw=true "Trivia Example 1")
2. Назвать сериал по актёрскому составу
![Trivia Example 2](https://github.com/antonkoatl/myshows/blob/master/example/trivia_example_2.png?raw=true "Trivia Example 2")
3.  Назвать сериал по описанию. Упомянутые в описании имена/места/организации будут закрыты.
![Trivia Example 3](https://github.com/antonkoatl/myshows/blob/master/example/trivia_example_3.png?raw=true "Trivia Example 3")

### Использование открытых инструментов машинного обучения
- [Dostoevsky](https://github.com/bureaucratic-labs/dostoevsky "Dostoevsky ") - анализ тональности текста для комментариев эпизодов.
![Episodes Example](https://github.com/antonkoatl/myshows/blob/master/example/episodes_example.png?raw=true "Episodes Example")
- [first-order-model](https://github.com/AliaksandrSiarohin/first-order-model "first-order-model") - анимирование статичных изображений актёров
![Actors Example](https://github.com/antonkoatl/myshows/blob/master/example/actors_animation.gif?raw=true "Actors Example")
- [spaCy](https://github.com/explosion/spaCy "spaCy") - выделение именованных сущностей в тексте.
![Named Entities Example 1](https://github.com/antonkoatl/myshows/blob/master/example/named_entities_1.png?raw=true "Named Entities Example 1")
![Named Entities Example 2](https://github.com/antonkoatl/myshows/blob/master/example/named_entities_2.png?raw=true "Named Entities Example 2")

### Менеджер задач Celery
- **Автоматический веб-скрапинг** - сбор новостей с сайта [myshows.me](https://myshows.me "myshows.me") каждые 8 часов.
- **Подготовка кэшированных данных** - формирование топа эпизодов по проанализированным комментариям каждый час.
- **Выполнение в фоне долгих вычислений** - анализ текстов на именованные сущности при добавлении/изменении данных.