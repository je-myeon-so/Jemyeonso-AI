FROM python:3.12.7-slim

COPY ./requirements.txt /fastapi/
COPY . /fastapi

WORKDIR /fastapi

RUN pip install pip==24.2 && pip install --no-cache-dir -r ./requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
