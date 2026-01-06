# store/webpay.py
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
from django.conf import settings

class WebpayService:
    """
    Clase utilitaria para manejar transacciones con Transbank.
    Usa credenciales de INTEGRACIÓN por defecto si DEBUG=True.
    """
    
    def __init__(self):
        # Configuramos para Integración (Pruebas)
        # En producción, estos valores vendrían de settings.py usando os.environ
        if settings.DEBUG:
            self.commerce_code = IntegrationCommerceCodes.WEBPAY_PLUS
            self.api_key = IntegrationApiKeys.WEBPAY
            self.environment = WebpayOptions(self.commerce_code, self.api_key, "https://webpay3gint.transbank.cl")
        else:
            # Aquí irían tus credenciales reales de Producción
            pass 
        
        self.transaction = Transaction(WebpayOptions(self.commerce_code, self.api_key, "https://webpay3gint.transbank.cl"))

    def create_transaction(self, buy_order, session_id, amount, return_url):
        """
        Inicia una transacción en Webpay y devuelve la URL y Token.
        """
        response = self.transaction.create(
            buy_order=buy_order,
            session_id=session_id,
            amount=amount,
            return_url=return_url
        )
        return response

    def commit_transaction(self, token):
        """
        Confirma la transacción cuando el usuario vuelve a la tienda.
        """
        return self.transaction.commit(token)