data "aws_vpc" "team02" {
  id = "vpc-0470126a6455c60cd"
}

data "aws_subnet" "team02_public" {
  id = "subnet-07ee0dd0e0342e11f"
}

