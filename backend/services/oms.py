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

        # 3. Risk Clamp - adjusted by safety modulator
        # Safety modulator scales the risk: 0 = most conservative, 10 = full limit
        safety_factor = (settings.SAFETY_MODULATOR + 1) / 11  # 0.09 to 1.0
        adjusted_limit = settings.MAX_ORDER_NOTIONAL * safety_factor
        
        if notional_value > adjusted_limit:
            raise ValueError(
                f"Order rejected: Notional value {notional_value:.2f} exceeds "
                f"safety-adjusted limit {adjusted_limit:.2f} "
                f"(Safety Modulator: {settings.SAFETY_MODULATOR}/10)"
            )

        # 4. Execute
        # The exchange service handles the PAPER/TESTNET/LIVE logic for the actual call
        return await self.exchange_service.create_order(symbol, order_type, side, amount)
