# 🤖 Dockerfile KanterMator + Sylvie
# Multi-stage build pour optimisation

FROM python:3.11-slim as builder

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Création de l'environnement virtuel
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage de production
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="Kanter"
LABEL description="KanterMator + Sylvie - Agent d'automatisation éducative"
LABEL version="1.0.0"

# Création de l'utilisateur non-root
RUN groupadd -r kantermator && useradd -r -g kantermator kantermator

# Installation des dépendances système minimales
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie de l'environnement virtuel
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Répertoire de travail
WORKDIR /app

# Copie du code source
COPY app/ ./app/
COPY *.py ./

# Création des dossiers nécessaires
RUN mkdir -p logs credentials && \
    chown -R kantermator:kantermator /app

# Variables d'environnement
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/system/status || exit 1

# Port d'exposition
EXPOSE 8000

# Commande par défaut (avec Sylvie)
USER kantermator
CMD ["python", "-m", "app.main_sylvie"]
