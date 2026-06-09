import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

# ── Configurações ──────────────────────────────────────────────────────────────
DATA_DIR   = "."              # pasta onde estão os CSVs
VLIM       = 19.9             # limite de tensão em módulo (V)
COL_V      = "Voltage (V)"    # nome da coluna de tensão no CSV
COL_I      = "Current (A)"    # nome da coluna de corrente no CSV

# Descrição de cada lâmina: (arquivo_A, label_A, arquivo_B, label_B)
LAMINAS = {
    1: ("lamina1_xx.csv", "XX", "lamina1_yy.csv", "YY"),
    2: ("lamina2_xx.csv", "XX", "lamina2_yy.csv", "YY"),
    3: ("lamina3_xx.csv", "XX", "lamina3_yy.csv", "YY"),
    4: ("lamina4_xy1.csv", "XY1", "lamina4_xy2.csv", "XY2"),
}

CORES = {"A": "#1f77b4", "B": "#d62728"}   # azul / vermelho

# ── Funções auxiliares ─────────────────────────────────────────────────────────
def carregar_csv(caminho: str) -> pd.DataFrame:
    """Lê o CSV, filtra |V| < 19.9 V e retorna DataFrame limpo."""
    df = pd.read_csv(caminho)
    df.columns = df.columns.str.strip()

    if COL_V not in df.columns or COL_I not in df.columns:
        raise ValueError(
            f"Arquivo '{caminho}' não possui colunas '{COL_V}' e '{COL_I}'.\n"
            f"Colunas encontradas: {list(df.columns)}"
        )

    df = df[[COL_V, COL_I]].dropna()
    df = df.sort_values(COL_V).reset_index(drop=True)

    dentro = df[df[COL_V].abs() < VLIM]
    abaixo = df[df[COL_V] <= -VLIM]
    acima  = df[df[COL_V] >=  VLIM]

    partes = [dentro]
    if not abaixo.empty:
        partes.insert(0, abaixo.loc[[abaixo[COL_I].abs().idxmin()]])
    if not acima.empty:
        partes.append(acima.loc[[acima[COL_I].abs().idxmin()]])

    df = pd.concat(partes).reset_index(drop=True)
    df[COL_I] = df[COL_I] * 1000   # A → mA
    return df


def plotar_lamina(num: int, arq_a: str, lbl_a: str, arq_b: str, lbl_b: str):
    """Gera e salva o gráfico VxI de uma lâmina."""
    caminho_a = os.path.join(DATA_DIR, arq_a)
    caminho_b = os.path.join(DATA_DIR, arq_b)

    fig, ax = plt.subplots(figsize=(8, 5))

    for caminho, label, cor_key in [
        (caminho_a, lbl_a, "A"),
        (caminho_b, lbl_b, "B"),
    ]:
        if not os.path.exists(caminho):
            print(f"  [AVISO] Arquivo não encontrado: {caminho}")
            continue
        df = carregar_csv(caminho)
        ax.plot(df[COL_V], df[COL_I], label=label,
                color=CORES[cor_key], linewidth=1.8, marker="o",
                markersize=3, markerfacecolor="white")

    # linhas de referência em 0
    ax.axhline(0, color="gray", linewidth=0.7, linestyle="--")
    ax.axvline(0, color="gray", linewidth=0.7, linestyle="--")

    ax.set_title(f"Curva I×V — Lâmina {num}", fontsize=14, fontweight="bold")
    ax.set_xlabel("Tensão (V)", fontsize=12)
    ax.set_ylabel("Corrente (mA)", fontsize=12)
    ax.legend(fontsize=11, framealpha=0.9)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.margins(0.05)

    saida = f"lamina{num}_vxi.png"
    fig.tight_layout()
    fig.savefig(saida, dpi=150)
    print(f"  Salvo: {saida}")
    plt.close(fig)


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Gerando gráficos V×I (corte em |V| < {VLIM} V)...\n")
    for num, (arq_a, lbl_a, arq_b, lbl_b) in LAMINAS.items():
        print(f"Lâmina {num}: {arq_a}  +  {arq_b}")
        plotar_lamina(num, arq_a, lbl_a, arq_b, lbl_b)
    print("\nConcluído! Verifique os arquivos lamina*_vxi.png na pasta atual.")