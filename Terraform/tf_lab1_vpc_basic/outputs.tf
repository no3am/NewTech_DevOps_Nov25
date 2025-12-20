output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_id" {
  description = "ID of the public subnet"
  value       = aws_subnet.public.id
}

output "private_subnet_id" {
  description = "ID of the private subnet"
  value       = aws_subnet.private.id
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "nat_gateway_id" {
  description = "ID of the NAT Gateway"
  value       = aws_nat_gateway.main.id
}

output "public_security_group_id" {
  description = "ID of the public subnet security group"
  value       = aws_security_group.public.id
}

output "private_security_group_id" {
  description = "ID of the private subnet security group"
  value       = aws_security_group.private.id
}

output "public_instance_id" {
  description = "ID of the EC2 instance in public subnet"
  value       = aws_instance.public.id
}

output "public_instance_private_ip" {
  description = "Private IP address of the public EC2 instance"
  value       = aws_instance.public.private_ip
}

output "public_instance_public_ip" {
  description = "Public IP address of the public EC2 instance"
  value       = aws_instance.public.public_ip
}

output "private_instance_id" {
  description = "ID of the EC2 instance in private subnet"
  value       = aws_instance.private.id
}

output "private_instance_private_ip" {
  description = "Private IP address of the private EC2 instance"
  value       = aws_instance.private.private_ip
}

output "public_route_table_id" {
  description = "ID of the public route table"
  value       = aws_route_table.public.id
}

output "private_route_table_id" {
  description = "ID of the private route table"
  value       = aws_route_table.private.id
}

output "ssh_public_instance" {
  description = "SSH command to connect to the public instance"
  value       = "ssh -i teaching_devops_keypair.pem ec2-user@${aws_instance.public.public_ip}"
}

output "ssh_private_instance_via_bastion" {
  description = "SSH command to connect to the private instance via the public instance (bastion)"
  value       = "ssh -i teaching_devops_keypair.pem -J ec2-user@${aws_instance.public.public_ip} ec2-user@${aws_instance.private.private_ip}"
}

