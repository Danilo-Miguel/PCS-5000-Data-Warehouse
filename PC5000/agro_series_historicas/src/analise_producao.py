import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Base do projeto (diretório pai da pasta src)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

def transformar_para_long(arquivo, nome_coluna_valor):
    print(f"Lendo arquivo em: {arquivo}")

    df = pd.read_excel(arquivo, header=None)

    anos = df.iloc[3, 1:].tolist()
    produtos = df.iloc[4, 1:].tolist()
    estados = df.iloc[5:, 0].tolist()
    valores = df.iloc[5:, 1:].values

    df_long = pd.DataFrame(columns=["Estado", "Ano", "Produto", nome_coluna_valor])

    for i, estado in enumerate(estados):
        for j, valor in enumerate(valores[i]):
            df_long.loc[len(df_long)] = {
                "Estado": estado,
                "Ano": int(anos[j]),
                "Produto": produtos[j],
                nome_coluna_valor: pd.to_numeric(valor, errors='coerce')
            }

    print(df_long.head())
    return df_long

# Corrigindo os caminhos corretamente
arquivo_area_colhida = os.path.join(OUTPUT_DIR, "area_colhida.xlsx")
arquivo_quantidade_produzida = os.path.join(OUTPUT_DIR, "quantidade_produzida_toneladas.xlsx")
arquivo_rendimento_medio = os.path.join(OUTPUT_DIR, "rendimento_médio_da_produção.xlsx")

# Transforma os arquivos em formato longo
df_area_colhida_long = transformar_para_long(arquivo_area_colhida, "Area_colhida_ha")
df_area_colhida_long.to_csv(os.path.join(OUTPUT_DIR, "area_colhida_long.csv"), index=False)

df_quantidade_produzida_long = transformar_para_long(arquivo_quantidade_produzida, "Quantidade_produzida_t")
df_quantidade_produzida_long.to_csv(os.path.join(OUTPUT_DIR, "quantidade_produzida_long.csv"), index=False)

df_rendimento_medio_long = transformar_para_long(arquivo_rendimento_medio, "Rendimento_medio_kg_ha")
df_rendimento_medio_long.to_csv(os.path.join(OUTPUT_DIR, "rendimento_medio_long.csv"), index=False)

# Unificação
def unificar_dataframes(df1, df2, df3):
    df_unificado = pd.merge(df1, df2, on=["Estado", "Ano", "Produto"], how="outer")
    df_unificado = pd.merge(df_unificado, df3, on=["Estado", "Ano", "Produto"], how="outer")
    return df_unificado

df_unificado = unificar_dataframes(df_area_colhida_long, df_quantidade_produzida_long, df_rendimento_medio_long)
df_unificado.to_csv(os.path.join(OUTPUT_DIR, "dados_unificados.csv"), index=False)
print("✅ Dados unificados salvos em output/dados_unificados.csv")

# Preenche NaNs
df_unificado.fillna(0, inplace=True)

# Gráficos
sns.set(style="whitegrid")

# Gráfico 1: Evolução da área colhida de soja no Acre
estado_foco = "Acre"
df_acre = df_unificado[(df_unificado["Estado"] == estado_foco) & (df_unificado["Produto"].str.contains("Soja", na=False))]

plt.figure(figsize=(10,6))
sns.lineplot(data=df_acre, x="Ano", y="Area_colhida_ha", marker="o")
plt.title(f"Evolução da Área Colhida de Soja em {estado_foco}")
plt.ylabel("Área Colhida (ha)")
plt.xlabel("Ano")
plt.tight_layout()
plt.show()

# Gráfico 2: Dispersão da soja - Área vs Produção
df_soja = df_unificado[df_unificado["Produto"].str.contains("Soja", na=False)]

plt.figure(figsize=(10,6))
sns.scatterplot(data=df_soja, x="Area_colhida_ha", y="Quantidade_produzida_t", hue="Estado", alpha=0.7)
plt.title("Relação entre Área Colhida e Quantidade Produzida (Soja)")
plt.xlabel("Área Colhida (ha)")
plt.ylabel("Quantidade Produzida (t)")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2)
plt.tight_layout()
plt.show()

