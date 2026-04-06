#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="jenkins"
IMAGE="jenkins/jenkins:lts"

if docker ps -a --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
  docker start "${CONTAINER_NAME}" >/dev/null
else
  docker run -d --name "${CONTAINER_NAME}" -p 8080:8080 -p 50000:50000 "${IMAGE}" >/dev/null
fi

echo "Jenkins is running at http://localhost:8080"
echo "To get admin password: docker exec ${CONTAINER_NAME} cat /var/jenkins_home/secrets/initialAdminPassword"