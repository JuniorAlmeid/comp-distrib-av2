#!/bin/bash
export MSYS_NO_PATHCONV=1

echo "🧹 1. Limpando a casa..."
docker-compose down 2>/dev/null
rm -rf python_api ruby_api docker-compose.yml

echo "📁 2. Criando estruturas e arquivos..."
mkdir -p python_api ruby_api locust/resultados

# --- ARQUIVOS DO PYTHON ---
cat << 'EOF' > python_api/Dockerfile
FROM python:3.9-alpine
WORKDIR /app
RUN pip install flask redis beautifulsoup4 requests
COPY linkextractor.py .
CMD ["python", "linkextractor.py"]
EOF

cat << 'EOF' > python_api/linkextractor.py
import os, redis, requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

app = Flask(__name__)
redis_url = os.environ.get('REDIS_URL')
cache = redis.from_url(redis_url) if redis_url else None

@app.route('/api/links')
def links():
    url = request.args.get('url')
    if cache:
        try:
            cached = cache.get(url)
            if cached: return cached
        except: pass
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = [a.get('href') for a in soup.find_all('a') if a.get('href')]
        result = jsonify({"url": url, "links": links})
        if cache:
            try: cache.set(url, result.get_data(), ex=300)
            except: pass
        return result
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

# --- ARQUIVOS DO RUBY ---
cat << 'EOF' > ruby_api/Dockerfile
FROM ruby:3.1-alpine
RUN apk add --no-cache build-base patch zlib-dev libxml2-dev libxslt-dev
WORKDIR /app
COPY Gemfile .
RUN bundle install
COPY linkextractor.rb .
CMD ["ruby", "linkextractor.rb"]
EOF

cat << 'EOF' > ruby_api/Gemfile
source 'https://rubygems.org'
gem 'sinatra'
gem 'nokogiri'
gem 'webrick'
gem 'redis'
EOF

cat << 'EOF' > ruby_api/linkextractor.rb
require 'sinatra'
require 'open-uri'
require 'nokogiri'
require 'json'
require 'redis'

set :bind, '0.0.0.0'
set :port, 5000

redis_url = ENV['REDIS_URL']
cache = (redis_url && !redis_url.empty?) ? Redis.new(url: redis_url) : nil

get '/api/links' do
  url = params['url']
  if cache
    begin
      cached = cache.get(url)
      return cached if cached
    rescue
    end
  end
  begin
    doc = Nokogiri::HTML(URI.open(url, "User-Agent" => "Mozilla/5.0", :read_timeout => 10))
    links = doc.css('a').map { |a| a['href'] }.compact
    result = { url: url, links: links }.to_json
    if cache
      begin cache.setex(url, 300, result) rescue nil end
    end
    content_type :json
    result
  rescue => e
    status 400
    { error: e.message }.to_json
  end
end
EOF

# --- ARQUIVO DO LOCUST ---
cat << 'EOF' > locust/link_extractor.py
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
EOF

echo "🚀 3. Iniciando Matriz de Testes..."

USUARIOS=(30 60 90)
TEMPO_TESTE="1m"
SPAWN_RATE="10"

# Matriz: Nome | Pasta do Código | URL do Cache (Vazio = Sem Cache)
CENARIOS=(
    "python_semcache|python_api|"
    "python_comcache|python_api|redis://redis:6379"
    "ruby_semcache|ruby_api|"
    "ruby_comcache|ruby_api|redis://redis:6379"
)

for cenario_info in "${CENARIOS[@]}"; do
    IFS="|" read -r NOME_CENARIO PASTA_BUILD REDIS_URL <<< "$cenario_info"

    echo "================================================="
    echo " TESTANDO: $NOME_CENARIO"
    echo "================================================="

    # O Docker Compose agora vai compilar direto da pasta correta
    cat <<EOF > docker-compose.yml
version: '3'
services:
  api:
    build: ./${PASTA_BUILD}
    ports:
      - "5000:5000"
    environment:
      - REDIS_URL=$REDIS_URL
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  locust:
    image: locustio/locust
    volumes:
      - ./locust:/locust
    entrypoint: ["tail", "-f", "/dev/null"]
EOF

    docker-compose down 2>/dev/null
    docker-compose up -d api redis locust
    echo "Aguardando 10 segundos para os servidores subirem..."
    sleep 10

    for USERS in "${USUARIOS[@]}"; do
        echo "-> Atacando com $USERS usuários..."
        NOME_ARQUIVO="${NOME_CENARIO}_usr${USERS}"

        docker-compose exec -T locust locust \
            -f /locust/link_extractor.py \
            --host=http://api:5000 \
            --headless \
            -u $USERS \
            -r $SPAWN_RATE \
            --run-time $TEMPO_TESTE \
            --csv=/locust/resultados/$NOME_ARQUIVO
            
        echo "   ✅ $NOME_ARQUIVO.csv salvo!"
    done
done

echo "🎉 Todos os testes finalizados com sucesso!"
docker-compose down