FROM tensorflow/tensorflow:2.4.2

# install debian packages
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -qq \
 && apt-get install --no-install-recommends -y \
    # install essentials
    build-essential \
    wget \
    git \
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

RUN mkdir /opt/lacmus
WORKDIR /opt/lacmus
COPY . .

RUN pip3 install --upgrade setuptools \
    && pip3 install opencv-python \
    && pip3 install git+https://github.com/lacmus-foundation/keras-resnet.git \
    && pip3 install . \
    && python3 setup.py build_ext --inplace 

ENTRYPOINT ["bash"]