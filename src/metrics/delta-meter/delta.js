/**
 * Delta Meter
 * Measures and visualizes changes/deltas over time
 */

class DeltaMeter {
  constructor(options = {}) {
    this.values = [];
    this.maxHistory = options.maxHistory || 100;
    this.baseline = options.baseline || 0;
  }

  /**
   * Add a new value and calculate delta
   */
  addValue(value, timestamp = Date.now()) {
    const previousValue = this.values.length > 0 
      ? this.values[this.values.length - 1].value 
      : this.baseline;
    
    const delta = value - previousValue;
    const deltaPercent = previousValue !== 0 ? (delta / previousValue) * 100 : 0;

    this.values.push({
      value,
      timestamp,
      delta,
      deltaPercent,
    });

    // Maintain max history size
    if (this.values.length > this.maxHistory) {
      this.values.shift();
    }

    return {
      value,
      delta,
      deltaPercent,
    };
  }

  /**
   * Get current delta
   */
  getCurrentDelta() {
    if (this.values.length < 2) {
      return { delta: 0, deltaPercent: 0 };
    }

    const latest = this.values[this.values.length - 1];
    return {
      delta: latest.delta,
      deltaPercent: latest.deltaPercent,
    };
  }

  /**
   * Get delta over a time period
   */
  getDeltaOverPeriod(periodMs) {
    if (this.values.length === 0) return { delta: 0, deltaPercent: 0 };

    const now = Date.now();
    const cutoff = now - periodMs;
    const startValue = this.values.find(v => v.timestamp >= cutoff);

    if (!startValue) {
      return { delta: 0, deltaPercent: 0 };
    }

    const endValue = this.values[this.values.length - 1];
    const delta = endValue.value - startValue.value;
    const deltaPercent = startValue.value !== 0 
      ? (delta / startValue.value) * 100 
      : 0;

    return { delta, deltaPercent };
  }

  /**
   * Get all historical values
   */
  getHistory() {
    return [...this.values];
  }

  /**
   * Reset the meter
   */
  reset() {
    this.values = [];
  }
}

export default DeltaMeter;
