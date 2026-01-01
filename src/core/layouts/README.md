# Core Layouts

This directory contains layout components that define page structure and component arrangement.

## Purpose

Layout components provide consistent patterns for organizing UI elements across different dashboards and views.

## Layout Types

Planned layouts include:
- **Grid Layout**: Responsive grid system for dashboard tiles
- **Sidebar Layout**: Side navigation with main content area
- **Split Layout**: Dual-pane views for comparison
- **Stack Layout**: Vertical arrangement with flexible sizing

## Usage

Layouts are higher-order components that manage spacing, positioning, and responsive behavior:

```javascript
import { GridLayout } from './layouts/grid.js';
// Use in HTML: <ui-grid-layout cols="3">...</ui-grid-layout>
```

## Design Principles

All layouts should:
- Be responsive and mobile-friendly
- Support nested layouts
- Respect theme spacing variables
- Handle overflow gracefully
- Support dynamic content insertion
