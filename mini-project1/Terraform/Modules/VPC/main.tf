
resource "aws_vpc" "main" {
 cidr_block = var.vpc_cidr
 
 tags = {
   Name = var.vpc_tag_name
 }
}

resource "aws_subnet" "public_subnet" {
  vpc_id = aws_vpc.main.id
  cidr_block = var.public_subnet_cidr
  availability_zone = var.availability_zone
  map_public_ip_on_launch = true

  tags = {
    Name = var.public_subnet_name
  }
}


resource "aws_internet_gateway" "gw" {
 vpc_id = aws_vpc.main.id

 tags = {
   Name = var.igw_name
 }
}

resource "aws_route_table" "public" {
 vpc_id = aws_vpc.main.id

 tags = {
   Name = var.rt_name
 }
}

resource "aws_route" "public_internet_access" {
  route_table_id = aws_route_table.public.id
  gateway_id = aws_internet_gateway.gw.id
  destination_cidr_block = var.route_cidr
}


resource "aws_route_table_association" "public_subnet_asso" {
  route_table_id = aws_route_table.public.id
  subnet_id = aws_subnet.public_subnet.id
}