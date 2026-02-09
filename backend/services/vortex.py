class Vortex:
    def __init__(self):
        self.base_stake = 8.00  # updated from 10.50 to 8.00
        self.e_n = 0.5
        self.stop_loss_pct = 0.015  # 1.5% stop-loss

    async def pulse_monitor(self, data):
        # ... other code ...
        loss_pct = (data['buy_price'] - current_price) / data['buy_price']
        if loss_pct >= self.stop_loss_pct:
            await self.execute_exit(symbol, profit, force=True, reason='STOP_LOSS')  # stop-loss check

    async def execute_exit(self, symbol, profit, force=False, reason='MANUAL'):
        # Handle different status messages based on the reason parameter.
        if reason == 'STOP_LOSS':
            message = f"⚔️ VORTEX V6.9 BERSERKER ENGAGED. LIVE FIRE MODE - $8.00 STAKES"
        else:
            message = f"Stake back to $8.00"
        # logging and other operations
        self._log(f"🛡️ STOP-LOSS: {self.stop_loss_pct*100}% | 🎯 TARGET: ${self.target_profit_range[0]}-${self.target_profit_range[1]}")
        # ... other code ...
        self.base_stake = 8.00  # updated from 10.50 to 8.00
