# Скрейпер спортивных ставок Fonbet

Этот проект предоставляет Python-скрипт для сбора данных о спортивных ставках (названия команд и коэффициенты) с сайта https://fonbet.kz/sports. Скрипт использует библиотеку SeleniumBase для автоматизации взаимодействия с браузером и извлечения данных, сохраняя их в JSON-файл для дальнейшего использования.

## Возможности

- Извлекает названия команд и коэффициенты ставок (1, X, 2) для футбольных матчей.
- Обрабатывает динамическую загрузку контента с помощью прокрутки и времени ожидания.
- Сохраняет собранные данные в JSON-файл (`outputs/betting_data.json`).
- Ведет логи процесса скрейпинга для отладки (`logs/scrape_log.txt`).
- Сохраняет скриншоты для визуальной отладки (`outputs/screenshot.png`).
- Сохраняет исходный код страницы для дальнейшего анализа (`outputs/page_source.html`).

## Требования

Перед запуском скрипта убедитесь, что у вас установлены следующие компоненты:

- **Python 3.8+**: Скрипт написан на Python.
- **SeleniumBase**: Библиотека Python для автоматизации браузера.
- **Браузер Chrome**: SeleniumBase использует Chrome для скрейпинга. Убедитесь, что Chrome установлен на вашей системе.
- **ChromeDriver**: SeleniumBase автоматически управляет ChromeDriver, но убедитесь, что версия Chrome совместима.

## Установка

1. **Клонируйте репозиторий** (если применимо):
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Настройте виртуальное окружение** (опционально, но рекомендуется):
   ```bash
   python -m venv venv
   source venv/bin/activate  # На Windows: venv\Scripts\activate
   ```

3. **Установите зависимости**:
   ```bash
   pip install seleniumbase
   ```

4. **Проверьте установку Chrome**: Убедитесь, что Google Chrome установлен на вашей системе. SeleniumBase автоматически загрузит подходящую версию ChromeDriver.

## Руководство по использованию

### 1. Подготовьте скрипт
Убедитесь, что скрипт (`scrape_fonbet.py`) находится в директории вашего проекта. Скрипт предназначен для сбора данных о ставках с сайта https://fonbet.kz/sports и сохранения результатов в `outputs/betting_data.json`.

### 2. Запустите скрипт
Выполните скрипт с помощью Python:

```bash
python scrape_fonbet.py
```

### 3. Следите за процессом
- Скрипт откроет окно браузера Chrome и перейдет на https://fonbet.kz/sports.
- Он будет ждать загрузки коэффициентов, прокручивать страницу для загрузки дополнительных событий, а затем извлекать данные.
- Логи будут записаны в `logs/scrape_log.txt` для отслеживания процесса скрейпинга.
- Скриншот страницы будет сохранен в `outputs/screenshot.png` для визуальной отладки.
- Исходный код страницы будет сохранен в `outputs/page_source.html` для дальнейшего анализа.

### 4. Проверьте результат
Собранные данные будут сохранены в `outputs/betting_data.json` в следующем формате:

```json
[
    {
        "team1": "Barcelona",
        "team2": "Borussia Dortm...",
        "odd1": "1.33",
        "oddX": "6.00",
        "odd2": "9.35"
    },
    {
        "team1": "PSG",
        "team2": "Aston Villa",
        "odd1": "1.51",
        "oddX": "4.83",
        "odd2": "6.43"
    }
    // ... другие события
]
```

Если файл пуст (`[]`), проверьте логи на наличие ошибок (см. раздел "Устранение неполадок").

### 5. Обработка CAPTCHA (если применимо)
Если обнаружена CAPTCHA от Cloudflare, скрипт предложит вам решить её вручную в течение 120 секунд:

```
Обнаружена CAPTCHA. Пожалуйста, решите её вручную в течение 120 секунд.
```

Решите CAPTCHA в окне браузера, и скрипт продолжит работу автоматически.

## Подробности скрипта

Скрипт (`scrape_fonbet.py`) выполняет следующие шаги:

### Настройка:
- Создает директории `outputs` и `logs` для хранения результатов и логов.
- Инициализирует Driver из SeleniumBase с использованием незаметного Chrome-браузера.

### Навигация:
- Переходит на https://fonbet.kz/sports.
- Проверяет наличие CAPTCHA от Cloudflare и запрашивает ручное решение, если она обнаружена.

### Извлечение данных:
- Ожидает появления элементов с коэффициентами (`factor-value--`), что указывает на готовность страницы.
- Дополнительно ждет 20 секунд, чтобы убедиться, что динамический контент (например, названия команд) полностью загружен.
- Прокручивает страницу для загрузки дополнительных событий.
- Определяет строки событий с помощью XPath-селектора, который ищет `<div>`, содержащий как названия команд (с "—"), так и коэффициенты.
- Извлекает названия команд и коэффициенты (1, X, 2) для каждого события.

### Вывод:
- Сохраняет извлеченные данные в `outputs/betting_data.json`.
- Записывает процесс в лог `logs/scrape_log.txt`.
- Сохраняет скриншот и исходный код страницы для отладки.

