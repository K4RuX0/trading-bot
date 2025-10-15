import subprocess
import re
import os
import numpy as np
import pandas as pd

def executar_backtest(fast_window, slow_window, risk_per_trade, stop_loss, take_profit, atr_multiplier, use_atr_stop_loss, output_filename):
    """Executa o backtest com os parâmetros especificados e retorna os resultados."""
    print(f"Executando backtest com: fast_window={fast_window}, slow_window={slow_window}, risk_per_trade={risk_per_trade}, stop_loss={stop_loss}, take_profit={take_profit}, atr_multiplier={atr_multiplier}, use_atr_stop_loss={use_atr_stop_loss}, output_filename={output_filename}")
    # Comando para executar o backtest (adapte ao seu projeto)
    # Obter o caminho para o executável do Python no ambiente virtual
    python_executable = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")  # Adaptação para Windows

    comando = [
        python_executable,  # Usar o Python do ambiente virtual
        "main.py",
        "--mode",
        "backtest",
        "--datafile",
        "data/sample_ohlcv.csv",
        "--fast_window",
        str(fast_window),
        "--slow_window",
        str(slow_window),
        "--risk_per_trade",
        str(risk_per_trade),
        "--stop_loss",
        str(stop_loss),
        "--take_profit",
        str(take_profit),
        "--atr_multiplier",
        str(atr_multiplier),
        "--output_filename", # Passa o nome do arquivo para o gráfico
        output_filename
    ]

    # Adiciona o argumento --use_atr_stop_loss se for True
    if use_atr_stop_loss:
        comando.append("--use_atr_stop_loss")

    try:
        # Execute o comando e capture a saída
        resultado = subprocess.run(comando, capture_output=True, text=True, check=True)
        saida = resultado.stdout
        erro = resultado.stderr

        # Imprimir a saída para debug
        print(f"Saída do main.py:\n{saida}")
        if erro:
            print(f"Erros do main.py:\n{erro}")

        # Imprimir o caminho do executável do Python
        print(f"Usando o executável do Python: {python_executable}")

        # Extrair os resultados da saída (use regex para encontrar os resultados)
        match_total_return = re.search(r"TOTAL_RETURN:\s*([-+]?\d*\.\d+|\d+)", saida)
        match_max_drawdown = re.search(r"MAX_DRAWDOWN:\s*([-+]?\d*\.\d+|\d+)", saida)
        match_sharpe_approx = re.search(r"SHARPE_APPROX:\s*([-+]?\d*\.\d+|\d+)", saida)
        match_n_trades = re.search(r"N_TRADES:\s*([-+]?\d*\.\d+|\d+)", saida)

        total_return = float(match_total_return.group(1)) if match_total_return else np.nan
        max_drawdown = float(match_max_drawdown.group(1)) if match_max_drawdown else np.nan
        sharpe_approx = float(match_sharpe_approx.group(1)) if match_sharpe_approx else np.nan
        n_trades = int(match_n_trades.group(1)) if match_n_trades else 0

        return total_return, max_drawdown, sharpe_approx, n_trades

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar main.py: {e}")
        print(f"Saída do erro:\n{e.stderr}")
        return np.nan, np.nan, np.nan, 0

def otimizar_parametros(num_combinations=200):
    """Otimiza os parâmetros da estratégia de trading."""
    # Definição dos intervalos dos parâmetros
    fast_window_range = (5, 30)
    slow_window_range = (30, 60)
    risk_per_trade_range = (0.005, 0.02)
    stop_loss_range = (0.01, 0.05)
    take_profit_range = (0.05, 0.15)
    atr_multiplier_range = (2.0, 4.0)
    use_atr_stop_loss_values = [True, False]

    # Criação do DataFrame para armazenar os resultados
    results_df = pd.DataFrame(columns=[
        "fast_window", "slow_window", "risk_per_trade", "stop_loss", "take_profit", "atr_multiplier", "use_atr_stop_loss",
        "total_return", "max_drawdown", "sharpe_approx", "n_trades"
    ])

    # Cria o diretório para salvar as curvas de capital, se não existir
    output_dir = "equity_curves"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Loop para testar diferentes combinações de parâmetros
    for i in range(num_combinations):
        print(f"Testando combinação: {i+1}/{num_combinations}")

        # Geração de parâmetros aleatórios dentro dos intervalos definidos
        fast_window = np.random.randint(fast_window_range[0], fast_window_range[1])
        slow_window = np.random.randint(slow_window_range[0], slow_window_range[1])
        risk_per_trade = np.random.uniform(risk_per_trade_range[0], risk_per_trade_range[1])
        stop_loss = np.random.uniform(stop_loss_range[0], stop_loss_range[1])
        take_profit = np.random.uniform(take_profit_range[0], take_profit_range[1])
        atr_multiplier = np.random.uniform(atr_multiplier_range[0], atr_multiplier_range[1])
        use_atr_stop_loss = np.random.choice(use_atr_stop_loss_values)

        # Nome do arquivo para a curva de capital
        output_filename = os.path.join(output_dir, f"equity_curve_{i+1}.png")

        # Executa o backtest com os parâmetros atuais
        total_return, max_drawdown, sharpe_approx, n_trades = executar_backtest(
            fast_window, slow_window, risk_per_trade, stop_loss, take_profit, atr_multiplier, use_atr_stop_loss, output_filename
        )

        # Adiciona os resultados ao DataFrame
        results_df = pd.concat([results_df, pd.DataFrame([{
            "fast_window": fast_window,
            "slow_window": slow_window,
            "risk_per_trade": risk_per_trade,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "atr_multiplier": atr_multiplier,
            "use_atr_stop_loss": use_atr_stop_loss,
            "total_return": total_return,
            "max_drawdown": max_drawdown,
            "sharpe_approx": sharpe_approx,
            "n_trades": n_trades
        }])], ignore_index=True)

    # Salva os resultados em um arquivo CSV
    results_df.to_csv("backtest_results.csv", index=False)
    print("Resultados salvos em backtest_results.csv")

if __name__ == "__main__":
    otimizar_parametros(num_combinations=200)