"""
🤖 Agent Sylvie - Cœur de l'intelligence conversationnelle
Phase 3.11 - Agent principal avec Google Workspace complet

Sylvie : Votre assistante IA hybride (GPT + Gemini) pour KanterMator
Intégration complète : Gmail + Calendar + Drive + Sheets + Tasks + Keep
"""

import uuid
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import structlog
import asyncio

from app.services.sylvie_config import (
    SylvieConfig, ConversationMessage, SylvieIntent, 
    SylvieResponse, SylvieCapability, ConversationRole
)
from app.services.hybrid_ai import hybrid_ai, TaskType
from app.services.sheets_reader import SheetsReader
from app.services.drive_manager import DriveManager
from app.services.scheduler import AutomationScheduler
from app.services.gmail_service import gmail_service
from app.services.calendar_service import calendar_service
from app.services.tasks_service import tasks_service
from app.services.keep_service import keep_service
from app.utils.config import settings
from app.utils.database import db_manager

logger = structlog.get_logger(__name__)

class SylvieAgent:
    """Agent conversationnel intelligent Sylvie avec IA hybride et Google Workspace complet"""
    
    def __init__(self):
        # Plus de client OpenAI direct - utilisation du service hybride
        self.conversations: Dict[str, List[ConversationMessage]] = {}
        self.sheets_reader = SheetsReader()
        self.drive_manager = DriveManager()
        self.scheduler = AutomationScheduler()
        self.gmail_service = gmail_service
        self.calendar_service = calendar_service
        self.tasks_service = tasks_service
        self.keep_service = keep_service
        
        # Initialisation de Sylvie avec IA hybride et Google Workspace complet
        logger.info("🤖 Sylvie Agent hybride + Google Workspace COMPLET initialisé", 
                   ai_strategy=settings.AI_MODEL_STRATEGY,
                   primary_model=settings.PRIMARY_MODEL,
                   services=["Gmail", "Calendar", "Drive", "Sheets", "Tasks", "Keep"])
    
    async def process_message(self, message: str, conversation_id: str = None) -> SylvieResponse:
        """
        Traitement principal d'un message utilisateur
        
        Args:
            message: Message de l'utilisateur
            conversation_id: ID de conversation (optionnel)
            
        Returns:
            SylvieResponse avec la réponse et métadonnées
        """
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Ajout du message utilisateur à l'historique
        self._add_to_conversation(conversation_id, ConversationRole.USER, message)
        
        logger.info("💬 Message utilisateur reçu", 
                   message=message[:100],
                   conversation_id=conversation_id)
        
        try:
            # 1. Analyse de l'intention
            intent = await self._analyze_intent(message, conversation_id)
            
            # 2. Exécution de l'action si nécessaire
            action_taken = None
            action_result = None
            
            if intent and intent.action_required:
                action_taken, action_result = await self._execute_action(intent)
            
            # 3. Génération de la réponse
            response_message = await self._generate_response(
                message, intent, action_taken, action_result, conversation_id
            )
            
            # 4. Génération de suggestions
            suggestions = await self._generate_suggestions(intent, action_result)
            
            # Ajout de la réponse à l'historique
            self._add_to_conversation(conversation_id, ConversationRole.ASSISTANT, response_message)
            
            # Construction de la réponse finale
            response = SylvieResponse(
                message=response_message,
                intent=intent,
                action_taken=action_taken,
                action_result=action_result,
                suggestions=suggestions,
                conversation_id=conversation_id
            )
            
            logger.info("✅ Réponse Sylvie générée", 
                       intent=intent.intent if intent else "non détectée",
                       action_taken=bool(action_taken))
            
            return response
            
        except Exception as e:
            logger.error("❌ Erreur traitement message", error=str(e))
            error_response = SylvieResponse(
                message=f"🚨 Désolée, j'ai rencontré une erreur : {str(e)}",
                conversation_id=conversation_id
            )
            return error_response
    
    async def _analyze_intent(self, message: str, conversation_id: str) -> Optional[SylvieIntent]:
        """Analyse de l'intention de l'utilisateur avec IA hybride"""
        
        try:
            # Contexte de conversation pour l'analyse
            conversation_context = self._get_conversation_context(conversation_id, last_n=3)
            
            intent_prompt = f"""
            Analyse ce message utilisateur pour KanterMator et retourne un JSON avec l'intention détectée.
            
            Message : "{message}"
            Contexte : {conversation_context}
            
            Format JSON requis :
            {{
                "intent": "nom_intention",
                "confidence": 0.95,
                "capability": "une_des_capacités",
                "action_required": true/false,
                "entities": {{}},
                "parameters": {{}}
            }}
            
            Capacités disponibles (capability) :
            - automation_control : start_automation, stop_automation, automation_status
            - monitoring : system_health, check_logs, performance_metrics
            - sheets_analysis : read_sheets, analyze_data, generate_report
            - drive_management : list_files, organize_files, share_document
            - email_management : check_emails, search_emails, send_email
            - calendar_management : check_schedule, upcoming_events, create_event, check_conflicts
            - tasks_management : get_tasks, create_task, complete_task, task_summary
            - notes_management : create_note, search_notes, get_notes, note_summary
            - system_status : system_health, check_integrations, view_logs
            - help_guidance : help_request, explain_feature, show_capabilities
            - error_resolution : resolve_error, reconnect_google, fix_permissions
            """
            
            # Utilisation du service IA hybride pour l'analyse d'intention
            ai_response = await hybrid_ai.generate_response(
                prompt=intent_prompt,
                task_type=TaskType.INTENT_ANALYSIS,
                max_tokens=300,
                temperature=0.3  # Plus déterministe pour l'analyse
            )
            
            # Parsing de la réponse JSON
            try:
                intent_data = json.loads(ai_response.content)
                
                return SylvieIntent(
                    intent=intent_data["intent"],
                    confidence=intent_data["confidence"],
                    entities=intent_data.get("entities", {}),
                    capability=SylvieCapability(intent_data["capability"]),
                    action_required=intent_data.get("action_required", False),
                    parameters=intent_data.get("parameters", {})
                )
                
            except json.JSONDecodeError:
                logger.warning("⚠️ Réponse IA non parsable comme JSON", response=ai_response.content)
                return None
                
        except Exception as e:
            logger.error("❌ Erreur lors de l'analyse d'intention", error=str(e))
            return None
    
    async def _execute_action(self, intent: SylvieIntent) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Exécution de l'action demandée par l'utilisateur"""
        try:
            action_result = None
            action_taken = None
            
            logger.info("🎯 Exécution d'action Sylvie", 
                       intent=intent.intent,
                       capability=intent.capability)
            
            # Actions selon la capacité
            if intent.capability == SylvieCapability.AUTOMATION_CONTROL:
                action_taken, action_result = await self._handle_automation_control(intent)
                
            elif intent.capability == SylvieCapability.MONITORING:
                action_taken, action_result = await self._handle_monitoring(intent)
                
            elif intent.capability == SylvieCapability.SHEETS_ANALYSIS:
                action_taken, action_result = await self._handle_sheets_analysis(intent)
                
            elif intent.capability == SylvieCapability.DRIVE_MANAGEMENT:
                action_taken, action_result = await self._handle_drive_management(intent)
                
            elif intent.capability == SylvieCapability.EMAIL_MANAGEMENT:
                action_taken, action_result = await self._handle_email_management(intent)
                
            elif intent.capability == SylvieCapability.CALENDAR_MANAGEMENT:
                action_taken, action_result = await self._handle_calendar_management(intent)
                
            elif intent.capability == SylvieCapability.TASKS_MANAGEMENT:
                action_taken, action_result = await self._handle_tasks_management(intent)
                
            elif intent.capability == SylvieCapability.NOTES_MANAGEMENT:
                action_taken, action_result = await self._handle_notes_management(intent)
                
            elif intent.capability == SylvieCapability.SYSTEM_STATUS:
                action_taken, action_result = await self._handle_system_status(intent)
                
            elif intent.capability == SylvieCapability.HELP_GUIDANCE:
                action_taken, action_result = await self._handle_help_guidance(intent)
                
            elif intent.capability == SylvieCapability.ERROR_RESOLUTION:
                action_taken, action_result = await self._handle_error_resolution(intent)
            
            return action_taken, action_result
            
        except Exception as e:
            logger.error("❌ Erreur lors de l'exécution d'action", 
                        intent=intent.intent if intent else "unknown",
                        error=str(e))
            return f"Erreur: {str(e)}", {"error": str(e)}
    
    # [Handlers existants gardés identiques...]
    
    async def _handle_tasks_management(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Gestion des commandes Google Tasks"""
        
        if intent.intent == "get_tasks":
            # Récupération des tâches
            try:
                completed = intent.parameters.get("completed", False)
                max_results = intent.parameters.get("max_results", 20)
                
                tasks = await self.tasks_service.get_tasks(
                    completed=completed,
                    max_results=max_results
                )
                summary = await self.tasks_service.get_tasks_summary_for_sylvie()
                
                return "Récupération des tâches", {
                    "tasks": tasks,
                    "count": len(tasks),
                    "summary": summary
                }
            except Exception as e:
                return f"Erreur récupération tâches: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "create_task":
            # Création d'une tâche
            title = intent.parameters.get("title", "")
            notes = intent.parameters.get("notes", "")
            due_date_str = intent.parameters.get("due_date", "")
            
            if not title:
                return "Titre manquant pour création tâche", {
                    "error": "title requis"
                }
            
            try:
                due_date = None
                if due_date_str:
                    due_date = datetime.fromisoformat(due_date_str)
                
                success = await self.tasks_service.create_task(
                    title=title,
                    notes=notes,
                    due_date=due_date
                )
                
                if success:
                    return f"Tâche créée: {title}", {
                        "title": title,
                        "notes": notes,
                        "due_date": due_date_str
                    }
                else:
                    return f"Échec création tâche: {title}", {"error": "Création échouée"}
            except Exception as e:
                return f"Erreur création tâche: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "complete_task":
            # Complétion d'une tâche
            task_id = intent.parameters.get("task_id", "")
            
            if not task_id:
                return "ID tâche manquant", {"error": "task_id requis"}
            
            try:
                success = await self.tasks_service.complete_task(task_id)
                if success:
                    return f"Tâche terminée: {task_id}", {"task_id": task_id}
                else:
                    return f"Échec complétion tâche: {task_id}", {"error": "Complétion échouée"}
            except Exception as e:
                return f"Erreur complétion tâche: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "task_summary":
            # Résumé des tâches
            try:
                summary = await self.tasks_service.get_tasks_summary_for_sylvie()
                return "Résumé des tâches", summary
            except Exception as e:
                return f"Erreur résumé tâches: {str(e)}", {"error": str(e)}
        
        return "Action tâches non reconnue", {"error": "Action non supportée"}
    
    async def _handle_notes_management(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Gestion des commandes Google Keep (Notes)"""
        
        if intent.intent == "create_note":
            # Création d'une note
            title = intent.parameters.get("title", "")
            content = intent.parameters.get("content", "")
            labels = intent.parameters.get("labels", [])
            color = intent.parameters.get("color", "white")
            
            if not all([title, content]):
                return "Paramètres manquants pour création note", {
                    "error": "title et content requis"
                }
            
            try:
                note = await self.keep_service.create_note(
                    title=title,
                    content=content,
                    labels=labels,
                    color=color
                )
                
                if note:
                    return f"Note créée: {title}", {
                        "title": title,
                        "note_id": note.get("id"),
                        "filename": note.get("filename")
                    }
                else:
                    return f"Échec création note: {title}", {"error": "Création échouée"}
            except Exception as e:
                return f"Erreur création note: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "search_notes":
            # Recherche dans les notes
            query = intent.parameters.get("query", "")
            max_results = intent.parameters.get("max_results", 10)
            
            if not query:
                return "Terme de recherche manquant", {"error": "query requis"}
            
            try:
                notes = await self.keep_service.search_notes(query, max_results)
                return f"Recherche notes: '{query}'", {
                    "query": query,
                    "notes": notes,
                    "count": len(notes)
                }
            except Exception as e:
                return f"Erreur recherche notes: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "get_notes":
            # Récupération des notes récentes
            try:
                max_results = intent.parameters.get("max_results", 20)
                notes = await self.keep_service.get_notes(max_results)
                
                return "Récupération des notes", {
                    "notes": notes,
                    "count": len(notes)
                }
            except Exception as e:
                return f"Erreur récupération notes: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "note_summary":
            # Résumé des notes
            try:
                summary = await self.keep_service.get_notes_summary_for_sylvie()
                return "Résumé des notes", summary
            except Exception as e:
                return f"Erreur résumé notes: {str(e)}", {"error": str(e)}
        
        return "Action notes non reconnue", {"error": "Action non supportée"}
    
    # [Reste des méthodes existantes...]
    
    async def _generate_response(self, user_message: str,
                               intent: Optional[SylvieIntent],
                               action_taken: Optional[str],
                               action_result: Optional[Dict[str, Any]],
                               conversation_id: str) -> str:
        """Génération de la réponse conversationnelle de Sylvie"""
        
        response_prompt = f"""
        Tu es Sylvie, l'assistante IA hybride de KanterMator avec accès complet Google Workspace.
        
        Message utilisateur : "{user_message}"
        
        Contexte :
        - Intention détectée : {intent.intent if intent else "Non détectée"}
        - Action effectuée : {action_taken}
        - Résultat : {json.dumps(action_result, default=str) if action_result else "Aucun"}
        
        Tes services disponibles :
        📧 Gmail - 📅 Calendar - 📁 Drive - 📊 Sheets - ✅ Tasks - 📝 Keep
        
        Règles pour ta réponse :
        1. Utilise des emojis appropriés
        2. Sois concise mais informative  
        3. Explique clairement ce qui a été fait
        4. Propose une aide supplémentaire si pertinent
        5. Reste dans le contexte éducatif
        6. Maximum 200 mots
        
        Génère uniquement ta réponse directe, sans préambule.
        """
        
        try:
            # Utilisation du service IA hybride
            ai_response = await hybrid_ai.generate_response(
                prompt=response_prompt,
                task_type=TaskType.CONVERSATION,
                max_tokens=400,
                temperature=0.7,
                system_prompt=SylvieConfig.SYSTEM_PROMPT
            )
            
            return ai_response.content.strip()
        except:
            # Réponse de fallback
            if action_taken:
                return f"✅ J'ai effectué l'action : {action_taken}. Comment puis-je vous aider davantage ?"
            else:
                return "😊 Je suis là pour vous aider avec KanterMator et Google Workspace ! Que souhaitez-vous faire ?"
    
    async def _generate_suggestions(self, intent: Optional[SylvieIntent], 
                                  action_result: Optional[Dict[str, Any]]) -> List[str]:
        """Génération de suggestions contextuelles"""
        
        suggestions = []
        
        if intent:
            if intent.capability == SylvieCapability.TASKS_MANAGEMENT:
                suggestions = [
                    "✅ Créer une nouvelle tâche",
                    "📋 Voir le résumé des tâches",
                    "🔍 Rechercher une tâche spécifique"
                ]
            elif intent.capability == SylvieCapability.NOTES_MANAGEMENT:
                suggestions = [
                    "📝 Créer une nouvelle note",
                    "🔍 Rechercher dans mes notes",
                    "📚 Voir le résumé des notes"
                ]
            elif intent.capability == SylvieCapability.EMAIL_MANAGEMENT:
                suggestions = [
                    "📧 Vérifier les emails urgents",
                    "🔍 Rechercher un email spécifique",
                    "📤 Envoyer un email automatisé"
                ]
            elif intent.capability == SylvieCapability.CALENDAR_MANAGEMENT:
                suggestions = [
                    "📅 Voir le planning du jour",
                    "⏰ Vérifier les conflits d'horaires",
                    "➕ Créer un nouvel événement"
                ]
            else:
                suggestions = [
                    "📚 Analyser une feuille Google Sheets",
                    "📁 Organiser les fichiers Drive",
                    "🔄 Vérifier l'état des automatisations"
                ]
        else:
            suggestions = [
                "💡 Afficher mes capacités",
                "📧 Vérifier mes emails",
                "📅 Consulter mon planning",
                "✅ Gérer mes tâches"
            ]
        
        return suggestions[:3]  # Maximum 3 suggestions
    
    # [Méthodes utilitaires existantes gardées identiques...]
    
    def _add_to_conversation(self, conversation_id: str, role: ConversationRole, content: str):
        """Ajout d'un message à l'historique de conversation"""
        
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        message = ConversationMessage(role=role, content=content)
        self.conversations[conversation_id].append(message)
        
        # Limitation de la taille de l'historique
        if len(self.conversations[conversation_id]) > SylvieConfig.MAX_CONVERSATION_LENGTH:
            self.conversations[conversation_id] = self.conversations[conversation_id][-SylvieConfig.MAX_CONVERSATION_LENGTH:]
    
    def _get_conversation_context(self, conversation_id: str, last_n: int = 5) -> str:
        """Récupération du contexte de conversation"""
        
        if conversation_id not in self.conversations:
            return "Nouvelle conversation"
        
        recent_messages = self.conversations[conversation_id][-last_n:]
        context_parts = []
        
        for msg in recent_messages:
            role_emoji = "👤" if msg.role == ConversationRole.USER else "🤖"
            context_parts.append(f"{role_emoji} {msg.content[:100]}")
        
        return " | ".join(context_parts)
    
    def get_conversation_history(self, conversation_id: str) -> List[ConversationMessage]:
        """Récupération de l'historique complet d'une conversation"""
        return self.conversations.get(conversation_id, [])
    
    def clear_conversation(self, conversation_id: str):
        """Nettoyage d'une conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info("🧹 Conversation supprimée", conversation_id=conversation_id)

# Instance globale de l'agent Sylvie
sylvie = SylvieAgent()
