variable "aws_region" {
  description = "AWS region containing the TEAM02 infrastructure"
  type        = string
  default     = "us-west-1"
}

variable "vpc_cidr" {
  description = "CIDR range for the TEAM02 VPC"
  type        = string
  default     = "10.20.0.0/16"
}

variable "subnet_cidr" {
  description = "CIDR range for the TEAM02 public subnet"
  type        = string
  default     = "10.20.1.0/24"
}

variable "allowed_ssh_cidr" {
  description = "CIDR allowed to SSH into TEAM02 instances"
  type        = string
  default     = "18.144.155.75/32"

  validation {
    condition     = can(cidrnetmask(var.allowed_ssh_cidr))
    error_message = "allowed_ssh_cidr must be a valid IPv4 CIDR."
  }
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "team_users" {
  description = "RACF users receiving one EC2 instance each"
  type        = set(string)
}
