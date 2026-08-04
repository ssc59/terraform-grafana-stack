data "aws_vpc" "team02" {
  id = "vpc-0470126a6455c60cd"
}

data "aws_subnet" "team02_public" {
  id = "subnet-07ee0dd0e0342e11f"
}

resource "aws_internet_gateway" "team02" {
  vpc_id = data.aws_vpc.team02.id

  tags = {
    Name = "TEAM02-IGW"
  }
}

resource "aws_route_table" "public" {
  vpc_id = data.aws_vpc.team02.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.team02.id
  }

  tags = {
    Name = "TEAM02-PUBLIC-RT"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id = data.aws_subnet.team02_public.id
  route_table_id = aws_route_table.public.id
}
