docker stop matting
#sh scripts/build.sh
docker run -d --rm -p=8080:8080 -p=8081:8081 -p=8082:8082 --name=matting mattingnetwork.azurecr.io/networks/matting
docker logs -f matting