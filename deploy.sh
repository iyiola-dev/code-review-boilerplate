#!/usr/bin/env bash
# One-shot deploy script for the Code Review Crew.
# Run this from Cloud Shell after cloning the repo.
#
#   ./deploy.sh
#
# It reads your active gcloud project, enables the APIs we need, and deploys
# the agent to Cloud Run with the ADK dev UI attached.

set -euo pipefail

# --- Config ---
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-code-review-crew}"
PROJECT_ID="$(gcloud config get-value project 2>/dev/null)"

if [[ -z "${PROJECT_ID}" ]]; then
  echo "❌ No active gcloud project set."
  echo "   Run: gcloud config set project YOUR_PROJECT_ID"
  exit 1
fi

echo "📦 Project:  ${PROJECT_ID}"
echo "🌍 Region:   ${REGION}"
echo "🤖 Service:  ${SERVICE_NAME}"
echo ""

# --- Enable APIs (idempotent — safe to re-run) ---
echo "🔧 Enabling required APIs..."
gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  --project="${PROJECT_ID}" \
  --quiet

# --- Environment for the deployed agent ---
# We use Vertex AI (no API key needed — uses the Cloud Run service's identity).
export GOOGLE_CLOUD_PROJECT="${PROJECT_ID}"
export GOOGLE_CLOUD_LOCATION="${REGION}"
export GOOGLE_GENAI_USE_VERTEXAI="True"

# --- Deploy ---
echo "🚀 Deploying to Cloud Run (takes ~2-3 minutes)..."
adk deploy cloud_run \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --service_name="${SERVICE_NAME}" \
  --with_ui \
  ./agent

echo ""
echo "✅ Deployed. Your agent URL is printed above."
echo "   Open it in a browser to see the ADK dev UI — or point the"
echo "   custom UI (ui/index.html) at it by setting AGENT_URL in ui/app.js."
