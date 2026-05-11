#!/bin/bash
# Run this once to create the Kubernetes secret.
# Do NOT commit actual credentials — copy .env.example to .env and fill in real values.
set -euo pipefail

if [ ! -f .env ]; then
  echo "Error: .env file not found. Copy .env.example and fill in real values."
  exit 1
fi

source .env

kubectl create secret generic flask-db-secret \
  --from-literal=POSTGRES_USER="$POSTGRES_USER" \
  --from-literal=POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
  --from-literal=POSTGRES_DB="$POSTGRES_DB" \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --dry-run=client -o yaml | kubectl apply -f -
