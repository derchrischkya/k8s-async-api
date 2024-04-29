NAMESPACE = rabbitmq
NAME = rabbitmq
K8S_NAME = k8s-local

# Deploy Kind k8s cluster if not already running
# + Start rabbitmq on K8S via Helm and force namespace creation
# Start python container to interact with rabbitmq with installed confluent_rabbitmq
start:
	kind get clusters | grep -q ${K8S_NAME} || kind create cluster --name ${K8S_NAME} --config ./kind-cluster.yaml
	kubectl create namespace ${NAMESPACE} || true
	helm install ${NAME} --namespace ${NAMESPACE} -f helm/rabbitmq/values.yaml --create-namespace oci://registry-1.docker.io/bitnamicharts/rabbitmq
	kubectl apply -f ./api.yaml
stop:
	kind delete cluster --name ${K8S_NAME}

uninstall:
	helm uninstall ${NAME} --namespace ${NAMESPACE}