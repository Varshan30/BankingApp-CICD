variable "aws_region" {
  description = "AWS region for infrastructure"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project prefix for resource naming"
  type        = string
  default     = "banking-devops"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.10.0.0/16"
}

variable "cluster_version" {
  description = "Kubernetes version for EKS control plane"
  type        = string
  default     = "1.30"
}

variable "node_instance_types" {
  description = "Managed node group instance types"
  type        = list(string)
  default     = ["t3.large"]
}

variable "node_desired_size" {
  description = "Desired node count for managed node group"
  type        = number
  default     = 3
}

variable "node_min_size" {
  description = "Minimum node count for managed node group"
  type        = number
  default     = 2
}

variable "node_max_size" {
  description = "Maximum node count for managed node group"
  type        = number
  default     = 6
}

variable "cluster_public_access_cidrs" {
  description = "Allowed CIDRs for EKS public endpoint access"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}
