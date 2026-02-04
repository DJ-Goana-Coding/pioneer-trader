# Updated vortex.py

# Your current code will have the existing lines where base_stake is utilized. Update line 11 here:

base_stake = 8.00  # Changed from 10.50 to 8.00

# After line 22, add:

stop_loss_pct = 0.015  # New stop loss percentage

# In pulse_monitor method (starting at line 71), add the stop-loss check before the profit target check:

loss_pct = (data['buy_price'] - current_price) / data['buy_price']  # Calculate loss percentage
if loss_pct >= self.stop_loss_pct:
    self.execute_exit(reason='STOP_LOSS')  # Call execute_exit with reason

# Update the execute_exit method signature:
def execute_exit(self, reason='MANUAL'):
    # Existing code...
    if reason == 'STOP_LOSS':
        # Add conditional handling for stop loss here
        print('Exiting due to stop-loss')
    elif reason == 'MANUAL':
        print('Exiting manually')

# Update ladder reset:
ladder_reset = 8.00  # Now using 8.00 instead of 10.50

# Update startup log message:
print("LIVE FIRE MODE")  # Changed log message
