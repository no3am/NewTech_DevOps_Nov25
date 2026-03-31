
  module "vpc" {
    source = "./Modules/VPC"
  }

  module "sg" {
    source = "./Modules/SG"

    vpc_id = module.vpc.vpc_id
    my_ip  = "93.175.45.172/32"
  }

  module "ec2" {
  source = "./Modules/EC2"

  ami_id        = "ami-0ecb62995f68bb549"
  instance_type = "t3.micro"
  subnet_id     = module.vpc.public_subnet_id
  sg_id         = module.sg.sg_id
  key_name      = "my-key"
  volume_size   = 10

  instance_name = "mini-project1-ec2_2"
  environment   = "dev"
  project       = "mini-project"
}