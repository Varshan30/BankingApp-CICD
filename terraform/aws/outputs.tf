output "eks_cluster_name" {
  value       = module.eks.cluster_name
  description = "EKS cluster name"
}

output "eks_cluster_endpoint" {
  value       = module.eks.cluster_endpoint
  description = "EKS cluster endpoint"
}

output "eks_cluster_version" {
  value       = module.eks.cluster_version
  description = "EKS cluster Kubernetes version"
}

output "eks_cluster_security_group_id" {
  value       = module.eks.cluster_security_group_id
  description = "EKS control plane security group ID"
}

output "vpc_id" {
  value       = module.vpc.vpc_id
  description = "VPC ID for EKS"
}

output "private_subnet_ids" {
  value       = module.vpc.private_subnets
  description = "Private subnet IDs used by EKS nodes"
}

output "ecr_repository_url" {
  value       = aws_ecr_repository.banking_backend.repository_url
  description = "ECR repository URL for mobile banking backend"
}
