# Benchmarking e Análise de Desempenho de Infraestrutura Web

Este repositório consolida as entregas práticas das avaliações de Infraestrutura, focando em testes de carga, escalabilidade horizontal, conteinerização de microsserviços e estratégias de cache.

## 👥 Equipe
* **Rogério Bruno** - Matrícula: [2316922]
* **Amanda Evellin** - Matrícula: [2315774]
* **Pedro Enrique** - Matrícula: [2315773]

---

## 🏗️ Estrutura Geral do Projeto

O repositório está dividido em dois laboratórios independentes, orquestrados via Docker Compose e automatizados por scripts Bash.

```text
📁 TRABALHO-INFRA/
│
├── 📁 trabalho3_wordpress/       # Análise de Escalabilidade Horizontal
│   ├── 📁 html/                  # Arquivos estáticos e mídias dos testes
│   ├── 📁 graficos_csvs/         # Gráficos, csvs e scripts do Locust
│   ├── 🐳 docker-compose.yml     # Orquestração (Nginx, WP, MariaDB)
│   ├── ⚙️ nginx.conf              # Configuração do Load Balancer (Round Robin)
│   └── 📜 run_tests.sh           # Automação da matriz de testes (1, 2 e 3 instâncias)
│
└── 📁 trabalho4_links/           # Comparativo de Microsserviços e Cache
    ├── 📁 graficos_csvs/         # Gráficos, csvs e scripts do Locust
    ├── 📁 python_api/            # API customizada do Link Extractor em Python (Flask)
    ├── 📁 ruby_api/              # API customizada do Link Extractor em Ruby (Sinatra)
    ├── 🐳 docker-compose.yml     # Orquestração gerada dinamicamente pelo script
    └── 📜 run_links.sh           # Automação de build, testes e troca de linguagens
```

---

## 🛠️ Ferramenta de Teste de Carga Utilizada: Locust

Para a injeção de carga e simulação de estresse, utilizamos o **Locust**, uma ferramenta open-source baseada em Python. A escolha se deu pela sua arquitetura orientada a eventos, que permite simular milhares de usuários simultâneos consumindo poucos recursos da máquina atacante, e pela flexibilidade de definir o comportamento do usuário através de código puro.

Os testes foram executados no modo *Headless* (sem interface gráfica), garantindo que todo o processamento fosse dedicado à injeção de requisições e à coleta precisa das métricas (Latência P95, Vazão/RPS e Taxa de Falhas).

### Comportamento do Usuário Virtual (Scripts de Configuração)
Em ambos os trabalhos, o comportamento base foi definido para gerar o **estresse máximo contínuo**, utilizando `wait_time = constant(0)`. Isso significa que o usuário virtual não tem tempo de "leitura" na página; assim que recebe a resposta do servidor, ele dispara a próxima requisição imediatamente.

#### Script de Usuário - Trabalho 3 (Exemplo: Cenário Pesado)
No Trabalho 3, o usuário virtual acessa rotas específicas do WordPress que carregam mídias de diferentes tamanhos.
```python
from locust import HttpUser, task, constant

class WordPressUser(HttpUser):
    wait_time = constant(0) # Estresse contínuo sem pausas

    @task
    def acessar_post_pesado(self):
        # Acessa um post contendo uma imagem não otimizada de 1MB
        self.client.get("/?p=12", name="Carga_Pesada_1MB")
```

#### Script de Usuário - Trabalho 4 (Web Scraping de Alta Carga)
No Trabalho 4, o usuário virtual faz requisições à API passando um array de URLs densas de projetos Open Source (para evitar bloqueios de WAF/Anti-Bot), forçando o processador do servidor a realizar *parsing* intenso de HTML.
```python
from locust import HttpUser, task, constant

class ExtractorUser(HttpUser):
    wait_time = constant(0)

    @task
    def extrair_links(self):
        urls_pesadas = [
            "[https://www.python.org](https://www.python.org)",
            "[https://ubuntu.com](https://ubuntu.com)",
            "[https://www.apache.org](https://www.apache.org)",
            "[https://www.nginx.com](https://www.nginx.com)",
            "[https://www.postgresql.org](https://www.postgresql.org)",
            "[https://www.gnu.org](https://www.gnu.org)",
            "[https://www.w3.org](https://www.w3.org)"
        ]
        
        for url in urls_pesadas:
            # Ataca a rota da API mandando extrair os links dos portais
            self.client.get(f"/api/links?url={url}", name="Extracao_Pesada")
```

---

## 📊 Trabalho 3: Escalabilidade Nginx + WordPress

### Descrição dos Cenários Avaliados
O objetivo foi avaliar como a adição de instâncias (1, 2 e 3 réplicas do WordPress atrás de um proxy reverso Nginx) reage sob estresse. Os testes duraram 2 minutos por rodada, com cargas de `100`, `150` e `156` usuários simultâneos em 4 perfis distintos:

1. **Cenário Leve:** Requisição de uma página simples contendo apenas uma imagem otimizada de `300KB`.
2. **Cenário Médio:** Requisição de um post focado em processamento de banco de dados, contendo um texto longo de `400KB`.
3. **Cenário Pesado:** Requisição de um post contendo uma imagem pesada de `1MB`, visando saturar a banda e a memória.
4. **Cenário Híbrido:** Os usuários virtuais sorteiam aleatoriamente o acesso entre os 3 cenários anteriores, simulando o tráfego real e imprevisível de um site.

### Como Executar (T3)
1. Navegue até a pasta: `cd trabalho3_wordpress`
2. Execute o script de automação: `bash run_tests.sh`
3. Para gerar os gráficos analíticos: `cd locust/graficos && python gerar_graficos.py`

---

## 🚀 Trabalho 4: Desempenho de Microsserviços (Python vs Ruby + Redis)

### Descrição dos Cenários Avaliados
O foco deste laboratório foi analisar o tempo de processamento bruto de linguagens diferentes ao executar tarefas de processamento de strings (*Web Scraping*) e medir o impacto direto da introdução de uma camada de Cache em memória (Redis). 

Os testes foram executados com cargas de `30`, `60` e `90` usuários simultâneos (com *spawn rate* de 10 usuários/s), cada teste durando 1 minuto nos seguintes cenários arquiteturais:

* **Cenário 1: Python (Sem Cache):** API construída em Flask utilizando BeautifulSoup4 para extração de dados. Cada requisição obriga o contêiner a baixar a página inteira da internet e varrer o DOM do zero.
* **Cenário 2: Python (Com Cache):** Mesma API em Flask, mas integrada a um contêiner Redis. Se a URL já foi extraída nos últimos 5 minutos (TTL 300s), o processamento é ignorado e o JSON é devolvido instantaneamente pela RAM.
* **Cenário 3: Ruby (Sem Cache):** API equivalente construída em Sinatra utilizando a *gem* Nokogiri. Executa o mesmo processo de download e *parsing* intensivo a cada requisição.
* **Cenário 4: Ruby (Com Cache):** API em Sinatra integrada ao Redis, utilizando a mesma lógica de *bypass* de processamento via leitura em memória.

### Como Executar (T4)
1. Navegue até a pasta: `cd trabalho4_links`
2. Execute o script mestre (ele fará o *build* local das imagens e rodará a matriz de testes): `bash run_links.sh`
3. Para gerar os gráficos comparativos lado a lado: `cd locust && python gerar_graficos.py`