# auth.py
from ninja.security import HttpBearer
from django.conf import settings
from keycloak import KeycloakOpenID
from .models import UserProfile
import logging
import uuid
import jwt

logger = logging.getLogger(__name__)

class KeycloakBearer(HttpBearer):
    """
    Validates Bearer tokens issued by Keycloak and syncs user data into UserProfile.
    Uses realm roles: role_user, role_cook
    """

    def authenticate(self, request, token: str):
        if not token:
            return None

        try:
            keycloak_openid = KeycloakOpenID(
                server_url=f"https://dermic-captiously-enrique.ngrok-free.dev/",
                realm_name="mm",
                client_id="mm-api",
                client_secret_key="euCmMIbtIXHP6lmZNaTjWFkNcTDH0nxl",
                verify=True,
            )
            print("Keycloak OpenID initialized." + str(keycloak_openid))

            # Decode JWT manually using Keycloak's JWKS
            jwks_uri = f"https://dermic-captiously-enrique.ngrok-free.dev/realms/mm/protocol/openid-connect/certs"
            import requests
            jwks = requests.get(jwks_uri).json()
            public_keys = {key["kid"]: jwt.algorithms.RSAAlgorithm.from_jwk(key) for key in jwks["keys"]}
            print("JWKS fetched and public keys prepared." + str(public_keys))

            header = jwt.get_unverified_header(token)
            key = public_keys[header["kid"]]

            decoded_token = jwt.decode(
                token,
                key=key,
                algorithms=["RS256"],
                audience="mm-api",
                issuer=f"https://dermic-captiously-enrique.ngrok-free.dev/realms/mm",
            )

            sub = decoded_token.get("sub")
            username = decoded_token.get("preferred_username", "unknown")
            email = decoded_token.get("email", "")
            roles = decoded_token.get("realm_access", {}).get("roles", [])

            # Map Keycloak realm roles → app role
            if "role_cook" in roles:
                role = "cook"
            elif "role_user" in roles:
                role = "user"
            else:
                role = "user"  # default fallback

            # Sync with UserProfile
            user, created = UserProfile.objects.update_or_create(
                keycloak_id=uuid.UUID(sub),
                defaults={
                    "username": username,
                    "email": email,
                    "role": role,
                },
            )
            print(f"UserProfile synced: {user.username} (created={created})")

            request.user = user
            request.roles = roles
            return user

        except Exception as ex:
            logger.warning(f"Keycloak authentication failed: {ex}")
            return None
