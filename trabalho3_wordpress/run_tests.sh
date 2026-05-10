#!/bin/bash
export MSYS_NO_PATHCONV=1

CENARIOS=("leve" "medio" "pesado" "hibrido")
INSTANCIAS=(1 2 3)
USUARIOS=(100 155 158) # Seus usuários definidos
TEMPO_TESTE="2m"
SPAWN_RATE="3"

# Garante que todos os contêineres estão rodando antes de começar
docker-compose up -d

for INSTANCIA in "${INSTANCIAS[@]}"; do
    echo "========================================="
    echo "CONFIGURANDO PARA $INSTANCIA INSTÂNCIA(S)"
    echo "========================================="
    
    # Restaura o Nginx para 3 instâncias por padrão (remove comentários)
    sed -i 's/#server wordpress/server wordpress/g' nginx.conf

    if [ "$INSTANCIA" -eq 1 ]; then
        sed -i 's/server wordpress2;/#server wordpress2;/g' nginx.conf
        sed -i 's/server wordpress3;/#server wordpress3;/g' nginx.conf
        docker-compose stop wordpress2 wordpress3
    elif [ "$INSTANCIA" -eq 2 ]; then
        sed -i 's/server wordpress3;/#server wordpress3;/g' nginx.conf
        docker-compose start wordpress2
        docker-compose stop wordpress3
    else
        docker-compose start wordpress2 wordpress3
    fi

    # Reinicia o Nginx para aplicar as regras
    docker-compose restart nginx
    sleep 5 # Dá um tempo pro Nginx e o WP respirarem

    for CENARIO in "${CENARIOS[@]}"; do
        for USERS in "${USUARIOS[@]}"; do
            echo "-> Rodando: $CENARIO | Instâncias: $INSTANCIA | Usuários: $USERS"
            NOME_ARQUIVO="${CENARIO}_inst${INSTANCIA}_usr${USERS}"
            
            # Roda o Locust via Docker apontando para as NOVAS PASTAS
            docker-compose exec -T locust locust \
                -f /locust/codigos_carga/${CENARIO}.py \
                --host=http://nginx \
                --headless \
                -u $USERS \
                -r $SPAWN_RATE \
                --run-time $TEMPO_TESTE \
                --csv=/locust/csvs/$NOME_ARQUIVO
            
            echo "   Concluído: $NOME_ARQUIVO.csv salvo em locust/csvs."
        done
    done
done

echo "Todos os testes finalizados com sucesso! Vai beber uma água."