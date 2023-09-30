FROM python:3.11.4-slim

LABEL maintainer 'Raphael Navegantes <raphaelnavegantes@gmail.com>'

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./prisma/schema.prisma ./prisma/schema.prisma

COPY ./src ./src

RUN prisma generate

EXPOSE 8000

CMD ["uvicorn", "src.main:app",  "--proxy-headers", "--host", "0.0.0.0", "--port", "8000", "--reload"]
