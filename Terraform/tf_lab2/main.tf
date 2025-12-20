# Create a DB Server and output the private iP
# Create a web server and ensure it has a fixed public IP
# Create a security group for the web server opening ports 80 and 443
# Run the provided script on the web server to install Apache and a custom HTML page


provider "aws" {
    region = "eu-central-1"
}

resource "aws_instance" "web" {
    ami = "ami-015f3aa67b494b27e"
    instance_type = "t3.micro"
    security_groups = [aws_security_group.web_sg.name]
    user_data = file("server-script.sh")
    tags = {
        Name = "Web Server"
    }
}

resource "aws_instance" "db" {
    ami = "ami-015f3aa67b494b27e"
    instance_type = "t3.micro"
    tags = {
        Name = "DB Server"
    }
}

resource "aws_eip" "web_ip" {
    instance = aws_instance.web.id
}

variable "ingress_rules" {
    type = list(number({
        default = [80,443]
    }))
}

variable "egress_rules" {
    type = list(number({
        default = [80,443]
    }))
}

resource "aws_security_group" "web_sg" {
    name = "Allow Web Traffic"
    description = "Allow HTTP and HTTPS traffic"
    
    dynamic "ingress" {
        iterator = port
        for_each = var.ingress_rules
        content {
            from_port = port.value
            to_port = port.value
            protocol = "TCP"
            cidr_blocks = ["0.0.0.0/0"]
        }
    }

    dynamic "egress" {
        iterator = port
        for_each = var.egress_rules
        content {
            from_port = port.value
            to_port = port.value
            protocol = "TCP"
            cidr_blocks = ["0.0.0.0/0"]
        }
    }
}

output "web_ip" {
    value = aws_eip.web_ip.public_ip
}

output "db_private_ip" {
    value = aws_instance.db.private_ip
}