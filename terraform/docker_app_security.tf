resource "aws_security_group_rule" "docker_app_ingress" {
  description       = "Allow access to the Flask Docker application"
  type              = "ingress"
  from_port         = 5000
  to_port           = 5000
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.frontend.id
}
