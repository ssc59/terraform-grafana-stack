output "frontend_ip" {
  description = "Elastic IP of the frontend host (Grafana + Pushgateway)"
  value       = aws_eip.frontend.public_ip
}

output "frontend_private_ip" {
  description = "Private IP of the frontend host (used for intra-VPC communication)"
  value       = aws_instance.frontend.private_ip
}

output "backend_ip" {
  description = "Public IP of the backend host (Prometheus + Loki + Promtail)"
  value       = aws_instance.backend.public_ip
}

output "ssm_key_parameter" {
  description = "SSM Parameter Store path for the SSH private key"
  value       = aws_ssm_parameter.ssh_private_key.name
}

output "docker_app_ecr_repository_url" {
  description = "ECR repository URL for the Docker application"
  value       = aws_ecr_repository.docker_app.repository_url
}
