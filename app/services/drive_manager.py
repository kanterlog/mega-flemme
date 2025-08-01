"""
💾 Service Drive Manager pour Sylvie
Phase 3.13 - Gestionnaire Google Drive

Gestion avancée des fichiers et dossiers Google Drive pour KanterMator
"""

import structlog
import io
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

from app.services.google_auth import GoogleAuthService

logger = structlog.get_logger(__name__)

class DriveManager:
    """Service de gestion avancée de Google Drive"""
    
    def __init__(self):
        self.auth_service = GoogleAuthService()
        self.drive_service = None
        # Pas d'initialisation synchrone, sera fait lors du premier appel async
    
    async def _ensure_service_initialized(self):
        """Assure que le service Drive est initialisé"""
        if self.drive_service is None:
            try:
                credentials = await self.auth_service.get_credentials()
                self.drive_service = build('drive', 'v3', credentials=credentials)
                logger.info("✅ Service Drive Manager initialisé")
            except Exception as e:
                logger.error("❌ Erreur initialisation Drive Manager", error=str(e))
                raise
    
    async def create_folder(self, name: str, parent_folder_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Crée un nouveau dossier
        
        Args:
            name: Nom du dossier
            parent_folder_id: ID du dossier parent (optionnel)
            
        Returns:
            Informations sur le dossier créé
        """
        await self._ensure_service_initialized()
        
        try:
            folder_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            folder = self.drive_service.files().create(
                body=folder_metadata,
                fields='id, name, webViewLink, createdTime'
            ).execute()
            
            logger.info("📁 Dossier créé", name=name, folder_id=folder['id'])
            
            return {
                'id': folder['id'],
                'name': folder['name'],
                'url': folder['webViewLink'],
                'created_time': folder['createdTime'],
                'type': 'folder'
            }
            
        except Exception as e:
            logger.error("❌ Erreur création dossier", error=str(e))
            return None
    
    async def upload_file(
        self, 
        file_path: str, 
        drive_folder_id: Optional[str] = None,
        file_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Upload un fichier vers Drive
        
        Args:
            file_path: Chemin vers le fichier local
            drive_folder_id: ID du dossier de destination
            file_name: Nom du fichier (optionnel)
            
        Returns:
            Informations sur le fichier uploadé
        """
        await self._ensure_service_initialized()
        
        try:
            import os
            
            if not os.path.exists(file_path):
                logger.error("❌ Fichier introuvable", file_path=file_path)
                return None
            
            file_metadata = {
                'name': file_name or os.path.basename(file_path)
            }
            
            if drive_folder_id:
                file_metadata['parents'] = [drive_folder_id]
            
            media = MediaFileUpload(file_path, resumable=True)
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, size, mimeType'
            ).execute()
            
            logger.info("📤 Fichier uploadé", name=file['name'], file_id=file['id'])
            
            return {
                'id': file['id'],
                'name': file['name'],
                'url': file['webViewLink'],
                'size': file.get('size', 0),
                'mime_type': file['mimeType'],
                'type': 'file'
            }
            
        except Exception as e:
            logger.error("❌ Erreur upload fichier", error=str(e))
            return None
    
    async def download_file(self, file_id: str, download_path: str) -> bool:
        """
        Télécharge un fichier depuis Drive
        
        Args:
            file_id: ID du fichier Drive
            download_path: Chemin de destination local
            
        Returns:
            True si succès, False sinon
        """
        await self._ensure_service_initialized()
        
        try:
            request = self.drive_service.files().get_media(fileId=file_id)
            file_handle = io.BytesIO()
            
            downloader = MediaIoBaseDownload(file_handle, request)
            done = False
            
            while done is False:
                status, done = downloader.next_chunk()
            
            file_handle.seek(0)
            
            with open(download_path, 'wb') as f:
                f.write(file_handle.read())
            
            logger.info("📥 Fichier téléchargé", file_id=file_id, path=download_path)
            return True
            
        except Exception as e:
            logger.error("❌ Erreur téléchargement fichier", error=str(e))
            return False
    
    async def search_files(
        self, 
        query: str, 
        max_results: int = 20,
        file_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Recherche des fichiers dans Drive
        
        Args:
            query: Terme de recherche
            max_results: Nombre maximum de résultats
            file_type: Type de fichier (document, spreadsheet, presentation, etc.)
            
        Returns:
            Liste des fichiers trouvés
        """
        await self._ensure_service_initialized()
        
        try:
            search_query = f"name contains '{query}'"
            
            if file_type:
                mime_types = {
                    'document': 'application/vnd.google-apps.document',
                    'spreadsheet': 'application/vnd.google-apps.spreadsheet',
                    'presentation': 'application/vnd.google-apps.presentation',
                    'folder': 'application/vnd.google-apps.folder',
                    'pdf': 'application/pdf',
                    'image': 'image/',
                    'video': 'video/',
                    'audio': 'audio/'
                }
                
                if file_type in mime_types:
                    if file_type in ['image', 'video', 'audio']:
                        search_query += f" and mimeType contains '{mime_types[file_type]}'"
                    else:
                        search_query += f" and mimeType='{mime_types[file_type]}'"
            
            results = self.drive_service.files().list(
                q=search_query,
                pageSize=max_results,
                orderBy='modifiedTime desc',
                fields='files(id, name, mimeType, modifiedTime, webViewLink, size)'
            ).execute()
            
            files = results.get('files', [])
            
            search_results = []
            for file in files:
                search_results.append({
                    'id': file['id'],
                    'name': file['name'],
                    'mime_type': file['mimeType'],
                    'modified_time': file['modifiedTime'],
                    'url': file['webViewLink'],
                    'size': file.get('size', 0),
                    'type': self._get_file_type(file['mimeType'])
                })
            
            logger.info("🔍 Recherche Drive effectuée", query=query, results=len(search_results))
            return search_results
            
        except Exception as e:
            logger.error("❌ Erreur recherche Drive", error=str(e))
            return []
    
    async def get_folder_contents(self, folder_id: str) -> List[Dict[str, Any]]:
        """
        Récupère le contenu d'un dossier
        
        Args:
            folder_id: ID du dossier
            
        Returns:
            Liste des fichiers et dossiers
        """
        await self._ensure_service_initialized()
        
        try:
            query = f"'{folder_id}' in parents"
            
            results = self.drive_service.files().list(
                q=query,
                orderBy='name',
                fields='files(id, name, mimeType, modifiedTime, webViewLink, size)'
            ).execute()
            
            files = results.get('files', [])
            contents = []
            
            for file in files:
                contents.append({
                    'id': file['id'],
                    'name': file['name'],
                    'mime_type': file['mimeType'],
                    'modified_time': file['modifiedTime'],
                    'url': file['webViewLink'],
                    'size': file.get('size', 0),
                    'type': self._get_file_type(file['mimeType'])
                })
            
            logger.info("📂 Contenu dossier récupéré", folder_id=folder_id, items=len(contents))
            return contents
            
        except Exception as e:
            logger.error("❌ Erreur contenu dossier", error=str(e))
            return []
    
    async def share_file(
        self, 
        file_id: str, 
        email: Optional[str] = None,
        role: str = "reader",
        notify: bool = True
    ) -> bool:
        """
        Partage un fichier
        
        Args:
            file_id: ID du fichier
            email: Email de la personne (None pour partage public)
            role: Rôle (reader, writer, owner)
            notify: Envoyer une notification
            
        Returns:
            True si succès, False sinon
        """
        await self._ensure_service_initialized()
        
        try:
            permission = {
                'role': role
            }
            
            if email:
                permission['type'] = 'user'
                permission['emailAddress'] = email
            else:
                permission['type'] = 'anyone'
            
            self.drive_service.permissions().create(
                fileId=file_id,
                body=permission,
                sendNotificationEmail=notify
            ).execute()
            
            logger.info("🔗 Fichier partagé", file_id=file_id, email=email or "public", role=role)
            return True
            
        except Exception as e:
            logger.error("❌ Erreur partage fichier", error=str(e))
            return False
    
    async def delete_file(self, file_id: str) -> bool:
        """Supprime un fichier"""
        await self._ensure_service_initialized()
        
        try:
            self.drive_service.files().delete(fileId=file_id).execute()
            logger.info("🗑️ Fichier supprimé", file_id=file_id)
            return True
            
        except Exception as e:
            logger.error("❌ Erreur suppression fichier", error=str(e))
            return False
    
    async def get_storage_info(self) -> Dict[str, Any]:
        """Récupère les informations de stockage"""
        await self._ensure_service_initialized()
        
        try:
            about = self.drive_service.about().get(fields='storageQuota, user').execute()
            storage = about.get('storageQuota', {})
            
            return {
                'total_bytes': int(storage.get('limit', 0)),
                'used_bytes': int(storage.get('usage', 0)),
                'available_bytes': int(storage.get('limit', 0)) - int(storage.get('usage', 0)),
                'usage_percentage': round((int(storage.get('usage', 0)) / int(storage.get('limit', 1))) * 100, 2)
            }
            
        except Exception as e:
            logger.error("❌ Erreur info stockage", error=str(e))
            return {}
    
    def _get_file_type(self, mime_type: str) -> str:
        """Détermine le type de fichier à partir du MIME type"""
        if 'folder' in mime_type:
            return 'folder'
        elif 'document' in mime_type:
            return 'document'
        elif 'spreadsheet' in mime_type:
            return 'spreadsheet'
        elif 'presentation' in mime_type:
            return 'presentation'
        elif 'image' in mime_type:
            return 'image'
        elif 'video' in mime_type:
            return 'video'
        elif 'audio' in mime_type:
            return 'audio'
        elif 'pdf' in mime_type:
            return 'pdf'
        else:
            return 'file'
    
    async def get_drive_summary_for_sylvie(self) -> Dict[str, Any]:
        """Génère un résumé de Drive pour Sylvie"""
        try:
            # Récupération des fichiers récents
            recent_files = await self.search_files("", max_results=10)
            
            # Informations de stockage
            storage_info = await self.get_storage_info()
            
            # Classification des fichiers récents
            file_types = {}
            for file in recent_files:
                file_type = file['type']
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            return {
                'recent_files_count': len(recent_files),
                'recent_files': recent_files[:5],
                'file_types_distribution': file_types,
                'storage_info': storage_info,
                'drive_health': 'good' if storage_info.get('usage_percentage', 0) < 80 else 'warning'
            }
            
        except Exception as e:
            logger.error("❌ Erreur résumé Drive", error=str(e))
            return {
                'recent_files_count': 0,
                'recent_files': [],
                'file_types_distribution': {},
                'storage_info': {},
                'drive_health': 'unknown'
            }

# Instance globale du gestionnaire
drive_manager = DriveManager()

