"""
📊 Service Sheets Reader pour Sylvie
Phase 3.14 - Lecteur Google Sheets

Gestion avancée de la lecture et écriture dans Google Sheets pour KanterMator
"""

import structlog
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.services.google_auth import GoogleAuthService

logger = structlog.get_logger(__name__)

class SheetsReader:
    """Service de gestion des Google Sheets"""
    
    def __init__(self):
        self.auth_service = GoogleAuthService()
        self.sheets_service = None
        self.drive_service = None
        # Pas d'initialisation synchrone, sera fait lors du premier appel async
    
    async def _ensure_service_initialized(self):
        """Assure que le service Sheets est initialisé"""
        if self.sheets_service is None:
            try:
                credentials = await self.auth_service.get_credentials()
                self.sheets_service = build('sheets', 'v4', credentials=credentials)
                self.drive_service = build('drive', 'v3', credentials=credentials)
                logger.info("✅ Service Sheets Reader initialisé")
            except Exception as e:
                logger.error("❌ Erreur initialisation Sheets Reader", error=str(e))
                raise
    
    async def create_spreadsheet(self, title: str, sheets: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Crée une nouvelle feuille de calcul
        
        Args:
            title: Titre de la feuille
            sheets: Liste des noms d'onglets à créer
            
        Returns:
            Informations sur la feuille créée
        """
        await self._ensure_service_initialized()
        
        try:
            spreadsheet_body = {
                'properties': {
                    'title': title
                }
            }
            
            # Ajout des onglets personnalisés
            if sheets:
                spreadsheet_body['sheets'] = []
                for sheet_name in sheets:
                    spreadsheet_body['sheets'].append({
                        'properties': {
                            'title': sheet_name
                        }
                    })
            
            spreadsheet = self.sheets_service.spreadsheets().create(
                body=spreadsheet_body
            ).execute()
            
            spreadsheet_id = spreadsheet['spreadsheetId']
            
            logger.info("📊 Feuille de calcul créée", title=title, spreadsheet_id=spreadsheet_id)
            
            return {
                'id': spreadsheet_id,
                'title': title,
                'url': f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit",
                'sheet_count': len(spreadsheet.get('sheets', [])),
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("❌ Erreur création feuille", error=str(e))
            return None
    
    async def read_range(self, spreadsheet_id: str, range_name: str) -> List[List[str]]:
        """
        Lit une plage de cellules
        
        Args:
            spreadsheet_id: ID de la feuille
            range_name: Plage à lire (ex: 'Sheet1!A1:C10')
            
        Returns:
            Données sous forme de liste de listes
        """
        await self._ensure_service_initialized()
        
        try:
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            logger.info("📖 Plage lue", spreadsheet_id=spreadsheet_id, range=range_name, rows=len(values))
            
            return values
            
        except Exception as e:
            logger.error("❌ Erreur lecture plage", error=str(e))
            return []
    
    async def write_range(
        self, 
        spreadsheet_id: str, 
        range_name: str, 
        values: List[List[Any]],
        input_option: str = "USER_ENTERED"
    ) -> bool:
        """
        Écrit dans une plage de cellules
        
        Args:
            spreadsheet_id: ID de la feuille
            range_name: Plage à écrire (ex: 'Sheet1!A1:C10')
            values: Données à écrire
            input_option: Option d'entrée (USER_ENTERED ou RAW)
            
        Returns:
            True si succès, False sinon
        """
        await self._ensure_service_initialized()
        
        try:
            body = {
                'values': values
            }
            
            result = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=input_option,
                body=body
            ).execute()
            
            logger.info("✏️ Plage écrite", 
                       spreadsheet_id=spreadsheet_id, 
                       range=range_name, 
                       cells_updated=result.get('updatedCells', 0))
            
            return True
            
        except Exception as e:
            logger.error("❌ Erreur écriture plage", error=str(e))
            return False
    
    async def append_rows(
        self, 
        spreadsheet_id: str, 
        sheet_name: str, 
        values: List[List[Any]]
    ) -> bool:
        """
        Ajoute des lignes à la fin d'une feuille
        
        Args:
            spreadsheet_id: ID de la feuille
            sheet_name: Nom de l'onglet
            values: Données à ajouter
            
        Returns:
            True si succès, False sinon
        """
        await self._ensure_service_initialized()
        
        try:
            body = {
                'values': values
            }
            
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A:A",
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            
            logger.info("📝 Lignes ajoutées", 
                       spreadsheet_id=spreadsheet_id, 
                       sheet=sheet_name, 
                       rows_added=len(values))
            
            return True
            
        except Exception as e:
            logger.error("❌ Erreur ajout lignes", error=str(e))
            return False
    
    async def get_spreadsheet_info(self, spreadsheet_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'une feuille de calcul"""
        await self._ensure_service_initialized()
        
        try:
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            sheets_info = []
            for sheet in spreadsheet.get('sheets', []):
                sheet_props = sheet['properties']
                sheets_info.append({
                    'id': sheet_props['sheetId'],
                    'title': sheet_props['title'],
                    'rows': sheet_props.get('gridProperties', {}).get('rowCount', 0),
                    'columns': sheet_props.get('gridProperties', {}).get('columnCount', 0)
                })
            
            return {
                'id': spreadsheet['spreadsheetId'],
                'title': spreadsheet['properties']['title'],
                'url': f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit",
                'sheets': sheets_info
            }
            
        except Exception as e:
            logger.error("❌ Erreur info feuille", error=str(e))
            return None
    
    async def create_sheet_in_spreadsheet(self, spreadsheet_id: str, sheet_name: str) -> bool:
        """Ajoute un nouvel onglet à une feuille existante"""
        await self._ensure_service_initialized()
        
        try:
            requests = [{
                'addSheet': {
                    'properties': {
                        'title': sheet_name
                    }
                }
            }]
            
            body = {
                'requests': requests
            }
            
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            logger.info("📄 Onglet créé", spreadsheet_id=spreadsheet_id, sheet_name=sheet_name)
            return True
            
        except Exception as e:
            logger.error("❌ Erreur création onglet", error=str(e))
            return False
    
    async def format_cells(
        self, 
        spreadsheet_id: str, 
        sheet_id: int,
        start_row: int, 
        end_row: int,
        start_col: int, 
        end_col: int,
        format_options: Dict[str, Any]
    ) -> bool:
        """
        Formate des cellules
        
        Args:
            spreadsheet_id: ID de la feuille
            sheet_id: ID de l'onglet
            start_row, end_row: Lignes (0-indexées)
            start_col, end_col: Colonnes (0-indexées)
            format_options: Options de formatage
            
        Returns:
            True si succès, False sinon
        """
        await self._ensure_service_initialized()
        
        try:
            requests = [{
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': start_row,
                        'endRowIndex': end_row,
                        'startColumnIndex': start_col,
                        'endColumnIndex': end_col
                    },
                    'cell': {
                        'userEnteredFormat': format_options
                    },
                    'fields': 'userEnteredFormat'
                }
            }]
            
            body = {
                'requests': requests
            }
            
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            logger.info("🎨 Cellules formatées", spreadsheet_id=spreadsheet_id)
            return True
            
        except Exception as e:
            logger.error("❌ Erreur formatage", error=str(e))
            return False
    
    async def get_spreadsheets(self, max_results: int = 15) -> List[Dict[str, Any]]:
        """Récupère les feuilles de calcul récentes"""
        await self._ensure_service_initialized()
        
        try:
            # Recherche via Drive
            query = "mimeType='application/vnd.google-apps.spreadsheet'"
            results = self.drive_service.files().list(
                q=query,
                pageSize=max_results,
                orderBy='modifiedTime desc',
                fields='files(id, name, modifiedTime, createdTime, webViewLink)'
            ).execute()
            
            files = results.get('files', [])
            spreadsheets = []
            
            for file in files:
                spreadsheets.append({
                    'id': file['id'],
                    'title': file['name'],
                    'url': file['webViewLink'],
                    'modified_time': file['modifiedTime'],
                    'created_time': file['createdTime']
                })
            
            logger.info("📊 Feuilles de calcul récupérées", count=len(spreadsheets))
            return spreadsheets
            
        except Exception as e:
            logger.error("❌ Erreur récupération feuilles", error=str(e))
            return []
    
    async def create_educational_gradebook(self, class_name: str, students: List[str]) -> Optional[Dict[str, Any]]:
        """Crée un carnet de notes éducatif"""
        await self._ensure_service_initialized()
        
        try:
            # Création de la feuille
            title = f"Carnet de notes - {class_name}"
            spreadsheet_info = await self.create_spreadsheet(title, ["Notes", "Statistiques"])
            
            if not spreadsheet_info:
                return None
            
            spreadsheet_id = spreadsheet_info['id']
            
            # En-têtes pour les notes
            headers = ["Nom de l'élève", "Moyenne", "Participation", "Devoirs", "Examens", "Commentaires"]
            
            # Données des élèves
            student_data = []
            student_data.append(headers)
            
            for student in students:
                student_data.append([student, "", "", "", "", ""])
            
            # Écriture des données
            await self.write_range(spreadsheet_id, "Notes!A1:F100", student_data)
            
            # Formatage des en-têtes
            spreadsheet_details = await self.get_spreadsheet_info(spreadsheet_id)
            if spreadsheet_details:
                notes_sheet_id = None
                for sheet in spreadsheet_details['sheets']:
                    if sheet['title'] == 'Notes':
                        notes_sheet_id = sheet['id']
                        break
                
                if notes_sheet_id is not None:
                    # Formatage en gras pour les en-têtes
                    await self.format_cells(
                        spreadsheet_id, 
                        notes_sheet_id,
                        0, 1, 0, len(headers),
                        {
                            'textFormat': {'bold': True},
                            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                        }
                    )
            
            logger.info("📋 Carnet de notes créé", class_name=class_name, students_count=len(students))
            
            return spreadsheet_info
            
        except Exception as e:
            logger.error("❌ Erreur création carnet", error=str(e))
            return None
    
    async def get_sheets_summary_for_sylvie(self) -> Dict[str, Any]:
        """Génère un résumé des feuilles pour Sylvie"""
        try:
            spreadsheets = await self.get_spreadsheets(max_results=50)
            
            total_spreadsheets = len(spreadsheets)
            recent_spreadsheets = spreadsheets[:5]
            
            # Analyse des feuilles récentes
            spreadsheets_this_week = 0
            spreadsheets_this_month = 0
            
            now = datetime.now()
            
            for sheet in spreadsheets:
                try:
                    modified_date = datetime.fromisoformat(sheet['modified_time'].replace('Z', ''))
                    days_ago = (now - modified_date).days
                    
                    if days_ago <= 7:
                        spreadsheets_this_week += 1
                    if days_ago <= 30:
                        spreadsheets_this_month += 1
                        
                except:
                    pass
            
            return {
                'total_spreadsheets': total_spreadsheets,
                'recent_spreadsheets': recent_spreadsheets,
                'spreadsheets_this_week': spreadsheets_this_week,
                'spreadsheets_this_month': spreadsheets_this_month,
                'productivity_indicator': 'active' if spreadsheets_this_week > 0 else 'low'
            }
            
        except Exception as e:
            logger.error("❌ Erreur résumé feuilles", error=str(e))
            return {
                'total_spreadsheets': 0,
                'recent_spreadsheets': [],
                'spreadsheets_this_week': 0,
                'spreadsheets_this_month': 0,
                'productivity_indicator': 'unknown'
            }

# Instance globale du lecteur
sheets_reader = SheetsReader()

