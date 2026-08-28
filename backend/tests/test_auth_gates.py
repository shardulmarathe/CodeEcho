"""Auth-gate matrix: identity headers, JWT verification, and guest claim.

Uses the in-memory session store (Supabase service-role key cleared). No live
Supabase. Pytest is the intended runner; this module is also executable so the
same assertions can run via TestClient when pytest is not installed.
"""

from __future__ import annotations

import sys
import time
import uuid
from pathlib import Path

import jwt
from fastapi.testclient import TestClient

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.config import settings  # noqa: E402
from app.main import app  # noqa: E402
from app.services import session_store  # noqa: E402

TEST_JWT_SECRET = "gates-test-jwt-secret-32bytes!!!"
TEST_SUPABASE_URL = "https://codeecho-test.supabase.co"
TEST_USER_ID = "11111111-2222-4333-8444-555555555555"


def _force_in_memory_auth_settings() -> None:
    """Point JWT verification at a test secret and keep persistence in-memory."""
    settings.supabase_jwt_secret = TEST_JWT_SECRET
    settings.supabase_url = TEST_SUPABASE_URL
    settings.supabase_service_role_key = ""
    settings.rerank_enabled = False
    settings.rag_enabled = False


def _mint_user_jwt(user_id: str = TEST_USER_ID) -> str:
    now = int(time.time())
    return jwt.encode(
        {
            "sub": user_id,
            "aud": "authenticated",
            "iss": TEST_SUPABASE_URL.rstrip("/") + "/auth/v1",
            "iat": now,
            "exp": now + 3600,
            "role": "authenticated",
            "email": "user@example.com",
        },
        TEST_JWT_SECRET,
        algorithm="HS256",
    )


def _guest_headers(token: str) -> dict[str, str]:
    return {"X-Guest-Token": token}


