from backend.core.config import settings
from backend.services.exchange import ExchangeService

class OMS:
    def __init__(self, exchange_service: ExchangeService):
        self.exchange_service = exchange_service

    async def place_order(self, symbol: str, side: str, amount: float, order_type: str = "market"):
        # 1. Symbol Validation
        if "/" not in symbol:
            raise ValueError("Invalid symbol format. Must contain '/' (e.g. BTC/USDT)")

        # 2. Fetch current price for risk calculation
        ticker = await self.exchange_service.fetch_ticker(symbol)
        current_price = ticker['last']
        notional_value = amount * current_price

        # 3. Risk Clamp
        if notional_value > settings.MAX_ORDER_NOTIONAL:
            raise ValueError(f"Order rejected: Notional value {notional_value} exceeds limit {settings.MAX_ORDER_NOTIONAL}")

        # 4. Execute
        # The exchange service handles the PAPER/TESTNET/LIVE logic for the actual call
        return await self.exchange_service.create_order(symbol, order_type, side, amount)
