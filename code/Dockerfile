FROM python:3.10
ADD . /code
WORKDIR /code   
RUN pip install -r requirements.txt
ENV TZ=America/Sao_Paulo
CMD python ${script}
