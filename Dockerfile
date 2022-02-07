FROM pytorch/torchserve:latest-gpu

COPY torchserve /home/model-server/torchserve
COPY model /home/model-server/model
COPY torchserve/checkpoints /home/model-server/checkpoints

ENV PYTHONPATH /home/model-server/model

USER root
RUN chown model-server:model-server -R /home/model-server
USER model-server

RUN torch-model-archiver   --model-name=matting   \
    --version=1.0   \
    --model-file=/home/model-server/model/model.py   \
    --serialized-file=/home/model-server/checkpoints/resnet50.pth   \
    --handler=/home/model-server/torchserve/handler.py   \
    --export-path=/home/model-server/model-store

CMD ["torchserve", \
    "--start", \
    "--ts-config=/home/model-server/torchserve/config.properties", \
    "--model-store=/home/model-server/model-store", \
    "--models", "matting=matting.mar"]
