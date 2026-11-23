output "app_url" {
  description = "Public address of the API (through the load balancer)"
  value       = "http://${aws_lb.main.dns_name}"
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  value = aws_ecs_service.app.name
}

output "db_endpoint" {
  description = "Private DNS name, reachable only from inside the VPC"
  value       = aws_db_instance.main.address
}

output "github_deploy_role_arn" {
  description = "Role assumed by GitHub Actions (set as repo variable AWS_ROLE_ARN)"
  value       = aws_iam_role.github_deploy.arn
}
