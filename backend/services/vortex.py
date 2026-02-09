class Vortex:
    def __init__(self):
        self.base_stake = 8.00
        self.stop_loss_pct = 0.015  # 1.5% stop-loss

    async def monitor(self, data):
        # Monitoring logic
        pass

    async def execute_exit(self, symbol, profit, force=False, reason='MANUAL'):
        if reason == 'STOP_LOSS':
            status = "🛡️ STOP-LOSS HIT"
        elif reason == 'TARGET':
            status = "💰 TARGET REACHED"
        elif reason == 'TIMEOUT':
            status = "⏱️ TIMEOUT EXIT"
        else:
            status = "🔄 MANUAL EXIT"
        self._log(f"{status}: {symbol} | Profit: ${profit:+.2f}")
        # More logic

    async def some_other_method(self):
        # Logic with reset value
        pass
