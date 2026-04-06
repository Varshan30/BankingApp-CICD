aws_region   = "ap-south-1"
project_name = "banking-devops"
environment  = "dev"

create_minikube_ec2 = false
ec2_size_profile    = "small"
ec2_instance_type_override = ""
key_name            = ""

allowed_ssh_cidr = "YOUR_PUBLIC_IP/32"
allowed_app_cidr = "YOUR_PUBLIC_IP/32"
