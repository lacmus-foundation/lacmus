FROM tensorflow/tensorflow:1.12.0-py3

# install debian packages
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -qq \
 && apt-get install --no-install-recommends -y \
    # install essentials
    build-essential \
    g++ \
    git \
    wget \
    apt-transport-https \
    curl \
    cython \
    # requirements for numpy
    libopenblas-base \
    python3-numpy \
    python3-scipy \
    # requirements for keras
    python3-h5py \
    python3-yaml \
    python3-pydot \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# manually update numpy
RUN pip3 --no-cache-dir install -U numpy==1.13.3

ARG KERAS_VERSION=2.2.4
ENV KERAS_BACKEND=tensorflow
RUN pip3 --no-cache-dir install --no-dependencies git+https://github.com/fchollet/keras.git@${KERAS_VERSION}

# quick test and dump package lists
RUN python3 -c "import tensorflow; print(tensorflow.__version__)" \
 && dpkg-query -l > /dpkg-query-l.txt \
 && pip3 freeze > /pip3-freeze.txt

# install application
RUN mkdir /app && cd /app && mkdir install

WORKDIR /app/install

# git clone
RUN wget -q https://packages.microsoft.com/config/ubuntu/16.04/packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb
RUN apt-get update && apt-get install -y dotnet-sdk-2.2

RUN pip3 install --upgrade setuptools

COPY ./RetinaNet ./RetinaNet

RUN cd RetinaNet \
    && pip3 install opencv-python \
    && pip3 install numpy --user && pip3 install . --user \
    && python3 setup.py build_ext --inplace && pip3 install flask

COPY ./RescuerLaApp ./RescuerLaApp

RUN cd RescuerLaApp \
    && dotnet restore && dotnet add package Avalonia.Skia.Linux.Natives --version 1.68
RUN cd RescuerLaApp \
    && dotnet publish --framework netcoreapp2.2 --runtime="ubuntu.16.10-x64" -c Release -o /app

RUN cp -r /app/install/RetinaNet /app/python

RUN cd /app/python/snapshots \
    && wget -O resnet50_liza_alert_v1_interface.h5 https://github.com/gosha20777/rescuer-la/releases/download/0.1.1/resnet50_liza_alert_v1_interface.h5

RUN apt-get install -y libgtk-3-dev python3-tk

WORKDIR /app
ENTRYPOINT ["/app/RescuerLaApp"]