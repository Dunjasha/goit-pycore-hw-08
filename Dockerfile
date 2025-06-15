# Вказуємо базовий образ Python
FROM python:3.11-slim

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо Pipfile і Pipfile.lock (якщо використовуєш pipenv)
COPY Pipfile* ./

# Встановлюємо pipenv і залежності
RUN pip install pipenv && pipenv install --system --ignore-pipfile


# Копіюємо решту файлів проєкту
COPY . .

# Вказуємо команду для запуску програми
CMD ["python", "main.py"]
    