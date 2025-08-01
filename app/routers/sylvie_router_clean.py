"""
🤖 Router Sylvie - Interface Web et API pour l'Agent Sylvie
========================================================

Ce module fournit l'interface web complète et les endpoints API 
pour interagir avec Sylvie, l'assistant IA de KanterMator.

Fonctionnalités :
- Interface de chat responsive HTML/CSS/JavaScript
- API endpoints pour conversation avec Sylvie
- Gestion des sessions de conversation
- Support des suggestions interactives
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import structlog
from typing import Optional

from ..services.sylvie_agent import sylvie_agent
from ..models import ChatMessage, ChatResponse

# Configuration logging
logger = structlog.get_logger(__name__)

# Router principal
router = APIRouter(prefix="/api/v1/sylvie", tags=["sylvie"])

@router.get("/", response_class=HTMLResponse)
async def get_sylvie_interface():
    """
    Interface web principale pour Sylvie
    
    Returns:
        Interface de chat HTML complète avec CSS et JavaScript
    """
    html_content = '''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🤖 Sylvie - Assistant IA KanterMator</title>
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
                box-shadow: 0 20px 60px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 800px;
                height: 90vh;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            
            .chat-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 20px 20px 0 0;
            }
            
            .chat-header h1 {
                font-size: 2rem;
                margin-bottom: 5px;
            }
            
            .chat-header p {
                opacity: 0.9;
                font-size: 0.9rem;
            }
            
            .chat-messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                background: #f8f9ff;
            }
            
            .message {
                display: flex;
                margin-bottom: 20px;
                animation: fadeIn 0.3s ease-out;
                align-items: flex-start;
                gap: 12px;
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
                font-size: 1.2rem;
                flex-shrink: 0;
            }
            
            .message.user .message-avatar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .message.assistant .message-avatar {
                background: #e3f2fd;
                color: #1976d2;
            }
            
            .message-content {
                background: white;
                padding: 15px 20px;
                border-radius: 18px;
                max-width: 70%;
                word-wrap: break-word;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                line-height: 1.5;
            }
            
            .message.user .message-content {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .typing-indicator {
                display: none;
                padding: 20px;
                text-align: center;
                color: #666;
                font-style: italic;
                animation: pulse 1.5s infinite;
            }
            
            .typing-indicator.show {
                display: block;
            }
            
            .chat-input {
                padding: 20px;
                background: white;
                border-top: 1px solid #eee;
                border-radius: 0 0 20px 20px;
            }
            
            .input-container {
                display: flex;
                gap: 10px;
                align-items: flex-end;
            }
            
            .message-input {
                flex: 1;
                border: 2px solid #f0f0f0;
                border-radius: 25px;
                padding: 15px 20px;
                font-size: 16px;
                resize: none;
                outline: none;
                transition: border-color 0.3s;
                font-family: inherit;
                line-height: 1.4;
                min-height: 50px;
                max-height: 120px;
            }
            
            .message-input:focus {
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
                transition: transform 0.2s;
                font-size: 1.2rem;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            }
            
            .send-button:hover {
                transform: scale(1.05);
            }
            
            .send-button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .suggestions {
                display: flex;
                gap: 10px;
                margin-top: 15px;
                flex-wrap: wrap;
            }
            
            .suggestion {
                background: #f0f8ff;
                border: 1px solid #667eea;
                border-radius: 20px;
                padding: 8px 15px;
                font-size: 0.9rem;
                cursor: pointer;
                transition: all 0.3s;
                color: #667eea;
            }
            
            .suggestion:hover {
                background: #667eea;
                color: white;
                transform: translateY(-2px);
            }
            
            .typing-indicator.show {
                display: block;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 0.7; }
                50% { opacity: 1; }
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
                    <div class="suggestion" onclick="sendSuggestion('Vérifier mes emails urgents')">📧 Vérifier mes emails</div>
                    <div class="suggestion" onclick="sendSuggestion('Créer une tâche pour demain')">✅ Créer une tâche</div>
                    <div class="suggestion" onclick="sendSuggestion('Faire une présentation sur l\\'IA')">📊 Créer une présentation</div>
                    <div class="suggestion" onclick="sendSuggestion('Organiser mes fichiers Drive')">📁 Organiser Drive</div>
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
            
            // Define sendSuggestion function globally
            function sendSuggestion(text) {
                messageInput.value = text;
                sendMessage();
            }
            
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
                        throw new Error('Erreur de communication avec Sylvie');
                    }
                    
                    const data = await response.json();
                    
                    // Update conversation ID
                    conversationId = data.conversation_id;
                    
                    // Add Sylvie's response
                    addMessage('assistant', data.message);
                    
                    // Update suggestions if provided
                    if (data.suggestions) {
                        updateSuggestions(data.suggestions);
                    }
                    
                } catch (error) {
                    console.error('Erreur:', error);
                    addMessage('assistant', 'Désolée, je rencontre un problème technique. Pouvez-vous réessayer ?');
                } finally {
                    // Hide typing indicator and re-enable button
                    typingIndicator.classList.remove('show');
                    sendButton.disabled = false;
                    messageInput.focus();
                }
            }
            
            function addMessage(type, content) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;
                
                const avatar = document.createElement('div');
                avatar.className = 'message-avatar';
                avatar.textContent = type === 'user' ? '👤' : '🤖';
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';
                contentDiv.innerHTML = content;
                
                messageDiv.appendChild(avatar);
                messageDiv.appendChild(contentDiv);
                
                chatMessages.appendChild(messageDiv);
                
                // Scroll to bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            function updateSuggestions(suggestions) {
                suggestionsContainer.innerHTML = '';
                suggestions.forEach(suggestion => {
                    const suggestionDiv = document.createElement('div');
                    suggestionDiv.className = 'suggestion';
                    suggestionDiv.textContent = suggestion;
                    suggestionDiv.onclick = () => sendSuggestion(suggestion);
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
            metadata=response.metadata
        )
        
        logger.info("✅ Réponse Sylvie générée",
                   conversation_id=api_response.conversation_id,
                   intent=api_response.intent,
                   action_taken=api_response.action_taken)
        
        return api_response
        
    except Exception as e:
        logger.error("❌ Erreur lors du traitement du message",
                    error=str(e),
                    message=message.message[:100])
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement du message: {str(e)}"
        )

@router.get("/status")
async def get_sylvie_status():
    """
    Endpoint pour vérifier le statut de Sylvie
    
    Returns:
        Statut de tous les services Sylvie
    """
    try:
        status = await sylvie_agent.get_status()
        return {
            "status": "operational",
            "sylvie_agent": status,
            "timestamp": "2025-08-01T00:00:00Z"
        }
    except Exception as e:
        logger.error("❌ Erreur lors de la vérification du statut", error=str(e))
        return {
            "status": "error",
            "error": str(e),
            "timestamp": "2025-08-01T00:00:00Z"
        }

@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Récupère l'historique d'une conversation
    
    Args:
        conversation_id: ID de la conversation
        
    Returns:
        Historique de la conversation
    """
    try:
        history = await sylvie_agent.get_conversation_history(conversation_id)
        return {
            "conversation_id": conversation_id,
            "messages": history,
            "total_messages": len(history)
        }
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération de la conversation",
                    error=str(e),
                    conversation_id=conversation_id)
        raise HTTPException(
            status_code=404,
            detail=f"Conversation introuvable: {conversation_id}"
        )

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Supprime une conversation
    
    Args:
        conversation_id: ID de la conversation à supprimer
        
    Returns:
        Confirmation de suppression
    """
    try:
        await sylvie_agent.delete_conversation(conversation_id)
        return {
            "message": "Conversation supprimée",
            "conversation_id": conversation_id
        }
    except Exception as e:
        logger.error("❌ Erreur lors de la suppression de la conversation",
                    error=str(e),
                    conversation_id=conversation_id)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )
