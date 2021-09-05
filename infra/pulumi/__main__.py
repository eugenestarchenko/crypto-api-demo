import os
import json
import pulumi
import pulumi_eks as eks
import pulumi_aws as aws
import pulumi_kubernetes as k8s

project_name = pulumi.get_project()

# AWS named profile to use.
profile_name = os.getenv("AWS_PROFILE")

# Create an AWS provider instance using the named profile creds
# and current region.
aws_provider = aws.Provider(
    "aws-provider", profile=profile_name, region=aws.get_region().name
)

# Define the AWS provider credential opts to configure the cluster's
# kubeconfig auth.
kubeconfig_opts = eks.KubeconfigOptionsArgs(profile_name=profile_name)

# Define values
cluster_name = "eks-demo"
cluster_tag = f"kubernetes.io/cluster/{cluster_name}"

public_subnet_cidrs = ["172.31.0.0/20", "172.31.48.0/20"]

# Use 2 AZs for our cluster
avail_zones = ["us-east-1a", "us-east-1b"]

# Create VPC for EKS Cluster
vpc = aws.ec2.Vpc("eks-vpc", cidr_block="172.31.0.0/16")

igw = aws.ec2.InternetGateway(
    "eks-igw",
    vpc_id=vpc.id,
)

route_table = aws.ec2.RouteTable(
    "eks-route-table",
    vpc_id=vpc.id,
    routes=[{"cidr_block": "0.0.0.0/0", "gateway_id": igw.id}],
)

public_subnet_ids = []

# Create public subnets that will be used for the AWS Load Balancer Controller
for zone, public_subnet_cidr in zip(avail_zones, public_subnet_cidrs):
    public_subnet = aws.ec2.Subnet(
        f"eks-public-subnet-{zone}",
        assign_ipv6_address_on_creation=False,
        vpc_id=vpc.id,
        map_public_ip_on_launch=True,
        cidr_block=public_subnet_cidr,
        availability_zone=zone,
        tags={
            # Custom tags for subnets
            "Name": f"eks-public-subnet-{zone}",
            cluster_tag: "owned",
            "kubernetes.io/role/elb": "1",
        },
    )

    aws.ec2.RouteTableAssociation(
        f"eks-public-rta-{zone}",
        route_table_id=route_table.id,
        subnet_id=public_subnet.id,
    )
    public_subnet_ids.append(public_subnet.id)

# Create an EKS cluster.
cluster = eks.Cluster(
    cluster_name,
    name=cluster_name,
    vpc_id=vpc.id,
    instance_type="t2.medium",
    desired_capacity=1,
    min_size=1,
    max_size=1,
    provider_credential_opts=kubeconfig_opts,
    public_subnet_ids=public_subnet_ids,
    create_oidc_provider=True,
)

# Export the cluster's kubeconfig.
pulumi.export("kubeconfig", cluster.kubeconfig)


# AWS Load Balancer Controller

aws_lb_ns = "aws-lb-controller"
service_account_name = (
    f"system:serviceaccount:{aws_lb_ns}:aws-lb-controller-serviceaccount"
)
oidc_arn = cluster.core.oidc_provider.arn
oidc_url = cluster.core.oidc_provider.url

# Create IAM role for AWS LB controller service account
iam_role = aws.iam.Role(
    "aws-loadbalancer-controller-role",
    assume_role_policy=pulumi.Output.all(oidc_arn, oidc_url).apply(
        lambda args: json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Federated": args[0],
                        },
                        "Action": "sts:AssumeRoleWithWebIdentity",
                        "Condition": {
                            "StringEquals": {f"{args[1]}:sub": service_account_name},
                        },
                    }
                ],
            }
        )
    ),
)

with open("files/iam_policy.json") as policy_file:
    policy_doc = policy_file.read()

iam_policy = aws.iam.Policy(
    "aws-loadbalancer-controller-policy",
    policy=policy_doc,
    opts=pulumi.ResourceOptions(parent=iam_role),
)

# Attach IAM Policy to IAM Role
aws.iam.PolicyAttachment(
    "aws-loadbalancer-controller-attachment",
    policy_arn=iam_policy.arn,
    roles=[iam_role.name],
    opts=pulumi.ResourceOptions(parent=iam_role),
)

provider = k8s.Provider("provider", kubeconfig=cluster.kubeconfig)

namespace = k8s.core.v1.Namespace(
    f"{aws_lb_ns}-ns",
    metadata={
        "name": aws_lb_ns,
        "labels": {
            "app.kubernetes.io/name": "aws-load-balancer-controller",
        },
    },
    opts=pulumi.ResourceOptions(
        provider=provider,
        parent=provider,
    ),
)

service_account = k8s.core.v1.ServiceAccount(
    "aws-lb-controller-sa",
    metadata={
        "name": "aws-lb-controller-serviceaccount",
        "namespace": namespace.metadata["name"],
        "annotations": {
            "eks.amazonaws.com/role-arn": iam_role.arn.apply(lambda arn: arn)
        },
    },
)

# This transformation is needed to remove the status field from the CRD
# otherwise the Chart fails to deploy


def remove_status(obj, opts):
    if obj["kind"] == "CustomResourceDefinition":
        del obj["status"]


k8s.helm.v3.Chart(
    "lb",
    k8s.helm.v3.ChartOpts(
        chart="aws-load-balancer-controller",
        version="1.2.0",
        fetch_opts=k8s.helm.v3.FetchOpts(repo="https://aws.github.io/eks-charts"),
        namespace=namespace.metadata["name"],
        values={
            "region": "us-east-1",
            "serviceAccount": {
                "name": "aws-lb-controller-serviceaccount",
                "create": False,
            },
            "vpcId": cluster.eks_cluster.vpc_config.vpc_id,
            "clusterName": cluster.eks_cluster.name,
            "podLabels": {"stack": pulumi.get_stack(), "app": "aws-lb-controller"},
        },
        transformations=[remove_status],
    ),
    pulumi.ResourceOptions(provider=provider, parent=namespace),
)

# Create private ECR repository
# Attach the IAM policy to the EKS worker nodes

ecr_repo = aws.ecr.Repository("crypto-api-demo")

repo_policy = aws.ecr.RepositoryPolicy(
    "crypto-api-demo-ecr-repo-policy",
    policy="""{
        "Version": "2008-10-17",
        "Statement": [
            {
                "Sid": "new policy",
                "Effect": "Allow",
                "Principal": "*",
                "Action": [
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:PutImage",
                    "ecr:InitiateLayerUpload",
                    "ecr:UploadLayerPart",
                    "ecr:CompleteLayerUpload",
                    "ecr:DescribeRepositories",
                    "ecr:GetRepositoryPolicy",
                    "ecr:ListImages",
                    "ecr:DeleteRepository",
                    "ecr:BatchDeleteImage",
                    "ecr:SetRepositoryPolicy",
                    "ecr:DeleteRepositoryPolicy"
                ]
            }
        ]
    }""",
    repository=ecr_repo.name,
)

ecr_access_policy = aws.iam.Policy(
    "ecr-access-iam-policy",
    policy="""{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "ecr:BatchCheckLayerAvailability",
            "ecr:BatchGetImage",
            "ecr:GetDownloadUrlForLayer",
            "ecr:GetAuthorizationToken"
          ],
          "Resource": "*"
        }
      ]
    }""",
)

nodeInstanceRole = aws.iam.RolePolicyAttachment(
    "eks-NodeInstanceRole-policy-attach",
    role=cluster.instance_roles[0].name,
    policy_arn=ecr_access_policy.arn,
)

pulumi.export("ecr_repo_url", ecr_repo.repository_url)
