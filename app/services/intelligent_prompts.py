"""
🧠 Système de Prompts Intelligents pour Sylvie
Version 2.0 - Compréhension flexible et naturelle

Ce module contient tous les prompts optimisés pour une interaction
naturelle et une compréhension contextuelle avancée.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re

class IntelligentPrompts:
    """Gestionnaire de prompts intelligents pour Sylvie"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Prompt système principal - Version optimisée"""
        return """Tu es Sylvie, mon assistante IA personnelle avec accès complet à Google Workspace.

🎯 TON RÔLE :
Tu es là pour m'aider dans ma vie quotidienne. Tu comprends le langage naturel et t'adaptes à mon style de communication.

🧠 COMPRÉHENSION :
- Tu comprends les expressions familières ("check mes mails", "regarde mon planning")
- Tu gères les références temporelles flexibles ("demain", "la semaine prochaine", "dans 2h")
- Tu déduis les intentions même avec des formulations incomplètes
- Tu poses des questions de clarification quand c'est nécessaire

📱 CAPACITÉS GOOGLE WORKSPACE :
📧 EMAILS : Lecture, envoi, tri, recherche dans Gmail
📅 CALENDRIER : Consultation, création d'événements, gestion des conflits
✅ TÂCHES : Création, suivi, organisation dans Google Tasks
📁 DRIVE : Organisation, recherche, partage de fichiers
📝 DOCUMENTS : Création/édition de Docs, Sheets, Slides
📋 NOTES : Prise de notes rapides avec Google Keep

💬 STYLE DE COMMUNICATION :
- Naturel et décontracté, comme un vrai assistant
- Réponses concises mais complètes
- Confirme les actions importantes avant de les faire
- Proactive dans les suggestions utiles
- Utilise des emojis avec parcimonie

🎯 APPROCHE :
- Privilégie l'action sur les longs discours
- Adapte-toi à mon rythme et mes préférences
- Sois efficace et précise
- En cas de doute, demande plutôt que d'assumer"""

    @staticmethod
    def get_intent_analysis_prompt(message: str, context: str = "") -> str:
        """Prompt d'analyse d'intention - Version flexible"""
        return f"""Analyse ce message utilisateur et identifie l'intention.

MESSAGE: "{message}"
CONTEXTE: {context}

Retourne UNIQUEMENT le JSON suivant (sans balises markdown):
{{
    "intent": "action_précise",
    "confidence": 0.95,
    "capability": "domaine_action",
    "action_required": true/false,
    "entities": {{}},
    "parameters": {{}}
}}

DOMAINES (capability):
- email_management: check_emails, search_emails, send_email, organize_emails
- calendar_management: check_schedule, upcoming_events, create_event, check_conflicts  
- tasks_management: get_tasks, create_task, complete_task, task_summary
- drive_management: list_files, organize_files, share_document, search_files
- docs_management: create_document, edit_document, search_document
- notes_management: create_note, search_notes, get_notes
- system_status: health_check, view_logs, performance_check
- help_guidance: help_request, show_capabilities, explain_feature

EXEMPLES DE COMPRÉHENSION FLEXIBLE:

📧 EMAILS:
"check mes mails" → intent: "check_emails"
"regarde si j'ai reçu quelque chose" → intent: "check_emails"
"envoie un mail à Pierre" → intent: "send_email", entities: {{"recipient": "Pierre"}}
"cherche les mails de cette semaine" → intent: "search_emails", parameters: {{"timeframe": "week"}}

📅 CALENDRIER:
"mon planning" / "qu'est-ce que j'ai aujourd'hui" → intent: "check_schedule"
"crée un rdv demain 14h" → intent: "create_event", parameters: {{"date": "tomorrow", "time": "14:00"}}
"planifie une réunion équipe vendredi" → intent: "create_event", parameters: {{"title": "réunion équipe", "date": "friday"}}
"mes prochains rendez-vous" → intent: "upcoming_events"

✅ TÂCHES:
"ajoute une tâche" / "note que je dois" → intent: "create_task"
"mes tâches" / "qu'est-ce que j'ai à faire" → intent: "get_tasks"
"marque comme fait" → intent: "complete_task"

📁 DRIVE:
"mes fichiers" / "montre mes docs" → intent: "list_files"
"cherche le document budget" → intent: "search_files", parameters: {{"query": "budget"}}
"organise mon drive" → intent: "organize_files"

RÈGLES D'EXTRACTION:
- Dates flexibles: "demain" → date calculée, "vendredi" → prochain vendredi
- Heures: "14h", "2h de l'aprem", "midi" → format 24h
- Durées: "1h", "30min", "toute la matinée" → minutes
- Personnes: noms propres → entities["recipient"]
- Actions implicites: "Pierre réunion demain" → create_event avec titre et destinataire"""

    @staticmethod
    def get_response_generation_prompt(
        message: str, 
        intent: Optional[str] = None,
        action_taken: Optional[str] = None,
        action_result: Optional[Dict] = None,
        context: str = ""
    ) -> str:
        """Prompt de génération de réponse - Version naturelle"""
        
        result_info = ""
        if action_result:
            if action_result.get("error"):
                result_info = f"Erreur rencontrée: {action_result['error']}"
            elif action_result.get("count") is not None:
                result_info = f"Résultat: {action_result['count']} éléments trouvés"
            elif action_result.get("event"):
                result_info = f"Événement créé: {action_result['event'].get('title')}"
            else:
                result_info = f"Action réussie: {action_taken}"

        return f"""Génère une réponse naturelle et personnelle basée sur:

MESSAGE UTILISATEUR: "{message}"
INTENTION DÉTECTÉE: {intent}
ACTION EFFECTUÉE: {action_taken}
RÉSULTAT: {result_info}
CONTEXTE: {context}

STYLE DE RÉPONSE:
- Confirme l'action avec un ton naturel
- Sois concise mais informative  
- Utilise le tutoiement
- Emoji léger si approprié
- Propose une action de suivi logique si pertinent

EXEMPLES DE BONNES RÉPONSES:
❌ "J'ai procédé à la vérification de votre messagerie électronique..."
✅ "J'ai vérifié tes emails !"

❌ "L'événement a été créé avec succès dans votre calendrier..."
✅ "C'est noté ! Ton rdv est planifié pour demain 14h 👍"

❌ "Erreur lors de l'exécution de la requête..."
✅ "Oups, un petit souci... Peux-tu préciser l'heure ?"

RÈGLES:
- Pas de formules robotiques
- Confirme ce qui a été fait
- Si erreur, explique simplement et propose une solution
- Reste positive et efficace"""

    @staticmethod
    def extract_time_references(text: str) -> Dict[str, Any]:
        """Extraction intelligente des références temporelles"""
        now = datetime.now()
        time_info = {}
        
        # Références de date
        date_patterns = {
            r'\bdemain\b': now + timedelta(days=1),
            r'\baprès[-\s]?demain\b': now + timedelta(days=2),
            r'\bce\s+soir\b': now.replace(hour=20, minute=0, second=0, microsecond=0),
            r'\bce\s+matin\b': now.replace(hour=9, minute=0, second=0, microsecond=0),
            r'\bcet\s+après[-\s]?midi\b': now.replace(hour=14, minute=0, second=0, microsecond=0),
            r'\blundi\b': IntelligentPrompts._next_weekday(now, 0),
            r'\bmardi\b': IntelligentPrompts._next_weekday(now, 1),
            r'\bmercredi\b': IntelligentPrompts._next_weekday(now, 2),
            r'\bjeudi\b': IntelligentPrompts._next_weekday(now, 3),
            r'\bvendredi\b': IntelligentPrompts._next_weekday(now, 4),
            r'\bsamedi\b': IntelligentPrompts._next_weekday(now, 5),
            r'\bdimanche\b': IntelligentPrompts._next_weekday(now, 6),
        }
        
        # Références d'heure
        time_patterns = {
            r'\b(\d{1,2})[h:](\d{2})\b': lambda m: f"{int(m.group(1)):02d}:{m.group(2)}",
            r'\b(\d{1,2})h\b': lambda m: f"{int(m.group(1)):02d}:00",
            r'\bmidi\b': "12:00",
            r'\bminuit\b': "00:00",
        }
        
        text_lower = text.lower()
        
        # Extraction des dates
        for pattern, date_value in date_patterns.items():
            if re.search(pattern, text_lower):
                if isinstance(date_value, datetime):
                    time_info['date'] = date_value.strftime('%Y-%m-%d')
                else:
                    time_info['date'] = date_value
                break
        
        # Extraction des heures
        for pattern, time_format in time_patterns.items():
            match = re.search(pattern, text_lower)
            if match:
                if callable(time_format):
                    time_info['time'] = time_format(match)
                else:
                    time_info['time'] = time_format
                break
        
        return time_info
    
    @staticmethod
    def _next_weekday(current_date: datetime, weekday: int) -> str:
        """Calcule la prochaine occurrence d'un jour de la semaine"""
        days_ahead = weekday - current_date.weekday()
        if days_ahead <= 0:  # Le jour est passé cette semaine
            days_ahead += 7
        next_date = current_date + timedelta(days=days_ahead)
        return next_date.strftime('%Y-%m-%d')

    @staticmethod
    def get_error_handling_prompt(error_type: str, context: str = "") -> str:
        """Prompt pour la gestion d'erreurs naturelle"""
        return f"""Génère une réponse d'erreur naturelle et utile.

TYPE D'ERREUR: {error_type}
CONTEXTE: {context}

STYLE:
- Ton décontracté et rassurant
- Explication simple du problème
- Proposition de solution concrète
- Pas de jargon technique

EXEMPLES:
- Credentials manquants → "Oups, j'ai besoin d'accéder à ton compte Google. On peut configurer ça ?"
- API error → "Petit souci technique... Peux-tu réessayer dans un moment ?"
- Format incorrect → "Je n'ai pas bien compris le format. Tu peux me dire ça autrement ?"
- Permission denied → "Je n'ai pas les droits pour ça. Vérifions les permissions ensemble ?"

Reste positive et propose toujours une solution !"""
