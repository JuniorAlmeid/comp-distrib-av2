from locust import HttpUser, task, constant

class HibridoUser(HttpUser):
    wait_time = constant(0)

    @task
    def load_hibrido(self):
        # Executa os 3 em sequência
        self.client.get("/post-imagem-300kb/")
        self.client.get("/post-texto-400k/")
        self.client.get("/post-imagem-1mb/")