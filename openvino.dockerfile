FROM openvino/ubuntu18_runtime:latest

RUN mkdir /home/openvino/lacmus
WORKDIR /home/openvino/lacmus
COPY cli_inference_openvino.py .

CMD bash -c "source ${INTEL_OPENVINO_DIR}/bin/setupvars.sh"