import locale
import logging

logger = logging.getLogger(__name__)

def format_currency(value):
    """
    Formata um valor numérico como moeda no padrão brasileiro (R$).
    Tenta usar o locale 'pt_BR.UTF-8' para uma formatação precisa.
    Se o locale não estiver disponível, usa uma formatação manual como fallback.

    Args:
        value (float or int): O valor a ser formatado.

    Returns:
        str: O valor formatado como string de moeda (ex: "R$ 1.234,56").
    """
    try:
        # Tenta configurar o locale para português do Brasil
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        # Usa a função de formatação de moeda do locale
        return locale.currency(value, grouping=True, symbol=True)
    except (locale.Error, TypeError):
        # Se o locale não estiver disponível ou ocorrer um erro, usa um fallback manual
        logger.warning("Locale 'pt_BR.UTF-8' não está disponível. Usando formatação de moeda manual.")
        if not isinstance(value, (int, float)):
            value = 0.0  # Garante que o valor seja numérico
        # Formatação manual para o padrão brasileiro
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
