#!/usr/bin/env bash
set -euo pipefail

REPO_URL="$1"
TAG="$2"
REGION="$3"
REGISTRY="${REPO_URL%%/*}"
REPO_NAME="${REPO_URL#*/}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if aws ecr describe-images --region "$REGION" --repository-name "$REPO_NAME" \
     --image-ids imageTag="$TAG" >/dev/null 2>&1; then
  echo "Image $REPO_URL:$TAG already exists, skipping"
  exit 0
fi

aws ecr get-login-password --region "$REGION" \
  | docker login --username AWS --password-stdin "$REGISTRY"

docker build --platform linux/arm64 -t "$REPO_URL:$TAG" "$ROOT"
docker push "$REPO_URL:$TAG"
