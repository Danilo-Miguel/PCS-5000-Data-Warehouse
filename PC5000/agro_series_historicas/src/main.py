import pandas as pd
import os
base_dir = os.path.dirname(os.path.abspath(__file__))

# Caminho da planilha original
arquivo_origem = os.path.join(base_dir, "../data/tabela1612.xlsx")
pasta_saida = os.path.join(base_dir, "../output")

# Cria pasta de saída se não existir
os.makedirs(pasta_saida, exist_ok=True)

# Carrega os nomes das abas
abas = pd.ExcelFile(arquivo_origem).sheet_names
print("Abas encontradas:", abas)

# Itera pelas abas e salva como planilha separada
for aba in abas:
    print(f"Processando aba: {aba}")
    df = pd.read_excel(arquivo_origem, sheet_name=aba)
    nome_limpo = aba.strip().lower().replace(" ", "_")
    caminho_saida = os.path.join(pasta_saida, f"{nome_limpo}.xlsx")
    df.to_excel(caminho_saida, index=False)

print("✅ Abas separadas com sucesso!")
