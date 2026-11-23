variable "aws_region" {
  description = "AWS region (this account allows only eu-north-1)"
  type        = string
  default     = "eu-north-1"
}

variable "project_name" {
  description = "Prefix for all resource names"
  type        = string
  default     = "travel-planner"
}

variable "alert_email" {
  description = "Email for budget alerts (set in terraform.tfvars, which is not committed)"
  type        = string
}

variable "monthly_budget_usd" {
  description = "Monthly cost budget; alerts at 50% and 100%"
  type        = number
  default     = 10
}

variable "image_tag" {
  description = "Image tag deployed by Terraform on first apply; CI/CD later deploys commit-hash tags"
  type        = string
  default     = "initial"
}

variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "db_name" {
  type    = string
  default = "travel_planner"
}

variable "db_username" {
  type    = string
  default = "travel_admin"
}

variable "app_port" {
  type    = number
  default = 8000
}
