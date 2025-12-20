provider "aws" {
    region = "eu-central-1"
}

variable "ingress_rules" {
    type = list(number({
        default = [80,443]
    }))
}

variable "egress_rules" {
    type = list(number({
        default = [80,443,25,53]
    }))
}

resource "aws_instance" "web" {
    ami = "ami-015f3aa67b494b27e"
    instance_type = "t3.micro"
    security_groups = [aws_security_group.webtraffic.id]
}

resource "aws_security_group" "webtraffic" {
    name = "Allow HTTPS"
    
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
