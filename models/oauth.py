from models.database_manager import DatabaseManager


class OAuthManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self._create_tables()

    def _create_tables(self):
        self.db_manager.execute_action("""
                                       CREATE TABLE IF NOT EXISTS oauth_accounts
                                       (
                                           id
                                           INTEGER
                                           PRIMARY
                                           KEY
                                           AUTOINCREMENT,
                                           provider
                                           TEXT
                                           NOT
                                           NULL,
                                           provider_user_id
                                           TEXT
                                           NOT
                                           NULL,
                                           user_id
                                           INTEGER
                                           NOT
                                           NULL,
                                           provider_email
                                           TEXT,
                                           FOREIGN
                                           KEY
                                       (
                                           user_id
                                       ) REFERENCES users
                                       (
                                           user_id
                                       ),
                                           UNIQUE
                                       (
                                           provider,
                                           provider_user_id
                                       )
                                           )
                                       """)

    def get_user_by_provider_id(self, provider, provider_user_id):
        """get user by OAuth provider ID"""
        result = self.db_manager.execute_query(
            """
            SELECT u.user_id, u.username, u.email, u.verified
            FROM users u
                     JOIN oauth_accounts o ON u.user_id = o.user_id
            WHERE o.provider = ?
              AND o.provider_user_id = ?
            """,
            (provider, provider_user_id)
        )
        return result[0] if result else None

    def link_oauth_account(self, user_id, provider, provider_user_id, provider_email=None):
        """link OAuth account to a user"""
        try:
            self.db_manager.execute_action(
                """
                INSERT INTO oauth_accounts (provider, provider_user_id, user_id, provider_email)
                VALUES (?, ?, ?, ?)
                """,
                (provider, provider_user_id, user_id, provider_email)
            )
            return True
        except Exception as e:
            print(f"Error linking OAuth account: {e}")
            return False

    def create_user_from_oauth(self, username, email, provider, provider_user_id, risk_tolerance="Medium"):
        """create new user from OAuth and link account"""
        try:
            #insert new user with verified=1 (verified through OAuth)
            self.db_manager.execute_action(
                """
                INSERT INTO users (username, email, password, risk_tolerance, verification_code, verified)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (username, email, "oauth-login-no-password", risk_tolerance, "")
            )

            # get new user's ID
            result = self.db_manager.execute_query(
                "SELECT user_id FROM users WHERE email = ?",
                (email,)
            )

            if not result:
                return None

            user_id = result[0][0]

            self.link_oauth_account(user_id, provider, provider_user_id, email)

            return user_id, username
        except Exception as e:
            print(f"Error creating user from OAuth: {e}")
            return None