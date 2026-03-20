# ═══════════════════════════════════════════════════════════════
# OnboardAI — AI-Adaptive Onboarding Engine
# Multi-stage Docker build
# ═══════════════════════════════════════════════════════════════

# ── Stage 1: Frontend Build ──────────────────────────────────────
FROM node:20-slim AS frontend-build

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# ── Stage 2: Final Backend Image ─────────────────────────────────
FROM python:3.11-slim AS final

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend (served as static files)
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Expose port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
