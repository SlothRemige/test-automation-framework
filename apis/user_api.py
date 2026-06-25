from __future__ import annotations

from typing import Any

from apis.base_api import BaseApi


class ApiResponse(dict[str, Any]):
    """Dict-like response wrapper that also exposes HTTP status code."""

    def __init__(self, data: dict[str, Any], status_code: int) -> None:
        super().__init__(data)
        self.status_code = status_code


class UserApi(BaseApi):
    def _call(self, method: str, path: str, **kwargs) -> ApiResponse:
        resp = getattr(self.client, method)(path, **kwargs)
        try:
            body = resp.json()
        except Exception:
            body = {"_raw": resp.text}
        return ApiResponse(body, resp.status_code)

    def login(self, username: str, password: str) -> ApiResponse:
        return self._call(
            "post", "/auth/login",
            json={"username": username, "password": password},
        )

    def get_profile(self, user_id: str) -> ApiResponse:
        return self._call("get", f"/users/{user_id}")

    def create_user(self, payload: dict[str, Any]) -> ApiResponse:
        return self._call("post", "/users", json=payload)

    def update_user(self, user_id: str, payload: dict[str, Any]) -> ApiResponse:
        return self._call("put", f"/users/{user_id}", json=payload)

    def delete_user(self, user_id: str) -> ApiResponse:
        return self._call("delete", f"/users/{user_id}")
