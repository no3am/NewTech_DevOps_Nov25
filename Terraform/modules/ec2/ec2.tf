variable "ec2name" {
    type = string
}

resource "aws_instance" "web" {
    ami = "ami-015f3aa67b494b27e"
    instance_type = "t3.micro"
    tags = {
        Name = var.ec2name
    }
}

output "instance_id" {
    value = aws_instance.web.id
}