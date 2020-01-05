FROM tensorflow/tensorflow:1.14.0-gpu-py3

# install debian packages
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -qq \
 && apt-get install --no-install-recommends -y \
    # install essentials
    build-essential \
    wget \
    git \
    g++ \
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

# install application
ARG KERAS_VERSION=2.3.1
ENV KERAS_BACKEND=tensorflow

RUN mkdir /app
WORKDIR /app
COPY . .

RUN pip3 install --upgrade setuptools \
    && pip3 --no-cache-dir install -U numpy==1.16 \
    && pip3 --no-cache-dir install --no-dependencies git+https://github.com/fchollet/keras.git@${KERAS_VERSION} \
    && pip3 install opencv-python \
    && pip3 install . --user \
    && pip3 install flask pybase64 \
    && python3 setup.py build_ext --inplace \
    && cd /app/snapshots \
    && wget -O resnet50_liza_alert_v1_interface.h5 https://github.com/lizaalert/lacmus/releases/download/0.1.1/resnet50_liza_alert_v1_interface.h5

EXPOSE 5000/tcp
EXPOSE 5000/udp

ENTRYPOINT ["python3", "inference.py" , "--gpu", "0"]