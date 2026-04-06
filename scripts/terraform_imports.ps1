$ErrorActionPreference = "Stop"

terraform -chdir=terraform/aws import 'module.eks.module.kms.aws_kms_alias.this["cluster"]' alias/eks/banking-devops-eks
terraform -chdir=terraform/aws import 'module.eks.module.eks_managed_node_group["default"].aws_eks_node_group.this[0]' banking-devops-eks:default-20260404142904187700000001
terraform -chdir=terraform/aws import 'module.eks.aws_eks_addon.this["coredns"]' banking-devops-eks:coredns
terraform -chdir=terraform/aws import 'module.eks.aws_eks_addon.this["kube-proxy"]' banking-devops-eks:kube-proxy
terraform -chdir=terraform/aws import 'module.eks.aws_eks_addon.this["vpc-cni"]' banking-devops-eks:vpc-cni
