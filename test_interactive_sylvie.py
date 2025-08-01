#!/usr/bin/env python3
"""
🎯 Test Interactif Sylvie v2.0 Email IA
"""

import asyncio
import aiohttp
import json

async def test_sylvie_response(message):
    """Test une phrase avec Sylvie"""
    async with aiohttp.ClientSession() as session:
        try:
            response = await session.post(
                "http://localhost:8002/api/v1/sylvie/chat",
                json={
                    "message": message,
                    "conversation_id": "test_interactive"
                },
                timeout=30
            )
            
            if response.status == 200:
                data = await response.json()
                print(f"✅ Message: '{message}'")
                print(f"🤖 Réponse: {data.get('response', '')}")
                
                if 'action_result' in data and data['action_result']:
                    print(f"🔧 Action result: {json.dumps(data['action_result'], indent=2, ensure_ascii=False)}")
                print("=" * 80)
                return True
            else:
                print(f"❌ Erreur HTTP: {response.status}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
            return False

async def main():
    """Tests interactifs"""
    print("🚀 Tests Interactifs Sylvie v2.0 Email IA")
    print("=" * 60)
    
    test_messages = [
        "check mes mails",
        "vérifie mes emails",
        "regarde ma boîte mail",
        "fais-moi un résumé de mes emails",
        "analyse mes emails avec IA",
        "montre-moi mes emails urgents",
        "y a-t-il des messages importants ?"
    ]
    
    for message in test_messages:
        await test_sylvie_response(message)
        await asyncio.sleep(2)  # Pause entre les tests

if __name__ == "__main__":
    asyncio.run(main())
