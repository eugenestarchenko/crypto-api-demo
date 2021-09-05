# Deploy AWS EKS cluter with ALB Ingress

To deploy EKS infrastructure, follow the below steps.

## Install Pulumi

```
brew install pulumi
Warning: pulumi 3.11.0 is already installed and up-to-date.
```

## Install Python Requirements

```
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

## Perform an initial deployment, run the following commands:

```
pulumi login

Logged in to pulumi.com as eugenestarchenko (https://app.pulumi.com/eugenestarchenko)
pulumi stack init crypto-api-infra
Created stack 'crypto-api-infra'
```

## Set AWS_PROFILE:

```
pulumi config set aws:profile yourprofile
```

## Set AWS_REGION:

```
pulumi config set aws:region us-east-1
```

## Review, Deploy the "crypto-api-infra" project

```
pulumi preview
```
```
pulumi up

     Type                 Name                    Plan
 +   pulumi:pulumi:Stack      crypto-api-infra-infra  create...
 +   ├─ pulumi:providers:aws  aws-provider            create
 +   ├─ aws:ecr:Repository    crypto-api-demo         create..
 +   ├─ aws:iam:Policy        ecr-access-iam-policy   create..
 +   ├─ aws:ec2:Vpc               eks-vpc                          create
 +   ├─ aws:ecr:RepositoryPolicy  crypto-api-demo-ecr-repo-policy  create
 +   ├─ aws:ec2:InternetGateway   eks-igw                          create
 +   ├─ aws:ec2:Subnet            eks-public-subnet-us-east-1b     create..
 +   ├─ aws:ec2:Subnet            eks-public-subnet-us-east-1a     create
 +   ├─ aws:ec2:RouteTable             eks-route-table                  create
 +   ├─ aws:ec2:RouteTableAssociation  eks-public-rta-us-east-1a        create
 +   ├─ aws:ec2:RouteTableAssociation  eks-public-rta-us-east-1b        create
 +   pulumi:pulumi:Stack               crypto-api-infra-infra           create..
 +      ├─ eks:index:ServiceRole       eks-demo-eksRole                 create
 +      ├─ eks:index:ServiceRole       eks-demo-instanceRole             create
 +      ├─ aws:ec2:SecurityGroup       eks-demo-eksClusterSecurityGroup  create
 +      ├─ aws:ec2:SecurityGroup       eks-demo-eksClusterSecurityGroup  create
 +      ├─ aws:ec2:SecurityGroup       eks-demo-eksClusterSecurityGroup  create
 +      ├─ eks:index:RandomSuffix      eks-demo-cfnStackName                  create
 +      ├─ eks:index:RandomSuffix           eks-demo-cfnStackName                  create
 +      ├─ eks:index:RandomSuffix           eks-demo-cfnStackName                  create
 +      ├─ eks:index:RandomSuffix           eks-demo-cfnStackName                  create
 +      ├─ eks:index:RandomSuffix           eks-demo-cfnStackName                  create
 +      ├─ eks:index:RandomSuffix           eks-demo-cfnStackName                  create
 +      ├─ aws:ec2:SecurityGroupRule        eks-demo-eksClusterInternetEgressRule  create
 +      ├─ aws:eks:Cluster                  eks-demo-eksCluster                    create
 +      ├─ aws:iam:InstanceProfile          eks-demo-instanceProfile               create
 +      ├─ eks:index:VpcCni                 eks-demo-vpc-cni                       create
 +      ├─ aws:iam:OpenIdConnectProvider    eks-demo-oidcProvider                  create
 +      ├─ pulumi:providers:kubernetes      eks-demo-eks-k8s                       create
 +      ├─ aws:ec2:SecurityGroup            eks-demo-nodeSecurityGroup             create
 +      ├─ kubernetes:core/v1:ConfigMap     eks-demo-nodeAccess                    create
 +      ├─ aws:ec2:SecurityGroupRule        eks-demo-eksNodeIngressRule            create..
 +      ├─ aws:ec2:SecurityGroupRule        eks-demo-eksClusterIngressRule              create
 +      ├─ aws:ec2:SecurityGroupRule        eks-demo-eksExtApiServerClusterIngressRule  create..
 +      ├─ aws:ec2:SecurityGroupRule        eks-demo-eksNodeClusterIngressRule          create..
 +      ├─ aws:ec2:SecurityGroupRule        eks-demo-eksNodeInternetEgressRule          create
 +      ├─ aws:ec2:LaunchConfiguration      eks-demo-nodeLaunchConfiguration            create
 +      ├─ aws:cloudformation:Stack         eks-demo-nodes                              create
 +   │  └─ pulumi:providers:kubernetes      eks-demo-provider                           create
 +   ├─ pulumi:providers:kubernetes         provider                                    create
 +   ├─ aws:iam:Role                        aws-loadbalancer-controller-role            create
 +   ├─ aws:iam:Role                        aws-loadbalancer-controller-role            create
 +   │  └─ aws:iam:Policy                   aws-loadbalancer-controller-policy          create
 +   │  └─ aws:iam:Policy                   aws-loadbalancer-controller-policy          create
 +   │  └─ aws:iam:PolicyAttachment         aws-loadbalancer-controller-attachment      create
 +   ├─ aws:iam:RolePolicyAttachment        eks-NodeInstanceRole-policy-attach          create
 +   pulumi:pulumi:Stack                    crypto-api-infra-infra                      create

Resources:
    + 48 to create

Do you want to perform this update?  [Use arrows to move, enter to select, type to filter]
  yes
> no
  details

Resources:
    + 55 created

Duration: 21m48s

```
## Access EKS Kubernetes cluster

```
aws eks list-clusters --region us-east-1 --profile yourprofile
aws eks --region us-east-1 --profile yourprofile update-kubeconfig --name eks-demo
kubectl get pods -A
```

### Kube config with pulumi
```
pulumi stack output kubeconfig > ~/.kube/config
```

## Destroy the "crypto-api-infra" project

```
cd $PWD/infra/pulumi
pulumi destroy
```

## Remove the "crypto-api-infra" project from Stack

```
cd $PWD/infra/pulumi
pulumi stack rm crypto-api-infra
```

## Source:

<https://www.pulumi.com/docs/get-started/>

<https://www.pulumi.com/docs/reference/pkg/>

<https://www.pulumi.com/docs/intro/concepts/state/>

<https://www.pulumi.com/docs/guides/continuous-delivery/github-actions/>

<https://github.com/pulumi/actions>
