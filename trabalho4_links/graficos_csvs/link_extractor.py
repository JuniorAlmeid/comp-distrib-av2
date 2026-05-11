from locust import HttpUser, task, constant

class ExtractorUser(HttpUser):
    wait_time = constant(0)

    @task
    def extrair_links(self):
        urls = [
            "https://www.python.org",
            "https://ubuntu.com",
            "https://www.apache.org",
            "https://www.nginx.com",
            "https://www.postgresql.org",
            "https://www.gnu.org",
            "https://www.w3.org"
        ]
        for url in urls:
            self.client.get(f"/api/links?url={url}", name="Extracao_Pesada")
