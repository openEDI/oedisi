import docker # Used docker 0.5.3
from kubernetes import client, config

# Need to set up connection with docker and kubernetes first
# On windows, this means running docker desktop.
# kubernetes should be installed using:
# winget install -e --id Kubernetes.kubectl

# Kubernetes should then be enabled in DockerDesktop under settings.

# Repository could look something like tarekelgindy/tarek-test
class KubernetesEnvironment:
    docker_images = []

    def pull_docker_images(self,image_list):
        # Create a Docker client
        docker_client = docker.from_env()
        
        for image in image_list:
            # Pull an image from Docker Hub
            docker_image = docker_client.images.pull(repository)
            self.docker_images.append(docker_image)
        

    def __init__(self,image_list):
        self.pull_docker_images(image_list)
        self.create_kubernetes_environment()


    def create_kubernetes_environment(self):
        config.load_kube_config()
        container_list = []
        image_count = 1
        for image in self.docker_images:
            container = {
                            "name": image.tags[0],
                            "image": image.id,
                            "ports": [
                                {
                                    "containerPort": 5000+image_count
                                }
                            ]
                        }
            container_list.append(container)
            image_count+=1
        
        # Create a deployment object
        deployment = client.AppsV1Api().create_namespaced_deployment(
            body={
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "example-deployment"
                },
                "spec": {
                    "replicas": 1,
                    "selector": {
                        "matchLabels": {
                            "app": "example"
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": "example"
                            }
                        },
                        "spec": {
                            "containers": container_list 
                        }
                    }
                }
            },
            namespace="default"
        )

        # Print the deployment object
        print(deployment)



