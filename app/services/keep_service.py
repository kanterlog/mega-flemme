"""
📝 Service Keep pour Sylvie
Phase 3.10 - Intégration Google Keep (via Drive)

Gestion des notes Google Keep pour KanterMator
Note: Google Keep n'a pas d'API publique, simulation via Drive
"""

import structlog
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.services.google_auth import GoogleAuthService

logger = structlog.get_logger(__name__)

class KeepService:
    """Service de gestion des notes Google Keep (simulation via Drive)"""
    
    def __init__(self):
        self.auth_service = GoogleAuthService()
        self.drive_service = None
        self.notes_folder_id = None
        # Pas d'initialisation synchrone, sera fait lors du premier appel async
    
    async def _ensure_service_initialized(self):
        """Assure que le service Keep/Drive est initialisé"""
        if self.drive_service is None:
            try:
                credentials = await self.auth_service.get_credentials()
                self.drive_service = build('drive', 'v3', credentials=credentials)
                await self._ensure_notes_folder_exists()
                logger.info("✅ Service Keep (via Drive) initialisé")
            except Exception as e:
                logger.error("❌ Erreur initialisation Keep", error=str(e))
                raise
    
    async def _ensure_notes_folder_exists(self):
        """Assure que le dossier Notes existe dans Drive"""
        try:
            # Recherche du dossier Notes
            query = "name='KanterMator Notes' and mimeType='application/vnd.google-apps.folder'"
            results = self.drive_service.files().list(q=query).execute()
            items = results.get('files', [])
            
            if items:
                self.notes_folder_id = items[0]['id']
            else:
                # Création du dossier Notes
                folder_metadata = {
                    'name': 'KanterMator Notes',
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = self.drive_service.files().create(body=folder_metadata).execute()
                self.notes_folder_id = folder['id']
                logger.info("📁 Dossier Notes créé", folder_id=self.notes_folder_id)
                
        except Exception as e:
            logger.error("❌ Erreur création dossier Notes", error=str(e))
            self.notes_folder_id = None
    
    async def create_note(self, title: str, content: str, labels: List[str] = None, color: str = "white") -> Optional[Dict[str, Any]]:
        """
        Crée une nouvelle note
        
        Args:
            title: Titre de la note
            content: Contenu de la note
            labels: Labels optionnels
            color: Couleur de la note
            
        Returns:
            Informations sur la note créée
        """
        await self._ensure_service_initialized()
        
        if not self.notes_folder_id:
            return None
        
        try:
            # Création du contenu de la note
            note_data = {
                'title': title,
                'content': content,
                'labels': labels or [],
                'color': color,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Nom du fichier
            filename = f"{title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Métadonnées du fichier
            file_metadata = {
                'name': filename,
                'parents': [self.notes_folder_id],
                'description': f'Note KanterMator: {title}'
            }
            
            # Création du fichier avec le contenu JSON
            from googleapiclient.http import MediaIoBaseUpload
            import io
            
            content_json = json.dumps(note_data, ensure_ascii=False, indent=2)
            media = MediaIoBaseUpload(
                io.BytesIO(content_json.encode('utf-8')),
                mimetype='application/json'
            )
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media
            ).execute()
            
            logger.info("✅ Note créée", title=title, file_id=file['id'])
            
            return {
                'id': file['id'],
                'title': title,
                'filename': filename,
                'content': content,
                'labels': labels,
                'color': color,
                'created_at': note_data['created_at']
            }
            
        except Exception as e:
            logger.error("❌ Erreur création note", error=str(e))
            return None
    
    async def get_notes(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Récupère les notes récentes
        
        Args:
            max_results: Nombre maximum de notes
            
        Returns:
            Liste des notes
        """
        await self._ensure_service_initialized()
        
        if not self.notes_folder_id:
            return []
        
        try:
            # Recherche des fichiers dans le dossier Notes
            query = f"'{self.notes_folder_id}' in parents and trashed=false"
            results = self.drive_service.files().list(
                q=query,
                pageSize=max_results,
                orderBy='modifiedTime desc',
                fields='files(id, name, description, modifiedTime, createdTime)'
            ).execute()
            
            files = results.get('files', [])
            notes = []
            
            for file in files:
                try:
                    # Lecture du contenu du fichier
                    content = self.drive_service.files().get_media(fileId=file['id']).execute()
                    note_data = json.loads(content.decode('utf-8'))
                    
                    notes.append({
                        'id': file['id'],
                        'title': note_data.get('title', 'Note sans titre'),
                        'content': note_data.get('content', ''),
                        'labels': note_data.get('labels', []),
                        'color': note_data.get('color', 'white'),
                        'created_at': note_data.get('created_at'),
                        'updated_at': note_data.get('updated_at'),
                        'filename': file['name']
                    })
                    
                except Exception as e:
                    logger.warning("⚠️ Erreur lecture note", file_id=file['id'], error=str(e))
                    continue
            
            logger.info("📝 Notes récupérées", count=len(notes))
            return notes
            
        except Exception as e:
            logger.error("❌ Erreur récupération notes", error=str(e))
            return []
    
    async def search_notes(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Recherche dans les notes
        
        Args:
            query: Terme de recherche
            max_results: Nombre maximum de résultats
            
        Returns:
            Liste des notes correspondantes
        """
        notes = await self.get_notes(max_results * 2)  # Récupère plus pour filtrer
        
        matching_notes = []
        query_lower = query.lower()
        
        for note in notes:
            if (query_lower in note['title'].lower() or 
                query_lower in note['content'].lower() or
                any(query_lower in label.lower() for label in note['labels'])):
                matching_notes.append(note)
                
                if len(matching_notes) >= max_results:
                    break
        
        logger.info("🔍 Recherche notes", query=query, found=len(matching_notes))
        return matching_notes
    
    async def update_note(self, note_id: str, title: str = None, content: str = None, labels: List[str] = None) -> bool:
        """Met à jour une note existante"""
        await self._ensure_service_initialized()
        
        try:
            # Lecture du contenu actuel
            current_content = self.drive_service.files().get_media(fileId=note_id).execute()
            note_data = json.loads(current_content.decode('utf-8'))
            
            # Mise à jour des champs
            if title is not None:
                note_data['title'] = title
            if content is not None:
                note_data['content'] = content
            if labels is not None:
                note_data['labels'] = labels
            
            note_data['updated_at'] = datetime.now().isoformat()
            
            # Réécriture du fichier
            from googleapiclient.http import MediaIoBaseUpload
            import io
            
            content_json = json.dumps(note_data, ensure_ascii=False, indent=2)
            media = MediaIoBaseUpload(
                io.BytesIO(content_json.encode('utf-8')),
                mimetype='application/json'
            )
            
            self.drive_service.files().update(
                fileId=note_id,
                media_body=media
            ).execute()
            
            logger.info("✅ Note mise à jour", note_id=note_id)
            return True
            
        except Exception as e:
            logger.error("❌ Erreur mise à jour note", error=str(e))
            return False
    
    async def delete_note(self, note_id: str) -> bool:
        """Supprime une note"""
        await self._ensure_service_initialized()
        
        try:
            self.drive_service.files().delete(fileId=note_id).execute()
            logger.info("✅ Note supprimée", note_id=note_id)
            return True
            
        except Exception as e:
            logger.error("❌ Erreur suppression note", error=str(e))
            return False
    
    async def get_notes_summary_for_sylvie(self) -> Dict[str, Any]:
        """Génère un résumé des notes pour Sylvie"""
        try:
            notes = await self.get_notes(max_results=100)
            
            # Analyse des notes
            total_notes = len(notes)
            labels_count = {}
            colors_count = {}
            recent_notes = notes[:5]
            
            for note in notes:
                # Comptage des labels
                for label in note['labels']:
                    labels_count[label] = labels_count.get(label, 0) + 1
                
                # Comptage des couleurs
                color = note['color']
                colors_count[color] = colors_count.get(color, 0) + 1
            
            return {
                'total_notes': total_notes,
                'recent_notes': recent_notes,
                'popular_labels': dict(sorted(labels_count.items(), key=lambda x: x[1], reverse=True)[:5]),
                'color_distribution': colors_count,
                'notes_this_week': len([n for n in notes if self._is_recent(n['created_at'], days=7)]),
                'notes_this_month': len([n for n in notes if self._is_recent(n['created_at'], days=30)])
            }
            
        except Exception as e:
            logger.error("❌ Erreur résumé notes", error=str(e))
            return {
                'total_notes': 0,
                'recent_notes': [],
                'popular_labels': {},
                'color_distribution': {},
                'notes_this_week': 0,
                'notes_this_month': 0
            }
    
    def _is_recent(self, date_str: str, days: int) -> bool:
        """Vérifie si une date est récente"""
        try:
            note_date = datetime.fromisoformat(date_str.replace('Z', ''))
            return (datetime.now() - note_date).days <= days
        except:
            return False

# Instance globale du service
keep_service = KeepService()
