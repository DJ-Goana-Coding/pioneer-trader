/**
 * Cartographer Agent
 * Maps data relationships, visualizes structures, and maintains navigation
 */

class CartographerAgent {
  constructor(config = {}) {
    this.name = config.name || 'Cartographer';
    this.maps = new Map();
    this.currentMap = null;
  }

  /**
   * Create a new map
   */
  createMap(mapId, options = {}) {
    const map = {
      id: mapId,
      name: options.name || mapId,
      nodes: new Map(),
      edges: [],
      metadata: options.metadata || {},
      created: Date.now(),
      lastUpdated: Date.now(),
    };

    this.maps.set(mapId, map);
    console.log(`${this.name} created map: ${mapId}`);
    return map;
  }

  /**
   * Add a node to a map
   */
  addNode(mapId, nodeId, data) {
    const map = this.maps.get(mapId);
    if (!map) {
      console.error(`Map ${mapId} not found`);
      return false;
    }

    map.nodes.set(nodeId, {
      id: nodeId,
      data,
      connections: [],
      timestamp: Date.now(),
    });

    map.lastUpdated = Date.now();
    return true;
  }

  /**
   * Add an edge between two nodes
   */
  addEdge(mapId, fromId, toId, properties = {}) {
    const map = this.maps.get(mapId);
    if (!map) {
      console.error(`Map ${mapId} not found`);
      return false;
    }

    if (!map.nodes.has(fromId) || !map.nodes.has(toId)) {
      console.error(`Node not found`);
      return false;
    }

    const edge = {
      from: fromId,
      to: toId,
      properties,
      timestamp: Date.now(),
    };

    map.edges.push(edge);
    map.nodes.get(fromId).connections.push(toId);
    map.lastUpdated = Date.now();

    return true;
  }

  /**
   * Find a path between two nodes
   */
  findPath(mapId, startId, endId) {
    const map = this.maps.get(mapId);
    if (!map) return null;

    // Simple BFS pathfinding
    const queue = [[startId]];
    const visited = new Set([startId]);

    while (queue.length > 0) {
      const path = queue.shift();
      const current = path[path.length - 1];

      if (current === endId) {
        return path;
      }

      const node = map.nodes.get(current);
      if (node) {
        for (const neighbor of node.connections) {
          if (!visited.has(neighbor)) {
            visited.add(neighbor);
            queue.push([...path, neighbor]);
          }
        }
      }
    }

    return null; // No path found
  }

  /**
   * Get neighbors of a node
   */
  getNeighbors(mapId, nodeId) {
    const map = this.maps.get(mapId);
    if (!map) return [];

    const node = map.nodes.get(nodeId);
    return node ? node.connections : [];
  }

  /**
   * Export map structure
   */
  exportMap(mapId) {
    const map = this.maps.get(mapId);
    if (!map) return null;

    return {
      id: map.id,
      name: map.name,
      nodes: Array.from(map.nodes.values()),
      edges: map.edges,
      metadata: map.metadata,
      stats: {
        nodeCount: map.nodes.size,
        edgeCount: map.edges.length,
        created: map.created,
        lastUpdated: map.lastUpdated,
      },
    };
  }

  /**
   * Visualize map as ASCII
   */
  visualize(mapId) {
    const map = this.maps.get(mapId);
    if (!map) {
      console.log(`Map ${mapId} not found`);
      return;
    }

    console.log(`\n=== Map: ${map.name} ===`);
    console.log(`Nodes: ${map.nodes.size}, Edges: ${map.edges.length}`);
    console.log('\nNodes:');
    map.nodes.forEach((node, id) => {
      console.log(`  ${id}: ${node.connections.length} connections`);
    });
    console.log('\nEdges:');
    map.edges.forEach(edge => {
      console.log(`  ${edge.from} -> ${edge.to}`);
    });
  }

  /**
   * Delete a map
   */
  deleteMap(mapId) {
    const deleted = this.maps.delete(mapId);
    if (deleted) {
      console.log(`${this.name} deleted map: ${mapId}`);
    }
    return deleted;
  }
}

export default CartographerAgent;
