import argparse
import logging
import pandas as pd
import pandas_ta as ta  # Importa a biblioteca pandas_ta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

def load_data(datafile):
    """
    Carrega os dados do arquivo CSV.
    """
    try:
        df = pd.read_csv(datafile)
        logger.info(f"Dados carregados do arquivo: {datafile}")
        return df
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {datafile}")
        return None
    except Exception as e:
        logger.error(f"Erro ao carregar o arquivo: {e}")
        return None

def initialize_portfolio(initial_cash):
    """
    Inicializa o portfólio com o valor inicial em dinheiro.
    """
    return {'cash': initial_cash, 'positions': []}

def calculate_position_size(portfolio, price, position_size_percentage):
    """
    Calcula o tamanho da posição com base no dinheiro disponível no portfólio e na porcentagem desejada.
    """
    cash = portfolio['cash']
    position_size = (cash * position_size_percentage) / price
    return position_size

def execute_trade(portfolio, signal, price, index):
    """
    Executa a ordem de compra ou venda, atualizando o portfólio.
    """
    if signal == 'BUY':
        position_size = calculate_position_size(portfolio, price, position_size_percentage)
        portfolio['cash'] -= position_size * price
        portfolio['positions'].append({'index': index, 'price': price, 'size': position_size})
        logger.info(f"Compra: {position_size} unidades a {price}")
    elif signal == 'SELL':
        if portfolio['positions']:
            position = portfolio['positions'].pop()
            portfolio['cash'] += position['size'] * price
            logger.info(f"Venda: Posição fechada a {price}")
        else:
            logger.warning("Não há posições para vender.")

def get_signal(df, index, oversold, overbought, rsi_length):
    """
    Gera sinais de negociação com base no RSI.
    """
    if index < rsi_length:
        return 'HOLD'  # Não há dados suficientes para calcular o RSI

    rsi_series = ta.rsi(df['close'], length=rsi_length)
    if index >= len(rsi_series):
        return 'HOLD'  # Índice fora dos limites da série RSI

    rsi = rsi_series.loc[index]

    if pd.isna(rsi):
        return 'HOLD'  # Se o RSI for NaN, retorna HOLD

    if rsi < oversold:
        return 'BUY'
    elif rsi > overbought:
        return 'SELL'
    else:
        return 'HOLD'

