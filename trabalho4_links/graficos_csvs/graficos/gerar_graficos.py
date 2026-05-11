import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

PASTA_RESULTADOS = '../resultados'

# Extrai os dados dos 12 CSVs do Locust (Trabalho 4)
def carregar_dados():
    dados = []
    if not os.path.exists(PASTA_RESULTADOS):
        return pd.DataFrame()

    for arquivo in os.listdir(PASTA_RESULTADOS):
        if arquivo.endswith('_stats.csv'):
            nome_base = arquivo.replace('_stats.csv', '')
            partes = nome_base.split('_usr')
            cenario = partes[0]
            usuarios = int(partes[1])
            
            df = pd.read_csv(os.path.join(PASTA_RESULTADOS, arquivo))
            total_row = df[df['Name'] == 'Aggregated']
            if total_row.empty: continue
            total = total_row.iloc[0]
            
            p95 = total['95%']
            req_totais = total['Request Count']
            falhas = total['Failure Count']
            taxa_falha = (falhas / req_totais * 100) if req_totais > 0 else 0
            
            dados.append({
                'Cenario': cenario,
                'Usuarios': usuarios,
                'P95': p95,
                'Taxa_Falha': taxa_falha
            })
    return pd.DataFrame(dados)

# Função de segurança para evitar o erro "IndexError: size 0"
def pegar_valor_seguro(df_filtrado, metrica):
    valores = df_filtrado[metrica].values
    return valores[0] if len(valores) > 0 else 0

# 1. Gera 8 Gráficos: Isolados por Cenário (Eixo X = Usuários)
def plotar_por_cenarios_isolados(df, metrica, titulo, y_label):
    cenarios = ['python_semcache', 'python_comcache', 'ruby_semcache', 'ruby_comcache']
    for cenario in cenarios:
        dados_cenario = df[df['Cenario'] == cenario]
        if dados_cenario.empty: continue
        
        usuarios = sorted(df['Usuarios'].unique())
        valores = [pegar_valor_seguro(dados_cenario[dados_cenario['Usuarios'] == u], metrica) for u in usuarios]

        x = np.arange(len(usuarios))
        width = 0.5

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(x, valores, width, color='#3498db')

        ax.set_ylabel(y_label, fontweight='bold')
        ax.set_xlabel('Número de Usuários')
        ax.set_title(f'{titulo} - Cenário {cenario.upper()}')
        ax.set_xticks(x)
        ax.set_xticklabels([f"{u} Usr" for u in usuarios])
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(f'grafico_{metrica}_Cenario_{cenario}.png')
        plt.close()

# 2. Gera 6 Gráficos: Comparativos por Usuários (Eixo X = Cenários)
def plotar_por_usuarios_comparativo(df, metrica, titulo, y_label):
    usuarios = sorted(df['Usuarios'].unique())
    cenarios_ordem = ['python_semcache', 'python_comcache', 'ruby_semcache', 'ruby_comcache']
    labels = ['Py (Sem Cache)', 'Py (Com Cache)', 'Rb (Sem Cache)', 'Rb (Com Cache)']
    cores = ['#e74c3c', '#2ecc71', '#9b59b6', '#3498db']
    
    for usr in usuarios:
        dados_usr = df[df['Usuarios'] == usr]
        if dados_usr.empty: continue
        
        valores = [pegar_valor_seguro(dados_usr[dados_usr['Cenario'] == c], metrica) for c in cenarios_ordem]

        x = np.arange(len(cenarios_ordem))
        width = 0.6

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(x, valores, width, color=cores)

        ax.set_ylabel(y_label, fontweight='bold')
        ax.set_xlabel('Cenários (Linguagem e Cache)')
        ax.set_title(f'{titulo} - {usr} Usuários Simultâneos')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        plt.tight_layout()
        plt.savefig(f'grafico_{metrica}_Cenarios_{usr}usr.png')
        plt.close()

if __name__ == '__main__':
    print("Extraindo dados dos CSVs do Link Extractor...")
    df = carregar_dados()
    
    if not df.empty:
        # Gera os 8 Gráficos da primeira parte
        plotar_por_cenarios_isolados(df, 'P95', 'P95 Tempo de Resposta (ms)', 'Tempo (ms)')
        plotar_por_cenarios_isolados(df, 'Taxa_Falha', 'Taxa de Erros (%)', 'Falhas (%)')
        
        # Gera os 6 Gráficos da segunda parte
        plotar_por_usuarios_comparativo(df, 'P95', 'P95 Tempo de Resposta (ms)', 'Tempo (ms)')
        plotar_por_usuarios_comparativo(df, 'Taxa_Falha', 'Taxa de Erros (%)', 'Falhas (%)')
        
        print("Os 14 gráficos foram gerados e salvos com sucesso na mesma estrutura do T3!")
    else:
        print("Erro: Nenhum dado foi encontrado na pasta 'resultados'.")