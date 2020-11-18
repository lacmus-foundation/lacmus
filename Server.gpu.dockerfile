FROM tensorflow/tensorflow:2.3.0-gpu

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
    ffmpeg \
    libsm6 \
    libxext6 \
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
ENV KERAS_BACKEND=tensorflow

RUN mkdir /app
WORKDIR /app
COPY . .

RUN pip3 install --upgrade setuptools \
    && pip3 --no-cache-dir install keras==2.4.3 \
    && pip3 install opencv-python \
    && pip3 install . --user \
    && pip3 install flask pybase64 \
    && python3 setup.py build_ext --inplace

EXPOSE 5000/tcp
EXPOSE 5000/udp

ENTRYPOINT ["python3", "inference.py" , "--gpu", "0"]