# 🎨 UI Stencil Pack

A fully structured, modular repository containing a UI stencil pack built from clean web components. Designed for extension, theming, and integration with external data sources.

## 📋 Project Purpose

The UI Stencil Pack provides a foundation for building modern, themeable web dashboards and applications. It offers:

- **Modular Components**: Reusable, framework-agnostic web components
- **Multiple Themes**: Pre-built themes (Cyberpunk, Rainforest, Terminal)
- **Specialized Dashboards**: Purpose-built layouts for trading, monitoring, and governance
- **Data Adaptors**: Flexible connectors for REST APIs, WebSockets, and mock data
- **Intelligent Agents**: Automated assistants for discovery, tracking, execution, styling, and mapping
- **Metrics & Indicators**: Visual feedback for state changes and deltas

## 🚀 Installation

### Prerequisites

- Node.js 16+ (for package management)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Python 3 (optional, for local dev server)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/DJ-Goana-Coding/pioneer-trader.git
cd pioneer-trader

# Install dependencies (if any)
npm install

# Start local development server
npm run dev

# Open in browser
# Visit http://localhost:8000/public/demo/
```

## 📖 Usage Examples

### Using Themes

```html
<!-- Link to a theme in your HTML -->
<link rel="stylesheet" href="/src/themes/cyberpunk/theme.css">
```

### Importing Agents

```javascript
// Import and use agents
import ScoutAgent from './src/agents/scout/scout.js';
import StylistAgent from './src/agents/stylist/stylist.js';

// Initialize scout to discover opportunities
const scout = new ScoutAgent({ interval: 5000 });
scout.start();

// Use stylist to manage themes
const stylist = new StylistAgent();
stylist.applyTheme('rainforest');
```

### Using Adaptors

```javascript
// REST API communication
import RestAdaptor from './src/adaptors/rest/rest.js';

const api = new RestAdaptor('https://api.example.com');
const data = await api.get('/markets');

// WebSocket for real-time data
import WsAdaptor from './src/adaptors/ws/ws.js';

const ws = new WsAdaptor('wss://api.example.com/stream');
await ws.connect();
ws.on('price_update', (data) => {
  console.log('New price:', data);
});
```

### Using Metrics

```javascript
// Track deltas over time
import DeltaMeter from './src/metrics/delta-meter/delta.js';

const priceMeter = new DeltaMeter();
priceMeter.addValue(45000);
priceMeter.addValue(45500);
const delta = priceMeter.getCurrentDelta(); // { delta: 500, deltaPercent: 1.11 }

// State indicators
import StateIndicator from './src/metrics/state-indicators/indicator.js';

const indicator = new StateIndicator({
  states: ['idle', 'active', 'warning', 'error']
});
indicator.setState('active');
```

## 🏗️ Component Philosophy

All components in this stencil pack follow these principles:

1. **Web Standards First**: Built with native Web Components APIs
2. **Framework Agnostic**: Works with vanilla JS, React, Vue, or any framework
3. **Themeable**: All components respect CSS custom properties
4. **Accessible**: ARIA labels, keyboard navigation, and semantic HTML
5. **Composable**: Components can be nested and combined
6. **Event-Driven**: Clear communication via standard DOM events

### Component Guidelines

- Use Custom Elements for reusable components
- Leverage Shadow DOM for encapsulation when appropriate
- Expose clean, documented APIs via attributes and properties
- Emit custom events for state changes
- Support theming through CSS variables
- Ensure cross-browser compatibility

## 🎯 Architecture

### Directory Structure

```
ui-stencil-pack/
├─ src/
│  ├─ core/              # Core components and layouts
│  ├─ themes/            # Visual themes (cyberpunk, rainforest, terminal)
│  ├─ dashboards/        # Pre-built dashboard templates
│  ├─ adaptors/          # Data source connectors (REST, WS, mock)
│  ├─ metrics/           # Measurement and visualization tools
│  └─ agents/            # Intelligent automation agents
├─ public/demo/          # Live demonstration
├─ .github/workflows/    # CI/CD automation
├─ package.json          # Project metadata
├─ README.md             # This file
└─ AGENT_BLUEPRINT.md    # Agent architecture documentation
```

## 🎨 Available Themes

### Cyberpunk
Neon-infused, high-contrast theme with electric colors and glowing effects.

### Rainforest
Natural, earthy theme with green tones inspired by lush rainforests.

### Terminal
Classic terminal/console theme with monospace fonts and minimal colors.

## 📊 Dashboards

### Trading Dashboard
Real-time market data, active positions, order book, and performance metrics.

### Monitoring Dashboard
System health, active agents, network activity, and error logs.

### Governance Dashboard
Proposals, voting power, decision history, and participant tracking.

## 🤖 Agents

### Scout Agent
Discovers and monitors market opportunities and data sources.

### Hound Agent
Tracks and pursues specific targets or patterns.

### Sniper Agent
Executes precise, targeted actions at optimal moments.

### Stylist Agent
Manages themes, UI styling, and visual consistency.

### Cartographer Agent
Maps data relationships, visualizes structures, and maintains navigation.

## 🔌 Adaptors

### REST Adaptor
HTTP REST API communication with timeout and error handling.

### WebSocket Adaptor
Real-time communication with automatic reconnection.

### Mock Adaptor
Static test data for development and testing.

## 📈 Metrics

### Delta Meter
Measures and visualizes changes/deltas over time with historical tracking.

### State Indicators
Tracks and displays system state with visual feedback and history.

## 🧪 Development

```bash
# Run development server
npm run dev

# View demo
open http://localhost:8000/public/demo/

# View specific dashboard
open http://localhost:8000/src/dashboards/trading/

# Run tests (when available)
npm test
```

## 🤝 Contributing

This is a structured template repository. To extend:

1. Add new components to `src/core/components/`
2. Create custom themes in `src/themes/`
3. Build new dashboards in `src/dashboards/`
4. Implement additional agents in `src/agents/`
5. Add data adaptors in `src/adaptors/`

## 📄 License

MIT License - See LICENSE file for details

## 🔗 Links

- [Repository](https://github.com/DJ-Goana-Coding/pioneer-trader)
- [Agent Blueprint](./AGENT_BLUEPRINT.md)
- [Demo](./public/demo/index.html)

## 📝 Notes

- All placeholder files are ready for implementation
- Themes use CSS custom properties for easy customization
- Agents follow a consistent interface pattern
- Adaptors are promise-based for async operations
- All code is ES6+ module format
