
FROM python:3.10-slim

WORKDIR /app

# Copia apenas o requirements primeiro para otimizar cache
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

RUN pip install faiss-gpu
# Agora copia o restante do código
COPY . /app
RUN python index_form.py

EXPOSE 5000

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "python api/app.py || (echo 'App crashed, container will not restart automatically.'; tail -f /dev/null)"]