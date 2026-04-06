#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="jenkins"
IMAGE="local/jenkins-devops:lts"
VOLUME_NAME="jenkins_home"

docker build -t "${IMAGE}" -f jenkins/Dockerfile . >/dev/null
docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
docker run -d --name "${CONTAINER_NAME}" --user root -p 8081:8080 -p 50000:50000 -v "${VOLUME_NAME}:/var/jenkins_home" -v "/var/run/docker.sock:/var/run/docker.sock" "${IMAGE}" >/dev/null

echo "Jenkins is running at http://localhost:8081"
echo "To get admin password: docker exec ${CONTAINER_NAME} cat /var/jenkins_home/secrets/initialAdminPassword"