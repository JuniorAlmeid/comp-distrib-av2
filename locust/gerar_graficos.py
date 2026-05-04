import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

PASTA_RESULTADOS = './resultados'

# Extrai os dados dos 36 CSVs do Locust
def carregar_dados():
    dados = []
    for arquivo in os.listdir(PASTA_RESULTADOS):
        if arquivo.endswith('_stats.csv'):
            partes = arquivo.replace('_stats.csv', '').split('_')
            cenario = partes[0]
            instancias = int(partes[1].replace('inst', ''))
            usuarios = int(partes[2].replace('usr', ''))
            
            df = pd.read_csv(os.path.join(PASTA_RESULTADOS, arquivo))
            # Pega a linha "Aggregated" (linha final de totais do CSV do Locust)
            total = df[df['Name'] == 'Aggregated'].iloc[0]
            
            p95 = total['95%']
            req_totais = total['Request Count']
            falhas = total['Failure Count']
            taxa_falha = (falhas / req_totais * 100) if req_totais > 0 else 0
            
            dados.append({
                'Cenario': cenario.capitalize(),
                'Instancias': instancias,
                'Usuarios': usuarios,
                'P95': p95,
                'Taxa_Falha': taxa_falha
            })
    return pd.DataFrame(dados)

# Gera os gráficos por USUÁRIO (Eixo X = Usuários, Barras = Instâncias 1, 2, 3)
def plotar_por_usuarios(df, metrica, titulo, y_label):
    cenarios = df['Cenario'].unique()
    for cenario in cenarios:
        dados_cenario = df[df['Cenario'] == cenario]
        
        usuarios = sorted(dados_cenario['Usuarios'].unique())
        inst1 = [dados_cenario[(dados_cenario['Usuarios'] == u) & (dados_cenario['Instancias'] == 1)][metrica].values[0] for u in usuarios]
        inst2 = [dados_cenario[(dados_cenario['Usuarios'] == u) & (dados_cenario['Instancias'] == 2)][metrica].values[0] for u in usuarios]
        inst3 = [dados_cenario[(dados_cenario['Usuarios'] == u) & (dados_cenario['Instancias'] == 3)][metrica].values[0] for u in usuarios]

        x = np.arange(len(usuarios))
        width = 0.25

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(x - width, inst1, width, label='1 Instância', color='#a8c8e6')
        ax.bar(x, inst2, width, label='2 Instâncias', color='#f6dfba')
        ax.bar(x + width, inst3, width, label='3 Instâncias', color='#f2b7b5')

        ax.set_ylabel(y_label)
        ax.set_xlabel('Número de Usuários')
        ax.set_title(f'{titulo} - Cenário {cenario}')
        ax.set_xticks(x)
        ax.set_xticklabels(usuarios)
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(f'grafico_{metrica}_Cenario_{cenario}.png')
        plt.close()

# Gera os gráficos por INSTÂNCIA (Eixo X = Instâncias, Barras = Cenários)
def plotar_por_instancias(df, metrica, titulo, y_label):
    usuarios = df['Usuarios'].unique()
    for usr in usuarios:
        dados_usr = df[df['Usuarios'] == usr]
        
        instancias = sorted(dados_usr['Instancias'].unique())
        c_leve = [dados_usr[(dados_usr['Instancias'] == i) & (dados_usr['Cenario'] == 'Leve')][metrica].values[0] for i in instancias]
        c_medio = [dados_usr[(dados_usr['Instancias'] == i) & (dados_usr['Cenario'] == 'Medio')][metrica].values[0] for i in instancias]
        c_pesado = [dados_usr[(dados_usr['Instancias'] == i) & (dados_usr['Cenario'] == 'Pesado')][metrica].values[0] for i in instancias]
        c_hibrido = [dados_usr[(dados_usr['Instancias'] == i) & (dados_usr['Cenario'] == 'Hibrido')][metrica].values[0] for i in instancias]

        x = np.arange(len(instancias))
        width = 0.2

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.bar(x - 1.5*width, c_leve, width, label='Leve', color='#c6e0b4')
        ax.bar(x - 0.5*width, c_medio, width, label='Médio', color='#bdd7ee')
        ax.bar(x + 0.5*width, c_pesado, width, label='Pesado', color='#ffe699')
        ax.bar(x + 1.5*width, c_hibrido, width, label='Híbrido', color='#f8cbad')

        ax.set_ylabel(y_label)
        ax.set_xlabel('Número de Instâncias')
        ax.set_title(f'{titulo} - {usr} Usuários')
        ax.set_xticks(x)
        ax.set_xticklabels(instancias)
        ax.legend()

        plt.tight_layout()
        plt.savefig(f'grafico_{metrica}_Instancias_{usr}usr.png')
        plt.close()

if __name__ == '__main__':
    df = carregar_dados()
    
    # 8 Gráficos por Usuário (4 cenários x 2 métricas)
    plotar_por_usuarios(df, 'P95', 'P95 Tempo de Resposta (ms)', 'Tempo (ms)')
    plotar_por_usuarios(df, 'Taxa_Falha', 'Taxa de Erros (%)', 'Falhas (%)')
    
    # 6 Gráficos por Instância (3 cargas de usuários x 2 métricas)
    plotar_por_instancias(df, 'P95', 'P95 Tempo de Resposta (ms)', 'Tempo (ms)')
    plotar_por_instancias(df, 'Taxa_Falha', 'Taxa de Erros (%)', 'Falhas (%)')
    
    print("Os 14 gráficos foram gerados e salvos na pasta raiz!")