"""
🤖 Router Sylvie pour KanterMator
Interface API pour l'agent conversationnel Sylvie

Endpoints pour interagir avec l'IA hybride + Google Workspace
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import structlog
from datetime import datetime

from app.services.sylvie_agent import sylvie_agent
from app.services.sylvie_config import SylvieResponse

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["🤖 Sylvie Agent"])

# Modèles Pydantic pour l'API
class ChatMessage(BaseModel):
    """Message de chat avec Sylvie"""
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Réponse de Sylvie"""
    message: str
    conversation_id: str
    intent: Optional[str] = None
    action_taken: Optional[str] = None
    action_result: Optional[Dict[str, Any]] = None
    suggestions: List[str] = []
    timestamp: str

class ConversationHistory(BaseModel):
    """Historique de conversation"""
    conversation_id: str
    messages: List[Dict[str, Any]]

@router.get("/", response_class=HTMLResponse)
async def sylvie_interface():
    """Interface web pour chat avec Sylvie"""
    
    html_content = '''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🤖 Sylvie - Assistant KanterMator</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .chat-container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 800px;
                height: 80vh;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            
            .chat-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            
            .chat-header h1 {
                font-size: 2em;
                margin-bottom: 10px;
            }
            
            .chat-header p {
                opacity: 0.9;
                font-size: 1.1em;
            }
            
            .chat-messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                background: #f8f9fa;
            }
            
            .message {
                margin-bottom: 20px;
                display: flex;
                gap: 15px;
                animation: fadeIn 0.3s ease-in;
            }
            
            .message.user {
                flex-direction: row-reverse;
            }
            
            .message-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5em;
                flex-shrink: 0;
            }
            
            .user .message-avatar {
                background: #007bff;
                color: white;
            }
            
            .assistant .message-avatar {
                background: #28a745;
                color: white;
            }
            
            .message-content {
                max-width: 70%;
                padding: 15px 20px;
                border-radius: 20px;
                line-height: 1.5;
            }
            
            .user .message-content {
                background: #007bff;
                color: white;
                border-bottom-right-radius: 5px;
            }
            
            .assistant .message-content {
                background: white;
                color: #333;
                border: 1px solid #e9ecef;
                border-bottom-left-radius: 5px;
            }
            
            .chat-input {
                padding: 20px;
                background: white;
                border-top: 1px solid #e9ecef;
            }
            
            .input-container {
                display: flex;
                gap: 10px;
                align-items: flex-end;
            }
            
            .message-input {
                flex: 1;
                border: 2px solid #e9ecef;
                border-radius: 20px;
                padding: 15px 20px;
                font-size: 16px;
                resize: none;
                max-height: 120px;
                transition: border-color 0.3s;
            }
            
            .message-input:focus {
                outline: none;
                border-color: #667eea;
            }
            
            .send-button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                cursor: pointer;
                font-size: 1.2em;
                transition: transform 0.2s;
                flex-shrink: 0;
            }
            
            .send-button:hover {
                transform: scale(1.1);
            }
            
            .send-button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }
            
            .suggestions {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-top: 15px;
            }
            
            .suggestion {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 20px;
                padding: 8px 15px;
                font-size: 0.9em;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .suggestion:hover {
                background: #e9ecef;
                transform: translateY(-2px);
            }
            
            .typing-indicator {
                display: none;
                padding: 15px;
                color: #666;
                font-style: italic;
            }
            
            .typing-indicator.show {
                display: block;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @media (max-width: 768px) {
                .chat-container {
                    height: 95vh;
                    margin: 10px;
                }
                
                .message-content {
                    max-width: 85%;
                }
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <h1>🤖 Sylvie</h1>
                <p>Assistant IA pour KanterMator • Google Workspace • IA Hybride</p>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="message assistant">
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">
                        <strong>Bonjour ! Je suis Sylvie, votre assistante IA pour KanterMator.</strong><br><br>
                        Je peux vous aider avec :
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li>📧 Gestion de vos emails Gmail</li>
                            <li>📅 Organisation de votre calendrier</li>
                            <li>✅ Gestion de vos tâches</li>
                            <li>📝 Création de notes et documents</li>
                            <li>📊 Analyse de données et présentations</li>
                            <li>📁 Organisation de vos fichiers Drive</li>
                        </ul>
                        Comment puis-je vous aider aujourd'hui ?
                    </div>
                </div>
            </div>
            
            <div class="typing-indicator" id="typingIndicator">
                🤖 Sylvie réfléchit...
            </div>
            
            <div class="chat-input">
                <div class="input-container">
                    <textarea 
                        id="messageInput" 
                        class="message-input" 
                        placeholder="Tapez votre message à Sylvie..."
                        rows="1"></textarea>
                    <button id="sendButton" class="send-button">📤</button>
                </div>
                <div class="suggestions" id="suggestions">
                    <div class="suggestion" onclick="window.sendSuggestion && window.sendSuggestion('Vérifier mes emails urgents')">📧 Vérifier mes emails</div>
                    <div class="suggestion" onclick="window.sendSuggestion && window.sendSuggestion('Créer une tâche pour demain')">✅ Créer une tâche</div>
                    <div class="suggestion" onclick="window.sendSuggestion && window.sendSuggestion('Faire une présentation sur l\\'IA')">📊 Créer une présentation</div>
                    <div class="suggestion" onclick="window.sendSuggestion && window.sendSuggestion('Organiser mes fichiers Drive')">📁 Organiser Drive</div>
                </div>
            </div>
        </div>

        <script>
            let conversationId = null;
            
            const chatMessages = document.getElementById('chatMessages');
            const messageInput = document.getElementById('messageInput');
            const sendButton = document.getElementById('sendButton');
            const typingIndicator = document.getElementById('typingIndicator');
            const suggestionsContainer = document.getElementById('suggestions');
            
            // Define sendSuggestion function globally first
            window.sendSuggestion = function(text) {
                messageInput.value = text;
                sendMessage();
            };
            
            // Auto-resize textarea
            messageInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            });
            
            // Send message on Enter (but allow Shift+Enter for new line)
            messageInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
            
            sendButton.addEventListener('click', sendMessage);
            
            async function sendMessage() {
                const message = messageInput.value.trim();
                if (!message) return;
                
                // Add user message to chat
                addMessage('user', message);
                
                // Clear input and disable button
                messageInput.value = '';
                messageInput.style.height = 'auto';
                sendButton.disabled = true;
                
                // Show typing indicator
                typingIndicator.classList.add('show');
                
                try {
                    const response = await fetch('/api/v1/sylvie/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            conversation_id: conversationId
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error('Erreur réseau');
                    }
                    
                    const data = await response.json();
                    
                    // Update conversation ID
                    conversationId = data.conversation_id;
                    
                    // Add Sylvie's response
                    addMessage('assistant', data.message);
                    
                    // Update suggestions
                    updateSuggestions(data.suggestions);
                    
                } catch (error) {
                    addMessage('assistant', '❌ Désolée, j\'ai rencontré une erreur. Veuillez réessayer.');
                } finally {
                    typingIndicator.classList.remove('show');
                    sendButton.disabled = false;
                }
            }
            
            function addMessage(role, content) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${role}`;
                
                const avatar = role === 'user' ? '👤' : '🤖';
                
                messageDiv.innerHTML = `
                    <div class="message-avatar">${avatar}</div>
                    <div class="message-content">${content.replace(/\n/g, '<br>')}</div>
                `;
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            function updateSuggestions(suggestions) {
                if (!suggestions || suggestions.length === 0) return;
                
                suggestionsContainer.innerHTML = '';
                suggestions.forEach(suggestion => {
                    const suggestionDiv = document.createElement('div');
                    suggestionDiv.className = 'suggestion';
                    suggestionDiv.textContent = suggestion;
                    suggestionDiv.onclick = () => window.sendSuggestion(suggestion);
                    suggestionsContainer.appendChild(suggestionDiv);
                });
            }
        </script>
    </body>
    </html>
    '''
    
    return HTMLResponse(content=html_content)

