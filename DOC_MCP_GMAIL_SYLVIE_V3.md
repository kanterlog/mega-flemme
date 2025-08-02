# 📧 Documentation Technique MCP Gmail pour Sylvie v3.0

## Endpoints & Outils Gmail

### 1. `search_emails_advanced`
- **Description** : Recherche avancée d’emails avec opérateurs Gmail
- **Input** :
  - `query` (str) : Syntaxe Gmail (ex : `from:john@example.com has:attachment`)
  - `max_results` (int, optionnel)
- **Output** : Liste d’emails enrichis (subject, sender, snippet, labels, attachments)
- **Exemple** :
```json
{
  "query": "from:manager@company.com after:2025/01/01 is:unread",
  "max_results": 20
}
```

### 2. `send_email_smart`
- **Description** : Envoi d’email intelligent (texte, HTML, pièces jointes)
- **Input** :
  - `to`, `cc`, `bcc` (list)
  - `subject` (str)
  - `body_text` (str)
  - `body_html` (str, optionnel)
  - `attachments` (list, optionnel)
- **Output** : Statut d’envoi, ID du message
- **Exemple** :
```json
{
  "to": ["recipient@example.com"],
  "subject": "Rapport mensuel",
  "body_text": "Bonjour, voici le rapport.",
  "attachments": ["/path/to/rapport.pdf"]
}
```

### 3. `get_email_content`
- **Description** : Récupération détaillée d’un email (texte, HTML, pièces jointes, headers)
- **Input** :
  - `message_id` (str)
- **Output** : Structure complète EmailContent
- **Exemple** :
```json
{
  "message_id": "182ab45cd67ef"
}
```

### 4. `create_draft`
- **Description** : Création de brouillon avec CC/BCC et pièces jointes
- **Input** : Identique à `send_email_smart`, mais mode brouillon
- **Output** : Statut, ID du brouillon

### 5. `list_labels`
- **Description** : Liste tous les labels Gmail (système et utilisateur)
- **Input** : Aucun
- **Output** :
  - `all_labels`, `system_labels`, `user_labels`, `counts`

### 6. `batch_email_operations`
- **Description** : Opérations par lot (modification/suppression de labels, suppression d’emails)
- **Input** :
  - `message_ids` (list)
  - `operation_type` (str: modify/delete)
  - `add_labels`, `remove_labels` (list, optionnel)
  - `batch_size` (int, optionnel)
- **Output** : Statut, nombre succès/échecs, erreurs

### 7. `manage_attachments`
- **Description** : Téléchargement et gestion des pièces jointes
- **Input** :
  - `message_id` (str)
  - `attachment_id` (str)
  - `save_path` (str, optionnel)
  - `custom_filename` (str, optionnel)
- **Output** : Statut, chemin du fichier, taille

### 8. `search_threads`
- **Description** : Recherche dans les conversations Gmail
- **Input** :
  - `query` (str)
- **Output** : Liste de threads

---

## Sécurité & Authentification
- OAuth2 automatisé (stockage global, Docker/cloud compatible)
- Credentials jamais commités, stockés dans `~/.gmail-mcp/`

## Exemples d’Opérateurs Gmail
- `from:`, `to:`, `subject:`, `has:attachment`, `after:`, `before:`, `is:unread`, `label:`

## Format des Réponses
- Tous les endpoints renvoient des objets enrichis (subject, sender, labels, attachments, analytics)
- Gestion des erreurs détaillée (statut, message, code)

## Tests & Validation
- Couverture unitaire et intégration (voir `test_gmail_mcp_advanced.py`)
- Cas extrêmes : batch, pièces jointes volumineuses, labels multiples

---

Pour toute question ou exemple d’usage, voir les fichiers :
- `/app/services/gmail_mcp_advanced.py`
- `/test_gmail_mcp_advanced.py`
- `/NOTE_TECHNIQUE_SYLVIE_V3.md`
- `/PLAN_SYLVIE_V3_LOBECHAT.md`
