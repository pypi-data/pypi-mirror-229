source ./deploy_eks/config.sh

# delete deployment
# kubectl delete deployment {name-your-service}

# delete service
# kubectl delete service {name-your-service}

# kubectl apply -f ./deploy_eks/app-aws_gke-stg.yaml
kubectl create namespace ${NAME_DASHED}
#kubectl create deployment {name-your-service} --image=$IMAGE_PATH
# Replace the placeholder with the actual image path
IMAGE_PATH=$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$NAME:$TAG
sed "s|IMAGE_PLACEHOLDER|${IMAGE_PATH}|g" ./deploy_eks/app-aws_gke-stg.yaml > ./deploy_eks/app-aws_gke-stg-modified.yaml
kubectl apply -f ./deploy_eks/app-aws_gke-stg-modified.yaml
kubectl apply -f ./deploy_eks/app-aws_gke_service-stg.yaml

# kubectl get deployments
# kubectl get services
# kubectl get all -n $NAME
# kubectl delete all --all -n {name-your-service-dashed}

pause 'Press [Enter] key to continue...'