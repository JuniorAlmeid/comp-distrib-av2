import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

PASTA_RESULTADOS = '../csvs'

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

# Função de segurança para evitar o erro "IndexError: size 0"
def pegar_valor_seguro(df_filtrado, metrica):
    valores = df_filtrado[metrica].values
    return valores[0] if len(valores) > 0 else 0

# Gera os gráficos por USUÁRIO (Eixo X = Usuários, Barras = Instâncias 1, 2, 3)
def plotar_por_usuarios(df, metrica, titulo, y_label):
    cenarios = df['Cenario'].unique()
    for cenario in cenarios:
        dados_cenario = df[df['Cenario'] == cenario]
        
        usuarios = sorted(dados_cenario['Usuarios'].unique())
        
        # Agora usamos a função segura em vez de chamar .values[0] direto
        inst1 = [pegar_valor_seguro(dados_cenario[(dados_cenario['Usuarios'] == u) & (dados_cenario['Instancias'] == 1)], metrica) for u in usuarios]
        inst2 = [pegar_valor_seguro(dados_cenario[(dados_cenario['Usuarios'] == u) & (dados_cenario['Instancias'] == 2)], metrica) for u in usuarios]
        inst3 = [pegar_valor_seguro(dados_cenario[(dados_cenario['Usuarios'] == u) & (dados_cenario['Instancias'] == 3)], metrica) for u in usuarios]

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

# NOVA ESTRUTURA: Eixo X = Cenários, Barras = Instâncias 1, 2, 3
def plotar_por_cenarios(df, metrica, titulo, y_label):
    usuarios = df['Usuarios'].unique()
    cenarios_ordem = ['Leve', 'Medio', 'Pesado', 'Hibrido']
    
    for usr in usuarios:
        dados_usr = df[df['Usuarios'] == usr]
        
        inst1 = [pegar_valor_seguro(dados_usr[(dados_usr['Cenario'] == c) & (dados_usr['Instancias'] == 1)], metrica) for c in cenarios_ordem]
        inst2 = [pegar_valor_seguro(dados_usr[(dados_usr['Cenario'] == c) & (dados_usr['Instancias'] == 2)], metrica) for c in cenarios_ordem]
        inst3 = [pegar_valor_seguro(dados_usr[(dados_usr['Cenario'] == c) & (dados_usr['Instancias'] == 3)], metrica) for c in cenarios_ordem]

        x = np.arange(len(cenarios_ordem))
        width = 0.25

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.bar(x - width, inst1, width, label='1 Instância', color='#a8c8e6')
        ax.bar(x, inst2, width, label='2 Instâncias', color='#f6dfba')
        ax.bar(x + width, inst3, width, label='3 Instâncias', color='#f2b7b5')

        ax.set_ylabel(y_label)
        ax.set_xlabel('Cenários')
        ax.set_title(f'{titulo} - {usr} Usuários')
        ax.set_xticks(x)
        ax.set_xticklabels(cenarios_ordem)
        ax.legend()

        plt.tight_layout()
        plt.savefig(f'grafico_{metrica}_Cenarios_{usr}usr.png')
        plt.close()

if __name__ == '__main__':
    df = carregar_dados()
    
    # 8 Gráficos por Usuário
    plotar_por_usuarios(df, 'P95', 'P95 Tempo de Resposta (ms)', 'Tempo (ms)')
    plotar_por_usuarios(df, 'Taxa_Falha', 'Taxa de Erros (%)', 'Falhas (%)')
    
    # 6 Gráficos por Cenário (Nova estrutura pedida)
    plotar_por_cenarios(df, 'P95', 'P95 Tempo de Resposta (ms)', 'Tempo (ms)')
    plotar_por_cenarios(df, 'Taxa_Falha', 'Taxa de Erros (%)', 'Falhas (%)')
    
    print("Os 14 gráficos foram gerados e salvos com sucesso na nova estrutura!")