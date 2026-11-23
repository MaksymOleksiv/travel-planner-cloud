resource "aws_ecr_repository" "app" {
  name                 = local.name
  image_tag_mutability = "IMMUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep only the last 10 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 10
      }
      action = { type = "expire" }
    }]
  })
}

resource "terraform_data" "initial_image" {
  triggers_replace = [aws_ecr_repository.app.repository_url, var.image_tag]

  provisioner "local-exec" {
    command = "${path.module}/../scripts/push-image.sh ${aws_ecr_repository.app.repository_url} ${var.image_tag} ${var.aws_region}"
  }
}
