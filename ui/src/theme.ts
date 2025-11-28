import { createSystem, defaultConfig, defineConfig } from '@chakra-ui/react';

const customConfig = defineConfig({
  theme: {
    tokens: {
      colors: {
        fedex: {
          purple: { value: '#4D148C' },
          purpleDark: { value: '#3d1070' },
          purpleLight: { value: '#f3ebf9' },
          orange: { value: '#FF6600' },
          orangeDark: { value: '#e65c00' },
          orangeLight: { value: '#ff944d' },
          green: { value: '#00CC00' },
          greenDark: { value: '#00b300' },
          blue: { value: '#0099CC' },
          blueDark: { value: '#0080b3' },
        },
      },
    },
    semanticTokens: {
      colors: {
        primary: { value: '{colors.fedex.purple}' },
        primaryDark: { value: '{colors.fedex.purpleDark}' },
        accent: { value: '{colors.fedex.orange}' },
        accentDark: { value: '{colors.fedex.orangeDark}' },
      },
    },
  },
});

export const system = createSystem(defaultConfig, customConfig);
