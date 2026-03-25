import pytest


@pytest.mark.asyncio
async def test_register_login_workspace_recharge_and_job_flow(client):
    register_response = await client.post(
        "/api/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Password123!",
            "workspace_name": "测试工作区",
        },
    )
    assert register_response.status_code == 200, register_response.text
    token = register_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Workspace-Id": register_response.json()["data"]["workspace"]["id"]}

    create_card_response = await client.post(
        "/api/admin/recharge-card-batches",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "测试批次", "credits_amount": 200, "total_count": 1},
    )
    assert create_card_response.status_code == 403

    admin_login = await client.post(
        "/api/auth/login",
        json={"username": "sysadmin", "password": "Admin12345!"},
    )
    assert admin_login.status_code == 200, admin_login.text
    admin_token = admin_login.json()["data"]["access_token"]

    batch_response = await client.post(
        "/api/admin/recharge-card-batches",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "测试批次", "credits_amount": 200, "total_count": 1},
    )
    assert batch_response.status_code == 200, batch_response.text
    card_code = batch_response.json()["data"]["cards"][0]["card_code"]

    redeem_response = await client.post(
        "/api/credits/recharge-cards/redeem",
        headers=headers,
        json={"card_code": card_code},
    )
    assert redeem_response.status_code == 200, redeem_response.text
    assert redeem_response.json()["data"]["wallet"]["balance"] == 200

    product_response = await client.post(
        "/api/products",
        headers=headers,
        json={"name": "保温杯", "product_type": "home", "notes": "304 不锈钢"},
    )
    assert product_response.status_code == 200, product_response.text
    product_id = product_response.json()["data"]["id"]

    prompt_response = await client.post(
        "/api/prompt-drafts/compile",
        headers=headers,
        json={
            "product_id": product_id,
            "platform": "douyin",
            "category": "scene_image",
            "controls": {"style": "极简高级感"},
        },
    )
    assert prompt_response.status_code == 200, prompt_response.text
    prompt_id = prompt_response.json()["data"]["id"]

    estimate_response = await client.post(
        "/api/pricing/estimate",
        headers=headers,
        json={
            "platform": "douyin",
            "items": [
                {
                    "category": "scene_image",
                    "count": 2,
                    "size": "m",
                    "flags": ["upscale"],
                    "model_key": "openai:gpt-image-1",
                }
            ],
        },
    )
    assert estimate_response.status_code == 200, estimate_response.text
    assert estimate_response.json()["data"]["total_credits"] == 15

    job_response = await client.post(
        "/api/jobs",
        headers=headers,
        json={
            "product_id": product_id,
            "platform": "douyin",
            "items": [
                {
                    "category": "scene_image",
                    "count": 2,
                    "size": "m",
                    "flags": ["upscale"],
                    "model_key": "openai:gpt-image-1",
                    "prompt_draft_id": prompt_id,
                }
            ],
        },
    )
    assert job_response.status_code == 200, job_response.text
    payload = job_response.json()["data"]
    assert payload["status"] == "queued"
    assert payload["credits_frozen"] == 15

    balance_response = await client.get("/api/credits/balance", headers=headers)
    assert balance_response.status_code == 200
    assert balance_response.json()["data"]["balance"] == 185
    assert balance_response.json()["data"]["frozen_balance"] == 15
