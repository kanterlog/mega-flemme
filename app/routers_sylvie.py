"""
🤖 Routeurs API pour l'agent Sylvie
Phase 3.3 - Interface REST pour Sylvie

Endpoints pour interagir avec l'agent conversationnel Sylvie
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import structlog

from app.services.sylvie_agent import sylvie
from app.services.sylvie_config import SylvieResponse, ConversationMessage
from app.services.hybrid_ai import hybrid_ai

logger = structlog.get_logger(__name__)

# Modèles Pydantic pour l'API Sylvie
class ChatMessage(BaseModel):
    """Message de chat avec Sylvie"""
    message: str = Field(..., min_length=1, max_length=2000, description="Message pour Sylvie")
    conversation_id: Optional[str] = Field(None, description="ID de conversation (optionnel)")

class ChatResponse(BaseModel):
    """Réponse de chat de Sylvie"""
    response: str
    conversation_id: str
    action_taken: Optional[str] = None
    action_result: Optional[dict] = None
    suggestions: List[str] = []
    needs_confirmation: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ConversationHistoryResponse(BaseModel):
    """Historique d'une conversation"""
    conversation_id: str
    messages: List[dict]
    total_messages: int
    created_at: Optional[datetime] = None

class SylvieCapabilitiesResponse(BaseModel):
    """Capacités de Sylvie"""
    capabilities: List[dict]
    examples: List[dict]
    help_text: str

# Router Sylvie
sylvie_router = APIRouter(prefix="/sylvie", tags=["🤖 Agent Sylvie"])

@sylvie_router.post("/chat", response_model=ChatResponse)
async def chat_with_sylvie(request: ChatMessage, background_tasks: BackgroundTasks):
    """
    Conversation avec l'agent Sylvie
    
    Envoyez un message à Sylvie et recevez une réponse intelligente
    avec des actions automatiques si nécessaire.
    """
    try:
        logger.info("💬 Nouveau message pour Sylvie", 
                   message_preview=request.message[:50],
                   conversation_id=request.conversation_id)
        
        # Traitement du message par Sylvie
        sylvie_response = await sylvie.process_message(
            message=request.message,
            conversation_id=request.conversation_id
        )
        
        # Conversion en réponse API
        response = ChatResponse(
            response=sylvie_response.message,
            conversation_id=sylvie_response.conversation_id,
            action_taken=sylvie_response.action_taken,
            action_result=sylvie_response.action_result,
            suggestions=sylvie_response.suggestions,
            needs_confirmation=sylvie_response.needs_user_confirmation
        )
        
        logger.info("✅ Sylvie a répondu", 
                   conversation_id=response.conversation_id,
                   action_taken=response.action_taken)
        
        return response
        
    except Exception as e:
        logger.error("❌ Erreur lors du chat avec Sylvie", error=str(e))
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors de la communication avec Sylvie: {str(e)}"
        )

@sylvie_router.get("/capabilities", response_model=SylvieCapabilitiesResponse)
async def get_sylvie_capabilities():
    """
    Récupération des capacités de Sylvie
    
    Découvrez tout ce que Sylvie peut faire pour vous aider
    avec KanterMator.
    """
    try:
        capabilities = [
            {
                "name": "Contrôle d'automatisation",
                "description": "Lance, programme et surveille l'automatisation hebdomadaire",
                "examples": ["Lance l'automatisation pour cette semaine", "Quel est l'état de l'automatisation ?"]
            },
            {
                "name": "Analyse des progressions",
                "description": "Vérifie et analyse vos progressions Google Sheets",
                "examples": ["Analyse mes progressions", "Y a-t-il des erreurs dans mes progressions ?"]
            },
            {
                "name": "Gestion Google Drive",
                "description": "Gère les dossiers, raccourcis et archivage",
                "examples": ["Vérifie l'espace Google Drive", "Archive les anciennes semaines"]
            },
            {
                "name": "Monitoring système",
                "description": "Surveille l'état de tous les composants",
                "examples": ["Comment va le système ?", "Vérifie les intégrations Google"]
            },
            {
                "name": "Aide et guidance",
                "description": "Guide et explique les fonctionnalités",
                "examples": ["Comment ça marche ?", "Que peux-tu faire ?"]
            },
            {
                "name": "Résolution d'erreurs",
                "description": "Détecte et résout automatiquement les problèmes",
                "examples": ["Il y a un problème", "Répare les connexions Google"]
            }
        ]
        
        examples = [
            {"message": "Lance l'automatisation pour la semaine 32", "category": "Automatisation"},
            {"message": "Vérifie mes progressions Google Sheets", "category": "Analyse"},
            {"message": "Comment va le système ?", "category": "Monitoring"},
            {"message": "Que peux-tu faire pour moi ?", "category": "Aide"},
            {"message": "Archive les dossiers de plus de 4 semaines", "category": "Drive"},
            {"message": "Il y a une erreur avec Google Sheets", "category": "Résolution"}
        ]
        
        help_text = """
        🤖 **Sylvie, votre assistante IA pour KanterMator**
        
        Je peux vous aider à :
        • Automatiser la création de vos dossiers hebdomadaires
        • Analyser et valider vos progressions pédagogiques  
        • Gérer votre organisation Google Drive
        • Surveiller l'état du système
        • Résoudre les problèmes automatiquement
        • Vous guider dans l'utilisation de KanterMator
        
        Parlez-moi naturellement, comme à une collègue ! 😊
        """
        
        return SylvieCapabilitiesResponse(
            capabilities=capabilities,
            examples=examples,
            help_text=help_text
        )
        
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des capacités", error=str(e))
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des capacités")

