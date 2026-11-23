resource "aws_security_group" "alb" {
  name        = "${local.name}-alb-sg"
  description = "Load balancer: HTTP from the internet"
  vpc_id      = aws_vpc.main.id
  tags        = { Name = "${local.name}-alb-sg" }
}

resource "aws_security_group" "app" {
  name        = "${local.name}-app-sg"
  description = "App tasks: only from the ALB"
  vpc_id      = aws_vpc.main.id
  tags        = { Name = "${local.name}-app-sg" }
}

resource "aws_security_group" "db" {
  name        = "${local.name}-db-sg"
  description = "Database: only from the app"
  vpc_id      = aws_vpc.main.id
  tags        = { Name = "${local.name}-db-sg" }
}

# --- ALB ---
resource "aws_vpc_security_group_ingress_rule" "alb_http" {
  security_group_id = aws_security_group.alb.id
  description       = "HTTP from anywhere"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
}

resource "aws_vpc_security_group_egress_rule" "alb_to_app" {
  security_group_id            = aws_security_group.alb.id
  description                  = "Forward to app tasks"
  referenced_security_group_id = aws_security_group.app.id
  ip_protocol                  = "tcp"
  from_port                    = var.app_port
  to_port                      = var.app_port
}

# --- App ---
resource "aws_vpc_security_group_ingress_rule" "app_from_alb" {
  security_group_id            = aws_security_group.app.id
  description                  = "App port from the ALB only"
  referenced_security_group_id = aws_security_group.alb.id
  ip_protocol                  = "tcp"
  from_port                    = var.app_port
  to_port                      = var.app_port
}

resource "aws_vpc_security_group_egress_rule" "app_all" {
  security_group_id = aws_security_group.app.id
  description       = "Outbound: ECR, Secrets Manager, CloudWatch Logs, database"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

# --- Database ---
resource "aws_vpc_security_group_ingress_rule" "db_from_app" {
  security_group_id            = aws_security_group.db.id
  description                  = "PostgreSQL from the app SG only"
  referenced_security_group_id = aws_security_group.app.id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
}
