from locust import HttpUser, task

class LeveUser(HttpUser):
    @task
    def load_leve(self):
        self.client.get("/2026/04/22/post-imagem-300kb/")