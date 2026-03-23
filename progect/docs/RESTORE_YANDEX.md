# Как вернуть Яндекс.Карты

Если OpenStreetMap не подойдет, вот как вернуть Яндекс.Карты:

## Вариант 1: Быстрое восстановление

Переименуйте файл бэкапа:
```bash
copy templates\index_yandex_backup.html templates\index.html
```

## Вариант 2: Получить API ключ для Яндекс.Карт

1. Перейдите: https://developer.tech.yandex.ru/services/3
2. Войдите через Яндекс аккаунт
3. Нажмите "Подключить API"
4. Выберите "JavaScript API и HTTP Геокодер"
5. Скопируйте ключ

6. Откройте `templates/index_yandex_backup.html`
7. Найдите строку:
   ```html
   <script src="https://api-maps.yandex.ru/2.1/?lang=ru_RU"
   ```
8. Замените на:
   ```html
   <script src="https://api-maps.yandex.ru/2.1/?apikey=ВАШ_КЛЮЧ&lang=ru_RU"
   ```

9. Сохраните как `templates/index.html`

## Что изменилось в OpenStreetMap версии:

✅ **Работает без API ключа** - сразу из коробки
✅ **Бесплатный поиск** - через Nominatim API
✅ **Маршруты по дорогам** - через OSRM (бесплатно)
✅ **Все функции работают** - поиск, метки, маршруты, сохранение

## Ограничения OpenStreetMap:

- Nominatim API имеет лимит 1 запрос в секунду
- Карты могут загружаться чуть медленнее
- Интерфейс немного отличается от Яндекс.Карт

Попробуйте OpenStreetMap версию - она должна работать сразу!
