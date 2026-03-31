variable "sg_name" {
  type        = string
  default     = "mini project sg"
}

variable "sg_description" {
  type        = string
  default     = "Allow SSH, HTTP, HTTPS, Flask"
}
variable "vpc_id" {}

variable "my_ip" {
  description = "Your public IP with /32"
}




