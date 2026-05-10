from locust import HttpUser, task, constant

class PesadoUser(HttpUser):
    wait_time = constant(0)

    @task
    def load_pesado(self):
        self.client.get("/post-imagem-1mb/")