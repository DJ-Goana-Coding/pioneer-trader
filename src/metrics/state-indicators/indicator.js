/**
 * State Indicator
 * Tracks and displays system state with visual indicators
 */

class StateIndicator {
  constructor(options = {}) {
    this.states = options.states || ['idle', 'active', 'warning', 'error'];
    this.currentState = options.initialState || this.states[0];
    this.stateHistory = [];
    this.maxHistory = options.maxHistory || 50;
    this.listeners = [];
  }

  /**
   * Set the current state
   */
  setState(newState, metadata = {}) {
    if (!this.states.includes(newState)) {
      console.warn(`State "${newState}" is not in allowed states`);
      return false;
    }

    const previousState = this.currentState;
    this.currentState = newState;

    const stateChange = {
      from: previousState,
      to: newState,
      timestamp: Date.now(),
      metadata,
    };

    this.stateHistory.push(stateChange);

    // Maintain max history size
    if (this.stateHistory.length > this.maxHistory) {
      this.stateHistory.shift();
    }

    // Notify listeners
    this._notifyListeners(stateChange);

    return true;
  }

  /**
   * Get current state
   */
  getState() {
    return this.currentState;
  }

  /**
   * Check if in specific state
   */
  isState(state) {
    return this.currentState === state;
  }

  /**
   * Get state history
   */
  getHistory() {
    return [...this.stateHistory];
  }

  /**
   * Get time in current state
   */
  getTimeInState() {
    if (this.stateHistory.length === 0) {
      return 0;
    }

    const lastChange = this.stateHistory[this.stateHistory.length - 1];
    return Date.now() - lastChange.timestamp;
  }

  /**
   * Subscribe to state changes
   */
  onChange(callback) {
    this.listeners.push(callback);
    return () => {
      const index = this.listeners.indexOf(callback);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  /**
   * Notify all listeners of state change
   */
  _notifyListeners(stateChange) {
    this.listeners.forEach(listener => {
      try {
        listener(stateChange);
      } catch (error) {
        console.error('Error in state change listener:', error);
      }
    });
  }

  /**
   * Reset indicator
   */
  reset(initialState = null) {
    this.currentState = initialState || this.states[0];
    this.stateHistory = [];
  }
}

export default StateIndicator;
