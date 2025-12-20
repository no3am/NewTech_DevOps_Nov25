provider "aws" {
    region = "eu-central-1"
}

resource "aws_instance" "web" {
    ami = "ami-015f3aa67b494b27e"
    instance_type = "t3.micro"
}

resource "aws_eip" "elastic_ip" {
    instance = aws_instance.web.id
}

output "elastic_ip" {
    value = aws_eip.elastic_ip.public_ip
}

output "instance_public_ip" {
    value = aws_instance.web.public_ip
}