import random

from locust import HttpUser, between, task

USERNAME = "test_user"
PASSWORD = "test_password"


class PortfoyarUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        response = self.client.post(
            "sign-in/", json={"username": USERNAME, "password": PASSWORD}
        )
        self.token = response.json().get("token")

    @task(1)
    def select_industry_commodity_type(self):
        response = self.client.get(
            "global-market/industry/",
            name="select_industry_commodity_type",
            headers={"Authorization": f"token {self.token}"},
        )
        result = response.json()
        self.industry_id_list = [industry["id"] for industry in result]

        industry_id = random.choice(self.industry_id_list)
        response = self.client.get(
            f"global-market/commodity-type/{industry_id}",
            name="select_industry_commodity_type",
            headers={"Authorization": f"token {self.token}"},
        )
        result = response.json()
        self.commodity_type_id_list = [
            commodity_type["id"] for commodity_type in result
        ]

    @task(2)
    def select_industry_commodity_type_commodity(self):
        response = self.client.get(
            "global-market/industry/",
            name="select_industry_commodity_type_commodity",
            headers={"Authorization": f"token {self.token}"},
        )
        result = response.json()
        self.industry_id_list = [industry["id"] for industry in result]

        industry_id = random.choice(self.industry_id_list)
        response = self.client.get(
            f"global-market/commodity-type/{industry_id}",
            name="select_industry_commodity_type_commodity",
            headers={"Authorization": f"token {self.token}"},
        )
        result = response.json()
        self.commodity_type_id_list = [
            commodity_type["id"] for commodity_type in result
        ]

        commodity_type_id = random.choice(self.commodity_type_id_list)
        response = self.client.get(
            f"global-market/commodity/{commodity_type_id}",
            name="select_industry_commodity_type_commodity",
            headers={"Authorization": f"token {self.token}"},
        )
        result = response.json()
        self.commodity_id_list = [commodity["id"] for commodity in result]

    @task(3)
    def select_industry_commodity_type_commodity_transit(self):
        response = self.client.get(
            "global-market/industry/",
            name="select_industry_commodity_type_commodity_transit",
            headers={"Authorization": f"token {self.token}"},
        )
        result = response.json()
        self.industry_id_list = [industry["id"] for industry in result]

        industry_id = random.choice(self.industry_id_list)
        response = self.client.get(
            f"global-market/commodity-type/{industry_id}",
            name="select_industry_commodity_type_commodity_transit",
            headers={"Authorization": f"token {self.token}"},
        )
        result = response.json()
        self.commodity_type_id_list = [
            commodity_type["id"] for commodity_type in result
        ]

        commodity_type_id = random.choice(self.commodity_type_id_list)
        response = self.client.get(
            f"global-market/commodity/{commodity_type_id}",
            name="select_industry_commodity_type_commodity_transit",
            headers={"Authorization": f"token {self.token}"},
        )
        result = response.json()
        self.commodity_id_list = [commodity["id"] for commodity in result]

        commodity_id = random.choice(self.commodity_id_list)
        self.client.get(
            f"global-market/transit/{commodity_id}",
            name="select_industry_commodity_type_commodity_transit",
            headers={"Authorization": f"token {self.token}"},
        )
