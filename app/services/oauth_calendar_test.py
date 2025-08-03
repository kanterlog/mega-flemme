import asyncio
from app.services.google_workspace_mcp_v23 import EnhancedGoogleWorkspaceMCP

async def main():
    user_email = "test@example.com"
    service_name = "calendar"
    mcp = EnhancedGoogleWorkspaceMCP()

    print("\n🔐 Génération de l'URL d'autorisation OAuth pour Calendar...")
    oauth_url = await mcp.start_oauth_flow(user_email, service_name)
    print(f"Ouvrez cette URL dans votre navigateur pour autoriser l'accès :\n{oauth_url}")
    print("Après autorisation, copiez le code et le state du callback ici.")
    code = input("Code OAuth : ").strip()
    state = input("State : ").strip()
    print("\n🔑 Callback OAuth pour Calendar...")
    token_info = await mcp.handle_oauth_callback(code, state)
    print(f"Token Calendar stocké : {token_info}")
    print("\nTest d'accès réel à l'API Calendar...")
    calendars = await mcp.list_calendars_enhanced(user_google_email=user_email, include_analytics=True)
    print(f"Calendriers trouvés : {calendars}")

if __name__ == "__main__":
    asyncio.run(main())
