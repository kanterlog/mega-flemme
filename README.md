# 🤖 KanterMator + Sylvie

**Agent d'automatisation Google Workspace avec intelligence artificielle conversationnelle**

---

## 🚀 Démarrage Rapide

### 1. **Installation**

```bash
# Clone et setup
git clone <votre-repo>
cd mega-flemme
make setup
```

### 2. **Configuration**

```bash
# Éditez le fichier .env avec vos credentials
cp .env.example .env
nano .env

# Placez vos credentials Google dans le dossier credentials/
mkdir credentials
# Ajoutez: google-credentials.json, service-account.json, etc.
```

### 3. **Lancement**

```bash
# Mode développement simple
make dev

# Mode avec agent Sylvie (recommandé)
make sylvie

# Mode production Docker
make prod
```

---

## 🏗️ Architecture

### **KanterMator Backend**
- **Progressions pédagogiques** : Synchronisation Google Sheets
- **Automatisation** : Création automatique de dossiers Drive
- **Planification** : Exécution programmée (samedi 23h)
- **API REST** : Interface complète

### **Agent Sylvie IA**
- **Conversation naturelle** : "Lance l'automatisation pour cette semaine"
- **Monitoring proactif** : Surveillance 24/7
- **Résolution automatique** : Correction des problèmes
- **Aide contextuelle** : Guidance intelligente

### **Infrastructure**
- **PostgreSQL** : Base de données
- **Redis** : Cache et queue Celery
- **Docker** : Containerisation complète

---

## 📋 Commandes Utiles

```bash
make help              # Liste toutes les commandes
make status            # État du système
make test              # Tests des composants
make credentials       # Guide configuration Google
make logs              # Affichage des logs
make clean             # Nettoyage complet
```

---

## 🎯 Utilisation

### **Interface Web**
- **API Docs** : http://localhost:8000/docs
- **pgAdmin** : http://localhost:5050
- **Monitoring** : http://localhost:8000/api/v1/system/status

### **Chat avec Sylvie**
```bash
curl -X POST http://localhost:8000/api/v1/sylvie/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Lance l automatisation pour cette semaine"}'
```

### **Automatisation manuelle**
```bash
curl -X POST http://localhost:8000/api/v1/automation/execute \
  -H "Content-Type: application/json" \
  -d '{"week_number": 32, "year": 2025}'
```

---

## 🔧 Configuration Google

1. **Console Google Cloud** : https://console.cloud.google.com/
2. **APIs à activer** :
   - Google Drive API
   - Google Sheets API
   - Google Calendar API (optionnel)
3. **Credentials OAuth 2.0** → Télécharger JSON
4. **Variables .env** :
   ```bash
   GOOGLE_CLIENT_ID=votre-client-id
   GOOGLE_CLIENT_SECRET=votre-secret
   GOOGLE_SHEETS_ID=id-de-votre-sheet
   DRIVE_CAHIER_JOURNAL_ID=id-dossier-principal
   ```

---

## 🆘 Support & Dépannage

### **Problèmes courants**
- **Erreur credentials** : Vérifiez les fichiers dans `credentials/`
- **Erreur base de données** : `make docker-up` puis `make db-reset`
- **Port occupé** : Changez les ports dans `docker-compose.yml`

### **Logs de débogage**
```bash
make logs                    # Logs application
make docker-logs            # Logs Docker
docker-compose logs sylvie   # Logs spécifiques Sylvie
```

---

## 🎉 Fonctionnalités

✅ **Automatisation complète** des progressions pédagogiques  
✅ **Agent IA conversationnel** pour contrôler le système  
✅ **Interface web** intuitive avec documentation  
✅ **Monitoring proactif** et résolution automatique  
✅ **Planification intelligente** et exécution fiable  
✅ **Infrastructure robuste** avec Docker  

---

**🤖 Développé avec amour pour simplifier la gestion éducative**