@sylvie_router.get("/conversations/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(conversation_id: str):
    """
    Récupération de l'historique d'une conversation
    
    Consultez l'historique complet de vos échanges avec Sylvie.
    """
    try:
        messages = sylvie.get_conversation_history(conversation_id)
        
        if not messages:
            raise HTTPException(status_code=404, detail="Conversation non trouvée")
        
        # Conversion des messages pour l'API
        api_messages = []
        for msg in messages:
            api_messages.append({
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            })
        
        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=api_messages,
            total_messages=len(api_messages),
            created_at=messages[0].timestamp if messages else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération de l'historique", 
                    conversation_id=conversation_id, 
                    error=str(e))
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération de l'historique")

@sylvie_router.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """
    Nettoyage d'une conversation
    
    Supprime l'historique d'une conversation avec Sylvie.
    """
    try:
        sylvie.clear_conversation(conversation_id)
        
        return {
            "message": f"Conversation {conversation_id} nettoyée avec succès",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Erreur lors du nettoyage de conversation", 
                    conversation_id=conversation_id, 
                    error=str(e))
        raise HTTPException(status_code=500, detail="Erreur lors du nettoyage")

@sylvie_router.post("/quick-actions/{action_name}")
async def execute_quick_action(action_name: str, background_tasks: BackgroundTasks):
    """
    Exécution d'actions rapides prédéfinies
    
    Actions disponibles :
    - system-status : Vérification complète du système
    - analyze-progressions : Analyse des progressions Google Sheets
    - automation-status : État de l'automatisation
    - help : Aide et capacités de Sylvie
    """
    try:
        # Mapping des actions rapides vers des messages
        quick_actions = {
            "system-status": "Vérifie l'état complet du système",
            "analyze-progressions": "Analyse mes progressions Google Sheets", 
            "automation-status": "Quel est l'état de l'automatisation ?",
            "help": "Que peux-tu faire pour moi ?"
        }
        
        if action_name not in quick_actions:
            raise HTTPException(
                status_code=400, 
                detail=f"Action '{action_name}' non disponible. Actions : {list(quick_actions.keys())}"
            )
        
        # Exécution de l'action via Sylvie
        message = quick_actions[action_name]
        sylvie_response = await sylvie.process_message(message)
        
        return {
            "action": action_name,
            "response": sylvie_response.message,
            "action_taken": sylvie_response.action_taken,
            "action_result": sylvie_response.action_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ Erreur lors de l'action rapide", action=action_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'exécution de {action_name}")

# Messages de démonstration pour les tests
@sylvie_router.get("/demo-messages")
async def get_demo_messages():
    """Messages de démonstration pour tester Sylvie"""
    return {
        "demo_messages": [
            "Bonjour Sylvie ! Comment vas-tu ?",
            "Lance l'automatisation pour la semaine prochaine",
            "Vérifie mes progressions Google Sheets",
            "Y a-t-il des erreurs dans le système ?",
            "Que peux-tu faire pour m'aider ?",
            "Archive les dossiers de plus de 4 semaines",
            "Quel est l'état de Google Drive ?",
            "Aide-moi à configurer KanterMator",
            "Il y a un problème avec l'authentification Google",
            "Merci Sylvie, tu es formidable !"
        ],
        "usage_tips": [
            "Parlez à Sylvie naturellement, comme à une collègue",
            "Utilisez les actions rapides pour les tâches courantes", 
            "Sylvie peut exécuter plusieurs actions automatiquement",
            "Le système hybride GPT+Gemini optimise chaque réponse"
        ],
        "ai_info": {
            "hybrid_system": True,
            "models": ["OpenAI GPT", "Google Gemini"],
            "strategy": hybrid_ai.get_service_status()
        }
    }

@sylvie_router.get("/ai-status")
async def get_ai_status():
    """État du système IA hybride"""
    try:
        return {
            "status": "active",
            "hybrid_ai": hybrid_ai.get_service_status(),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("❌ Erreur récupération statut IA", error=str(e))
        raise HTTPException(status_code=500, detail="Erreur statut IA")

@sylvie_router.post("/ai-compare")
async def compare_ai_models(request: ChatMessage):
    """Compare les réponses GPT vs Gemini (pour debug)"""
    try:
        if len(request.message) > 200:
            raise HTTPException(status_code=400, detail="Message trop long pour comparaison")
        
        responses = await hybrid_ai.compare_responses(request.message)
        
        return {
            "message": request.message,
            "responses": {
                model: {
                    "content": resp.content,
                    "model": resp.model,
                    "metadata": resp.metadata
                } for model, resp in responses.items()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Erreur comparaison IA", error=str(e))
        raise HTTPException(status_code=500, detail=f"Erreur comparaison: {str(e)}")
