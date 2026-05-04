from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3) 

    @task
    def test_post(self):
        self.client.get("/2026/04/22/post-imagem-1mb/")