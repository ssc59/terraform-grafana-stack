data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "tls_private_key" "monitoring" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "monitoring" {
  key_name   = "monitoring-key"
  public_key = tls_private_key.monitoring.public_key_openssh

  tags = {
    Project = var.project_tag
  }
}

resource "aws_ssm_parameter" "ssh_private_key" {
  name        = "/monitoring/ssh-private-key"
  description = "Private SSH key for monitoring EC2 instances"
  type        = "SecureString"
  value       = tls_private_key.monitoring.private_key_pem

  tags = {
    Project = var.project_tag
  }
}

resource "aws_instance" "frontend" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.frontend.id]
  key_name               = aws_key_pair.monitoring.key_name

  iam_instance_profile = "team02-frontend-worker"

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
  }

  tags = {
    Name    = "team02-HR-portal-frontend"
    Project = var.project_tag
    Role    = var.frontend_role_tag
  }
}

resource "aws_eip" "frontend" {
  instance = aws_instance.frontend.id
  domain   = "vpc"

  tags = {
    Name    = "monitoring-frontend-eip"
    Project = var.project_tag
  }

  depends_on = [aws_internet_gateway.monitoring]
}

resource "aws_instance" "backend" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.backend.id]
  key_name               = aws_key_pair.monitoring.key_name

  tags = {
    Name    = "team02-backend"
    Project = var.project_tag
    Role    = var.backend_role_tag
  }
}
