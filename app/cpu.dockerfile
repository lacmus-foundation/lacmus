FROM tensorflow/tensorflow:2.3.0

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
 && rm -rf /var/lib/apt/lists/* \
    # pip requirements
 && pip3 install --upgrade setuptools \
 && pip3 --no-cache-dir install \
    keras==2.4.3 \
    opencv-python \
    fastapi \
    fastapi-utils \
    python-multipart \
    uvicorn \
    python-dotenv

WORKDIR /opt/lacmus
COPY . .
RUN pip3 install . --user \
    && python3 setup.py build_ext --inplace \
    && mv /opt/lacmus/app/cpu.env /opt/lacmus/app/.env

WORKDIR /opt/lacmus/app
EXPOSE 5000/tcp
EXPOSE 5000/udp
ENV TEST="test"

ENTRYPOINT ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "5000"]