@router.post("/chat", response_model=ChatResponse)
async def chat_with_sylvie(message: ChatMessage) -> ChatResponse:
    """
    Endpoint principal pour discuter avec Sylvie
    
    Args:
        message: Message de l'utilisateur avec conversation_id optionnel
        
    Returns:
        Réponse de Sylvie avec métadonnées
    """
    try:
        logger.info("💬 Nouveau message pour Sylvie", 
                   message=message.message[:100],
                   conversation_id=message.conversation_id)
        
        # Appel à Sylvie Agent
        response = await sylvie_agent.process_message(
            message=message.message,
            conversation_id=message.conversation_id
        )
        
        # Conversion en réponse API
        api_response = ChatResponse(
            message=response.message,
            conversation_id=response.conversation_id,
            intent=response.intent.intent if response.intent else None,
            action_taken=response.action_taken,
            action_result=response.action_result,
            suggestions=response.suggestions,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info("✅ Réponse Sylvie envoyée", 
                   conversation_id=api_response.conversation_id,
                   intent=api_response.intent)
        
        return api_response
        
    except Exception as e:
        logger.error("❌ Erreur chat Sylvie", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement du message: {str(e)}"
        )

@router.get("/status")
async def sylvie_status():
    """Statut de Sylvie Agent"""
    try:
        return {
            "status": "operational",
            "services": [
                "Gmail", "Calendar", "Drive", "Sheets", 
                "Tasks", "Keep", "Slides", "Docs"
            ],
            "ai_models": ["OpenAI GPT-4o", "Google Gemini 1.5 Pro"],
            "conversation_count": len(sylvie_agent.conversations),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Erreur statut Sylvie", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Erreur statut Sylvie: {str(e)}"
        )

# Router principal pour export
sylvie_router = router
