output "vpc_id" {
  description = "TEAM02 VPC ID"
  value       = data.aws_vpc.team02.id
}

output "subnet_id" {
  description = "TEAM02 public subnet ID"
  value       = data.aws_subnet.team02_public.id
}

output "security_group_id" {
  description = "TEAM02 SSH security group ID"
  value       = data.aws_security_group.ssh.id
}

output "instance_information" {
  description = "Instance details for each RACF user"

  value = {
    for username, instance in aws_instance.team_user : username => {
      instance_id = instance.id
      public_ip   = instance.public_ip
      private_ip  = instance.private_ip
    }
  }
}

output "ansible_inventory" {
  description = "Inventory-style EC2 host listing"

  value = {
    for username, instance in aws_instance.team_user :
    username => instance.public_ip
  }
}