def _bearer_headers(jwt_token: str, guest_token: str | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {jwt_token}"}
    if guest_token:
        headers["X-Guest-Token"] = guest_token
    return headers


def _client() -> TestClient:
    _force_in_memory_auth_settings()
    session_store._sessions.clear()
    return TestClient(app)


def _create_attempt(client: TestClient, guest_token: str) -> str:
    response = client.post("/api/attempts", headers=_guest_headers(guest_token))
    assert response.status_code == 200, response.text
    return response.json()["session_id"]


def test_stream_no_identity_400() -> None:
    with _client() as client:
        response = client.get(f"/api/attempts/{uuid.uuid4()}/stream")
        assert response.status_code == 400, response.text


def test_stream_guest_b_cannot_read_guest_a_404() -> None:
    guest_a = str(uuid.uuid4())
    guest_b = str(uuid.uuid4())
    with _client() as client:
        attempt_id = _create_attempt(client, guest_a)
        response = client.get(
            f"/api/attempts/{attempt_id}/stream",
            headers=_guest_headers(guest_b),
        )
        assert response.status_code == 404, response.text


def test_stream_guest_a_own_attempt_not_401() -> None:
    guest_a = str(uuid.uuid4())
    with _client() as client:
        attempt_id = _create_attempt(client, guest_a)
        response = client.get(
            f"/api/attempts/{attempt_id}/stream",
            headers=_guest_headers(guest_a),
        )
        assert response.status_code != 401, response.text
        if response.status_code == 400:
            assert "No audio" in response.text


def test_analyze_no_identity_400() -> None:
    with _client() as client:
        response = client.post(f"/api/attempts/{uuid.uuid4()}/analyze")
        assert response.status_code == 400, response.text


def test_audio_no_identity_400() -> None:
    with _client() as client:
        response = client.get("/api/audio/whatever.webm")
        assert response.status_code == 400, response.text


def test_invalid_bearer_401() -> None:
    with _client() as client:
        response = client.get(
            "/api/me",
            headers={"Authorization": "Bearer not-a-valid-jwt"},
        )
        assert response.status_code == 401, response.text


def test_valid_hs256_jwt_me_authenticated() -> None:
    token = _mint_user_jwt()
    with _client() as client:
        response = client.get("/api/me", headers=_bearer_headers(token))
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["authenticated"] is True
        assert body["user_id"] == TEST_USER_ID
        assert body["profile"]["email"] == "user@example.com"


def test_claim_without_bearer_401() -> None:
    with _client() as client:
        response = client.post("/api/attempts/claim")
        assert response.status_code == 401, response.text


def test_claim_uses_header_not_body() -> None:
    guest_a = str(uuid.uuid4())
    guest_b = str(uuid.uuid4())
    token = _mint_user_jwt()
    with _client() as client:
        attempt_a = _create_attempt(client, guest_a)
        attempt_b = _create_attempt(client, guest_b)

        claimed = client.post(
            "/api/attempts/claim",
            headers=_bearer_headers(token, guest_token=guest_a),
            json={"guest_token": guest_b},
        )
        assert claimed.status_code == 200, claimed.text
        assert claimed.json()["transferred"] >= 1

        as_user = client.get(
            f"/api/attempts/{attempt_a}",
            headers=_bearer_headers(token),
        )
        assert as_user.status_code == 200, as_user.text

        as_guest_a = client.get(
            f"/api/attempts/{attempt_a}",
            headers=_guest_headers(guest_a),
        )
        assert as_guest_a.status_code == 404, as_guest_a.text

        steal = client.post(
            "/api/attempts/claim",
            headers=_bearer_headers(token),
            json={"guest_token": guest_b},
        )
        assert steal.status_code == 200, steal.text
        assert steal.json()["transferred"] == 0

        still_b = client.get(
            f"/api/attempts/{attempt_b}",
            headers=_guest_headers(guest_b),
        )
        assert still_b.status_code == 200, still_b.text


def test_get_question_no_identity_400() -> None:
    with _client() as client:
        response = client.get(f"/api/questions/{uuid.uuid4()}")
        assert response.status_code == 400, response.text


def test_guest_b_cannot_read_guest_a_question() -> None:
    guest_a = str(uuid.uuid4())
    guest_b = str(uuid.uuid4())
    with _client() as client:
        created = client.post(
            "/api/questions",
            headers=_guest_headers(guest_a),
            json={"qtype": "behavioral", "prompt": "Tell me about a time you failed."},
        )
        assert created.status_code == 200, created.text
        qid = created.json()["id"]
        as_b = client.get(f"/api/questions/{qid}", headers=_guest_headers(guest_b))
        assert as_b.status_code == 404, as_b.text
        as_a = client.get(f"/api/questions/{qid}", headers=_guest_headers(guest_a))
        assert as_a.status_code == 200, as_a.text


def test_clip_no_identity_400() -> None:
    with _client() as client:
        response = client.get("/api/clips/nope.mp3")
        assert response.status_code == 400, response.text


def test_clip_hmac_query_serves_file() -> None:
    from app.services import storage

    Path(settings.clips_dir).mkdir(parents=True, exist_ok=True)
    name = "hmac-clip.mp3"
    path = Path(settings.clips_dir) / name
    path.write_bytes(b"fake-mp3")
    try:
        url = storage.clip_url(name)
        assert "sig=" in url
        route, qs = url.split("?", 1)
        with _client() as client:
            ok = client.get(f"{route}?{qs}")
            assert ok.status_code == 200, ok.text
            bad = client.get(f"{route}?exp=1&sig=deadbeef")
            assert bad.status_code == 400, bad.text
    finally:
        path.unlink(missing_ok=True)


def test_guest_b_cannot_read_guest_a_clip() -> None:
    guest_a = str(uuid.uuid4())
    guest_b = str(uuid.uuid4())
    with _client() as client:
        attempt_id = _create_attempt(client, guest_a)
        Path(settings.clips_dir).mkdir(parents=True, exist_ok=True)
        name = f"{attempt_id}_0.mp3"
        path = Path(settings.clips_dir) / name
        path.write_bytes(b"fake-mp3")
        try:
            stolen = client.get(f"/api/clips/{name}", headers=_guest_headers(guest_b))
            assert stolen.status_code == 404, stolen.text
            owned = client.get(f"/api/clips/{name}", headers=_guest_headers(guest_a))
            assert owned.status_code == 200, owned.text
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    tests = [
        test_stream_no_identity_400,
        test_stream_guest_b_cannot_read_guest_a_404,
        test_stream_guest_a_own_attempt_not_401,
        test_analyze_no_identity_400,
        test_audio_no_identity_400,
        test_invalid_bearer_401,
        test_valid_hs256_jwt_me_authenticated,
        test_claim_without_bearer_401,
        test_claim_uses_header_not_body,
        test_get_question_no_identity_400,
        test_guest_b_cannot_read_guest_a_question,
        test_clip_no_identity_400,
        test_clip_hmac_query_serves_file,
        test_guest_b_cannot_read_guest_a_clip,
    ]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
        except Exception as exc:
            failed += 1
            print(f"FAIL {test.__name__}: {exc}")
    print(f"{len(tests) - failed} passed, {failed} failed")
    raise SystemExit(failed)
