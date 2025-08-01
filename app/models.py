"""
📊 Modèles de données KanterMator
Phase 2.2 - Structures de données

Définition des modèles SQLAlchemy et Pydantic
pour l'application KanterMator
"""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from pydantic import BaseModel, Field
import enum

Base = declarative_base()

# 📚 Modèles SQLAlchemy

class Progression(Base):
    """Progression pédagogique hebdomadaire"""
    __tablename__ = "progressions"
    
    id = Column(Integer, primary_key=True, index=True)
    week_number = Column(Integer, nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    subject = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    objectives = Column(JSON)  # Liste des objectifs
    materials = Column(JSON)   # Matériel nécessaire
    
    # Relations
    tasks = relationship("AutomationTask", back_populates="progression")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AutomationTask(Base):
    """Tâches d'automatisation KanterMator"""
    __tablename__ = "automation_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String(100), nullable=False)  # folder_creation, shortcut_creation
    status = Column(String(50), nullable=False, default="pending")  # pending, running, completed, failed
    week_number = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    
    # Relations
    progression_id = Column(Integer, ForeignKey("progressions.id"))
    progression = relationship("Progression", back_populates="tasks")
    
    # Données de la tâche
    task_data = Column(JSON)  # Configuration spécifique à la tâche
    result = Column(JSON)     # Résultat de l'exécution
    error_message = Column(Text)
    
    # Timestamps
    scheduled_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class DriveFolder(Base):
    """Dossiers Google Drive gérés"""
    __tablename__ = "drive_folders"
    
    id = Column(Integer, primary_key=True, index=True)
    folder_id = Column(String(255), nullable=False, unique=True, index=True)
    folder_name = Column(String(500), nullable=False)
    parent_id = Column(String(255))
    folder_path = Column(String(1000))
    week_number = Column(Integer)
    year = Column(Integer)
    subject = Column(String(100))
    
    # Métadonnées
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DriveShortcut(Base):
    """Raccourcis Google Drive gérés"""
    __tablename__ = "drive_shortcuts"
    
    id = Column(Integer, primary_key=True, index=True)
    shortcut_id = Column(String(255), nullable=False, unique=True, index=True)
    shortcut_name = Column(String(500), nullable=False)
    target_id = Column(String(255), nullable=False)  # ID du fichier/dossier cible
    parent_id = Column(String(255), nullable=False)  # Dossier parent du raccourci
    week_number = Column(Integer)
    year = Column(Integer)
    subject = Column(String(100))
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemLog(Base):
    """Logs système de KanterMator"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    component = Column(String(100), nullable=False)  # sheets_reader, drive_manager, etc.
    message = Column(Text, nullable=False)
    context = Column(JSON)  # Contexte additionnel
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

# 📋 Modèles Pydantic pour l'API

class ProgressionBase(BaseModel):
    """Modèle de base pour les progressions"""
    week_number: int = Field(..., ge=1, le=53)
    year: int = Field(..., ge=2020, le=2030)
    start_date: date
    end_date: date
    subject: str = Field(..., max_length=100)
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    objectives: Optional[List[str]] = []
    materials: Optional[List[str]] = []

class ProgressionCreate(ProgressionBase):
    """Modèle pour créer une progression"""
    pass

class ProgressionResponse(ProgressionBase):
    """Modèle de réponse pour les progressions"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AutomationTaskBase(BaseModel):
    """Modèle de base pour les tâches d'automatisation"""
    task_type: str = Field(..., pattern="^(folder_creation|shortcut_creation|archive_creation)$")
    week_number: int = Field(..., ge=1, le=53)
    year: int = Field(..., ge=2020, le=2030)
    task_data: Optional[dict] = {}
    scheduled_at: datetime

class AutomationTaskCreate(AutomationTaskBase):
    """Modèle pour créer une tâche d'automatisation"""
    progression_id: Optional[int] = None

class AutomationTaskResponse(AutomationTaskBase):
    """Modèle de réponse pour les tâches d'automatisation"""
    id: int
    status: str
    progression_id: Optional[int]
    result: Optional[dict]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class DriveFolderResponse(BaseModel):
    """Modèle de réponse pour les dossiers Drive"""
    id: int
    folder_id: str
    folder_name: str
    parent_id: Optional[str]
    folder_path: Optional[str]
    week_number: Optional[int]
    year: Optional[int]
    subject: Optional[str]
    is_archived: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class DriveShortcutResponse(BaseModel):
    """Modèle de réponse pour les raccourcis Drive"""
    id: int
    shortcut_id: str
    shortcut_name: str
    target_id: str
    parent_id: str
    week_number: Optional[int]
    year: Optional[int]
    subject: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class WeeklyAutomationRequest(BaseModel):
    """Requête pour l'automatisation hebdomadaire"""
    week_number: int = Field(..., ge=1, le=53)
    year: int = Field(..., ge=2020, le=2030)
    force_recreate: bool = Field(default=False)

class WeeklyAutomationResponse(BaseModel):
    """Réponse de l'automatisation hebdomadaire"""
    week_number: int
    year: int
    status: str
    folders_created: int
    shortcuts_created: int
    errors: List[str]
    execution_time: float

class SystemStatusResponse(BaseModel):
    """État du système KanterMator"""
    status: str
    version: str
    automation_enabled: bool
    last_automation: Optional[datetime]
    pending_tasks: int
    database_status: str
    google_auth_status: str

# 🤖 Modèles pour Sylvie Chat

class ChatMessage(BaseModel):
    """Message de chat pour Sylvie"""
    message: str = Field(..., description="Contenu du message de l'utilisateur")
    conversation_id: Optional[str] = Field(None, description="ID de conversation pour le contexte")

class ChatResponse(BaseModel):
    """Réponse de chat de Sylvie"""
    message: str = Field(..., description="Réponse de Sylvie")
    conversation_id: str = Field(..., description="ID de conversation")
    intent: Optional[str] = Field(None, description="Intention détectée")
    action_taken: Optional[str] = Field(None, description="Action effectuée")
    action_result: Optional[dict] = Field(None, description="Résultat de l'action")
    suggestions: Optional[List[str]] = Field(None, description="Suggestions de suivi")
    metadata: Optional[dict] = Field(None, description="Métadonnées additionnelles")
