$ErrorActionPreference = "Stop"

$containerName = "jenkins"
$image = "local/jenkins-devops:lts"
$volumeName = "jenkins_home"

docker build -t $image -f jenkins/Dockerfile . | Out-Null
docker rm -f $containerName 2>$null | Out-Null
docker run -d --name $containerName --user root -p 8081:8080 -p 50000:50000 -v "${volumeName}:/var/jenkins_home" -v "/var/run/docker.sock:/var/run/docker.sock" $image | Out-Null

Write-Output "Jenkins is running at http://localhost:8081"
Write-Output "To get admin password: docker exec $containerName cat /var/jenkins_home/secrets/initialAdminPassword"