
variable "vpcname" {
    type = string
    default = "myvpc"
}

variable "sshport" {
    type = number
    default = 22
}

variable "enabled" {
    type = bool
    default = false
}

variable "mylist" {
    type = list(string) 
    default = ["apple", "banana", "cherry"]
}

variable "mymap" {
    type = map(string)
    default = {
        "apple" = "red"
        "banana" = "yellow"
        "cherry" = "red"
    }
}

# Using String Interpolation
resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"

    tags = {
        Name = var.vpcname 
    }
}

# Using List
resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"

    tags = {
        Name = var.mylist[0]
    }
}

# Using Map
resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"

    tags = {
        Name = var.mymap["apple"]
    }
}

# Using Input Variable

variable "inputname" {
  type = string
  description = "The name of the VPC"
}

resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"

    tags = {
        Name = var.inputname
    }
}

# Tuples
variable "mytuple" {
  type = tuple([string, number, string])
  default = ["apple", 1, "banana"]
}

resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"

    tags = {
        Name = var.mytuple[0]
    }
}

# Objects
variable "myobject" {
  type = object({ name = string, age = number })
  default = { name = "John", age = 30 }
}

resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"

    tags = {
        Name = var.myobject.name
    }
}