def run_paper_trading(df, initial_cash, oversold=30, overbought=70, rsi_length=14, position_size_percentage=0.1, stop_loss_percentage=0.05, take_profit_percentage=0.15):
    """
    Executa a simulação de negociação em modo paper com RSI, stop loss e take profit.
    """
    portfolio = initialize_portfolio(initial_cash)
    logger.info(f"Starting cash: {portfolio['cash']}")

    # Calcula o RSI
    df['rsi'] = ta.rsi(df['close'], length=rsi_length)

    for index, row in df.iterrows():
        price = row['close']
        signal = get_signal(df, index, oversold, overbought, rsi_length)

        logger.info(f"Índice: {index}, Sinal: {signal}, Preço: {price:.2f}, RSI: {row['rsi']:.2f}")

        # Verifica se há posições abertas para aplicar stop loss ou take profit
        for position in list(portfolio['positions']):  # Itera sobre uma cópia da lista
            if price <= position['price'] * (1 - stop_loss_percentage):
                # Stop Loss
                logger.info(f"Stop loss acionado! Venda: Posição fechada a {price:.2f} (Stop Loss)")
                portfolio['cash'] += position['size'] * price
                portfolio['positions'].remove(position)  # Remove a posição da lista original
            elif price >= position['price'] * (1 + take_profit_percentage):
                # Take Profit
                logger.info(f"Take profit acionado! Venda: Posição fechada a {price:.2f} (Take Profit)")
                portfolio['cash'] += position['size'] * price
                portfolio['positions'].remove(position)  # Remove a posição da lista original

        if signal == 'BUY':
            # Calcula o tamanho da posição com base em uma porcentagem do capital
            available_cash = portfolio['cash']
            if available_cash > 0:
                position_size = calculate_position_size(portfolio, price, position_size_percentage)
                if position_size > 0:
                    cost = position_size * price
                    if cost <= available_cash:  # Garante que há dinheiro suficiente
                        portfolio['cash'] -= cost
                        portfolio['positions'].append({'index': index, 'price': price, 'size': position_size})
                        logger.info(f"Compra: {position_size:.2f} unidades a {price:.2f}, Custo: {cost:.2f}")
                    else:
                        logger.warning("Dinheiro insuficiente para comprar a posição completa.")
                else:
                    logger.warning("Tamanho da posição calculado é zero ou negativo.")
            else:
                logger.warning("Não há dinheiro disponível para comprar.")

        elif signal == 'SELL':
            # Vende todas as posições abertas
            total_profit = 0
            while portfolio['positions']:
                position = portfolio['positions'].pop(0)  # Remove a primeira posição
                profit = (price - position['price']) * position['size']
                total_profit += profit
                portfolio['cash'] += position['size'] * price
                logger.info(f"Venda: Posição fechada a {price:.2f}, Lucro: {profit:.2f}")
            logger.info(f"Venda total: Lucro total das posições vendidas: {total_profit:.2f}")

        # Calcula o valor das posições em aberto
        open_positions_value = sum(pos['size'] * price for pos in portfolio['positions'])

        # Calcula o valor total do portfólio
        current_portfolio_value = portfolio['cash'] + open_positions_value

        logger.info(f"Current portfolio value: {current_portfolio_value:.2f}, Cash: {portfolio['cash']:.2f}, Open Positions Value: {open_positions_value:.2f}")

    # Finalização da sessão
    logger.info(f"Paper session finished. Cash: {portfolio['cash']:.2f}, positions: {[pos['index'] for pos in portfolio['positions']]}, Final portfolio value: {current_portfolio_value:.2f}")


def main(mode, datafile, initial_cash=10000, oversold=30, overbought=70, rsi_length=14, position_size_percentage=0.1, stop_loss_percentage=0.05, take_profit_percentage=0.15):
    """
    Função principal para executar o bot de negociação.
    """
    logger.info("Executando main...")

    # Carrega os dados
    df = load_data(datafile)
    if df is None:
        logger.error("Falha ao carregar os dados. Encerrando.")
        return

    # Converte a coluna 'timestamp' para datetime
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        df = df.dropna(subset=['timestamp'])
    except ValueError as e:
        logger.error(f"Erro ao converter a coluna 'timestamp': {e}")
        return

    # Executa a negociação no modo especificado
    if mode == 'paper':
        run_paper_trading(df, initial_cash, oversold, overbought, rsi_length, position_size_percentage, stop_loss_percentage, take_profit_percentage)
    else:
        logger.error(f"Modo desconhecido: {mode}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trading Bot")
    parser.add_argument('--mode', type=str, default='paper', help='Modo de operação: paper ou live')
    parser.add_argument('--datafile', type=str, required=True, help='Caminho para o arquivo de dados CSV')
    parser.add_argument('--initial_cash', type=float, default=10000, help='Valor inicial em dinheiro para o portfólio')
    parser.add_argument('--oversold', type=int, default=30, help='Nível de RSI considerado como sobrevendido')
    parser.add_argument('--overbought', type=int, default=70, help='Nível de RSI considerado como sobrecomprado')
    parser.add_argument('--rsi_length', type=int, default=14, help='Período para cálculo do RSI')
    parser.add_argument('--position_size_percentage', type=float, default=0.1, help='Porcentagem do capital a ser usada em cada posição')
    parser.add_argument('--stop_loss_percentage', type=float, default=0.05, help='Porcentagem de stop loss')
    parser.add_argument('--take_profit_percentage', type=float, default=0.15, help='Porcentagem de take profit')

    args = parser.parse_args()

    main(**vars(args))