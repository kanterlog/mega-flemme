"""
📊 Service Slides pour Sylvie
Phase 3.10 - Intégration Google Slides

Gestion complète des présentations Google Slides pour KanterMator
"""

import structlog
from datetime import datetime
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.services.google_auth import GoogleAuthService

logger = structlog.get_logger(__name__)

class SlidesService:
    """Service de gestion des présentations Google Slides"""
    
    def __init__(self):
        self.auth_service = GoogleAuthService()
        self.slides_service = None
        self.drive_service = None
        # Pas d'initialisation synchrone, sera fait lors du premier appel async
    
    async def _ensure_service_initialized(self):
        """Assure que le service Slides est initialisé"""
        if self.slides_service is None:
            try:
                credentials = await self.auth_service.get_credentials()
                self.slides_service = build('slides', 'v1', credentials=credentials)
                self.drive_service = build('drive', 'v3', credentials=credentials)
                logger.info("✅ Service Slides initialisé")
            except Exception as e:
                logger.error("❌ Erreur initialisation Slides", error=str(e))
                raise
    
    async def create_presentation(self, title: str, template_type: str = "educational") -> Optional[Dict[str, Any]]:
        """
        Crée une nouvelle présentation
        
        Args:
            title: Titre de la présentation
            template_type: Type de template (educational, meeting, report)
            
        Returns:
            Informations sur la présentation créée
        """
        await self._ensure_service_initialized()
        
        try:
            # Création de la présentation
            presentation = {
                'title': title
            }
            
            created_presentation = self.slides_service.presentations().create(
                body=presentation
            ).execute()
            
            presentation_id = created_presentation['presentationId']
            
            # Application du template
            await self._apply_template(presentation_id, template_type)
            
            # Récupération des informations de la présentation
            presentation_info = self.slides_service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            logger.info("✅ Présentation créée", title=title, presentation_id=presentation_id)
            
            return {
                'id': presentation_id,
                'title': presentation_info['title'],
                'url': f"https://docs.google.com/presentation/d/{presentation_id}/edit",
                'slide_count': len(presentation_info.get('slides', [])),
                'template_type': template_type,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("❌ Erreur création présentation", error=str(e))
            return None
    
    async def _apply_template(self, presentation_id: str, template_type: str):
        """Applique un template à la présentation"""
        try:
            if template_type == "educational":
                await self._apply_educational_template(presentation_id)
            elif template_type == "meeting":
                await self._apply_meeting_template(presentation_id)
            elif template_type == "report":
                await self._apply_report_template(presentation_id)
                
        except Exception as e:
            logger.warning("⚠️ Erreur application template", error=str(e))
    
    async def _apply_educational_template(self, presentation_id: str):
        """Applique un template éducatif"""
        requests = [
            {
                'createSlide': {
                    'objectId': 'slide_title',
                    'insertionIndex': 1,
                    'slideLayoutReference': {
                        'predefinedLayout': 'TITLE_AND_BODY'
                    }
                }
            },
            {
                'insertText': {
                    'objectId': 'slide_title',
                    'text': 'Objectifs d\'apprentissage\n\n• Point 1\n• Point 2\n• Point 3'
                }
            }
        ]
        
        self.slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
    
    async def _apply_meeting_template(self, presentation_id: str):
        """Applique un template de réunion"""
        requests = [
            {
                'createSlide': {
                    'objectId': 'slide_agenda',
                    'insertionIndex': 1,
                    'slideLayoutReference': {
                        'predefinedLayout': 'TITLE_AND_BODY'
                    }
                }
            },
            {
                'insertText': {
                    'objectId': 'slide_agenda',
                    'text': 'Ordre du jour\n\n1. Introduction\n2. Points principaux\n3. Actions à suivre'
                }
            }
        ]
        
        self.slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
    
    async def _apply_report_template(self, presentation_id: str):
        """Applique un template de rapport"""
        requests = [
            {
                'createSlide': {
                    'objectId': 'slide_summary',
                    'insertionIndex': 1,
                    'slideLayoutReference': {
                        'predefinedLayout': 'TITLE_AND_BODY'
                    }
                }
            },
            {
                'insertText': {
                    'objectId': 'slide_summary',
                    'text': 'Résumé exécutif\n\n• Résultats clés\n• Recommandations\n• Prochaines étapes'
                }
            }
        ]
        
        self.slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
    
    async def get_presentations(self, max_results: int = 15) -> List[Dict[str, Any]]:
        """
        Récupère les présentations récentes
        
        Args:
            max_results: Nombre maximum de présentations
            
        Returns:
            Liste des présentations
        """
        await self._ensure_service_initialized()
        
        try:
            # Recherche des présentations via Drive
            query = "mimeType='application/vnd.google-apps.presentation'"
            results = self.drive_service.files().list(
                q=query,
                pageSize=max_results,
                orderBy='modifiedTime desc',
                fields='files(id, name, modifiedTime, createdTime, webViewLink)'
            ).execute()
            
            files = results.get('files', [])
            presentations = []
            
            for file in files:
                presentations.append({
                    'id': file['id'],
                    'title': file['name'],
                    'url': file['webViewLink'],
                    'modified_time': file['modifiedTime'],
                    'created_time': file['createdTime']
                })
            
            logger.info("📊 Présentations récupérées", count=len(presentations))
            return presentations
            
        except Exception as e:
            logger.error("❌ Erreur récupération présentations", error=str(e))
            return []
    
    async def add_slide_with_content(self, presentation_id: str, title: str, content: str, layout: str = "TITLE_AND_BODY") -> bool:
        """
        Ajoute une slide avec du contenu
        
        Args:
            presentation_id: ID de la présentation
            title: Titre de la slide
            content: Contenu de la slide
            layout: Layout de la slide
            
        Returns:
            True si succès, False sinon
        """
        await self._ensure_service_initialized()
        
        try:
            # Génération d'un ID unique pour la slide
            slide_id = f"slide_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            requests = [
                {
                    'createSlide': {
                        'objectId': slide_id,
                        'slideLayoutReference': {
                            'predefinedLayout': layout
                        }
                    }
                }
            ]
            
            # Ajout de la slide
            self.slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': requests}
            ).execute()
            
            # Ajout du contenu
            content_requests = [
                {
                    'insertText': {
                        'objectId': slide_id,
                        'text': f"{title}\n\n{content}"
                    }
                }
            ]
            
            self.slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': content_requests}
            ).execute()
            
            logger.info("✅ Slide ajoutée", presentation_id=presentation_id, title=title)
            return True
            
        except Exception as e:
            logger.error("❌ Erreur ajout slide", error=str(e))
            return False
    
    async def get_presentation_info(self, presentation_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'une présentation"""
        await self._ensure_service_initialized()
        
        try:
            presentation = self.slides_service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            return {
                'id': presentation['presentationId'],
                'title': presentation['title'],
                'slide_count': len(presentation.get('slides', [])),
                'url': f"https://docs.google.com/presentation/d/{presentation_id}/edit"
            }
            
        except Exception as e:
            logger.error("❌ Erreur info présentation", error=str(e))
            return None
    
    async def get_slides_summary_for_sylvie(self) -> Dict[str, Any]:
        """Génère un résumé des présentations pour Sylvie"""
        try:
            presentations = await self.get_presentations(max_results=50)
            
            total_presentations = len(presentations)
            recent_presentations = presentations[:5]
            
            # Analyse des présentations récentes
            presentations_this_week = 0
            presentations_this_month = 0
            
            now = datetime.now()
            
            for pres in presentations:
                try:
                    modified_date = datetime.fromisoformat(pres['modified_time'].replace('Z', ''))
                    days_ago = (now - modified_date).days
                    
                    if days_ago <= 7:
                        presentations_this_week += 1
                    if days_ago <= 30:
                        presentations_this_month += 1
                        
                except:
                    pass
            
            return {
                'total_presentations': total_presentations,
                'recent_presentations': recent_presentations,
                'presentations_this_week': presentations_this_week,
                'presentations_this_month': presentations_this_month,
                'productivity_indicator': 'active' if presentations_this_week > 0 else 'low'
            }
            
        except Exception as e:
            logger.error("❌ Erreur résumé présentations", error=str(e))
            return {
                'total_presentations': 0,
                'recent_presentations': [],
                'presentations_this_week': 0,
                'presentations_this_month': 0,
                'productivity_indicator': 'unknown'
            }

# Instance globale du service
slides_service = SlidesService()
