/**
 * WebSocket Adaptor
 * Handles real-time WebSocket communication
 */

class WsAdaptor {
  constructor(url, options = {}) {
    this.url = url;
    this.reconnectInterval = options.reconnectInterval || 5000;
    this.maxReconnectAttempts = options.maxReconnectAttempts || 5;
    this.reconnectAttempts = 0;
    this.ws = null;
    this.listeners = new Map();
  }

  /**
   * Connect to WebSocket server
   */
  connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        resolve();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket closed');
        this._handleReconnect();
      };

      this.ws.onmessage = (event) => {
        this._handleMessage(event.data);
      };
    });
  }

  /**
   * Send message through WebSocket
   */
  send(event, data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = JSON.stringify({ event, data });
      this.ws.send(message);
    } else {
      console.error('WebSocket is not connected');
    }
  }

  /**
   * Subscribe to specific events
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  /**
   * Unsubscribe from events
   */
  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  /**
   * Disconnect WebSocket
   */
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Handle incoming messages
   */
  _handleMessage(data) {
    try {
      const message = JSON.parse(data);
      const callbacks = this.listeners.get(message.event) || [];
      callbacks.forEach(callback => callback(message.data));
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  /**
   * Handle reconnection logic
   */
  _handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      setTimeout(() => this.connect(), this.reconnectInterval);
    } else {
      console.error('Max reconnect attempts reached');
    }
  }
}

export default WsAdaptor;
