from locust import HttpUser, task, constant

class LeveUser(HttpUser):
    wait_time = constant(0)
    
    @task
    def load_leve(self):
        self.client.get("/post-imagem-300kb/")