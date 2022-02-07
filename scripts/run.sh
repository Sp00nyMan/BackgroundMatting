docker stop matting
docker rm matting
docker system prune -f
docker build --tag=mattingnetwork.azurecr.io/networks/matting .
docker run -d -p 8080:8080 -p 8081:8081 -p 8082:8082 --name=matting \
mattingnetwork.azurecr.io/networks/matting
docker logs -f matting