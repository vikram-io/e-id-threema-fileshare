import os
import jwt
import uuid
import time
import json
import logging
import base64
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OID4VPService:
    def __init__(self):
        # In a production environment, these would be loaded from environment variables
        self.client_id = os.getenv('OID4VP_CLIENT_ID', 'https://5000-i3jprkh9dbwt212lh31ev-cb667664.manus.computer/callback')
        self.redirect_uri = os.getenv('OID4VP_REDIRECT_URI', 'https://5000-i3jprkh9dbwt212lh31ev-cb667664.manus.computer/callback')
        
        # Generate or load keys for signing
        self._init_keys()
        
        # Store active sessions
        self.active_sessions = {}
        
    def _init_keys(self):
        """Initialize or load cryptographic keys for signing JWTs"""
        try:
            # In a production environment, these would be securely stored
            # For this implementation, we'll generate new keys each time
            self.private_key = ec.generate_private_key(ec.SECP256R1())
            self.public_key = self.private_key.public_key()
            
            # Get the public key in PEM format for verification
            self.public_key_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')
            
            logger.info("Cryptographic keys initialized")
        except Exception as e:
            logger.error(f"Failed to initialize cryptographic keys: {e}")
            raise
    
    def create_presentation_request(self, file_id):
        """
        Create an OID4VP presentation request for the given file
        
        Args:
            file_id (str): ID of the file to be signed
            
        Returns:
            dict: The request data including JWT and state
        """
        try:
            # Generate unique identifiers
            request_id = str(uuid.uuid4())
            nonce = str(uuid.uuid4())
            state = str(uuid.uuid4())
            
            # Create the presentation definition
            presentation_definition = {
                "id": request_id,
                "input_descriptors": [
                    {
                        "id": "swiss-eid-descriptor",
                        "format": {
                            "jwt_vp": {
                                "alg": ["ES256"]
                            }
                        },
                        "constraints": {
                            "fields": [
                                {
                                    "path": ["$.type"],
                                    "filter": {
                                        "type": "string",
                                        "pattern": "SwissEID"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
            
            # Create the request payload
            payload = {
                "response_type": "vp_token",
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "response_mode": "direct_post",
                "presentation_definition": presentation_definition,
                "nonce": nonce,
                "state": state,
                "exp": int(time.time()) + 300  # 5 minutes expiration
            }
            
            # Sign the JWT (in a real implementation, this would use proper keys)
            # For this implementation, we'll use a simple JWT without actual signing
            jwt_token = jwt.encode(payload, "secret_key", algorithm="HS256")
            
            # Store session data
            self.active_sessions[state] = {
                "file_id": file_id,
                "request_id": request_id,
                "nonce": nonce,
                "created_at": datetime.now(),
                "status": "pending"
            }
            
            return {
                "jwt": jwt_token,
                "state": state,
                "request_id": request_id
            }
        except Exception as e:
            logger.error(f"Failed to create presentation request: {e}")
            return None
    
    def get_auth_url(self, jwt_token):
        """
        Generate the authorization URL for the E-ID app
        
        Args:
            jwt_token (str): The JWT token containing the request
            
        Returns:
            str: The authorization URL
        """
        # For mobile apps, use the openid:// scheme
        return f"openid://vp?request={jwt_token}"
    
    def verify_presentation(self, presentation_jwt, state):
        """
        Verify a presentation JWT from the E-ID app
        
        Args:
            presentation_jwt (str): The JWT containing the presentation
            state (str): The state parameter to match with the request
            
        Returns:
            dict: Verification result
        """
        try:
            # Check if the state exists in active sessions
            if state not in self.active_sessions:
                logger.warning(f"Unknown state: {state}")
                return {
                    "success": False,
                    "error": "Invalid state parameter"
                }
            
            session = self.active_sessions[state]
            
            # In a real implementation, this would verify the JWT signature
            # For this implementation, we'll decode without verification
            try:
                presentation = jwt.decode(
                    presentation_jwt, 
                    options={"verify_signature": False}
                )
            except jwt.PyJWTError as e:
                logger.error(f"JWT decode error: {e}")
                return {
                    "success": False,
                    "error": f"Invalid JWT: {str(e)}"
                }
            
            # Verify nonce to prevent replay attacks
            if presentation.get("nonce") != session["nonce"]:
                logger.warning("Nonce mismatch")
                return {
                    "success": False,
                    "error": "Invalid nonce"
                }
            
            # In a real implementation, we would:
            # 1. Resolve the DID to get the public key
            # 2. Verify the JWT signature
            # 3. Validate the credential against the Trust Registry
            # 4. Check for revocation
            
            # For this implementation, we'll simulate successful verification
            
            # Update session status
            session["status"] = "verified"
            session["verified_at"] = datetime.now()
            session["user_did"] = presentation.get("iss")
            
            return {
                "success": True,
                "file_id": session["file_id"],
                "user_did": presentation.get("iss")
            }
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return {
                "success": False,
                "error": f"Verification error: {str(e)}"
            }
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions (older than 10 minutes)"""
        now = datetime.now()
        expired_states = []
        
        for state, session in self.active_sessions.items():
            if now - session["created_at"] > timedelta(minutes=10):
                expired_states.append(state)
        
        for state in expired_states:
            del self.active_sessions[state]
            
        if expired_states:
            logger.info(f"Cleaned up {len(expired_states)} expired sessions")

# Singleton instance
oid4vp_service = OID4VPService()
