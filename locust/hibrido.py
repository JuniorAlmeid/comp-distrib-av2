from locust import HttpUser, task

class HibridoUser(HttpUser):
    @task
    def load_hibrido(self):
        # Executa os 3 em sequência
        self.client.get("/2026/04/22/post-imagem-300kb/")
        self.client.get("/2026/04/22/post-texto-400k/")
        self.client.get("/2026/04/22/post-imagem-1mb/")