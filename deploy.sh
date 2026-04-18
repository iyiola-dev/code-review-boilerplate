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

# --- Grant Cloud Build role to default compute service account ---
# New GCP projects (post Aug 2024) don't grant this automatically. Without it,
# `gcloud run deploy --source` fails with "IAM permission denied for service
# account XXXX-compute@developer.gserviceaccount.com".
echo "🔐 Granting Cloud Build role to default compute service account..."
PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${COMPUTE_SA}" \
  --role="roles/cloudbuild.builds.builder" \
  --condition=None \
  --quiet >/dev/null

# --- Environment for the deployed agent ---
# We use Vertex AI (no API key needed — uses the Cloud Run service's identity).
export GOOGLE_CLOUD_PROJECT="${PROJECT_ID}"
export GOOGLE_CLOUD_LOCATION="${REGION}"
export GOOGLE_GENAI_USE_VERTEXAI="True"

# --- Deploy ---
echo "🚀 Deploying to Cloud Run (takes ~2-3 minutes)..."
DEPLOY_LOG="$(mktemp)"
trap 'rm -f "${DEPLOY_LOG}"' EXIT

# adk deploy cloud_run wraps gcloud and sometimes swallows gcloud failures,
# returning 0 even when the deploy failed. Capture output so we can grep for
# the error ourselves.
set +e
uv run adk deploy cloud_run \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --service_name="${SERVICE_NAME}" \
  --with_ui \
  ./agent 2>&1 | tee "${DEPLOY_LOG}"
DEPLOY_EXIT=${PIPESTATUS[0]}
set -e

if [[ ${DEPLOY_EXIT} -ne 0 ]] || grep -qE "^Deploy failed:|^ERROR: " "${DEPLOY_LOG}"; then
  echo ""
  echo "❌ Deployment failed. Scroll up for the actual error."
  exit 1
fi

echo ""
echo "✅ Deployed. Your agent URL is printed above."
echo "   Open it in a browser to see the ADK dev UI — or point the"
echo "   custom UI (ui/index.html) at it by setting AGENT_URL in ui/app.js."
