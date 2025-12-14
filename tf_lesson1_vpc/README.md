# Terraform AWS VPC Infrastructure

This Terraform configuration creates a complete AWS VPC setup with public and private subnets, internet gateway, NAT gateway, security groups, and EC2 instances.

## Architecture

- **VPC**: 10.0.0.0/16
- **Public Subnet**: 10.0.1.0/24 (with Internet Gateway)
- **Private Subnet**: 10.0.2.0/24 (with NAT Gateway for outbound internet)
- **EC2 Instances**: One in each subnet
- **Security Groups**: Configured for SSH access and inter-subnet communication

## Prerequisites

1. AWS CLI configured with appropriate credentials
2. Terraform >= 1.0 installed
3. S3 bucket `naim-tf-state` exists in `eu-central-1` region for remote state storage

## Setup

1. Copy the example variables file:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. Edit `terraform.tfvars` and set:
   - Your IP address:
     ```hcl
     my_ip = "YOUR_IP_ADDRESS/32"
     ```
     You can find your IP at https://whatismyipaddress.com/
   - Your AWS key pair name (the name you see in AWS Console):
     ```hcl
     key_pair_name = "your-key-pair-name"
     ```
     Make sure you have the corresponding `.pem` file on your local machine.

3. Initialize Terraform:
   ```bash
   terraform init
   ```

4. Review the execution plan:
   ```bash
   terraform plan
   ```

5. Apply the configuration:
   ```bash
   terraform apply
   ```

## Variables

See `variables.tf` for all available variables. Key variables:

- `my_ip`: Your IP address in CIDR format (e.g., "1.2.3.4/32") for SSH access
- `key_pair_name`: **REQUIRED** - AWS key pair name for EC2 instances (must match an existing key pair in AWS)
- `instance_type`: EC2 instance type (default: t3.micro)

## SSH Access

After applying the configuration, you can SSH into the instances:

### Public Instance (Direct Access)
```bash
ssh -i ~/.ssh/your-key-pair-name.pem ec2-user@<public-ip>
```

Or use the output command:
```bash
terraform output -raw ssh_public_instance
```

### Private Instance (Via Public Instance - Bastion)
Since the private instance has no public IP, you need to connect through the public instance:

```bash
ssh -i ~/.ssh/your-key-pair-name.pem -J ec2-user@<public-ip> ec2-user@<private-ip>
```

Or use the output command:
```bash
terraform output -raw ssh_private_instance_via_bastion
```

**Note**: Make sure your private key file (`.pem`) has the correct permissions:
```bash
chmod 400 ~/.ssh/your-key-pair-name.pem
```

## Outputs

After applying, use `terraform output` to see:
- VPC and subnet IDs
- EC2 instance IDs and IP addresses
- Security group IDs
- Route table IDs

After applying, the following will show ssh commands:
- terraform output -raw ssh_public_instance
- terraform output -raw ssh_private_instance_via_bastion

## Remote State

The configuration uses S3 backend for state storage:
- Bucket: `naim-tf-state`
- Region: `eu-central-1`

Make sure the bucket exists before running `terraform init`.

## Cleanup

To destroy all resources:
```bash
terraform destroy
```

