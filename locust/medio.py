from locust import HttpUser, task

class MedioUser(HttpUser):
    @task
    def load_medio(self):
        self.client.get("/2026/04/22/post-texto-400k/")