### Очистка:
- Закрывает браузер в блоке `finally`, чтобы обеспечить корректное завершение.

## Устранение неполадок

Если скрипт не смог извлечь данные или создал пустой `betting_data.json`, выполните следующие шаги:

### Проверьте логи:
Откройте `logs/scrape_log.txt`, чтобы найти ошибки. Распространенные проблемы:
- `"Found 0 event rows"`: XPath-селектор не нашел ни одной строки события. Возможно, структура страницы изменилась.
- `"Timeout exceeded. Betting data might not have loaded."`: Элементы с коэффициентами не загрузились в течение 180 секунд.
- `"Error extracting event data: ..."`: Произошла ошибка при извлечении названий команд или коэффициентов.

### Проверьте скриншот:
Откройте `outputs/screenshot.png`, чтобы убедиться, что данные отображаются на странице. Если данные не видны, страница могла не загрузиться корректно (например, из-за проблем с сетью или CAPTCHA).

### Проверьте исходный код страницы:
1. Откройте `outputs/page_source.html` и найдите `factor-value--`, чтобы обнаружить элемент с коэффициентами.
2. Проследите вверх по дереву DOM, чтобы найти родительский `<div>`, который содержит как коэффициенты, так и названия команд (например, `<span>` с "—").
3. Обновите селектор строк событий в скрипте, чтобы он соответствовал этому родителю. Например:
   ```xpath
   '//div[contains(@class, "table-row--") and .//span[contains(text(), "—")] and .//div[contains(@class, "factor-value--")]]'
   ```

### Обработка динамического контента:
- Если названия команд не загружаются, увеличьте время ожидания после обнаружения коэффициентов (например, измените `time.sleep(20)` на `time.sleep(30)`).
- Убедитесь, что страница полностью прокручена для загрузки всех событий.

### Проблемы с CAPTCHA:
- Если CAPTCHA не решена в течение 120 секунд, скрипт может завершиться с ошибкой. Перезапустите скрипт и решите CAPTCHA быстрее.

### Проблемы с сетью:
- Убедитесь, что у вас стабильное интернет-соединение. Прерывания сети могут привести к неудачной загрузке страницы.

## Пример вывода

После успешного выполнения `outputs/betting_data.json` может выглядеть так:

```json
[
    {
        "team1": "Barcelona",
        "team2": "Borussia Dortm...",
        "odd1": "1.33",
        "oddX": "6.00",
        "odd2": "9.35"
    },
    {
        "team1": "PSG",
        "team2": "Aston Villa",
        "odd1": "1.51",
        "oddX": "4.83",
        "odd2": "6.43"
    },
    {
        "team1": "Bodo/Glimt",
        "team2": "Lazio",
        "odd1": "3.30",
        "oddX": "3.35",
        "odd2": "2.15"
    }
]
```

Логи (`logs/scrape_log.txt`) покажут прогресс:

```
2025-04-09 19:34:11 - Starting scraper
2025-04-09 19:34:19 - Navigated to fonbet.kz/sports
2025-04-09 19:34:19 - No CAPTCHA detected
2025-04-09 19:34:22 - Odds detected, page likely loaded
2025-04-09 19:34:42 - Waited 20 seconds for dynamic content
2025-04-09 19:34:42 - Scrolling to load all events
2025-04-09 19:34:52 - Finished scrolling
2025-04-09 19:34:52 - Screenshot saved to outputs/screenshot.png
2025-04-09 19:34:52 - Page source saved to outputs/page_source.html
2025-04-09 19:34:52 - Found 10 event rows
2025-04-09 19:34:52 - Successfully extracted event: Barcelona vs Borussia Dortm...
2025-04-09 19:34:52 - Successfully extracted event: PSG vs Aston Villa
2025-04-09 19:34:52 - Successfully extracted event: Bodo/Glimt vs Lazio
2025-04-09 19:34:52 - Extracted 10 betting events
2025-04-09 19:34:52 - Betting data saved to outputs/betting_data.json
2025-04-09 19:34:55 - Browser closed
```

## Ограничения

- **Динамический контент**: Скрипт полагается на ожидание и прокрутку для загрузки контента, что может не сработать, если сайт использует сложную ленивую загрузку.
- **CAPTCHA**: Требуется ручное вмешательство для решения CAPTCHA, что может прервать автоматизацию.
- **Изменения на сайте**: Если структура сайта изменится (например, названия классов или иерархия DOM), XPath-селекторы могут потребовать обновления.
- **Ограничения по частоте запросов**: Частый скрейпинг может привести к ограничению или блокировке со стороны сайта.

## Вклад в проект

Если вы столкнулись с проблемами или у вас есть предложения по улучшению, пожалуйста, создайте issue или отправьте pull request. Приветствуются любые улучшения, такие как повышение надежности селекторов, автоматическая обработка CAPTCHA или добавление поддержки для других типов данных.

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности смотрите в файле LICENSE.