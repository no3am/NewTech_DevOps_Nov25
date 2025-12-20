# Stateful vs Stateless

# Stateful: Allows traffic in and out of the instance.

# Stateless: You have to set inbound and outbound rules for each traffic.

provider "aws" {
    region = "eu-central-1"
}

resource "aws_instance" "web" {
    ami = "ami-015f3aa67b494b27e"
    instance_type = "t3.micro"
    security_groups = [aws_security_group.webtraffic.id]
}

# Like a firewall but stateful.
resource "aws_security_group" "webtraffic" {
    name = "Allow HTTPS"
    
    ingress {
        from_port = 443
        to_port = 443
        protocol = "TCP"
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
        from_port = 443
        to_port = 443
        protocol = "TCP"
        cidr_blocks = ["0.0.0.0/0"]
    }
}
