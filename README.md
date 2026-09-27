# Менеджер задач (Python)

[![hexlet-check](https://github.com/mrTelnor/python-project-52/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/mrTelnor/python-project-52/actions)

На практике узнаете о проектировании баз данных, PaaS, мониторинге ошибок, ORM, фреймворке Django, шаблонизации и Tailwind CSS.

Учебный проект Хекслета: https://ru.hexlet.io/programs/python
Как это должно работать: https://files.hexlet.app/a/0rkpse
Задеплоенное приложение: https://python-project-52-7cjv.onrender.com/

## Стек

- Python 3.13, Django
- PostgreSQL в продакшене, SQLite локально
- gunicorn, WhiteNoise
- uv, Ruff
- Render

## Установка

Нужны [uv](https://docs.astral.sh/uv/) и `make`. Команды ниже — для PowerShell.

```powershell
git clone https://github.com/mrTelnor/python-project-52.git
cd python-project-52
make install
Copy-Item .env.example .env
```

Заполните `.env`:

| Переменная | Назначение |
|---|---|
| `SECRET_KEY` | секретный ключ Django |
| `DEBUG` | `true` для локальной разработки, `false` в продакшене |
| `DATABASE_URL` | адрес PostgreSQL; для локального SQLite удалите эту строку из `.env` — пустое значение не допускается |

Сгенерировать `SECRET_KEY`:

```powershell
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Собрать статику и применить миграции:

```powershell
make setup
```

## Использование

```powershell
make start   # запустить сервер разработки: http://127.0.0.1:8000/
make lint    # проверить код Ruff
```

---

<details>
<summary>Автоматические тесты Хекслета</summary>

Тесты запускаются на каждый коммит. За запуск отвечает файл `.github/workflows/hexlet-check.yml` — не удаляйте и не переименовывайте ни его, ни репозиторий.

</details>

## О Хекслете

[Хекслет](https://ru.hexlet.io/) — школа программирования: авторские программы обучения с практикой, поддержкой наставников и реальными проектами, которые остаются в резюме. Этот репозиторий — один из таких проектов.
