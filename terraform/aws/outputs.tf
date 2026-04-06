output "ecr_repository_name" {
  value       = aws_ecr_repository.banking_backend.name
  description = "ECR repository name"
}

output "ecr_repository_url" {
  value       = aws_ecr_repository.banking_backend.repository_url
  description = "ECR repository URL for mobile banking backend"
}

output "minikube_ec2_public_ip" {
  value       = var.create_minikube_ec2 ? aws_instance.minikube_host[0].public_ip : null
  description = "Public IP of Minikube EC2 host (null when create_minikube_ec2=false)"
}

output "minikube_ec2_public_dns" {
  value       = var.create_minikube_ec2 ? aws_instance.minikube_host[0].public_dns : null
  description = "Public DNS of Minikube EC2 host (null when create_minikube_ec2=false)"
}

output "minikube_ssh_command" {
  value       = var.create_minikube_ec2 && var.key_name != "" ? "ssh -i <path-to-key.pem> ec2-user@${aws_instance.minikube_host[0].public_ip}" : null
  description = "Helpful SSH command template for Minikube EC2 host"
}
