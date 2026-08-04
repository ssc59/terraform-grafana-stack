data "aws_security_group" "ssh" {
  filter {
    name   = "group-name"
    values = ["TEAM02-SSH-SG"]
  }

  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.team02.id]
  }
}