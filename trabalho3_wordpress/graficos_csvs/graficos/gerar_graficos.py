import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

PASTA_RESULTADOS = '../csvs'

# Extrai os dados dos 36 CSVs do Locust
def carregar_dados():
    dados = []
    if not os.path.exists(PASTA_RESULTADOS):
        print(f"Aviso: Pasta {PASTA_RESULTADOS} não encontrada.")
        return pd.DataFrame()

    for arquivo in os.listdir(PASTA_RESULTADOS):
        if arquivo.endswith('_stats.csv'):
            partes = arquivo.replace('_stats.csv', '').split('_')
            cenario = partes[0]
            instancias = int(partes[1].replace('inst', ''))
            usuarios = int(partes[2].replace('usr', ''))
            
            df = pd.read_csv(os.path.join(PASTA_RESULTADOS, arquivo))
            # Pega a linha "Aggregated" (linha final de totais do CSV do Locust)
            total_row = df[df['Name'] == 'Aggregated']
            if total_row.empty: continue
            total = total_row.iloc[0]
            
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

# 1. Gráficos Originais (Eixo X = Usuários, Barras = Instâncias 1, 2, 3)
def plotar_por_usuarios(df, metrica, titulo, y_label):
    cenarios = df['Cenario'].unique()
    for cenario in cenarios:
        dados_cenario = df[df['Cenario'] == cenario]
        if dados_cenario.empty: continue
        
        usuarios = sorted(dados_cenario['Usuarios'].unique())
        
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

# 2. Gráficos Originais (Eixo X = Cenários, Barras = Instâncias 1, 2, 3)
def plotar_por_cenarios(df, metrica, titulo, y_label):
    usuarios = df['Usuarios'].unique()
    cenarios_ordem = ['Leve', 'Medio', 'Pesado', 'Hibrido']
    
    for usr in usuarios:
        dados_usr = df[df['Usuarios'] == usr]
        if dados_usr.empty: continue
        
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

# 3. NOVA ESTRUTURA (Eixo X = Instâncias, Barras = Leve, Medio, Pesado, Hibrido)
def plotar_por_instancias(df, metrica, titulo, y_label):
    usuarios = df['Usuarios'].unique()
    instancias = [1, 2, 3]
    cenarios_ordem = ['Leve', 'Medio', 'Pesado', 'Hibrido']
    cores = ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c'] # Verde, Amarelo, Laranja, Vermelho

    for usr in usuarios:
        dados_usr = df[df['Usuarios'] == usr]
        if dados_usr.empty: continue
        
        val_leve = [pegar_valor_seguro(dados_usr[(dados_usr['Cenario'] == 'Leve') & (dados_usr['Instancias'] == inst)], metrica) for inst in instancias]
        val_medio = [pegar_valor_seguro(dados_usr[(dados_usr['Cenario'] == 'Medio') & (dados_usr['Instancias'] == inst)], metrica) for inst in instancias]
        val_pesado = [pegar_valor_seguro(dados_usr[(dados_usr['Cenario'] == 'Pesado') & (dados_usr['Instancias'] == inst)], metrica) for inst in instancias]
        val_hibrido = [pegar_valor_seguro(dados_usr[(dados_usr['Cenario'] == 'Hibrido') & (dados_usr['Instancias'] == inst)], metrica) for inst in instancias]

        x = np.arange(len(instancias))
        width = 0.2

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x - 1.5*width, val_leve, width, label='Leve', color=cores[0])
        ax.bar(x - 0.5*width, val_medio, width, label='Médio', color=cores[1])
        ax.bar(x + 0.5*width, val_pesado, width, label='Pesado', color=cores[2])
        ax.bar(x + 1.5*width, val_hibrido, width, label='Híbrido', color=cores[3])

        ax.set_ylabel(y_label, fontweight='bold')
        ax.set_xlabel('Quantidade de Instâncias (WordPress)', fontweight='bold')
        ax.set_title(f'{titulo} - {usr} Usuários', fontsize=14, pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{i} Instância(s)" for i in instancias])
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.tight_layout()
        # Salva com um nome ligeiramente diferente para não sobrescrever os anteriores
        plt.savefig(f'grafico_{metrica}_EixoInstancias_{usr}usr.png', dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == '__main__':
    print("Iniciando geração de gráficos do Trabalho 3...")
    df = carregar_dados()
    
    if not df.empty:
        # 8 Gráficos originais por Usuário
        plotar_por_usuarios(df, 'P95', 'P95 Tempo de Resposta (ms)', 'Tempo (ms)')
        plotar_por_usuarios(df, 'Taxa_Falha', 'Taxa de Erros (%)', 'Falhas (%)')
        
        # 6 Gráficos originais por Cenário
        plotar_por_cenarios(df, 'P95', 'P95 Tempo de Resposta (ms)', 'Tempo (ms)')
        plotar_por_cenarios(df, 'Taxa_Falha', 'Taxa de Erros (%)', 'Falhas (%)')

        # 6 Gráficos NOVOS por Instâncias
        plotar_por_instancias(df, 'P95', 'P95 Tempo de Resposta (ms)', 'Tempo (ms)')
        plotar_por_instancias(df, 'Taxa_Falha', 'Taxa de Erros (%)', 'Falhas (%)')
        
        print("Sucesso! Os 20 gráficos foram gerados.")
    else:
        print("Nenhum dado encontrado para gerar gráficos.")