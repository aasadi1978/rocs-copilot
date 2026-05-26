/**
 * Typed brand tokens. Mirror of theme.css custom properties.
 * Spec §6.3: semantic mapping of FedEx palette.
 */
export const colors = {
  primary: "#007AB7",         // Digital Blue — primary action
  accentPurple: "#4D148C",
  accentOrange: "#FF6200",
  textStrong: "#1A1A1A",      // Gray 90
  textDefault: "#333333",     // Gray 80
  textMuted: "#666666",       // Gray 70
  surface1: "#F5F5F5",        // Gray 30 (deeper background)
  surface2: "#FAFAFA",        // Gray 20
  surface3: "#FFFFFF",        // Gray 10 (top surface)
  error: "#C8102E",           // FedEx red accent
} as const;

export const gradients = {
  signature:
    "linear-gradient(90deg,#4D148C 0%,#7D22C3 33%,#FF6200 100%)",
} as const;

export const typography = {
  body: '"Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
  mono: 'ui-monospace, "Cascadia Mono", "Source Code Pro", monospace',
} as const;
