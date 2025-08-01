"""
🤖 Agent Sylvie - Interface conversationnelle KanterMator
Phase 3.1 - Architecture et configuration

Ce module définit les configurations, modèles et paramètres
pour l'agent Sylvie, l'interface conversationnelle de KanterMator.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
import uuid

# Types d'énumérations pour Sylvie

class ConversationRole(str, Enum):
    """Rôles dans une conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class AIModel(str, Enum):
    """Modèles d'IA disponibles"""
    OPENAI = "openai"
    GEMINI = "gemini"

class SylvieCapability(str, Enum):
    """Capacités de Sylvie"""
    AUTOMATION_CONTROL = "automation_control"
    MONITORING = "monitoring"
    SHEETS_ANALYSIS = "sheets_analysis"
    DRIVE_MANAGEMENT = "drive_management"
    EMAIL_MANAGEMENT = "email_management"
    CALENDAR_MANAGEMENT = "calendar_management"
    TASKS_MANAGEMENT = "tasks_management"
    NOTES_MANAGEMENT = "notes_management"
    SLIDES_MANAGEMENT = "slides_management"
    DOCS_MANAGEMENT = "docs_management"
    SYSTEM_STATUS = "system_status"
    HELP_GUIDANCE = "help_guidance"
    ERROR_RESOLUTION = "error_resolution"
    
    # Nouvelles capacités Google Workspace MCP v2.2
    GOOGLE_WORKSPACE_MCP = "google_workspace_mcp"
    MULTI_ACCOUNT_MANAGEMENT = "multi_account_management"
    ADVANCED_GMAIL_SEARCH = "advanced_gmail_search"
    CALENDAR_INTELLIGENCE = "calendar_intelligence"
    PRODUCTIVITY_ANALYSIS = "productivity_analysis"
    MEETING_SUGGESTIONS = "meeting_suggestions"

class ConversationMessage(BaseModel):
    """Message dans une conversation"""
    role: ConversationRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

class SylvieIntent(BaseModel):
    """Intention détectée par Sylvie"""
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    entities: Dict[str, Any] = Field(default_factory=dict)
    capability: SylvieCapability
    action_required: bool = False
    parameters: Dict[str, Any] = Field(default_factory=dict)

class SylvieResponse(BaseModel):
    """Réponse de Sylvie"""
    message: str
    intent: Optional[SylvieIntent] = None
    action_taken: Optional[str] = None
    action_result: Optional[Dict[str, Any]] = None
    suggestions: List[str] = Field(default_factory=list)
    needs_user_confirmation: bool = False
    conversation_id: Optional[str] = None

class SylvieConfig:
    """Configuration de l'agent Sylvie"""
    
    # Longueur maximale de conversation
    MAX_CONVERSATION_LENGTH = 50
    
    # Prompt système pour Sylvie - Assistant personnel polyvalent
    SYSTEM_PROMPT = """Tu es Sylvie, mon assistante IA personnelle avec accès complet à Google Workspace.

🎯 Tes capacités Google Workspace :

📧 GESTION EMAIL (Gmail) :
- Lecture, tri et analyse de mes emails
- Envoi d'emails pour moi
- Recherche dans ma messagerie
- Organisation et filtrage

📅 GESTION CALENDRIER (Google Calendar) :
- Consultation de mon planning
- Création d'événements et rendez-vous
- Détection de conflits d'horaires
- Rappels et notifications

✅ GESTION TÂCHES (Google Tasks) :
- Création et suivi de mes tâches
- Organisation par priorités
- Rappels d'échéances
- Listes de tâches personnalisées

📁 GESTION DRIVE (Google Drive) :
- Organisation de mes fichiers
- Recherche de documents
- Partage et collaboration
- Sauvegarde et archivage

📝 CRÉATION DOCUMENTS :
- Google Docs : Rédaction et édition
- Google Sheets : Tableaux et calculs
- Google Slides : Présentations
- Templates personnalisés

📋 NOTES (Google Keep) :
- Prise de notes rapides
- Listes de courses et mémos
- Rappels géolocalisés
- Organisation par étiquettes

💬 PERSONNALITÉ :
- Ton amical et décontracté
- Réponses courtes et efficaces
- Proactive dans les suggestions
- Emojis appropriés mais sans excès

🎯 APPROCHE :
- Tu es MON assistante personnelle
- Tu m'aides dans TOUTES mes tâches quotidiennes
- Tu agis selon mes préférences
- Tu poses des questions pour clarifier si besoin

🛡️ RÈGLES :
- Confidentialité absolue
- Actions sûres et réversibles
- Demande confirmation pour actions importantes
- Reste concise, pas de longs discours

Réponds de manière naturelle et directe. Tu es là pour me simplifier la vie !"""

    # Prompts pour différents types de tâches
    INTENT_ANALYSIS_PROMPT = """
    Analyse ce message et retourne l'intention détectée au format JSON.
    
    Message: "{message}"
    Contexte: {context}
    
    Retourne uniquement le JSON sans formatage markdown:
    {{
        "intent": "nom_intention", 
        "confidence": 0.95,
        "capability": "capability_name",
        "action_required": true/false,
        "entities": {{}},
        "parameters": {{}}
    }}
    """
    
    RESPONSE_GENERATION_PROMPT = """
    Génère une réponse naturelle basée sur:
    
    Message utilisateur: {message}
    Intention détectée: {intent}
    Action effectuée: {action_taken}
    Résultat: {action_result}
    Contexte: {context}
    
    Réponds de manière personnelle, directe et utile.
    """
    
    # Configuration des timeouts
    REQUEST_TIMEOUT = 30
    CONVERSATION_TIMEOUT = 3600  # 1 heure
    
    # Taille des réponses
    MAX_RESPONSE_LENGTH = 2000
    MAX_SUGGESTION_COUNT = 4
    
    # Configuration Google Workspace
    GOOGLE_SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send", 
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/tasks",
        "https://www.googleapis.com/auth/keep"
    ]
