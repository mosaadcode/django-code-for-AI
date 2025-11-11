FROM python:3.11-slim-buster                    
ENV PYTHONBUFFERED=1                    
ENV PORT 8000       

RUN apt update && apt install -y git

WORKDIR /app
# COPY . /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt     

# Run app with gunicorn command
CMD gunicorn smart_mfis.wsgi:application --bind 0.0.0.0:"${PORT}"


EXPOSE ${PORT}                          