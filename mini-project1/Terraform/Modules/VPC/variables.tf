variable "vpc_tag_name" {
  type        = string
  default     = "Mini Project VPC"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
 type        = string
 description = "Public Subnet CIDR values"
 default     = "10.0.1.0/24"
}

variable "public_subnet_name" {
 type        = string
 description = "Public Subnet name"
 default     = "Mini project Subnet"
}

variable "availability_zone" {
 type        = string
 default     = "us-east-1a"
}

variable "igw_name" {
 type        = string
 default     = "Mini project IGW"
}

variable "rt_name" {
 type        = string
 default     = "Mini project Route Table"
}

variable "route_cidr" {
  type = string
  default = "0.0.0.0/0"
}