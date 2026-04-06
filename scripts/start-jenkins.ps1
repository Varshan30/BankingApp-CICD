$ErrorActionPreference = "Stop"

$containerName = "jenkins"
$image = "jenkins/jenkins:lts"

$existing = docker ps -a --filter "name=^${containerName}$" --format "{{.Names}}"
if ($existing -eq $containerName) {
  docker start $containerName | Out-Null
} else {
  docker run -d --name $containerName -p 8081:8080 -p 50000:50000 $image | Out-Null
}

Write-Output "Jenkins is running at http://localhost:8081"
Write-Output "To get admin password: docker exec $containerName cat /var/jenkins_home/secrets/initialAdminPassword"