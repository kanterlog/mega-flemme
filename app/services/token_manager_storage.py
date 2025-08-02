# Persistance et sécurité des tokens OAuth2
# Stockage local sécurisé (exemple: fichier JSON, chiffrement à prévoir)
import json
import os

TOKEN_FILE = 'tokens.json'

class TokenManagerStorage:
    def __init__(self, path=TOKEN_FILE):
        self.path = path
        self.tokens = self._load_tokens()

    def _load_tokens(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                return json.load(f)
        return {}

    def save_tokens(self):
        with open(self.path, 'w') as f:
            json.dump(self.tokens, f)

    def get_token(self, account_email):
        return self.tokens.get(account_email)

    def set_token(self, account_email, token):
        self.tokens[account_email] = token
        self.save_tokens()

    def list_accounts(self):
        return list(self.tokens.keys())

# TODO: Ajouter chiffrement, rotation, gestion multi-utilisateur
