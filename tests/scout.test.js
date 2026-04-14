/**
 * Comprehensive test suite for ScoutAgent
 * Tests agent lifecycle, source management, and discovery functionality
 */

import { jest } from '@jest/globals';
import ScoutAgent from '../../src/agents/scout/scout.js';

describe('ScoutAgent', () => {
  let scout;
  let mockSource;

  beforeEach(() => {
    jest.useFakeTimers();
    mockSource = {
      name: 'Test Source',
      url: 'https://test.com/api'
    };
  });

  afterEach(() => {
    if (scout && scout.isRunning) {
      scout.stop();
    }
    jest.clearAllTimers();
    jest.useRealTimers();
  });

  describe('Initialization', () => {
    test('should initialize with default config', () => {
      scout = new ScoutAgent();

      expect(scout.name).toBe('Scout');
      expect(scout.interval).toBe(5000);
      expect(scout.sources).toEqual([]);
      expect(scout.discoveries).toEqual([]);
      expect(scout.maxDiscoveries).toBe(100);
      expect(scout.isRunning).toBe(false);
    });

    test('should initialize with custom config', () => {
      scout = new ScoutAgent({
        name: 'CustomScout',
        interval: 10000,
        sources: [mockSource],
        maxDiscoveries: 50
      });

      expect(scout.name).toBe('CustomScout');
      expect(scout.interval).toBe(10000);
      expect(scout.sources).toHaveLength(1);
      expect(scout.maxDiscoveries).toBe(50);
    });
  });

  describe('Lifecycle Management', () => {
    beforeEach(() => {
      scout = new ScoutAgent({ interval: 1000 });
    });

    test('should start scouting', () => {
      scout.start();

      expect(scout.isRunning).toBe(true);
      expect(scout.intervalId).not.toBeNull();
    });

    test('should not start if already running', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

      scout.start();
      const firstIntervalId = scout.intervalId;
      scout.start();

      expect(scout.intervalId).toBe(firstIntervalId);
      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('already running'));

      consoleSpy.mockRestore();
    });

    test('should stop scouting', () => {
      scout.start();
      scout.stop();

      expect(scout.isRunning).toBe(false);
      expect(scout.intervalId).toBeNull();
    });

    test('should not stop if not running', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

      scout.stop();

      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('not running'));

      consoleSpy.mockRestore();
    });
  });

  describe('Source Management', () => {
    beforeEach(() => {
      scout = new ScoutAgent();
    });

    test('should add a source', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

      scout.addSource(mockSource);

      expect(scout.sources).toHaveLength(1);
      expect(scout.sources[0]).toBe(mockSource);
      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Added source'));

      consoleSpy.mockRestore();
    });

    test('should add multiple sources', () => {
      const source2 = { name: 'Source 2', url: 'https://test2.com' };

      scout.addSource(mockSource);
      scout.addSource(source2);

      expect(scout.sources).toHaveLength(2);
    });
  });

  describe('Discovery Management', () => {
    beforeEach(() => {
      scout = new ScoutAgent({ maxDiscoveries: 3 });
    });

    test('should get all discoveries', () => {
      scout.discoveries = [
        { source: 'test1', data: {}, timestamp: Date.now() },
        { source: 'test2', data: {}, timestamp: Date.now() }
      ];

      const discoveries = scout.getDiscoveries();

      expect(discoveries).toHaveLength(2);
      expect(discoveries).not.toBe(scout.discoveries); // Should be a copy
    });

    test('should limit discoveries to maxDiscoveries', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

      // Manually add discoveries
      for (let i = 0; i < 5; i++) {
        scout._recordDiscovery(mockSource, { value: i + 60 });
      }

      expect(scout.discoveries).toHaveLength(3);

      consoleSpy.mockRestore();
    });
  });

  describe('Scouting Functionality', () => {
    beforeEach(() => {
      scout = new ScoutAgent({ interval: 1000 });
      scout.addSource(mockSource);
    });

    test('should scout sources when running', async () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      const scoutSpy = jest.spyOn(scout, '_scout');

      scout.start();

      // Run first scout immediately
      await jest.runOnlyPendingTimersAsync();

      expect(scoutSpy).toHaveBeenCalled();

      consoleSpy.mockRestore();
      scoutSpy.mockRestore();
    });

    test('should check each source during scouting', async () => {
      const source2 = { name: 'Source 2' };
      scout.addSource(source2);

      const checkSourceSpy = jest.spyOn(scout, '_checkSource');
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

      await scout._scout();

      expect(checkSourceSpy).toHaveBeenCalledTimes(2);

      consoleSpy.mockRestore();
      checkSourceSpy.mockRestore();
    });

    test('should handle errors during source checking', async () => {
      const errorSpy = jest.spyOn(console, 'error').mockImplementation();
      const checkSourceSpy = jest.spyOn(scout, '_checkSource').mockRejectedValue(new Error('Test error'));
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

      await scout._scout();

      expect(errorSpy).toHaveBeenCalledWith(
        expect.stringContaining('Error scouting source'),
        expect.any(Error)
      );

      errorSpy.mockRestore();
      checkSourceSpy.mockRestore();
      consoleSpy.mockRestore();
    });
  });

  describe('Opportunity Detection', () => {
    beforeEach(() => {
      scout = new ScoutAgent();
    });

    test('should detect opportunity when value > 50', () => {
      const highValueData = { value: 75 };
      const lowValueData = { value: 25 };

      expect(scout._isOpportunity(highValueData)).toBe(true);
      expect(scout._isOpportunity(lowValueData)).toBe(false);
    });

    test('should record discovery for opportunities', async () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

      // Mock _checkSource to return high value
      jest.spyOn(scout, '_checkSource').mockResolvedValue({ value: 75 });

      scout.addSource(mockSource);
      await scout._scout();

      expect(scout.discoveries.length).toBeGreaterThan(0);

      consoleSpy.mockRestore();
    });

    test('should not record discovery for non-opportunities', async () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

      // Mock _checkSource to return low value
      jest.spyOn(scout, '_checkSource').mockResolvedValue({ value: 25 });

      scout.addSource(mockSource);
      await scout._scout();

      expect(scout.discoveries).toHaveLength(0);

      consoleSpy.mockRestore();
    });
  });

  describe('Discovery Recording', () => {
    beforeEach(() => {
      scout = new ScoutAgent();
    });

    test('should record discovery with correct structure', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      const testData = { value: 75, test: true };

      scout._recordDiscovery(mockSource, testData);

      expect(scout.discoveries).toHaveLength(1);
      expect(scout.discoveries[0]).toMatchObject({
        source: mockSource.name,
        data: testData
      });
      expect(scout.discoveries[0].timestamp).toBeDefined();

      consoleSpy.mockRestore();
    });

    test('should log discovery', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      const testData = { value: 75 };

      scout._recordDiscovery(mockSource, testData);

      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('discovered opportunity'),
        expect.any(Object)
      );

      consoleSpy.mockRestore();
    });
  });

  describe('Integration Tests', () => {
    test('should complete full scouting cycle', async () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

      scout = new ScoutAgent({ interval: 1000, maxDiscoveries: 10 });

      // Add multiple sources
      scout.addSource({ name: 'Source 1' });
      scout.addSource({ name: 'Source 2' });
      scout.addSource({ name: 'Source 3' });

      // Mock _checkSource to sometimes return opportunities
      let callCount = 0;
      jest.spyOn(scout, '_checkSource').mockImplementation(async () => {
        callCount++;
        return { value: callCount % 2 === 0 ? 75 : 25 };
      });

      // Run scout cycle
      await scout._scout();

      // Should have found opportunities from some sources
      expect(scout.discoveries.length).toBeGreaterThan(0);
      expect(scout.discoveries.length).toBeLessThanOrEqual(3);

      consoleSpy.mockRestore();
    });
  });
});
