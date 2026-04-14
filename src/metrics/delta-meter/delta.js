/**
 * Delta Meter
 * Measures and visualizes changes/deltas over time
 */

class DeltaMeter {
  constructor(options = {}) {
    this.values = [];
    this.maxHistory = options.maxHistory || 100;
    this.baseline = options.baseline || 0;
    this.name = options.name || 'DeltaMeter';
  }

  /**
   * Add a new value
   */
  addValue(value, timestamp = Date.now()) {
    this.values.push({
      value,
      timestamp,
    });

    // Maintain max history size
    if (this.values.length > this.maxHistory) {
      this.values.shift();
    }
  }

  /**
   * Get current value
   */
  getCurrentValue() {
    if (this.values.length === 0) return null;
    return this.values[this.values.length - 1].value;
  }

  /**
   * Get previous value
   */
  getPreviousValue() {
    if (this.values.length < 2) return null;
    return this.values[this.values.length - 2].value;
  }

  /**
   * Get current delta
   */
  getCurrentDelta() {
    const current = this.getCurrentValue();
    const previous = this.getPreviousValue();

    if (current === null) {
      return { delta: null, deltaPercent: null, current: null, previous: null };
    }

    if (previous === null) {
      return { delta: null, deltaPercent: null, current, previous };
    }

    const delta = current - previous;
    const deltaPercent = previous !== 0
      ? Math.round((delta / previous) * 10000) / 100
      : Infinity;

    return {
      delta,
      deltaPercent,
      current,
      previous,
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
  getAllValues() {
    return [...this.values];
  }

  /**
   * Get limited history
   */
  getHistory(limit) {
    if (!limit || limit >= this.values.length) {
      return [...this.values];
    }
    return this.values.slice(-limit);
  }

  /**
   * Clear all values
   */
  clear() {
    this.values = [];
  }

  /**
   * Get statistics
   */
  getStatistics() {
    if (this.values.length === 0) {
      return {
        average: null,
        min: null,
        max: null,
        range: null,
      };
    }

    const values = this.values.map(v => v.value);
    const sum = values.reduce((a, b) => a + b, 0);
    const average = sum / values.length;
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min;

    return {
      average,
      min,
      max,
      range,
    };
  }

  /**
   * Reset the meter (alias for clear)
   */
  reset() {
    this.clear();
  }
}

export default DeltaMeter;
