docker push europe-west1-docker.pkg.dev/mattingnetwork/networks/matting
gcloud ai-platform versions delete v1 --region=europe-west1 --model=networks
gcloud beta ai-platform versions create v1 \
--region=europe-west1 \
--model=networks \
--machine-type=n1-standard-2 \
--accelerator count=1,type=nvidia-tesla-v100 \
--image=europe-west1-docker.pkg.dev/mattingnetwork/networks/matting \
--ports=8080 \
--health-route=/ping \
--predict-route=/predictions/matting
