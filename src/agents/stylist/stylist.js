/**
 * Stylist Agent
 * Manages themes, UI styling, and visual consistency
 */

class StylistAgent {
  constructor(config = {}) {
    this.name = config.name || 'Stylist';
    this.availableThemes = ['cyberpunk', 'rainforest', 'terminal'];
    this.currentTheme = config.defaultTheme || 'cyberpunk';
    this.customStyles = new Map();
  }

  /**
   * Apply a theme to the page
   */
  applyTheme(themeName) {
    if (!this.availableThemes.includes(themeName)) {
      console.error(`Theme "${themeName}" not found`);
      return false;
    }

    // Remove existing theme stylesheets
    const existingThemes = document.querySelectorAll('link[data-theme]');
    existingThemes.forEach(link => link.remove());

    // Add new theme stylesheet
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = `/src/themes/${themeName}/theme.css`;
    link.setAttribute('data-theme', themeName);
    document.head.appendChild(link);

    this.currentTheme = themeName;
    console.log(`${this.name} applied theme: ${themeName}`);

    // Dispatch theme change event
    document.dispatchEvent(new CustomEvent('themechange', {
      detail: { theme: themeName },
    }));

    return true;
  }

  /**
   * Get current theme
   */
  getCurrentTheme() {
    return this.currentTheme;
  }

  /**
   * Get available themes
   */
  getAvailableThemes() {
    return [...this.availableThemes];
  }

  /**
   * Add a custom theme
   */
  addCustomTheme(themeName, cssUrl) {
    if (!this.availableThemes.includes(themeName)) {
      this.availableThemes.push(themeName);
    }
    console.log(`${this.name} registered custom theme: ${themeName}`);
  }

  /**
   * Apply custom styles to an element
   */
  applyCustomStyles(elementId, styles) {
    const element = document.getElementById(elementId);
    if (!element) {
      console.error(`Element ${elementId} not found`);
      return false;
    }

    Object.assign(element.style, styles);
    this.customStyles.set(elementId, styles);
    return true;
  }

  /**
   * Get CSS variable value
   */
  getCSSVariable(variableName) {
    return getComputedStyle(document.documentElement)
      .getPropertyValue(variableName)
      .trim();
  }

  /**
   * Set CSS variable value
   */
  setCSSVariable(variableName, value) {
    document.documentElement.style.setProperty(variableName, value);
    console.log(`${this.name} set ${variableName} to ${value}`);
  }

  /**
   * Reset custom styles for an element
   */
  resetStyles(elementId) {
    const element = document.getElementById(elementId);
    if (!element) {
      console.error(`Element ${elementId} not found`);
      return false;
    }

    element.removeAttribute('style');
    this.customStyles.delete(elementId);
    return true;
  }

  /**
   * Create a theme preview
   */
  generateThemePreview(themeName) {
    if (!this.availableThemes.includes(themeName)) {
      return null;
    }

    return {
      name: themeName,
      preview: {
        primary: this.getCSSVariable('--primary-color'),
        secondary: this.getCSSVariable('--secondary-color'),
        background: this.getCSSVariable('--background-color'),
        text: this.getCSSVariable('--text-color'),
      },
    };
  }
}

export default StylistAgent;
