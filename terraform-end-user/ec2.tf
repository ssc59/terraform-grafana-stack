data "aws_ssm_parameter" "amazon_linux_2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

data "aws_key_pair" "team02" {
  key_name = "team02-ec2-key"
}

resource "aws_ssm_parameter" "team02_private_key" {
  name        = "/team02/end-user/ssh-private-key"
  description = "SSH private key for TEAM02 end-user EC2 instances"
  type        = "SecureString"
  value       = tls_private_key.team02.private_key_openssh

  tags = {
    Project = "TEAM02"
  }
}

resource "aws_instance" "team_user" {
  for_each = var.team_users

  ami                         = data.aws_ssm_parameter.amazon_linux_2023.value
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.ssh.id]
  key_name                    = data.aws_key_pair.team02.key_name
  associate_public_ip_address = true

  tags = {
    Name    = "TEAM02-${each.value}"
    Owner   = each.value
    Project = "TEAM02"

    Role = contains(["USER04", "USER05"], each.value) ? "backend" : "frontend"
  }
}
