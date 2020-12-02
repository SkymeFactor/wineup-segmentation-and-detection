FROM fnndsc/ubuntu-python3

COPY . /app

WORKDIR /app

RUN apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6

RUN python3 -m pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "/usr/bin/python3" ]

CMD [ "/app/app.py" ]