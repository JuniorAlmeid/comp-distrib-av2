from locust import HttpUser, task, constant

class MedioUser(HttpUser):
    wait_time = constant(0)

    @task
    def load_medio(self):
        self.client.get("/post-texto-400k/")