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

variable "environment" {
  description = "Environment tag value (for example: dev, test, prod)"
  type        = string
  default     = "dev"
}

variable "create_minikube_ec2" {
  description = "Set true to create one EC2 host and install Minikube on it"
  type        = bool
  default     = false
}

variable "ec2_size_profile" {
  description = "Beginner-friendly EC2 size: small or medium"
  type        = string
  default     = "small"

  validation {
    condition     = contains(["small", "medium"], var.ec2_size_profile)
    error_message = "ec2_size_profile must be either small or medium."
  }
}

variable "ec2_instance_type_override" {
  description = "Optional advanced override for exact instance type (for example: t3.large). Keep empty for profile-based selection."
  type        = string
  default     = ""
}

variable "key_name" {
  description = "Optional EC2 key pair name for SSH"
  type        = string
  default     = ""
}

variable "allowed_ssh_cidr" {
  description = "CIDR allowed to SSH to Minikube EC2"
  type        = string
  default     = "0.0.0.0/0"
}

variable "allowed_app_cidr" {
  description = "CIDR allowed to access app ports on Minikube EC2"
  type        = string
  default     = "0.0.0.0/0"
}
