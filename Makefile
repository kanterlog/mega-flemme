# 🤖 KanterMator + Sylvie - Makefile
# Commandes simplifiées pour le développement

.PHONY: help dev sylvie prod test clean setup docker-up docker-down logs

help: ## Affiche cette aide
	@echo "🤖 KanterMator + Sylvie - Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Installation initiale du projet
	@echo "🔧 Installation de KanterMator..."
	python3 -m venv venv
	source venv/bin/activate && pip install -r requirements.txt
	cp .env.example .env
	@echo "✅ Setup terminé. Éditez le fichier .env avec vos credentials"

dev: ## Démarrage en mode développement
	@echo "🚀 Démarrage en mode développement..."
	./start.sh dev

sylvie: ## Démarrage avec l'agent Sylvie
	@echo "🤖 Démarrage avec l'agent Sylvie..."
	./start.sh sylvie

prod: ## Démarrage en mode production (Docker)
	@echo "🐳 Démarrage en mode production..."
	./start.sh prod

test: ## Tests des composants
	@echo "🧪 Exécution des tests..."
	./start.sh test

docker-up: ## Démarrage des services Docker
	@echo "🐳 Démarrage des services Docker..."
	docker-compose up -d

docker-down: ## Arrêt des services Docker
	@echo "🛑 Arrêt des services Docker..."
	docker-compose down

docker-logs: ## Affichage des logs Docker
	docker-compose logs -f

clean: ## Nettoyage du projet
	@echo "🧹 Nettoyage..."
	docker-compose down -v
	docker system prune -f
	rm -rf __pycache__
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

logs: ## Affichage des logs de l'application
	@echo "📋 Logs de l'application..."
	tail -f logs/*.log 2>/dev/null || echo "Aucun fichier de log trouvé"

db-reset: ## Réinitialisation de la base de données
	@echo "🗄️ Réinitialisation de la base de données..."
	docker-compose exec postgres psql -U kantermator_user -d kantermator -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

credentials: ## Guide pour configurer les credentials Google
	@echo "🔑 Configuration des credentials Google:"
	@echo "1. Aller sur https://console.cloud.google.com/"
	@echo "2. Créer un projet ou sélectionner un projet existant"
	@echo "3. Activer les APIs: Drive, Sheets, Calendar"
	@echo "4. Créer des credentials OAuth 2.0"
	@echo "5. Télécharger le fichier JSON et le placer dans credentials/"
	@echo "6. Mettre à jour les variables dans .env"

status: ## État du système
	@echo "📊 État du système KanterMator:"
	@echo -n "Docker: "
	@docker --version 2>/dev/null && echo "✅" || echo "❌"
	@echo -n "Python: "
	@python3 --version 2>/dev/null && echo "✅" || echo "❌"
	@echo -n "Services Docker: "
	@docker-compose ps --services --filter status=running 2>/dev/null | wc -l | sed 's/^/Services actifs: /'

check-env: ## Vérifie l'environnement Python et Docker
	@echo "🔎 Vérification de l'environnement..."
	@if [ -d "venv" ]; then echo "✅ venv présent"; else echo "❌ venv absent"; fi
	@docker --version 2>/dev/null && echo "✅ Docker présent" || echo "❌ Docker absent"

update-deps: ## Met à jour les dépendances Python et Docker
	@echo "⬆️  Mise à jour des dépendances..."
	@source venv/bin/activate && pip install --upgrade -r requirements.txt
	@docker-compose pull

backup: ## Sauvegarde des fichiers critiques
	@echo "💾 Sauvegarde des fichiers..."
	@tar czf sauvegarde_$(date +%Y%m%d_%H%M%S).tar.gz app/ requirements.txt docker-compose.yml .env

migrate: ## Migration du code vers un nouvel espace de travail
	@echo "🚚 Migration du code..."
	@echo "Copiez le fichier de sauvegarde dans le nouvel espace et extrayez-le."

check-credentials: ## Vérifie la configuration Google Credentials
	@echo "🔎 Vérification des credentials Google..."
	@if [ -f "credentials/credentials.json" ]; then echo "✅ credentials.json présent"; else echo "❌ credentials.json absent"; fi
	@if grep -q "GOOGLE_CLIENT_ID" .env; then echo "✅ Variables .env OK"; else echo "❌ Variables .env manquantes"; fi

git-push: ## Push automatique du projet sur un dépôt distant
	@echo "🚀 Push du projet sur le dépôt distant..."
	@if git remote | grep -q origin; then \
		git add . && git commit -m "Sauvegarde automatique"; \
		git branch -M main; \
		git push -u origin main; \
	else \
		echo "Aucun remote 'origin' configuré. Utilisez : make git-set-remote URL=https://github.com/ton-utilisateur/nom-du-projet.git"; \
	fi

git-set-remote: ## Configure l'URL du dépôt distant (ex: make git-set-remote URL=https://github.com/ton-utilisateur/nom-du-projet.git)
	@if [ -z "$(URL)" ]; then \
		echo "Veuillez fournir l'URL du dépôt distant avec URL=..."; \
	else \
		git remote add origin $(URL); \
		git branch -M main; \
		git push -u origin main; \
	fi
