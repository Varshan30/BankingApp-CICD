aws_region   = "ap-south-1"
project_name = "banking-devops"
vpc_cidr     = "10.10.0.0/16"

cluster_version = "1.30"

node_instance_types = ["t3.micro"]
node_desired_size   = 2
node_min_size       = 2
node_max_size       = 2

cluster_public_access_cidrs = ["183.82.204.32/32"]
