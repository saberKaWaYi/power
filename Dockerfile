FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install django djangorestframework

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]