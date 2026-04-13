FROM python:3.12-slim-trixie

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r app/requirements.txt

COPY . /app
WORKDIR app

# RUN python manage.py migrate
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]