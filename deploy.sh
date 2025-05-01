#!/bin/bash

echo "=========================================================="
echo "    Prometheus Host Type Exporter Deployment"
echo "=========================================================="
echo ""
echo "Please select deployment method:"
echo "1) Deploy on VM directly"
echo "2) Deploy in Docker container"
echo ""
read -p "Enter your choice (1 or 2): " choice

vm_port=8080
container_port=8081

case $choice in
  1)
    echo "Deploying directly on VM..."
    ansible-playbook -i ansible/inventory ansible/playbook.yml -e "deployment_type=vm vm_port=$vm_port" -K
    result=$?
    if [ $result -eq 0 ]; then
      echo "Service successfully deployed on VM, available at http://VM_IP:$vm_port"
      echo "Deployment completed!"
    else
      echo "Error: Deployment failed with exit code $result"
      exit $result
    fi
    ;;
  2)
    echo "Deploying in Docker container..."
    ansible-playbook -i ansible/inventory ansible/playbook.yml -e "deployment_type=container container_port=$container_port" -K
    result=$?
    if [ $result -eq 0 ]; then
      echo "Service successfully deployed in container, available at http://VM_IP:$container_port"
      echo "Deployment completed!"
    else
      echo "Error: Deployment failed with exit code $result"
      exit $result
    fi
    ;;
  *)
    echo "Invalid choice. Exiting."
    exit 1
    ;;
esac