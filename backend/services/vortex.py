# T.I.A. EMERGENCY PATCH V8.3 - LOT SIZE PROTECTION
async def execute_trade(self, slot_id, side, price, symbol, amount_usd=None):
    """Hardened Execution with Precision Shield for MEXC"""
    try:
        # Enforce $5.10 to clear MEXC's $5 minimum trade floor
        amount_usd = amount_usd or self.base_stake
        if amount_usd < 5.10: 
            logger.warning(f"⚠️ [STAKE] {symbol} stake ${amount_usd} below floor. Skipping.")
            return

        # 🛡️ PRECISION SHIELD: Calculate quantity with exchange lot-size rules
        amount_tokens = amount_usd / price
        # CCXT Built-in lot precision handler
        precise_amount = self.exchange.amount_to_precision(symbol, amount_tokens)
        
        if float(precise_amount) <= 0:
            logger.error(f"❌ [PRECISION] {symbol} amount {amount_tokens} rounded to zero.")
            return

        if side == 'buy':
            order = await self.exchange.create_market_buy_order(symbol, float(precise_amount))
            logger.info(f"✅ [Slot {slot_id}] {symbol} BUY: {precise_amount} tokens @ {price}")
        elif side == 'sell':
            order = await self.exchange.create_market_sell_order(symbol, float(precise_amount))
            logger.info(f"💰 [Slot {slot_id}] {symbol} SELL: Banked at {price}")

    except Exception as e:
        logger.error(f"❌ MEXC API FRACTURE in Slot {slot_id}: {e}")