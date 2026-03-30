aws_region       = "us-east-1"
project_name     = "banking-devops"
vpc_cidr         = "10.10.0.0/16"

cluster_version = "1.30"

node_instance_types = ["t3.medium"]
node_desired_size   = 2
node_min_size       = 2
node_max_size       = 4

cluster_public_access_cidrs = ["0.0.0.0/0"]
