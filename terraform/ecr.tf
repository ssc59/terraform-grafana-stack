resource "aws_ecr_repository" "docker_app" {
  name                 = "terraform-docker-app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name    = "terraform-docker-app"
    Project = "terraform-grafana-stack"
  }
}

resource "aws_ecr_lifecycle_policy" "docker_app" {
  repository = aws_ecr_repository.docker_app.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep only the latest 10 images"

        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }

        action = {
          type = "expire"
        }
      }
    ]
  })
}
