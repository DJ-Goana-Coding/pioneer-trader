/**
 * Comprehensive test suite for DeltaMeter
 * Tests delta calculation, history tracking, and value management
 */

import { jest } from '@jest/globals';
import DeltaMeter from '../../src/metrics/delta-meter/delta.js';

describe('DeltaMeter', () => {
  let deltaMeter;

  beforeEach(() => {
    deltaMeter = new DeltaMeter();
  });

  describe('Initialization', () => {
    test('should initialize with default config', () => {
      expect(deltaMeter.values).toEqual([]);
      expect(deltaMeter.maxHistory).toBe(100);
      expect(deltaMeter.name).toBe('DeltaMeter');
    });

    test('should initialize with custom config', () => {
      const customMeter = new DeltaMeter({
        name: 'PriceMeter',
        maxHistory: 50
      });

      expect(customMeter.name).toBe('PriceMeter');
      expect(customMeter.maxHistory).toBe(50);
    });
  });

  describe('Adding Values', () => {
    test('should add a single value', () => {
      deltaMeter.addValue(100);

      expect(deltaMeter.values).toHaveLength(1);
      expect(deltaMeter.values[0].value).toBe(100);
      expect(deltaMeter.values[0].timestamp).toBeDefined();
    });

    test('should add multiple values', () => {
      deltaMeter.addValue(100);
      deltaMeter.addValue(105);
      deltaMeter.addValue(110);

      expect(deltaMeter.values).toHaveLength(3);
      expect(deltaMeter.values[2].value).toBe(110);
    });

    test('should record timestamp for each value', () => {
      const before = Date.now();
      deltaMeter.addValue(100);
      const after = Date.now();

      const timestamp = deltaMeter.values[0].timestamp;
      expect(timestamp).toBeGreaterThanOrEqual(before);
      expect(timestamp).toBeLessThanOrEqual(after);
    });

    test('should limit history to maxHistory', () => {
      const smallMeter = new DeltaMeter({ maxHistory: 3 });

      smallMeter.addValue(1);
      smallMeter.addValue(2);
      smallMeter.addValue(3);
      smallMeter.addValue(4);
      smallMeter.addValue(5);

      expect(smallMeter.values).toHaveLength(3);
      expect(smallMeter.values[0].value).toBe(3);
      expect(smallMeter.values[2].value).toBe(5);
    });
  });

  describe('Getting Current Value', () => {
    test('should return null when no values', () => {
      const current = deltaMeter.getCurrentValue();

      expect(current).toBeNull();
    });

    test('should return latest value', () => {
      deltaMeter.addValue(100);
      deltaMeter.addValue(150);
      deltaMeter.addValue(200);

      const current = deltaMeter.getCurrentValue();

      expect(current).toBe(200);
    });
  });

  describe('Getting Previous Value', () => {
    test('should return null when no values', () => {
      const previous = deltaMeter.getPreviousValue();

      expect(previous).toBeNull();
    });

    test('should return null when only one value', () => {
      deltaMeter.addValue(100);

      const previous = deltaMeter.getPreviousValue();

      expect(previous).toBeNull();
    });

    test('should return second-to-last value', () => {
      deltaMeter.addValue(100);
      deltaMeter.addValue(150);
      deltaMeter.addValue(200);

      const previous = deltaMeter.getPreviousValue();

      expect(previous).toBe(150);
    });
  });

  describe('Calculating Delta', () => {
    test('should return null delta when insufficient values', () => {
      deltaMeter.addValue(100);

      const delta = deltaMeter.getCurrentDelta();

      expect(delta).toEqual({
        delta: null,
        deltaPercent: null,
        current: 100,
        previous: null
      });
    });

    test('should calculate positive delta', () => {
      deltaMeter.addValue(100);
      deltaMeter.addValue(150);

      const delta = deltaMeter.getCurrentDelta();

      expect(delta.delta).toBe(50);
      expect(delta.current).toBe(150);
      expect(delta.previous).toBe(100);
    });

    test('should calculate negative delta', () => {
      deltaMeter.addValue(150);
      deltaMeter.addValue(100);

      const delta = deltaMeter.getCurrentDelta();

      expect(delta.delta).toBe(-50);
      expect(delta.current).toBe(100);
      expect(delta.previous).toBe(150);
    });

    test('should calculate zero delta', () => {
      deltaMeter.addValue(100);
      deltaMeter.addValue(100);

      const delta = deltaMeter.getCurrentDelta();

      expect(delta.delta).toBe(0);
    });

    test('should calculate delta percentage', () => {
      deltaMeter.addValue(100);
      deltaMeter.addValue(150);

      const delta = deltaMeter.getCurrentDelta();

      expect(delta.deltaPercent).toBe(50); // 50% increase
    });

    test('should calculate negative delta percentage', () => {
      deltaMeter.addValue(100);
      deltaMeter.addValue(50);

      const delta = deltaMeter.getCurrentDelta();

      expect(delta.deltaPercent).toBe(-50); // 50% decrease
    });

    test('should round delta percentage to 2 decimals', () => {
      deltaMeter.addValue(100);
      deltaMeter.addValue(133.33);

      const delta = deltaMeter.getCurrentDelta();

      expect(delta.deltaPercent).toBe(33.33);
    });

    test('should handle division by zero in percentage', () => {
      deltaMeter.addValue(0);
      deltaMeter.addValue(100);

      const delta = deltaMeter.getCurrentDelta();

      expect(delta.deltaPercent).toBe(Infinity);
    });
  });

  describe('Getting All Values', () => {
    test('should return empty array when no values', () => {
      const values = deltaMeter.getAllValues();

      expect(values).toEqual([]);
    });

    test('should return all values', () => {
      deltaMeter.addValue(100);
      deltaMeter.addValue(150);
      deltaMeter.addValue(200);

      const values = deltaMeter.getAllValues();

      expect(values).toHaveLength(3);
      expect(values[0].value).toBe(100);
      expect(values[2].value).toBe(200);
    });

    test('should return a copy of values array', () => {
      deltaMeter.addValue(100);

      const values = deltaMeter.getAllValues();

      expect(values).not.toBe(deltaMeter.values);
      expect(values).toEqual(deltaMeter.values);
    });
  });

  describe('Getting History', () => {
    test('should return limited history', () => {
      deltaMeter.addValue(100);
      deltaMeter.addValue(110);
      deltaMeter.addValue(120);
      deltaMeter.addValue(130);
      deltaMeter.addValue(140);

      const history = deltaMeter.getHistory(3);

      expect(history).toHaveLength(3);
      expect(history[0].value).toBe(120);
      expect(history[2].value).toBe(140);
    });

    test('should return all values when limit exceeds length', () => {
      deltaMeter.addValue(100);
      deltaMeter.addValue(110);

      const history = deltaMeter.getHistory(10);

      expect(history).toHaveLength(2);
    });
  });

  describe('Clearing Values', () => {
    test('should clear all values', () => {
      deltaMeter.addValue(100);
      deltaMeter.addValue(150);
      deltaMeter.addValue(200);

      deltaMeter.clear();

      expect(deltaMeter.values).toEqual([]);
    });

    test('should return null delta after clearing', () => {
      deltaMeter.addValue(100);
      deltaMeter.addValue(150);
      deltaMeter.clear();

      const delta = deltaMeter.getCurrentDelta();

      expect(delta.delta).toBeNull();
    });
  });

  describe('Statistics', () => {
    test('should calculate average', () => {
      deltaMeter.addValue(100);
      deltaMeter.addValue(200);
      deltaMeter.addValue(300);

      const stats = deltaMeter.getStatistics();

      expect(stats.average).toBe(200);
    });

    test('should find minimum value', () => {
      deltaMeter.addValue(150);
      deltaMeter.addValue(100);
      deltaMeter.addValue(200);

      const stats = deltaMeter.getStatistics();

      expect(stats.min).toBe(100);
    });

    test('should find maximum value', () => {
      deltaMeter.addValue(150);
      deltaMeter.addValue(200);
      deltaMeter.addValue(100);

      const stats = deltaMeter.getStatistics();

      expect(stats.max).toBe(200);
    });

    test('should return null statistics when no values', () => {
      const stats = deltaMeter.getStatistics();

      expect(stats.average).toBeNull();
      expect(stats.min).toBeNull();
      expect(stats.max).toBeNull();
    });

    test('should calculate range', () => {
      deltaMeter.addValue(100);
      deltaMeter.addValue(200);
      deltaMeter.addValue(150);

      const stats = deltaMeter.getStatistics();

      expect(stats.range).toBe(100); // 200 - 100
    });
  });

  describe('Integration Tests', () => {
    test('should track price changes over time', () => {
      const priceMeter = new DeltaMeter({ name: 'BTC Price' });

      // Simulate price changes
      priceMeter.addValue(50000);
      priceMeter.addValue(51000);
      priceMeter.addValue(50500);
      priceMeter.addValue(52000);

      const delta = priceMeter.getCurrentDelta();
      const stats = priceMeter.getStatistics();

      expect(delta.delta).toBe(1500); // 52000 - 50500
      expect(stats.min).toBe(50000);
      expect(stats.max).toBe(52000);
      expect(stats.average).toBe(50875);
    });

    test('should handle rapid value changes', () => {
      for (let i = 0; i < 200; i++) {
        deltaMeter.addValue(100 + i);
      }

      // Should maintain only maxHistory values
      expect(deltaMeter.values.length).toBeLessThanOrEqual(deltaMeter.maxHistory);

      // Latest value should still be accessible
      expect(deltaMeter.getCurrentValue()).toBe(299);
    });
  });
});
