# Monitoring: app logs already go to CloudWatch Logs (ecs.tf).
# Here: a dashboard with the basic metrics and email alerts via SNS.

locals {
  alb_dim = aws_lb.main.arn_suffix             # e.g. app/travel-planner-alb/abc123
  tg_dim  = aws_lb_target_group.app.arn_suffix # e.g. targetgroup/travel-planner-tg/def456
}

# ---------- Alerts delivery: SNS topic -> email ----------
resource "aws_sns_topic" "alerts" {
  name = "${local.name}-alerts"
}

# AWS sends a confirmation email after apply; alerts arrive only after "Confirm subscription"
resource "aws_sns_topic_subscription" "alerts_email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# ---------- Alarms ----------
# 1) The app returns 5xx errors
resource "aws_cloudwatch_metric_alarm" "target_5xx" {
  alarm_name          = "${local.name}-5xx-errors"
  alarm_description   = "App returned 5xx responses (more than 5 in 1 minute)"
  namespace           = "AWS/ApplicationELB"
  metric_name         = "HTTPCode_Target_5XX_Count"
  dimensions          = { LoadBalancer = local.alb_dim }
  statistic           = "Sum"
  period              = 60
  evaluation_periods  = 1
  threshold           = 5
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching" # no requests = no errors
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
}

# 2) No healthy app instance behind the load balancer (health check failing)
resource "aws_cloudwatch_metric_alarm" "no_healthy_hosts" {
  alarm_name          = "${local.name}-unhealthy"
  alarm_description   = "No healthy targets: /health check is failing"
  namespace           = "AWS/ApplicationELB"
  metric_name         = "HealthyHostCount"
  dimensions          = { LoadBalancer = local.alb_dim, TargetGroup = local.tg_dim }
  statistic           = "Minimum"
  period              = 60
  evaluation_periods  = 2
  threshold           = 1
  comparison_operator = "LessThanThreshold"
  treat_missing_data  = "breaching" # no data from the target group is also a problem
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
}

# ---------- Dashboard ----------
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = local.name

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric", x = 0, y = 0, width = 12, height = 6
        properties = {
          title   = "Requests per minute"
          region  = var.aws_region
          stat    = "Sum"
          period  = 60
          view    = "timeSeries"
          metrics = [["AWS/ApplicationELB", "RequestCount", "LoadBalancer", local.alb_dim]]
        }
      },
      {
        type = "metric", x = 12, y = 0, width = 12, height = 6
        properties = {
          title  = "5xx errors"
          region = var.aws_region
          stat   = "Sum"
          period = 60
          view   = "timeSeries"
          metrics = [
            ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", local.alb_dim, { label = "from app" }],
            ["AWS/ApplicationELB", "HTTPCode_ELB_5XX_Count", "LoadBalancer", local.alb_dim, { label = "from ALB" }],
          ]
        }
      },
      {
        type = "metric", x = 0, y = 6, width = 12, height = 6
        properties = {
          title  = "Latency (seconds)"
          region = var.aws_region
          period = 60
          view   = "timeSeries"
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", local.alb_dim, { stat = "p50", label = "p50" }],
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", local.alb_dim, { stat = "p95", label = "p95" }],
          ]
        }
      },
      {
        type = "metric", x = 12, y = 6, width = 12, height = 6
        properties = {
          title  = "CPU and memory (%)"
          region = var.aws_region
          stat   = "Average"
          period = 60
          view   = "timeSeries"
          yAxis  = { left = { min = 0, max = 100 } }
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", aws_ecs_cluster.main.name, "ServiceName", aws_ecs_service.app.name, { label = "CPU" }],
            ["AWS/ECS", "MemoryUtilization", "ClusterName", aws_ecs_cluster.main.name, "ServiceName", aws_ecs_service.app.name, { label = "Memory" }],
          ]
        }
      },
      {
        type = "metric", x = 0, y = 12, width = 12, height = 6
        properties = {
          title  = "Healthy / unhealthy instances"
          region = var.aws_region
          stat   = "Minimum"
          period = 60
          view   = "timeSeries"
          metrics = [
            ["AWS/ApplicationELB", "HealthyHostCount", "TargetGroup", local.tg_dim, "LoadBalancer", local.alb_dim, { label = "healthy" }],
            ["AWS/ApplicationELB", "UnHealthyHostCount", "TargetGroup", local.tg_dim, "LoadBalancer", local.alb_dim, { label = "unhealthy" }],
          ]
        }
      },
      {
        type = "alarm", x = 12, y = 12, width = 12, height = 6
        properties = {
          title  = "Alarms"
          alarms = [aws_cloudwatch_metric_alarm.target_5xx.arn, aws_cloudwatch_metric_alarm.no_healthy_hosts.arn]
        }
      },
    ]
  })
}
