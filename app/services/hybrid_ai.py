"""
🧠 Service IA Hybride - GPT + Gemini pour Sylvie
Phase 3.6 - Intelligence artificielle multi-modèles

Service intelligent qui combine OpenAI GPT et Google Gemini
pour une expérience utilisateur optimale
"""

import asyncio
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import structlog
import json
from datetime import datetime
import google.generativeai as genai
from openai import OpenAI

from app.utils.config import settings

logger = structlog.get_logger(__name__)

class AIModel(str, Enum):
    """Modèles IA disponibles"""
    OPENAI = "openai"
    GEMINI = "gemini"

class AIStrategy(str, Enum):
    """Stratégies d'utilisation IA"""
    HYBRID = "hybrid"          # Utilise les deux modèles intelligemment
    OPENAI_ONLY = "openai"     # OpenAI uniquement
    GEMINI_ONLY = "gemini"     # Gemini uniquement
    FALLBACK = "fallback"      # Un modèle principal + fallback

class TaskType(str, Enum):
    """Types de tâches pour l'optimisation modèle"""
    CONVERSATION = "conversation"
    INTENT_ANALYSIS = "intent_analysis"
    CODE_GENERATION = "code_generation"
    DATA_ANALYSIS = "data_analysis"
    CREATIVE_WRITING = "creative_writing"
    TECHNICAL_SUPPORT = "technical_support"

class AIResponse:
    """Réponse unifiée des modèles IA"""
    def __init__(self, content: str, model: AIModel, metadata: Dict[str, Any] = None):
        self.content = content
        self.model = model
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()

