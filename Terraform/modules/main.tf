provider "aws" {
    region = "eu-central-1"
}

# you need to run terraform init every time you change the module (or add a new module)
module "ec2" {
    source = "./ec2" #you can also use a URL to the module
    ec2name = "web"
}

output "instance_id" {
    value = module.ec2.instance_id
}


module "security-group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "5.3.1"
}

module "ec2-instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "6.1.5"
  create_eip = true
}