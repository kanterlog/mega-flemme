"""
📄 Service Documents pour Sylvie
Phase 3.11 - Intégration Google Docs

Gestion complète des documents Google Docs pour KanterMator
"""

import structlog
from datetime import datetime
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.services.google_auth import GoogleAuthService

logger = structlog.get_logger(__name__)

class DocsService:
    """Service de gestion des documents Google Docs"""
    
    def __init__(self):
        self.auth_service = GoogleAuthService()
        self.docs_service = None
        self.drive_service = None
        # Pas d'initialisation synchrone, sera fait lors du premier appel async
    
    async def _ensure_service_initialized(self):
        """Assure que le service Docs est initialisé"""
        if self.docs_service is None:
            try:
                credentials = await self.auth_service.get_credentials()
                self.docs_service = build('docs', 'v1', credentials=credentials)
                self.drive_service = build('drive', 'v3', credentials=credentials)
                logger.info("✅ Service Docs initialisé")
            except Exception as e:
                logger.error("❌ Erreur initialisation Docs", error=str(e))
                raise
    
    async def create_document(self, title: str, template_type: str = "report") -> Optional[Dict[str, Any]]:
        """
        Crée un nouveau document
        
        Args:
            title: Titre du document
            template_type: Type de template (report, meeting_notes, lesson_plan, assignment)
            
        Returns:
            Informations sur le document créé
        """
        await self._ensure_service_initialized()
        
        try:
            # Création du document
            document = {
                'title': title
            }
            
            created_document = self.docs_service.documents().create(
                body=document
            ).execute()
            
            document_id = created_document['documentId']
            
            # Application du template
            await self._apply_template(document_id, template_type, title)
            
            logger.info("✅ Document créé", title=title, document_id=document_id)
            
            return {
                'id': document_id,
                'title': title,
                'url': f"https://docs.google.com/document/d/{document_id}/edit",
                'template_type': template_type,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("❌ Erreur création document", error=str(e))
            return None
    
    async def _apply_template(self, document_id: str, template_type: str, title: str):
        """Applique un template au document"""
        try:
            if template_type == "report":
                await self._apply_report_template(document_id, title)
            elif template_type == "meeting_notes":
                await self._apply_meeting_notes_template(document_id, title)
            elif template_type == "lesson_plan":
                await self._apply_lesson_plan_template(document_id, title)
            elif template_type == "assignment":
                await self._apply_assignment_template(document_id, title)
            else:
                await self._apply_basic_template(document_id, title)
                
        except Exception as e:
            logger.warning("⚠️ Erreur application template", error=str(e))
    
    async def _apply_report_template(self, document_id: str, title: str):
        """Applique un template de rapport"""
        content = f"""
{title}

Date: {datetime.now().strftime('%d/%m/%Y')}

I. RÉSUMÉ EXÉCUTIF
[Résumé des points clés]

II. INTRODUCTION
[Contexte et objectifs]

III. MÉTHODOLOGIE
[Approche utilisée]

IV. RÉSULTATS
[Principales découvertes]

V. ANALYSE
[Interprétation des résultats]

VI. RECOMMANDATIONS
[Actions proposées]

VII. CONCLUSION
[Synthèse finale]

VIII. ANNEXES
[Documents de support]
"""
        await self._insert_content(document_id, content)
    
    async def _apply_meeting_notes_template(self, document_id: str, title: str):
        """Applique un template de notes de réunion"""
        content = f"""
{title}

📅 Date: {datetime.now().strftime('%d/%m/%Y')}
⏰ Heure: {datetime.now().strftime('%H:%M')}
👥 Participants:
- 
- 
- 

📋 ORDRE DU JOUR
1. 
2. 
3. 

📝 NOTES DE RÉUNION

🎯 ACTIONS À SUIVRE
• Action 1 - Responsable: [Nom] - Échéance: [Date]
• Action 2 - Responsable: [Nom] - Échéance: [Date]
• Action 3 - Responsable: [Nom] - Échéance: [Date]

📊 DÉCISIONS PRISES
- 
- 
- 

🔄 PROCHAINE RÉUNION
Date: [À définir]
Objectif: [À définir]
"""
        await self._insert_content(document_id, content)
    
    async def _apply_lesson_plan_template(self, document_id: str, title: str):
        """Applique un template de plan de cours"""
        content = f"""
{title}

📚 INFORMATIONS GÉNÉRALES
Matière: [Matière]
Niveau: [Niveau]
Durée: [Durée]
Date: {datetime.now().strftime('%d/%m/%Y')}

🎯 OBJECTIFS PÉDAGOGIQUES
• Objectif 1: 
• Objectif 2: 
• Objectif 3: 

📖 PRÉREQUIS
• 
• 
• 

📝 DÉROULEMENT DU COURS

1. INTRODUCTION (X min)
   - Rappel des notions précédentes
   - Présentation des objectifs

2. DÉVELOPPEMENT (X min)
   - Point principal 1
   - Point principal 2
   - Exercices pratiques

3. SYNTHÈSE (X min)
   - Récapitulatif
   - Questions/Réponses

4. ÉVALUATION (X min)
   - Exercices d'application
   - Vérification des acquis

📚 RESSOURCES
• Manuel: 
• Documents: 
• Outils: 

🏠 TRAVAIL À LA MAISON
• Exercice 1: 
• Lecture: 
• Préparation: 

📊 ÉVALUATION DES ACQUIS
Critères d'évaluation:
• 
• 
• 
"""
        await self._insert_content(document_id, content)
    
    async def _apply_assignment_template(self, document_id: str, title: str):
        """Applique un template de devoir"""
        content = f"""
{title}

📋 INFORMATIONS
Matière: [Matière]
Classe: [Classe]
Date de remise: [Date]
Durée estimée: [Durée]

🎯 OBJECTIFS
Cet exercice vise à évaluer votre capacité à:
• 
• 
• 

📝 CONSIGNES
1. 
2. 
3. 

⚠️ CRITÈRES D'ÉVALUATION
• Critère 1 (X points): 
• Critère 2 (X points): 
• Critère 3 (X points): 

📚 RESSOURCES AUTORISÉES
• 
• 
• 

📤 MODALITÉS DE REMISE
Format: [Format attendu]
Où: [Lieu de dépôt]
Quand: [Date et heure limite]

💡 CONSEILS
• 
• 
• 
"""
        await self._insert_content(document_id, content)
    
    async def _apply_basic_template(self, document_id: str, title: str):
        """Applique un template de base"""
        content = f"""
{title}

Date: {datetime.now().strftime('%d/%m/%Y')}

[Votre contenu ici]
"""
        await self._insert_content(document_id, content)
    
    async def _insert_content(self, document_id: str, content: str):
        """Insère du contenu dans un document"""
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': 1
                    },
                    'text': content
                }
            }
        ]
        
        self.docs_service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()
    
    async def get_documents(self, max_results: int = 15) -> List[Dict[str, Any]]:
        """
        Récupère les documents récents
        
        Args:
            max_results: Nombre maximum de documents
            
        Returns:
            Liste des documents
        """
        await self._ensure_service_initialized()
        
        try:
            # Recherche des documents via Drive
            query = "mimeType='application/vnd.google-apps.document'"
            results = self.drive_service.files().list(
                q=query,
                pageSize=max_results,
                orderBy='modifiedTime desc',
                fields='files(id, name, modifiedTime, createdTime, webViewLink)'
            ).execute()
            
            files = results.get('files', [])
            documents = []
            
            for file in files:
                documents.append({
                    'id': file['id'],
                    'title': file['name'],
                    'url': file['webViewLink'],
                    'modified_time': file['modifiedTime'],
                    'created_time': file['createdTime']
                })
            
            logger.info("📄 Documents récupérés", count=len(documents))
            return documents
            
        except Exception as e:
            logger.error("❌ Erreur récupération documents", error=str(e))
            return []
    
    async def get_document_content(self, document_id: str) -> Optional[str]:
        """Récupère le contenu d'un document"""
        await self._ensure_service_initialized()
        
        try:
            document = self.docs_service.documents().get(
                documentId=document_id
            ).execute()
            
            content = []
            for element in document.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    paragraph = element['paragraph']
                    for text_run in paragraph.get('elements', []):
                        if 'textRun' in text_run:
                            content.append(text_run['textRun']['content'])
            
            return ''.join(content)
            
        except Exception as e:
            logger.error("❌ Erreur lecture document", error=str(e))
            return None
    
    async def append_to_document(self, document_id: str, text: str) -> bool:
        """Ajoute du texte à la fin d'un document"""
        await self._ensure_service_initialized()
        
        try:
            # Récupération de la longueur du document
            document = self.docs_service.documents().get(
                documentId=document_id
            ).execute()
            
            end_index = document['body']['content'][-1]['endIndex'] - 1
            
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': end_index
                        },
                        'text': f"\n\n{text}"
                    }
                }
            ]
            
            self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            logger.info("✅ Texte ajouté au document", document_id=document_id)
            return True
            
        except Exception as e:
            logger.error("❌ Erreur ajout texte", error=str(e))
            return False
    
    async def get_docs_summary_for_sylvie(self) -> Dict[str, Any]:
        """Génère un résumé des documents pour Sylvie"""
        try:
            documents = await self.get_documents(max_results=50)
            
            total_documents = len(documents)
            recent_documents = documents[:5]
            
            # Analyse des documents récents
            documents_this_week = 0
            documents_this_month = 0
            
            now = datetime.now()
            
            for doc in documents:
                try:
                    modified_date = datetime.fromisoformat(doc['modified_time'].replace('Z', ''))
                    days_ago = (now - modified_date).days
                    
                    if days_ago <= 7:
                        documents_this_week += 1
                    if days_ago <= 30:
                        documents_this_month += 1
                        
                except:
                    pass
            
            return {
                'total_documents': total_documents,
                'recent_documents': recent_documents,
                'documents_this_week': documents_this_week,
                'documents_this_month': documents_this_month,
                'productivity_indicator': 'active' if documents_this_week > 0 else 'low'
            }
            
        except Exception as e:
            logger.error("❌ Erreur résumé documents", error=str(e))
            return {
                'total_documents': 0,
                'recent_documents': [],
                'documents_this_week': 0,
                'documents_this_month': 0,
                'productivity_indicator': 'unknown'
            }

# Instance globale du service
docs_service = DocsService()
