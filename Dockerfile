FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY . /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install spaCy and the small Spanish model
RUN pip install spacy && python -m spacy download es_core_news_sm

EXPOSE 5000

CMD ["python", "app.py"]
