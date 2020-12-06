FROM python:3
WORKDIR /app
COPY flaskr /app/flaskr
COPY setup.py /app
COPY classifier/results/spam.db /app/classifier/results/spam.db
ENV FLASK_APP=app/flaskr
RUN pip install -e /app
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]