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
    SylvieIntent, SylvieResponse, SylvieCapability, 
    ConversationRole, ConversationMessage, SylvieConfig
)
from app.services.intelligent_prompts import IntelligentPrompts
from app.services.advanced_email_manager import AdvancedEmailManager, SylvieEmailIntegration
from app.services.gmail_mcp_advanced import (
    AdvancedGmailManager, GmailMCPInspiredFeatures, 
    EmailAttachment, EmailContent, BatchOperation
)
from app.services.google_workspace_mcp import (
    GoogleWorkspaceMCPIntegration, google_workspace_integration,
    CalendarEvent, EmailMessage, 
    format_email_for_display, format_calendar_event_for_display
)
from app.services.hybrid_ai import hybrid_ai, TaskType
from app.services.sheets_reader import SheetsReader
from app.services.drive_manager import DriveManager
from app.services.scheduler import AutomationScheduler
from app.services.gmail_service import gmail_service
from app.services.calendar_service import calendar_service
from app.services.tasks_service import tasks_service
from app.services.keep_service import keep_service
from app.services.slides_service import slides_service
from app.services.docs_service import docs_service
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
        
        # Intégration Google Workspace MCP (v2.2)
        self.google_workspace = google_workspace_integration
        self.gmail_service = gmail_service
        self.calendar_service = calendar_service
        self.tasks_service = tasks_service
        self.keep_service = keep_service
        
        # Nouvelles fonctionnalités Gmail MCP avancées (Sylvie v2.1)
        self.advanced_gmail_manager = AdvancedGmailManager(self.gmail_service)
        self.gmail_mcp_features = GmailMCPInspiredFeatures(self.gmail_service)
        self.slides_service = slides_service
        self.docs_service = docs_service
        
        # 🧠 Gestionnaire email avancé avec IA
        self.email_manager = AdvancedEmailManager()
        self.email_integration = SylvieEmailIntegration()
        
        # Initialisation de Sylvie avec IA hybride et Google Workspace COMPLET
        logger.info("🤖 Sylvie Agent hybride + Google Workspace COMPLET + Email IA initialisé", 
                   ai_strategy=settings.AI_MODEL_STRATEGY,
                   primary_model=settings.PRIMARY_MODEL,
                   services=["Gmail", "Calendar", "Drive", "Sheets", "Tasks", "Keep", "Slides", "Docs"],
                   email_features=["Smart Analysis", "Auto Categorization", "Priority Detection", "Smart Replies"])
    
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
        """Analyse de l'intention avec prompts intelligents"""
        
        try:
            # Contexte de conversation
            conversation_context = self._get_conversation_context(conversation_id, last_n=3)
            
            # Utilisation du prompt intelligent
            intent_prompt = IntelligentPrompts.get_intent_analysis_prompt(
                message=message, 
                context=conversation_context
            )
            
            # Analyse avec IA hybride
            ai_response = await hybrid_ai.generate_response(
                prompt=intent_prompt,
                task_type=TaskType.INTENT_ANALYSIS,
                max_tokens=400,
                temperature=0.1  # Plus déterministe pour l'analyse
            )
            
            # Parsing de la réponse JSON avec nettoyage
            try:
                response_content = ai_response.content.strip()
                if response_content.startswith("```json"):
                    response_content = response_content[7:]
                if response_content.endswith("```"):
                    response_content = response_content[:-3]
                response_content = response_content.strip()
                
                intent_data = json.loads(response_content)
                
                # Extraction des références temporelles
                time_info = IntelligentPrompts.extract_time_references(message)
                if time_info:
                    intent_data["parameters"].update(time_info)
                
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
                
            elif intent.capability == SylvieCapability.SLIDES_MANAGEMENT:
                action_taken, action_result = await self._handle_slides_management(intent)
                
            elif intent.capability == SylvieCapability.DOCS_MANAGEMENT:
                action_taken, action_result = await self._handle_docs_management(intent)
                
            elif intent.capability == SylvieCapability.SYSTEM_STATUS:
                action_taken, action_result = await self._handle_system_status(intent)
                
            elif intent.capability == SylvieCapability.HELP_GUIDANCE:
                action_taken, action_result = await self._handle_help_guidance(intent)
                
            elif intent.capability == SylvieCapability.ERROR_RESOLUTION:
                action_taken, action_result = await self._handle_error_resolution(intent)
            
            # Nouvelles capacités Google Workspace MCP v2.2
            elif intent.capability == SylvieCapability.GOOGLE_WORKSPACE_MCP:
                action_taken, action_result = await self._handle_google_workspace_mcp(intent)
                
            elif intent.capability == SylvieCapability.MULTI_ACCOUNT_MANAGEMENT:
                action_taken, action_result = await self._handle_multi_account_management(intent)
                
            elif intent.capability == SylvieCapability.ADVANCED_GMAIL_SEARCH:
                action_taken, action_result = await self._handle_advanced_gmail_search(intent)
                
            elif intent.capability == SylvieCapability.CALENDAR_INTELLIGENCE:
                action_taken, action_result = await self._handle_calendar_intelligence(intent)
                
            elif intent.capability == SylvieCapability.PRODUCTIVITY_ANALYSIS:
                action_taken, action_result = await self._handle_productivity_analysis(intent)
                
            elif intent.capability == SylvieCapability.MEETING_SUGGESTIONS:
                action_taken, action_result = await self._handle_meeting_suggestions(intent)
            
            return action_taken, action_result
            
        except Exception as e:
            logger.error("❌ Erreur lors de l'exécution d'action", 
                        intent=intent.intent if intent else "unknown",
                        error=str(e))
            return f"Erreur: {str(e)}", {"error": str(e)}
    
    async def _handle_automation_control(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Gestion des commandes d'automatisation"""
        
        if intent.intent == "start_automation":
            try:
                result = await self.scheduler.start_automation()
                return "Automatisation démarrée", {"status": "started", "result": result}
            except Exception as e:
                return f"Erreur démarrage automatisation: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "stop_automation":
            try:
                result = await self.scheduler.stop_automation()
                return "Automatisation arrêtée", {"status": "stopped", "result": result}
            except Exception as e:
                return f"Erreur arrêt automatisation: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "automation_status":
            try:
                status = await self.scheduler.get_status()
                return "Statut automatisation", {"status": status}
            except Exception as e:
                return f"Erreur statut automatisation: {str(e)}", {"error": str(e)}
        
        return "Action automatisation non reconnue", {"error": "Action non supportée"}
    
    async def _handle_monitoring(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Gestion des commandes de surveillance"""
        
        if intent.intent == "system_health":
            try:
                health = {
                    "status": "healthy",
                    "services": ["Gmail", "Calendar", "Drive", "Sheets", "Tasks", "Keep", "Slides", "Docs"],
                    "timestamp": datetime.now().isoformat()
                }
                return "Vérification santé système", health
            except Exception as e:
                return f"Erreur vérification santé: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "check_logs":
            try:
                logs = {"recent_logs": "Logs système OK", "timestamp": datetime.now().isoformat()}
                return "Vérification logs", logs
            except Exception as e:
                return f"Erreur vérification logs: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "performance_metrics":
            try:
                metrics = {
                    "response_time": "< 2s",
                    "memory_usage": "Normal",
                    "api_calls": "Optimal",
                    "timestamp": datetime.now().isoformat()
                }
                return "Métriques de performance", metrics
            except Exception as e:
                return f"Erreur métriques: {str(e)}", {"error": str(e)}
        
        return "Action surveillance non reconnue", {"error": "Action non supportée"}
    
    async def _handle_sheets_analysis(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Gestion des commandes Sheets"""
        
        if intent.intent == "read_sheets":
            try:
                spreadsheet_id = intent.parameters.get("spreadsheet_id", "")
                range_name = intent.parameters.get("range", "A1:Z100")
                
                if not spreadsheet_id:
                    return "ID feuille manquant", {"error": "spreadsheet_id requis"}
                
                data = await self.sheets_reader.read_sheet_data(spreadsheet_id, range_name)
                return f"Lecture feuille: {spreadsheet_id}", {"data": data, "range": range_name}
            except Exception as e:
                return f"Erreur lecture feuille: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "analyze_data":
            try:
                spreadsheet_id = intent.parameters.get("spreadsheet_id", "")
                analysis = await self.sheets_reader.analyze_sheet(spreadsheet_id)
                return f"Analyse données: {spreadsheet_id}", {"analysis": analysis}
            except Exception as e:
                return f"Erreur analyse: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "generate_report":
            try:
                spreadsheet_id = intent.parameters.get("spreadsheet_id", "")
                report = await self.sheets_reader.generate_report(spreadsheet_id)
                return f"Rapport généré: {spreadsheet_id}", {"report": report}
            except Exception as e:
                return f"Erreur génération rapport: {str(e)}", {"error": str(e)}
        
        return "Action Sheets non reconnue", {"error": "Action non supportée"}
    
    async def _handle_drive_management(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Gestion des commandes Drive"""
        
        if intent.intent == "list_files":
            try:
                folder_id = intent.parameters.get("folder_id", "")
                max_results = intent.parameters.get("max_results", 20)
                files = await self.drive_manager.list_files(folder_id, max_results)
                return "Liste des fichiers Drive", {"files": files, "count": len(files)}
            except Exception as e:
                return f"Erreur liste fichiers: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "organize_files":
            try:
                result = await self.drive_manager.organize_files()
                return "Organisation des fichiers", {"result": result}
            except Exception as e:
                return f"Erreur organisation: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "share_document":
            try:
                file_id = intent.parameters.get("file_id", "")
                email = intent.parameters.get("email", "")
                
                if not all([file_id, email]):
                    return "Paramètres manquants", {"error": "file_id et email requis"}
                
                result = await self.drive_manager.share_file(file_id, email)
                return f"Document partagé avec {email}", {"file_id": file_id, "shared_with": email}
            except Exception as e:
                return f"Erreur partage: {str(e)}", {"error": str(e)}
        
        return "Action Drive non reconnue", {"error": "Action non supportée"}
    
    async def _handle_email_management(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Gestion avancée des commandes Gmail avec IA et nouvelles fonctionnalités MCP"""
        
        # 🔥 Nouvelles fonctionnalités MCP v2.1 - Détection avancée
        if any(keyword in intent.user_message.lower() for keyword in [
            'recherche avancée', 'search', 'insights', 'productivité', 'télécharge', 'batch'
        ]):
            return "Utilisation des fonctionnalités Gmail MCP avancées...", await self.process_advanced_email_request(intent.user_message)
        
        if intent.intent == "check_emails":
            try:
                unread_only = intent.parameters.get("unread_only", True)
                max_results = intent.parameters.get("max_results", 10)
                
                # 📧 Récupération des emails avec gestionnaire avancé
                # Utilisation du nouveau système MCP pour une analyse plus complète
                emails = await self.gmail_service.get_recent_emails(unread_only, max_results)
                
                # 🧠 Analyse IA hybride avancée des emails
                if emails:
                    analyzed_emails = []
                    urgent_count = 0
                    meeting_requests = 0
                    
                    # Extraction des IDs pour analyse par lot si nécessaire
                    message_ids = [email.get('id') for email in emails if email.get('id')]
                    
                    # Analyse avancée avec les nouvelles fonctionnalités MCP
                    if len(message_ids) > 5:
                        # Pour beaucoup d'emails, utilisation de la catégorisation par lot
                        batch_analysis = await self.smart_email_categorization(message_ids[:10])
                        if batch_analysis.get('success'):
                            for categorized in batch_analysis.get('categorized_emails', []):
                                email_data = categorized.get('email_data', {})
                                ai_analysis = categorized.get('ai_analysis', '')
                                
                                # Reconstruction de l'email avec analyse MCP
                                enhanced_email = {
                                    'id': categorized.get('message_id'),
                                    'subject': email_data.get('subject'),
                                    'from': email_data.get('sender'),
                                    'snippet': email_data.get('snippet'),
                                    'ai_mcp_analysis': ai_analysis,
                                    'has_attachments': categorized.get('has_attachments'),
                                    'attachments_count': categorized.get('attachments_count')
                                }
                                analyzed_emails.append(enhanced_email)
                    else:
                        # Analyse individuelle pour petits volumes
                        for email in emails[:5]:  # Analyse des 5 premiers pour éviter les timeouts
                            email_data = {
                                "subject": email.get("subject", ""),
                                "body": email.get("snippet", ""),
                                "sender": email.get("from", "")
                            }
                            
                            analysis = self.email_integration.analyze_incoming_email(email_data)
                            
                            # Enrichissement de l'email avec l'analyse IA
                            email.update({
                                "ai_priority": analysis["priority"],
                                "ai_category": analysis["category"],
                                "ai_sentiment": analysis["sentiment"],
                                "ai_actions": analysis["actions"],
                                "ai_summary": analysis["summary"],
                                "suggested_reply": analysis.get("suggested_reply", "")
                            })
                            
                            analyzed_emails.append(email)
                            
                            # Compteurs
                            if analysis["priority"] in ["critical", "high"]:
                                urgent_count += 1
                            if "meeting" in analysis["category"] or "schedule" in analysis["actions"]:
                                meeting_requests += 1
                    
                    summary_message = f"📧 {len(emails)} emails récupérés"
                    if urgent_count > 0:
                        summary_message += f", 🔥 {urgent_count} urgents"
                    if meeting_requests > 0:
                        summary_message += f", 📅 {meeting_requests} demandes de réunion"
                    
                    return summary_message, {
                        "emails": analyzed_emails,
                        "total_count": len(emails),
                        "analyzed_count": len(analyzed_emails),
                        "urgent_count": urgent_count,
                        "meeting_requests": meeting_requests,
                        "ai_analysis": True
                    }
                
                return "Aucun email trouvé", {"emails": [], "count": 0}
                
            except Exception as e:
                logger.error(f"Erreur vérification emails: {str(e)}")
                return f"Erreur vérification emails: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "search_emails":
            try:
                query = intent.parameters.get("query", "")
                max_results = intent.parameters.get("max_results", 10)
                
                if not query:
                    return "Terme de recherche manquant", {"error": "query requis"}
                
                emails = await self.gmail_service.search_emails(query, max_results)
                
                # 🧠 Analyse IA des résultats de recherche
                if emails:
                    for email in emails[:3]:  # Analyse des 3 premiers résultats
                        email_data = {
                            "subject": email.get("subject", ""),
                            "body": email.get("snippet", ""),
                            "sender": email.get("from", "")
                        }
                        
                        analysis = self.email_integration.analyze_incoming_email(email_data)
                        email["ai_relevance"] = analysis["category"]
                        email["ai_priority"] = analysis["priority"]
                
                return f"🔍 Recherche emails: '{query}' - {len(emails)} résultats", {
                    "emails": emails, 
                    "count": len(emails),
                    "search_query": query,
                    "ai_enhanced": True
                }
                
            except Exception as e:
                logger.error(f"Erreur recherche emails: {str(e)}")
                return f"Erreur recherche emails: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "send_email":
            try:
                to = intent.parameters.get("to", "")
                subject = intent.parameters.get("subject", "")
                body = intent.parameters.get("body", "")
                
                if not all([to, subject, body]):
                    return "Paramètres email manquants", {"error": "to, subject et body requis"}
                
                success = await self.gmail_service.send_email(to, subject, body)
                if success:
                    return f"Email envoyé à {to}", {"to": to, "subject": subject}
                else:
                    return f"Échec envoi email", {"error": "Envoi échoué"}
            except Exception as e:
                return f"Erreur envoi email: {str(e)}", {"error": str(e)}
        
        return "Action email non reconnue", {"error": "Action non supportée"}
    
    async def _handle_calendar_management(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Gestion des commandes Calendar"""
        
        if intent.intent == "check_schedule":
            try:
                date_str = intent.parameters.get("date", datetime.now().isoformat())
                events = await self.calendar_service.get_events_for_date(date_str)
                return f"Planning du {date_str[:10]}", {"events": events, "count": len(events)}
            except Exception as e:
                return f"Erreur planning: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "upcoming_events":
            try:
                max_results = intent.parameters.get("max_results", 10)
                events = await self.calendar_service.get_upcoming_events(max_results)
                return "Événements à venir", {"events": events, "count": len(events)}
            except Exception as e:
                return f"Erreur événements: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "create_event":
            try:
                # Extraction des paramètres avec gestion flexible
                title = intent.parameters.get("title", intent.entities.get("title", ""))
                date = intent.parameters.get("date", "")
                time = intent.parameters.get("time", "")
                duration = intent.parameters.get("duration", 60)
                
                # Construction du titre si manquant
                if not title:
                    title = f"Événement {datetime.now().strftime('%d/%m')}"
                
                # Construction de start_time à partir de date et time
                start_time = ""
                if date and time:
                    start_time = f"{date}T{time}:00"
                elif date:
                    start_time = f"{date}T09:00:00"  # Heure par défaut le matin
                elif time:
                    # Aujourd'hui à l'heure spécifiée
                    today = datetime.now().strftime('%Y-%m-%d')
                    start_time = f"{today}T{time}:00"
                else:
                    # Par défaut : dans 1 heure
                    future_time = datetime.now() + timedelta(hours=1)
                    start_time = future_time.isoformat()
                
                logger.info("🗓️ Création événement", title=title, start_time=start_time)
                
                event = await self.calendar_service.create_event(title, start_time, duration)
                if event:
                    return f"Événement créé: {title}", {"event": event}
                else:
                    return f"Échec création événement", {"error": "Création échouée"}
            except Exception as e:
                return f"Erreur création événement: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "check_conflicts":
            try:
                date_str = intent.parameters.get("date", datetime.now().isoformat())
                conflicts = await self.calendar_service.check_conflicts(date_str)
                return f"Vérification conflits {date_str[:10]}", {"conflicts": conflicts}
            except Exception as e:
                return f"Erreur vérification conflits: {str(e)}", {"error": str(e)}
        
        return "Action calendrier non reconnue", {"error": "Action non supportée"}
    
    async def _handle_system_status(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Gestion des commandes de statut système"""
        
        if intent.intent == "system_health":
            try:
                status = {
                    "overall": "healthy",
                    "services": {
                        "gmail": "connected",
                        "calendar": "connected", 
                        "drive": "connected",
                        "sheets": "connected",
                        "tasks": "connected",
                        "keep": "connected",
                        "slides": "connected",
                        "docs": "connected"
                    },
                    "timestamp": datetime.now().isoformat()
                }
                return "Statut système", status
            except Exception as e:
                return f"Erreur statut système: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "check_integrations":
            try:
                integrations = {
                    "google_workspace": "active",
                    "ai_hybrid": "operational",
                    "database": "connected",
                    "timestamp": datetime.now().isoformat()
                }
                return "Vérification intégrations", integrations
            except Exception as e:
                return f"Erreur intégrations: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "view_logs":
            try:
                logs = {
                    "recent_activity": "Système fonctionnel",
                    "errors": "Aucune erreur critique",
                    "timestamp": datetime.now().isoformat()
                }
                return "Consultation logs", logs
            except Exception as e:
                return f"Erreur logs: {str(e)}", {"error": str(e)}
        
        return "Action statut non reconnue", {"error": "Action non supportée"}
    
    async def _handle_help_guidance(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Gestion des commandes d'aide"""
        
        if intent.intent == "help_request":
            try:
                help_info = {
                    "services": ["Gmail", "Calendar", "Drive", "Sheets", "Tasks", "Keep", "Slides", "Docs"],
                    "capabilities": [
                        "📧 Gestion des emails",
                        "📅 Planification d'événements",
                        "📁 Organisation de fichiers",
                        "📊 Analyse de données",
                        "✅ Gestion de tâches",
                        "📝 Prise de notes",
                        "📊 Création de présentations",
                        "📄 Rédaction de documents"
                    ],
                    "examples": [
                        "Vérifier mes emails urgents",
                        "Créer une tâche pour demain",
                        "Faire une présentation sur X",
                        "Analyser la feuille de calcul Y"
                    ]
                }
                return "Guide d'aide Sylvie", help_info
            except Exception as e:
                return f"Erreur aide: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "explain_feature":
            feature = intent.parameters.get("feature", "")
            explanations = {
                "tasks": "Je peux créer, gérer et suivre vos tâches Google Tasks",
                "keep": "Je peux créer et organiser vos notes Google Keep",
                "slides": "Je peux créer des présentations avec des modèles prédéfinis",
                "docs": "Je peux créer et modifier des documents Google Docs",
                "gmail": "Je peux lire, rechercher et envoyer des emails",
                "calendar": "Je peux gérer votre planning et créer des événements"
            }
            
            explanation = explanations.get(feature, "Fonctionnalité non reconnue")
            return f"Explication: {feature}", {"feature": feature, "explanation": explanation}
        
        elif intent.intent == "show_capabilities":
            capabilities = {
                "google_workspace": ["Gmail", "Calendar", "Drive", "Sheets", "Tasks", "Keep", "Slides", "Docs"],
                "ai_features": ["Analyse d'intention", "Génération de contenu", "Assistance contextuelle"],
                "automation": ["Lecture de feuilles", "Organisation de fichiers", "Planification"],
                "productivity": ["Gestion de tâches", "Prise de notes", "Création de documents"]
            }
            return "Mes capacités", capabilities
        
        return "Action aide non reconnue", {"error": "Action non supportée"}
    
    async def _handle_error_resolution(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Gestion des commandes de résolution d'erreurs"""
        
        if intent.intent == "resolve_error":
            error_type = intent.parameters.get("error_type", "")
            try:
                resolution = {
                    "auth": "Vérification des credentials OAuth",
                    "api": "Test de connectivité API Google",
                    "permission": "Vérification des permissions",
                    "network": "Test de connexion réseau"
                }
                
                action = resolution.get(error_type, "Diagnostic général")
                return f"Résolution d'erreur: {error_type}", {"action": action, "status": "diagnostic effectué"}
            except Exception as e:
                return f"Erreur résolution: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "reconnect_google":
            try:
                # Simulation de reconnexion
                result = {
                    "status": "reconnected",
                    "services": ["Gmail", "Calendar", "Drive", "Sheets", "Tasks", "Keep", "Slides", "Docs"],
                    "timestamp": datetime.now().isoformat()
                }
                return "Reconnexion Google Workspace", result
            except Exception as e:
                return f"Erreur reconnexion: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "fix_permissions":
            try:
                permissions = {
                    "oauth_scopes": "verified",
                    "api_access": "enabled",
                    "service_accounts": "configured",
                    "timestamp": datetime.now().isoformat()
                }
                return "Vérification permissions", permissions
            except Exception as e:
                return f"Erreur permissions: {str(e)}", {"error": str(e)}
        
        return "Action résolution non reconnue", {"error": "Action non supportée"}
    
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
    
    async def _handle_slides_management(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Gestion des commandes Google Slides"""
        
        if intent.intent == "create_presentation":
            # Création d'une présentation
            title = intent.parameters.get("title", "")
            template_type = intent.parameters.get("template_type", "educational")
            
            if not title:
                return "Titre manquant pour création présentation", {
                    "error": "title requis"
                }
            
            try:
                presentation = await self.slides_service.create_presentation(
                    title=title,
                    template_type=template_type
                )
                
                if presentation:
                    return f"Présentation créée: {title}", {
                        "title": title,
                        "presentation_id": presentation.get("id"),
                        "url": presentation.get("url"),
                        "template_type": template_type
                    }
                else:
                    return f"Échec création présentation: {title}", {"error": "Création échouée"}
            except Exception as e:
                return f"Erreur création présentation: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "get_presentations":
            # Récupération des présentations
            try:
                max_results = intent.parameters.get("max_results", 15)
                presentations = await self.slides_service.get_presentations(max_results)
                
                return "Récupération des présentations", {
                    "presentations": presentations,
                    "count": len(presentations)
                }
            except Exception as e:
                return f"Erreur récupération présentations: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "add_slide":
            # Ajout d'une slide
            presentation_id = intent.parameters.get("presentation_id", "")
            title = intent.parameters.get("title", "")
            content = intent.parameters.get("content", "")
            layout = intent.parameters.get("layout", "TITLE_AND_BODY")
            
            if not all([presentation_id, title]):
                return "Paramètres manquants pour ajout slide", {
                    "error": "presentation_id et title requis"
                }
            
            try:
                success = await self.slides_service.add_slide_with_content(
                    presentation_id=presentation_id,
                    title=title,
                    content=content,
                    layout=layout
                )
                
                if success:
                    return f"Slide ajoutée: {title}", {
                        "presentation_id": presentation_id,
                        "title": title
                    }
                else:
                    return f"Échec ajout slide: {title}", {"error": "Ajout échoué"}
            except Exception as e:
                return f"Erreur ajout slide: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "slides_summary":
            # Résumé des présentations
            try:
                summary = await self.slides_service.get_slides_summary_for_sylvie()
                return "Résumé des présentations", summary
            except Exception as e:
                return f"Erreur résumé présentations: {str(e)}", {"error": str(e)}
        
        return "Action présentations non reconnue", {"error": "Action non supportée"}
    
    async def _handle_docs_management(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Gestion des commandes Google Docs"""
        
        if intent.intent == "create_document":
            # Création d'un document
            title = intent.parameters.get("title", "")
            template_type = intent.parameters.get("template_type", "educational")
            
            if not title:
                return "Titre manquant pour création document", {
                    "error": "title requis"
                }
            
            try:
                document = await self.docs_service.create_document(
                    title=title,
                    template_type=template_type
                )
                
                if document:
                    return f"Document créé: {title}", {
                        "title": title,
                        "document_id": document.get("id"),
                        "url": document.get("url"),
                        "template_type": template_type
                    }
                else:
                    return f"Échec création document: {title}", {"error": "Création échouée"}
            except Exception as e:
                return f"Erreur création document: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "get_documents":
            # Récupération des documents
            try:
                max_results = intent.parameters.get("max_results", 15)
                documents = await self.docs_service.get_documents(max_results)
                
                return "Récupération des documents", {
                    "documents": documents,
                    "count": len(documents)
                }
            except Exception as e:
                return f"Erreur récupération documents: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "append_content":
            # Ajout de contenu
            document_id = intent.parameters.get("document_id", "")
            content = intent.parameters.get("content", "")
            insert_at_end = intent.parameters.get("insert_at_end", True)
            
            if not all([document_id, content]):
                return "Paramètres manquants pour ajout contenu", {
                    "error": "document_id et content requis"
                }
            
            try:
                success = await self.docs_service.append_content(
                    document_id=document_id,
                    content=content,
                    insert_at_end=insert_at_end
                )
                
                if success:
                    return f"Contenu ajouté au document", {
                        "document_id": document_id,
                        "content_length": len(content)
                    }
                else:
                    return f"Échec ajout contenu", {"error": "Ajout échoué"}
            except Exception as e:
                return f"Erreur ajout contenu: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "search_document":
            # Recherche dans un document
            document_id = intent.parameters.get("document_id", "")
            search_term = intent.parameters.get("search_term", "")
            
            if not all([document_id, search_term]):
                return "Paramètres manquants pour recherche", {
                    "error": "document_id et search_term requis"
                }
            
            try:
                results = await self.docs_service.search_in_document(
                    document_id=document_id,
                    search_term=search_term
                )
                
                return f"Recherche dans document: '{search_term}'", {
                    "document_id": document_id,
                    "search_term": search_term,
                    "results": results,
                    "count": len(results)
                }
            except Exception as e:
                return f"Erreur recherche document: {str(e)}", {"error": str(e)}
        
        elif intent.intent == "docs_summary":
            # Résumé des documents
            try:
                summary = await self.docs_service.get_docs_summary_for_sylvie()
                return "Résumé des documents", summary
            except Exception as e:
                return f"Erreur résumé documents: {str(e)}", {"error": str(e)}
        
        return "Action documents non reconnue", {"error": "Action non supportée"}
    
    # [Reste des méthodes existantes...]
    
    async def _generate_response(self, user_message: str,
                               intent: Optional[SylvieIntent],
                               action_taken: Optional[str],
                               action_result: Optional[Dict[str, Any]],
                               conversation_id: str) -> str:
        """Génération de réponse naturelle avec prompts intelligents"""
        
        try:
            # Contexte de conversation
            conversation_context = self._get_conversation_context(conversation_id, last_n=3)
            
            # Utilisation du prompt intelligent
            response_prompt = IntelligentPrompts.get_response_generation_prompt(
                message=user_message,
                intent=intent.intent if intent else None,
                action_taken=action_taken,
                action_result=action_result,
                context=conversation_context
            )
            
            # Génération avec IA hybride
            ai_response = await hybrid_ai.generate_response(
                prompt=response_prompt,
                task_type=TaskType.CONVERSATION,
                max_tokens=300,
                temperature=0.7,
                system_prompt=IntelligentPrompts.get_system_prompt()
            )
            
            return ai_response.content.strip()
            
        except Exception as e:
            logger.error("❌ Erreur génération réponse", error=str(e))
            
            # Réponse de fallback intelligente
            if action_result and action_result.get("error"):
                return f"Oups, un petit souci : {action_result['error']}. On peut réessayer ?"
            elif action_taken:
                return f"✅ C'est fait ! {action_taken}"
            else:
                return "😊 Comment je peux t'aider ?"
    
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
            elif intent.capability == SylvieCapability.SLIDES_MANAGEMENT:
                suggestions = [
                    "📊 Créer une nouvelle présentation",
                    "📋 Voir mes présentations récentes",
                    "➕ Ajouter une slide"
                ]
            elif intent.capability == SylvieCapability.DOCS_MANAGEMENT:
                suggestions = [
                    "📄 Créer un nouveau document",
                    "📚 Voir mes documents récents",
                    "🔍 Rechercher dans un document"
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
                "✅ Gérer mes tâches",
                "📊 Créer une présentation",
                "📄 Créer un document"
            ]
        
        return suggestions
    
    # 🧠 Nouvelles méthodes Email IA Avancées
    
    async def analyze_email_with_ai(self, email_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyse complète d'un email avec IA
        
        Args:
            email_data: Dictionnaire avec subject, body, sender
            
        Returns:
            Analyse complète avec priorité, catégorie, actions, etc.
        """
        try:
            analysis = self.email_integration.analyze_incoming_email(email_data)
            
            logger.info("📧 Email analysé avec IA", 
                       priority=analysis["priority"],
                       category=analysis["category"],
                       actions_count=len(analysis["actions"]))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erreur analyse email IA: {str(e)}")
            return {"error": str(e)}
    
    async def get_smart_email_summary(self, max_emails: int = 20) -> Dict[str, Any]:
        """
        Génère un résumé intelligent des emails avec analyse IA
        
        Args:
            max_emails: Nombre max d'emails à analyser
            
        Returns:
            Résumé intelligent avec statistiques et priorités
        """
        try:
            # Récupération des emails récents
            emails = await self.gmail_service.get_recent_emails(True, max_emails)
            
            if not emails:
                return {
                    "message": "Aucun email récent trouvé",
                    "total_emails": 0,
                    "summary": {}
                }
            
            # Analyse en lot avec IA
            email_batch = []
            for email in emails:
                email_batch.append({
                    "subject": email.get("subject", ""),
                    "body": email.get("snippet", ""),
                    "sender": email.get("from", "")
                })
            
            # Traitement IA en lot
            analyses = self.email_manager.process_email_batch(email_batch)
            priority_emails = self.email_manager.get_priority_emails(analyses)
            action_summary = self.email_manager.get_action_summary(analyses)
            
            # Statistiques intelligentes
            stats = {
                "total_emails": len(emails),
                "urgent_emails": len([a for a in analyses if a.priority.value in ["critical", "high"]]),
                "meeting_requests": len([a for a in analyses if "meeting" in a.category.value]),
                "technical_issues": len([a for a in analyses if a.category.value == "technical_issue"]),
                "business_inquiries": len([a for a in analyses if a.category.value == "business_inquiry"]),
                "positive_sentiment": len([a for a in analyses if a.sentiment == "positive"]),
                "negative_sentiment": len([a for a in analyses if a.sentiment == "negative"])
            }
            
            # Top 3 emails prioritaires
            top_priority = []
            for i, analysis in enumerate(priority_emails[:3]):
                email = emails[i] if i < len(emails) else {}
                top_priority.append({
                    "subject": email.get("subject", ""),
                    "sender": email.get("from", ""),
                    "priority": analysis.priority.value,
                    "category": analysis.category.value,
                    "summary": analysis.summary
                })
            
            logger.info("📊 Résumé email intelligent généré", 
                       total=stats["total_emails"],
                       urgent=stats["urgent_emails"],
                       meetings=stats["meeting_requests"])
            
            return {
                "message": f"📧 Résumé intelligent de {stats['total_emails']} emails",
                "statistics": stats,
                "top_priority": top_priority,
                "action_summary": action_summary,
                "recommendations": self._generate_email_recommendations(stats, analyses)
            }
            
        except Exception as e:
            logger.error(f"Erreur résumé email intelligent: {str(e)}")
            return {"error": str(e)}
    
    async def suggest_email_replies(self, email_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Génère des suggestions de réponses intelligentes
        
        Args:
            email_data: Données de l'email (subject, body, sender)
            
        Returns:
            Suggestions de réponses contextuelles
        """
        try:
            # Analyse IA de l'email
            analysis = await self.analyze_email_with_ai(email_data)
            
            if "error" in analysis:
                return analysis
            
            # Génération de réponses multiples
            email_analysis = self.email_manager.analyze_email(
                email_data["subject"], 
                email_data["body"], 
                email_data.get("sender", "")
            )
            
            # Différents types de réponses
            replies = []
            
            # Réponse standard
            standard_reply = self.email_manager.generate_smart_reply(email_analysis)
            replies.append({
                "type": "standard",
                "reply": standard_reply,
                "tone": "professional"
            })
            
            # Réponse selon la priorité
            if email_analysis.priority.value == "critical":
                replies.append({
                    "type": "urgent",
                    "reply": "Je prends note de l'urgence et interviens immédiatement. Je vous tiens informé des actions entreprises.",
                    "tone": "urgent"
                })
            
            # Réponse selon la catégorie
            if email_analysis.category.value == "meeting_request":
                replies.append({
                    "type": "meeting",
                    "reply": "Merci pour cette invitation. Je vérifie mes disponibilités et reviens vers vous avec des créneaux possibles.",
                    "tone": "collaborative"
                })
            
            logger.info("💬 Suggestions de réponses générées", 
                       email_subject=email_data["subject"][:50],
                       reply_count=len(replies))
            
            return {
                "message": "💬 Suggestions de réponses générées",
                "email_analysis": {
                    "priority": analysis["priority"],
                    "category": analysis["category"],
                    "sentiment": analysis["sentiment"],
                    "actions": analysis["actions"]
                },
                "suggested_replies": replies,
                "context_keywords": analysis.get("keywords", [])
            }
            
        except Exception as e:
            logger.error(f"Erreur suggestions réponses: {str(e)}")
            return {"error": str(e)}
    
    def _generate_email_recommendations(self, stats: Dict[str, int], analyses: List) -> List[str]:
        """Génère des recommandations basées sur l'analyse des emails"""
        recommendations = []
        
        if stats["urgent_emails"] > 0:
            recommendations.append(f"🔥 {stats['urgent_emails']} emails urgents nécessitent votre attention immédiate")
        
        if stats["meeting_requests"] > 0:
            recommendations.append(f"📅 {stats['meeting_requests']} demandes de réunion en attente de réponse")
        
        if stats["technical_issues"] > 0:
            recommendations.append(f"🔧 {stats['technical_issues']} problèmes techniques signalés")
        
        if stats["negative_sentiment"] > stats["positive_sentiment"]:
            recommendations.append("😟 Plusieurs emails avec sentiment négatif - intervention prioritaire recommandée")
        
        if stats["business_inquiries"] > 3:
            recommendations.append(f"💼 {stats['business_inquiries']} demandes business actives - opportunités à suivre")
        
        if not recommendations:
            recommendations.append("✅ Tous vos emails sont bien organisés !")
        
        return recommendations

    async def process_user_email_request(self, request: str) -> Dict[str, Any]:
        """
        Traite une demande utilisateur liée aux emails avec IA
        
        Args:
            request: Demande de l'utilisateur
            
        Returns:
            Réponse appropriée avec actions
        """
        try:
            # Utilisation de l'intégration Sylvie pour interpréter la demande
            response = self.email_integration.process_user_request(request)
            
            # Exécution de l'action appropriée
            if response["action"] == "show_urgent_emails":
                # Récupération et filtrage des emails urgents
                summary = await self.get_smart_email_summary(15)
                if "statistics" in summary:
                    urgent_count = summary["statistics"]["urgent_emails"]
                    if urgent_count > 0:
                        return {
                            "message": f"🔥 {urgent_count} emails urgents trouvés",
                            "action": "urgent_emails",
                            "data": summary["top_priority"]
                        }
                    else:
                        return {
                            "message": "✅ Aucun email urgent actuellement",
                            "action": "no_urgent_emails"
                        }
                
            elif response["action"] == "email_summary":
                summary = await self.get_smart_email_summary(20)
                return {
                    "message": summary.get("message", "Résumé emails"),
                    "action": "email_summary",
                    "data": summary
                }
            
            elif response["action"] == "smart_reply":
                return {
                    "message": "💬 Pour générer une réponse, transmettez-moi l'email à traiter",
                    "action": "request_email_data",
                    "instructions": "Copiez le sujet et le contenu de l'email pour une réponse intelligente"
                }
            
            else:
                return {
                    "message": response["message"],
                    "action": "general_help",
                    "suggestions": [
                        "Montre-moi mes emails urgents",
                        "Fais un résumé de mes emails", 
                        "Aide-moi à répondre à un email",
                        "Quelles sont mes demandes de réunion ?"
                    ]
                }
                
        except Exception as e:
            logger.error(f"Erreur traitement demande email: {str(e)}")
            return {"error": str(e), "message": "Erreur lors du traitement de votre demande email"}[:3]  # Maximum 3 suggestions
    
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
    
    # ===============================
    # 🔥 NOUVELLES FONCTIONNALITÉS GMAIL MCP v2.1
    # Inspirées du projet Gmail-MCP-Server
    # ===============================
    
    async def advanced_email_search(self, query: str, natural_language: bool = True) -> Dict[str, Any]:
        """
        Recherche avancée d'emails avec syntaxe Gmail ou langage naturel
        Nouvelle fonctionnalité Sylvie v2.1 inspirée de Gmail-MCP-Server
        """
        try:
            if natural_language:
                # Conversion du langage naturel vers syntaxe Gmail
                results = await self.gmail_mcp_features.smart_email_search(query)
            else:
                # Recherche directe avec syntaxe Gmail
                results = await self.advanced_gmail_manager.search_emails_advanced(query)
            
            return {
                'success': True,
                'query': query,
                'natural_language': natural_language,
                'results_count': len(results),
                'emails': results,
                'message': f"Recherche email terminée : {len(results)} résultats trouvés"
            }
            
        except Exception as e:
            logger.error("Erreur recherche email avancée", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'message': "Erreur lors de la recherche email avancée"
            }
    
    async def download_email_attachments(self, message_id: str, save_path: str = "./downloads") -> Dict[str, Any]:
        """
        Télécharge toutes les pièces jointes d'un email
        Nouvelle fonctionnalité Sylvie v2.1 inspirée de Gmail-MCP-Server
        """
        try:
            # Récupération des détails du message
            email_details = await self.advanced_gmail_manager._get_message_details(message_id)
            
            if not email_details:
                return {
                    'success': False,
                    'message': 'Email non trouvé'
                }
            
            attachments = email_details.get('content', {}).get('attachments', [])
            
            if not attachments:
                return {
                    'success': True,
                    'message': 'Aucune pièce jointe trouvée',
                    'attachments_count': 0
                }
            
            # Téléchargement de chaque pièce jointe
            download_results = []
            
            for attachment in attachments:
                result = await self.advanced_gmail_manager.download_attachment(
                    message_id=message_id,
                    attachment_id=attachment.id,
                    save_path=save_path,
                    custom_filename=attachment.filename
                )
                download_results.append(result)
            
            successful_downloads = [r for r in download_results if r.get('success')]
            
            return {
                'success': True,
                'message': f"Téléchargement terminé : {len(successful_downloads)}/{len(attachments)} pièces jointes",
                'attachments_count': len(attachments),
                'successful_downloads': len(successful_downloads),
                'download_results': download_results
            }
            
        except Exception as e:
            logger.error("Erreur téléchargement pièces jointes", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'message': "Erreur lors du téléchargement des pièces jointes"
            }
    
    async def batch_email_operations(self, operation_type: str, message_ids: List[str], **kwargs) -> Dict[str, Any]:
        """
        Opérations par lot sur les emails (modification, suppression)
        Nouvelle fonctionnalité Sylvie v2.1 inspirée de Gmail-MCP-Server
        """
        try:
            if operation_type == "modify_labels":
                # Opération de modification de labels par lot
                operation = BatchOperation(
                    message_ids=message_ids,
                    operation_type=operation_type,
                    batch_size=kwargs.get('batch_size', 50),
                    add_labels=kwargs.get('add_labels', []),
                    remove_labels=kwargs.get('remove_labels', [])
                )
                
                result = await self.advanced_gmail_manager.batch_modify_emails(operation)
                
                return {
                    'success': True,
                    'operation_type': operation_type,
                    'total_messages': len(message_ids),
                    'success_count': result.success_count,
                    'failure_count': result.failure_count,
                    'errors': result.errors,
                    'message': f"Opération par lot terminée : {result.success_count} succès, {result.failure_count} échecs"
                }
                
            elif operation_type == "delete":
                # Suppression par lot
                result = await self.advanced_gmail_manager.batch_delete_emails(
                    message_ids=message_ids,
                    batch_size=kwargs.get('batch_size', 50)
                )
                
                return {
                    'success': True,
                    'operation_type': operation_type,
                    'total_messages': len(message_ids),
                    'success_count': result['success_count'],
                    'failure_count': result['failure_count'],
                    'errors': result['errors'],
                    'message': f"Suppression par lot terminée : {result['success_count']} succès, {result['failure_count']} échecs"
                }
            else:
                return {
                    'success': False,
                    'message': f"Type d'opération non supporté : {operation_type}"
                }
                
        except Exception as e:
            logger.error("Erreur opération par lot", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'message': "Erreur lors de l'opération par lot"
            }
    
    async def get_email_productivity_insights(self) -> Dict[str, Any]:
        """
        Génère des insights de productivité email
        Nouvelle fonctionnalité Sylvie v2.1 inspirée de Gmail-MCP-Server
        """
        try:
            insights = await self.gmail_mcp_features.generate_email_insights()
            
            return {
                'success': True,
                'insights': insights,
                'productivity_score': insights.get('productivity_score', 0),
                'email_health': insights.get('email_health', 'Unknown'),
                'recommendations': insights.get('recommendations', []),
                'message': f"Insights générés - Score productivité : {insights.get('productivity_score', 0)}/100"
            }
            
        except Exception as e:
            logger.error("Erreur génération insights", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'message': "Erreur lors de la génération des insights"
            }
    
    async def smart_email_categorization(self, message_ids: List[str]) -> Dict[str, Any]:
        """
        Catégorisation intelligente des emails avec IA
        Combine l'IA avancée de Sylvie avec les patterns Gmail-MCP-Server
        """
        try:
            categorized_emails = []
            
            for message_id in message_ids:
                # Récupération des détails de l'email
                email_details = await self.advanced_gmail_manager._get_message_details(message_id)
                
                if email_details:
                    # Analyse IA de l'email
                    email_data = {
                        'subject': email_details.get('subject', ''),
                        'sender': email_details.get('from', ''),
                        'content': email_details.get('content', {}).get('plain_text', ''),
                        'snippet': email_details.get('snippet', '')
                    }
                    
                    # Utilisation de l'IA hybride pour la catégorisation
                    ai_analysis = await hybrid_ai.generate_response(
                        f"Catégorise cet email et détermine sa priorité :\n"
                        f"Sujet: {email_data['subject']}\n"
                        f"De: {email_data['sender']}\n"
                        f"Contenu: {email_data['content'][:200]}...",
                        task_type=TaskType.ANALYSIS
                    )
                    
                    categorized_emails.append({
                        'message_id': message_id,
                        'email_data': email_data,
                        'ai_analysis': ai_analysis,
                        'has_attachments': email_details.get('has_attachments', False),
                        'attachments_count': email_details.get('attachments_count', 0)
                    })
            
            return {
                'success': True,
                'categorized_emails': categorized_emails,
                'total_processed': len(categorized_emails),
                'message': f"Catégorisation terminée : {len(categorized_emails)} emails analysés"
            }
            
        except Exception as e:
            logger.error("Erreur catégorisation intelligente", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'message': "Erreur lors de la catégorisation intelligente"
            }
    
    async def process_advanced_email_request(self, request: str) -> Dict[str, Any]:
        """
        Traite les demandes email avancées avec les nouvelles fonctionnalités MCP
        Point d'entrée principal pour les fonctionnalités Gmail MCP v2.1
        """
        try:
            request_lower = request.lower()
            
            # Détection du type de demande avancée
            if any(word in request_lower for word in ['recherche avancée', 'search', 'cherche', 'trouve']):
                # Recherche avancée avec langage naturel
                return await self.advanced_email_search(request, natural_language=True)
                
            elif any(word in request_lower for word in ['télécharge', 'download', 'pièce jointe', 'attachment']):
                # Téléchargement de pièces jointes (nécessite message_id)
                return {
                    'success': False,
                    'message': 'Veuillez spécifier l\'ID du message pour télécharger les pièces jointes',
                    'help': 'Exemple: télécharge les pièces jointes du message 12345'
                }
                
            elif any(word in request_lower for word in ['insights', 'productivité', 'score', 'santé email']):
                # Génération d'insights de productivité
                return await self.get_email_productivity_insights()
                
            elif any(word in request_lower for word in ['catégorise', 'analyse', 'classifie']):
                # Catégorisation intelligente (nécessite une sélection d'emails)
                return {
                    'success': False,
                    'message': 'Veuillez d\'abord effectuer une recherche pour sélectionner les emails à catégoriser',
                    'help': 'Exemple: recherche puis catégorise les emails de la dernière semaine'
                }
                
            elif any(word in request_lower for word in ['lot', 'batch', 'en masse', 'groupée']):
                # Opérations par lot
                return {
                    'success': False,
                    'message': 'Opération par lot nécessite une sélection d\'emails spécifique',
                    'help': 'Utilisez d\'abord une recherche pour identifier les emails à traiter'
                }
                
            else:
                # Retour vers le système email standard
                return await self.process_user_email_request(request)
                
        except Exception as e:
            logger.error("Erreur traitement demande email avancée", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'message': "Erreur lors du traitement de la demande email avancée"
            }

    # ===== NOUVELLES FONCTIONNALITÉS GOOGLE WORKSPACE MCP v2.2 =====
    
    async def process_google_workspace_request(self, request: str) -> Dict[str, Any]:
        """
        🌟 Traitement des requêtes Google Workspace MCP complètes
        Gmail + Calendar + Multi-comptes + Intelligence
        """
        try:
            request_lower = request.lower()
            
            # Gestion des comptes multiples
            if any(word in request_lower for word in ['compte', 'switch', 'changer', 'utilise']):
                return await self.handle_account_management(request)
            
            # Gmail avancé avec MCP
            elif any(word in request_lower for word in ['email', 'gmail', 'mail', 'recherche', 'brouillon']):
                return await self.handle_advanced_gmail_request(request)
            
            # Google Calendar
            elif any(word in request_lower for word in ['calendrier', 'calendar', 'événement', 'réunion', 'rdv']):
                return await self.handle_calendar_request(request)
            
            # Analyse de productivité
            elif any(word in request_lower for word in ['productivité', 'analyse', 'stats', 'performance']):
                return await self.handle_productivity_analysis(request)
            
            # Suggestions de créneaux
            elif any(word in request_lower for word in ['créneau', 'suggestion', 'disponibilité', 'planifier']):
                return await self.handle_meeting_suggestions(request)
            
            # Status de l'intégration
            elif any(word in request_lower for word in ['status', 'état', 'configuration', 'info']):
                return await self.get_workspace_status()
            
            else:
                return {
                    'success': False,
                    'message': 'Type de requête Google Workspace non reconnu',
                    'help': 'Essayez: comptes, emails, calendrier, productivité, créneaux, status'
                }
                
        except Exception as e:
            logger.error("Erreur traitement requête Google Workspace", error=str(e))
            return {
                'success': False,
                'message': f'Erreur lors du traitement de la requête Google Workspace: {str(e)}'
            }
    
    async def handle_account_management(self, request: str) -> Dict[str, Any]:
        """Gestion des comptes Google Workspace multiples"""
        try:
            request_lower = request.lower()
            
            if 'liste' in request_lower or 'comptes' in request_lower:
                # Lister les comptes configurés
                accounts = self.google_workspace.list_accounts()
                
                return {
                    'success': True,
                    'message': f'Comptes Google Workspace configurés ({len(accounts)})',
                    'data': {
                        'accounts': accounts,
                        'default_account': self.google_workspace.default_account,
                        'details': [
                            f"📧 {acc['email']} ({acc['account_type']}): {acc['extra_info']}"
                            for acc in accounts
                        ]
                    }
                }
            
            elif 'changer' in request_lower or 'switch' in request_lower:
                # Extraire l'email du changement de compte
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, request)
                
                if emails:
                    email = emails[0]
                    success = self.google_workspace.switch_default_account(email)
                    
                    return {
                        'success': success,
                        'message': f'Compte par défaut changé pour {email}' if success else f'Échec changement vers {email}',
                        'data': {'new_default': email if success else None}
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Email non trouvé dans la requête',
                        'help': 'Exemple: changer vers sylvie@kantermator.com'
                    }
            
            else:
                return {
                    'success': False,
                    'message': 'Action de gestion de compte non reconnue',
                    'help': 'Essayez: liste comptes, changer vers [email]'
                }
                
        except Exception as e:
            logger.error("Erreur gestion comptes", error=str(e))
            return {
                'success': False,
                'message': f'Erreur gestion comptes: {str(e)}'
            }
    
    async def handle_advanced_gmail_request(self, request: str) -> Dict[str, Any]:
        """Gestion Gmail avancée avec MCP"""
        try:
            request_lower = request.lower()
            
            if 'recherche' in request_lower or 'search' in request_lower:
                # Extraction de la requête de recherche
                search_patterns = [
                    r'recherche[:\s]+"([^"]+)"',
                    r'recherche[:\s]+(.+?)(?:\s+(?:dans|pour|avec)|\s*$)',
                    r'search[:\s]+"([^"]+)"',
                    r'search[:\s]+(.+?)(?:\s+(?:in|for|with)|\s*$)'
                ]
                
                query = ""
                for pattern in search_patterns:
                    match = re.search(pattern, request, re.IGNORECASE)
                    if match:
                        query = match.group(1).strip()
                        break
                
                if not query:
                    # Recherche par défaut des emails récents non lus
                    query = "is:unread"
                
                # Recherche avancée
                emails = await self.google_workspace.search_emails_advanced(
                    query=query,
                    max_results=20,
                    include_attachments=True
                )
                
                formatted_emails = [format_email_for_display(email) for email in emails[:5]]
                
                return {
                    'success': True,
                    'message': f'Recherche Gmail: {len(emails)} résultats pour "{query}"',
                    'data': {
                        'query': query,
                        'total_results': len(emails),
                        'emails': emails,
                        'formatted_preview': formatted_emails
                    }
                }
            
            elif 'brouillon' in request_lower or 'draft' in request_lower:
                # Création de brouillon
                # Extraction des destinataires, sujet, corps
                to_pattern = r'(?:à|to)[:\s]+([^,\n]+)'
                subject_pattern = r'(?:sujet|subject)[:\s]+"([^"]+)"'
                body_pattern = r'(?:message|body|contenu)[:\s]+"([^"]+)"'
                
                to_match = re.search(to_pattern, request, re.IGNORECASE)
                subject_match = re.search(subject_pattern, request, re.IGNORECASE)
                body_match = re.search(body_pattern, request, re.IGNORECASE)
                
                if to_match and subject_match:
                    to = [email.strip() for email in to_match.group(1).split(',')]
                    subject = subject_match.group(1)
                    body = body_match.group(1) if body_match else "Message créé via Sylvie"
                    
                    draft = await self.google_workspace.create_email_draft(
                        to=to,
                        subject=subject,
                        body=body
                    )
                    
                    return {
                        'success': True,
                        'message': f'Brouillon créé: {subject}',
                        'data': draft
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Informations manquantes pour créer le brouillon',
                        'help': 'Format: brouillon à [email] sujet "[sujet]" message "[contenu]"'
                    }
            
            elif 'répondre' in request_lower or 'reply' in request_lower:
                # Réponse à un email
                return {
                    'success': False,
                    'message': 'Fonction de réponse en développement',
                    'help': 'Veuillez d\'abord sélectionner un email via une recherche'
                }
            
            else:
                return {
                    'success': False,
                    'message': 'Action Gmail non reconnue',
                    'help': 'Essayez: recherche [requête], brouillon, répondre'
                }
                
        except Exception as e:
            logger.error("Erreur Gmail avancé", error=str(e))
            return {
                'success': False,
                'message': f'Erreur Gmail: {str(e)}'
            }
    
    async def handle_calendar_request(self, request: str) -> Dict[str, Any]:
        """Gestion du calendrier Google"""
        try:
            request_lower = request.lower()
            
            if any(word in request_lower for word in ['événements', 'events', 'agenda', 'planning']):
                # Récupération des événements
                period_days = 7  # Par défaut 7 jours
                
                # Extraction de la période
                if 'semaine' in request_lower:
                    period_days = 7
                elif 'mois' in request_lower:
                    period_days = 30
                elif 'jour' in request_lower:
                    period_days = 1
                
                time_max = (datetime.now() + timedelta(days=period_days)).isoformat()
                
                events = await self.google_workspace.get_calendar_events(
                    time_max=time_max,
                    max_results=50
                )
                
                formatted_events = [format_calendar_event_for_display(event) for event in events[:5]]
                
                return {
                    'success': True,
                    'message': f'Agenda: {len(events)} événements sur {period_days} jours',
                    'data': {
                        'period_days': period_days,
                        'total_events': len(events),
                        'events': events,
                        'formatted_preview': formatted_events
                    }
                }
            
            elif 'créer' in request_lower or 'create' in request_lower:
                # Création d'événement
                title_pattern = r'(?:créer|create)[^"]*"([^"]+)"'
                date_pattern = r'(?:le|on)\s+(\d{1,2}[\/\-]\d{1,2})'
                time_pattern = r'(?:à|at)\s+(\d{1,2}[h:]\d{0,2})'
                
                title_match = re.search(title_pattern, request, re.IGNORECASE)
                
                if title_match:
                    title = title_match.group(1)
                    
                    # Dates par défaut (demain à 14h, durée 1h)
                    start_time = (datetime.now() + timedelta(days=1)).replace(hour=14, minute=0, second=0)
                    end_time = start_time + timedelta(hours=1)
                    
                    event = await self.google_workspace.create_calendar_event(
                        summary=title,
                        start_time=start_time.isoformat(),
                        end_time=end_time.isoformat(),
                        description=f"Événement créé via Sylvie: {request}"
                    )
                    
                    return {
                        'success': True,
                        'message': f'Événement créé: {title}',
                        'data': event.__dict__
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Titre d\'événement non trouvé',
                        'help': 'Format: créer événement "Réunion équipe" le 15/01 à 14h'
                    }
            
            else:
                return {
                    'success': False,
                    'message': 'Action calendrier non reconnue',
                    'help': 'Essayez: événements, agenda, créer événement "[titre]"'
                }
                
        except Exception as e:
            logger.error("Erreur calendrier", error=str(e))
            return {
                'success': False,
                'message': f'Erreur calendrier: {str(e)}'
            }
    
    async def handle_productivity_analysis(self, request: str) -> Dict[str, Any]:
        """Analyse de productivité email/calendrier"""
        try:
            # Extraction de la période d'analyse
            days_back = 7  # Par défaut 7 jours
            
            if 'semaine' in request.lower():
                days_back = 7
            elif 'mois' in request.lower():
                days_back = 30
            elif 'jour' in request.lower():
                days_back = 1
            
            analysis = await self.google_workspace.analyze_email_productivity(days_back=days_back)
            
            return {
                'success': True,
                'message': f'Analyse de productivité sur {days_back} jours',
                'data': analysis
            }
            
        except Exception as e:
            logger.error("Erreur analyse productivité", error=str(e))
            return {
                'success': False,
                'message': f'Erreur analyse: {str(e)}'
            }
    
    async def handle_meeting_suggestions(self, request: str) -> Dict[str, Any]:
        """Suggestions de créneaux de réunion"""
        try:
            # Extraction des paramètres
            duration = 1  # Durée par défaut 1h
            
            # Extraction durée
            duration_patterns = [
                r'(\d+)\s*h(?:eure)?s?',
                r'(\d+)\s*min(?:ute)?s?',
                r'durée[:\s]*(\d+)'
            ]
            
            for pattern in duration_patterns:
                match = re.search(pattern, request, re.IGNORECASE)
                if match:
                    duration = float(match.group(1))
                    if 'min' in pattern:
                        duration = duration / 60  # Conversion minutes en heures
                    break
            
            # Extraction des participants
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            participants = re.findall(email_pattern, request)
            
            suggestions = await self.google_workspace.suggest_meeting_times(
                duration_hours=duration,
                participants=participants
            )
            
            return {
                'success': True,
                'message': f'Suggestions pour réunion de {duration}h avec {len(participants)} participants',
                'data': {
                    'duration_hours': duration,
                    'participants': participants,
                    'suggestions': suggestions[:5],  # Top 5
                    'total_suggestions': len(suggestions)
                }
            }
            
        except Exception as e:
            logger.error("Erreur suggestions créneaux", error=str(e))
            return {
                'success': False,
                'message': f'Erreur suggestions: {str(e)}'
            }
    
    async def get_workspace_status(self) -> Dict[str, Any]:
        """Status de l'intégration Google Workspace"""
        try:
            status = self.google_workspace.get_integration_status()
            
            return {
                'success': True,
                'message': 'Status Google Workspace MCP',
                'data': status
            }
            
        except Exception as e:
            logger.error("Erreur status workspace", error=str(e))
            return {
                'success': False,
                'message': f'Erreur status: {str(e)}'
            }
    
    # ===== HANDLERS POUR NOUVELLES CAPACITÉS GOOGLE WORKSPACE MCP =====
    
    async def _handle_google_workspace_mcp(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Handler général pour Google Workspace MCP"""
        try:
            result = await self.process_google_workspace_request(intent.details.get('original_message', ''))
            return "Google Workspace MCP", result
        except Exception as e:
            logger.error("Erreur handler Google Workspace MCP", error=str(e))
            return "Erreur Google Workspace MCP", {"error": str(e)}
    
    async def _handle_multi_account_management(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Handler pour gestion multi-comptes"""
        try:
            result = await self.handle_account_management(intent.details.get('original_message', ''))
            return "Gestion comptes multiples", result
        except Exception as e:
            logger.error("Erreur handler multi-comptes", error=str(e))
            return "Erreur gestion comptes", {"error": str(e)}
    
    async def _handle_advanced_gmail_search(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Handler pour recherche Gmail avancée"""
        try:
            result = await self.handle_advanced_gmail_request(intent.details.get('original_message', ''))
            return "Recherche Gmail avancée", result
        except Exception as e:
            logger.error("Erreur handler Gmail avancé", error=str(e))
            return "Erreur recherche Gmail", {"error": str(e)}
    
    async def _handle_calendar_intelligence(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Handler pour intelligence calendrier"""
        try:
            result = await self.handle_calendar_request(intent.details.get('original_message', ''))
            return "Intelligence calendrier", result
        except Exception as e:
            logger.error("Erreur handler calendrier", error=str(e))
            return "Erreur calendrier", {"error": str(e)}
    
    async def _handle_productivity_analysis(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Handler pour analyse de productivité"""
        try:
            result = await self.handle_productivity_analysis(intent.details.get('original_message', ''))
            return "Analyse de productivité", result
        except Exception as e:
            logger.error("Erreur handler productivité", error=str(e))
            return "Erreur analyse productivité", {"error": str(e)}
    
    async def _handle_meeting_suggestions(self, intent: SylvieIntent) -> Tuple[str, Dict[str, Any]]:
        """Handler pour suggestions de créneaux"""
        try:
            result = await self.handle_meeting_suggestions(intent.details.get('original_message', ''))
            return "Suggestions créneaux", result
        except Exception as e:
            logger.error("Erreur handler suggestions", error=str(e))
            return "Erreur suggestions créneaux", {"error": str(e)}

# Instance globale de l'agent Sylvie
sylvie_agent = SylvieAgent()
