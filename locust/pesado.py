from locust import HttpUser, task

class PesadoUser(HttpUser):
    @task
    def load_pesado(self):
        self.client.get("/2026/04/22/post-imagem-1mb/")