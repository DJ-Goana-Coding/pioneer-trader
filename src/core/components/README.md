# Core Components

This directory contains reusable web components that form the foundation of the UI stencil pack.

## Purpose

Core components are atomic, framework-agnostic UI elements designed to be:
- **Modular**: Each component serves a single, well-defined purpose
- **Themeable**: All components respect the active theme CSS variables
- **Composable**: Components can be nested and combined to create complex UIs

## Component Philosophy

All components in this directory should:
- Use web standards (Custom Elements, Shadow DOM when appropriate)
- Expose clear, documented APIs via attributes and properties
- Emit standard events for state changes
- Be accessibility-friendly (ARIA labels, keyboard navigation)
- Work across all modern browsers

## Usage

Components are imported and registered globally or used as needed:

```javascript
import { Button } from './components/button.js';
// Use in HTML: <ui-button>Click me</ui-button>
```

## Future Components

Planned components include:
- Button
- Card
- Input
- Dropdown
- Modal
- Table
- Chart
- Grid
