
import os
from functools import lru_cache
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


bearer_scheme = HTTPBearer(auto_error=False)

ALLOWED_ALGORITHMS = {"ES256", "RS256"}


@lru_cache(maxsize=4)
def get_jwks_client(supabase_url: str) -> jwt.PyJWKClient:
    return jwt.PyJWKClient(
        f"{supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json",
        cache_jwk_set=True,
        timeout=5,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    # Missing credentials should consistently produce 401.
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")

    if not supabase_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured.",
        )

    token = credentials.credentials

    try:
        header = jwt.get_unverified_header(token)
        algorithm = header.get("alg")

        if algorithm not in ALLOWED_ALGORITHMS:
            raise jwt.InvalidTokenError("Unsupported signing algorithm")

        signing_key = get_jwks_client(
            supabase_url
        ).get_signing_key_from_jwt(token)

        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=list(ALLOWED_ALGORITHMS),
            audience="authenticated",
            issuer=f"{supabase_url}/auth/v1",
            options={
                "require": ["exp", "sub", "iss", "aud"],
            },
        )

        if (
            not claims.get("sub")
            or claims.get("role") != "authenticated"
        ):
            raise jwt.InvalidTokenError("Invalid authenticated user claims")

        return claims

    except jwt.PyJWKClientConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service temporarily unavailable.",
        ) from None

    except (jwt.InvalidTokenError, jwt.PyJWKClientError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