class HybridAIService:
    """Service IA hybride intelligent"""
    
    def __init__(self):
        self.openai_client = None
        self.gemini_model = None
        self.strategy = AIStrategy(settings.AI_MODEL_STRATEGY)
        
        # Initialisation des clients IA
        self._initialize_clients()
        
        # Configuration des spécialisations par tâche
        self.task_specialization = {
            TaskType.CONVERSATION: AIModel.OPENAI,      # GPT excelle en conversation
            TaskType.INTENT_ANALYSIS: AIModel.GEMINI,   # Gemini bon en analyse
            TaskType.CODE_GENERATION: AIModel.OPENAI,   # GPT meilleur en code
            TaskType.DATA_ANALYSIS: AIModel.GEMINI,     # Gemini efficace sur les données
            TaskType.CREATIVE_WRITING: AIModel.OPENAI,  # GPT plus créatif
            TaskType.TECHNICAL_SUPPORT: AIModel.GEMINI  # Gemini factuel
        }
        
        logger.info("🧠 Service IA hybride initialisé", 
                   strategy=self.strategy,
                   openai_available=self.openai_client is not None,
                   gemini_available=self.gemini_model is not None)
    
    def _initialize_clients(self):
        """Initialisation des clients IA"""
        
        # Client OpenAI
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-your-openai-key-here":
            try:
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✅ Client OpenAI initialisé")
            except Exception as e:
                logger.error("❌ Erreur initialisation OpenAI", error=str(e))
        
        # Client Gemini
        if settings.GOOGLE_AI_KEY and settings.GOOGLE_AI_KEY != "your-gemini-api-key-here":
            try:
                genai.configure(api_key=settings.GOOGLE_AI_KEY)
                self.gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
                logger.info("✅ Client Gemini initialisé")
            except Exception as e:
                logger.error("❌ Erreur initialisation Gemini", error=str(e))
    
    async def generate_response(self, 
                              prompt: str, 
                              task_type: TaskType = TaskType.CONVERSATION,
                              max_tokens: int = 1000,
                              temperature: float = 0.7,
                              system_prompt: str = None) -> AIResponse:
        """
        Génération de réponse avec sélection intelligente du modèle
        
        Args:
            prompt: Prompt utilisateur
            task_type: Type de tâche pour optimiser le choix du modèle
            max_tokens: Limite de tokens
            temperature: Créativité (0-1)
            system_prompt: Prompt système optionnel
            
        Returns:
            Réponse IA unifiée
        """
        
        # Sélection du modèle selon la stratégie
        selected_model = self._select_model(task_type)
        
        try:
            if selected_model == AIModel.OPENAI and self.openai_client:
                return await self._generate_openai_response(
                    prompt, max_tokens, temperature, system_prompt
                )
            elif selected_model == AIModel.GEMINI and self.gemini_model:
                return await self._generate_gemini_response(
                    prompt, max_tokens, temperature, system_prompt
                )
            else:
                # Fallback vers le modèle disponible
                return await self._generate_fallback_response(
                    prompt, max_tokens, temperature, system_prompt
                )
                
        except Exception as e:
            logger.error(f"❌ Erreur {selected_model}", error=str(e))
            
            # Tentative avec le modèle de fallback
            fallback_model = AIModel.GEMINI if selected_model == AIModel.OPENAI else AIModel.OPENAI
            
            try:
                if fallback_model == AIModel.OPENAI and self.openai_client:
                    return await self._generate_openai_response(
                        prompt, max_tokens, temperature, system_prompt
                    )
                elif fallback_model == AIModel.GEMINI and self.gemini_model:
                    return await self._generate_gemini_response(
                        prompt, max_tokens, temperature, system_prompt
                    )
            except Exception as fallback_error:
                logger.error("❌ Erreur fallback", error=str(fallback_error))
                
            # Réponse d'erreur gracieuse
            return AIResponse(
                content="😅 Désolée, j'ai un problème technique temporaire. Pouvez-vous réessayer ?",
                model=selected_model,
                metadata={"error": str(e)}
            )
    
    def _select_model(self, task_type: TaskType) -> AIModel:
        """Sélection intelligente du modèle selon la tâche et la stratégie"""
        
        if self.strategy == AIStrategy.OPENAI_ONLY:
            return AIModel.OPENAI
        elif self.strategy == AIStrategy.GEMINI_ONLY:
            return AIModel.GEMINI
        elif self.strategy == AIStrategy.HYBRID:
            # Sélection basée sur la spécialisation de tâche
            return self.task_specialization.get(task_type, AIModel.OPENAI)
        elif self.strategy == AIStrategy.FALLBACK:
            # Modèle principal avec fallback
            primary = AIModel(settings.PRIMARY_MODEL)
            return primary
        
        return AIModel.OPENAI  # Défaut
    
    async def _generate_openai_response(self, 
                                      prompt: str, 
                                      max_tokens: int, 
                                      temperature: float,
                                      system_prompt: str = None) -> AIResponse:
        """Génération de réponse via OpenAI GPT"""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return AIResponse(
            content=response.choices[0].message.content,
            model=AIModel.OPENAI,
            metadata={
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "model": settings.OPENAI_MODEL
            }
        )
    
    async def _generate_gemini_response(self, 
                                      prompt: str, 
                                      max_tokens: int, 
                                      temperature: float,
                                      system_prompt: str = None) -> AIResponse:
        """Génération de réponse via Google Gemini"""
        
        # Construction du prompt avec système si fourni
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUtilisateur: {prompt}"
        
        # Configuration de génération
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature
        )
        
        response = self.gemini_model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        return AIResponse(
            content=response.text,
            model=AIModel.GEMINI,
            metadata={
                "model": settings.GEMINI_MODEL,
                "candidates_count": len(response.candidates) if hasattr(response, 'candidates') else 1
            }
        )
    
    async def _generate_fallback_response(self, 
                                        prompt: str, 
                                        max_tokens: int, 
                                        temperature: float,
                                        system_prompt: str = None) -> AIResponse:
        """Génération avec le modèle disponible en fallback"""
        
        if self.openai_client:
            return await self._generate_openai_response(prompt, max_tokens, temperature, system_prompt)
        elif self.gemini_model:
            return await self._generate_gemini_response(prompt, max_tokens, temperature, system_prompt)
        else:
            raise Exception("Aucun modèle IA disponible")
    
    async def compare_responses(self, 
                              prompt: str, 
                              task_type: TaskType = TaskType.CONVERSATION) -> Dict[str, AIResponse]:
        """
        Compare les réponses des deux modèles (pour debug/optimisation)
        
        Returns:
            Dictionnaire avec les réponses des deux modèles
        """
        
        responses = {}
        
        # Test OpenAI
        if self.openai_client:
            try:
                responses["openai"] = await self._generate_openai_response(prompt, 500, 0.7)
            except Exception as e:
                logger.error("❌ Erreur comparaison OpenAI", error=str(e))
        
        # Test Gemini
        if self.gemini_model:
            try:
                responses["gemini"] = await self._generate_gemini_response(prompt, 500, 0.7)
            except Exception as e:
                logger.error("❌ Erreur comparaison Gemini", error=str(e))
        
        return responses
    
    def get_service_status(self) -> Dict[str, Any]:
        """État du service IA hybride"""
        return {
            "strategy": self.strategy,
            "models_available": {
                "openai": self.openai_client is not None,
                "gemini": self.gemini_model is not None
            },
            "configuration": {
                "primary_model": settings.PRIMARY_MODEL,
                "fallback_model": settings.FALLBACK_MODEL,
                "openai_model": settings.OPENAI_MODEL,
                "gemini_model": settings.GEMINI_MODEL
            },
            "task_specialization": {k.value: v.value for k, v in self.task_specialization.items()}
        }

# Instance globale du service IA hybride
hybrid_ai = HybridAIService()