# Gráfico 3: Boxplot do rendimento médio
plt.figure(figsize=(12,6))
sns.boxplot(data=df_soja, x="Ano", y="Rendimento_medio_kg_ha")
plt.title("Distribuição do Rendimento Médio de Soja por Ano")
plt.xlabel("Ano")
plt.ylabel("Rendimento Médio (kg/ha)")
plt.tight_layout()
plt.show()

# Novo bloco de gráficos para análise de crescimento por estado

# Filtra apenas soja
df_soja = df_unificado[df_unificado["Produto"].str.contains("Soja", na=False)]

# Agrupa a produção total por estado e ano
df_estado_ano = df_soja.groupby(["Estado", "Ano"])["Quantidade_produzida_t"].sum().reset_index()

# Pivot para colocar anos como colunas e facilitar cálculo de crescimento
df_pivot = df_estado_ano.pivot(index="Estado", columns="Ano", values="Quantidade_produzida_t")

# Remove estados com dados faltantes
df_pivot = df_pivot.dropna()

# Calcula crescimento percentual dos últimos 10 anos
anos_ordenados = sorted(df_pivot.columns)
ano_inicio = anos_ordenados[0]
ano_fim = anos_ordenados[-1]
df_pivot["Crescimento_percentual"] = ((df_pivot[ano_fim] - df_pivot[ano_inicio]) / df_pivot[ano_inicio]) * 100

# Ordena do maior crescimento ao menor
df_crescimento = df_pivot.sort_values(by="Crescimento_percentual", ascending=False)

# Gráfico: Top 10 estados que mais cresceram
plt.figure(figsize=(12,6))
sns.barplot(data=df_crescimento.head(10).reset_index(), x="Crescimento_percentual", y="Estado", palette="Greens_r")
plt.title("Top 10 Estados que Mais Cresceram na Produção de Soja (últimos 10 anos)")
plt.xlabel("Crescimento Percentual (%)")
plt.ylabel("Estado")
plt.tight_layout()
plt.show()

# Gráfico: Top 10 estados que menos cresceram ou diminuíram
plt.figure(figsize=(12,6))
sns.barplot(data=df_crescimento.tail(10).reset_index(), x="Crescimento_percentual", y="Estado", palette="Reds")
plt.title("Estados com Menor Crescimento ou Queda na Produção de Soja (últimos 10 anos)")
plt.xlabel("Crescimento Percentual (%)")
plt.ylabel("Estado")
plt.tight_layout()
plt.show()

# Gráfico: Evolução da produção total por região ao longo dos anos
# Mapeia estados para regiões (simplificado)
regioes = {
    "AC": "Norte", "AM": "Norte", "AP": "Norte", "PA": "Norte", "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste", "PB": "Nordeste", "PE": "Nordeste",
    "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MT": "Centro-Oeste", "MS": "Centro-Oeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul"
}
df_estado_ano["Regiao"] = df_estado_ano["Estado"].map(regioes)

df_regiao_ano = df_estado_ano.groupby(["Regiao", "Ano"])["Quantidade_produzida_t"].sum().reset_index()

plt.figure(figsize=(12,6))
sns.lineplot(data=df_regiao_ano, x="Ano", y="Quantidade_produzida_t", hue="Regiao", marker="o")
plt.title("Evolução da Produção de Soja por Região")
plt.xlabel("Ano")
plt.ylabel("Produção (toneladas)")
plt.legend(title="Região")
plt.tight_layout()
plt.show()

df_soja["Produtividade"] = df_soja["Quantidade_produzida_t"] / df_soja["Area_colhida_ha"]
produtividade_media = df_soja.groupby("Estado")["Produtividade"].mean().sort_values(ascending=False)


# Gráfico de barras
plt.figure(figsize=(12,6))
produtividade_media.plot(kind="bar", color="skyblue")
plt.title("Produtividade Média de Soja por Estado (t/ha)")
plt.xlabel("Estado")
plt.ylabel("Toneladas por hectare")
plt.tight_layout()
plt.show()
