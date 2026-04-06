locals {
  # Simple size presets for beginners.
  instance_type_by_profile = {
    small  = "t3.micro"
    medium = "t3.medium"
  }

  selected_instance_type = var.ec2_instance_type_override != "" ? var.ec2_instance_type_override : lookup(local.instance_type_by_profile, var.ec2_size_profile, "t3.micro")

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023*-x86_64"]
  }
}

resource "aws_ecr_repository" "banking_backend" {
  name                 = "${var.project_name}/mobile-banking-backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.tags
}

resource "aws_security_group" "minikube" {
  count = var.create_minikube_ec2 ? 1 : 0

  name        = "${var.project_name}-minikube-sg"
  description = "Security group for Minikube EC2 host"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.allowed_app_cidr]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.allowed_app_cidr]
  }

  ingress {
    description = "Kubernetes NodePort range"
    from_port   = 30000
    to_port     = 32767
    protocol    = "tcp"
    cidr_blocks = [var.allowed_app_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags, {
    Name = "${var.project_name}-minikube-sg"
  })
}

resource "aws_instance" "minikube_host" {
  count = var.create_minikube_ec2 ? 1 : 0

  ami                         = data.aws_ami.amazon_linux_2023.id
  instance_type               = local.selected_instance_type
  subnet_id                   = data.aws_subnets.default.ids[0]
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.minikube[0].id]
  key_name                    = var.key_name != "" ? var.key_name : null

  user_data = <<-EOF
    #!/bin/bash
    set -eux

    dnf update -y
    dnf install -y docker curl conntrack
    systemctl enable --now docker
    usermod -aG docker ec2-user

    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    install -m 0755 kubectl /usr/local/bin/kubectl

    curl -Lo /usr/local/bin/minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    chmod +x /usr/local/bin/minikube

    sudo -u ec2-user /usr/local/bin/minikube start --driver=docker --cpus=1 --memory=1400mb
  EOF

  root_block_device {
    volume_size = 12
    volume_type = "gp3"
  }

  tags = merge(local.tags, {
    Name = "${var.project_name}-minikube-host"
  })
}
