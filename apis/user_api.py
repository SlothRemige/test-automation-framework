from typing import Any

from apis.base_api import BaseApi


class UserApi(BaseApi):
    def login(self, username: str, password: str) -> dict[str, Any]:
        resp = self.client.post(
            "/auth/login",
            json={"username": username, "password": password},
        )
        return resp.json()

    def get_profile(self, user_id: str) -> dict[str, Any]:
        resp = self.client.get(f"/users/{user_id}")
        return resp.json()

    def create_user(self, payload: dict[str, Any]) -> dict[str, Any]:
        resp = self.client.post("/users", json=payload)
        return resp.json()

    def update_user(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        resp = self.client.put(f"/users/{user_id}", json=payload)
        return resp.json()

    def delete_user(self, user_id: str) -> dict[str, Any]:
        resp = self.client.delete(f"/users/{user_id}")
        return resp.json()
