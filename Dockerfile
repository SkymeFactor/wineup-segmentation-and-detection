FROM tensorflow/tensorflow

COPY . /app

WORKDIR /app

RUN apt update && apt install -y --no-install-recommends  wget unzip libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6

#RUN /app/setup.sh

RUN python3 -m pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT bash -c "/usr/bin/python3 /app/app.py"