variable "ami_id" {}
variable "instance_type" {}
variable "subnet_id" {}
variable "sg_id" {}
variable "key_name" {}
variable "volume_size" {}
variable "instance_name" {}
variable "environment" {}
variable "project" {}
variable "repo_url" {
  type = string
  default = "https://github.com/bahjatnsasra/NewTech_DevOps_Nov25.git"
}