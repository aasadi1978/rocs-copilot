import { Box, Flex } from '@chakra-ui/react';

interface FedExLogoProps {
  size?: 'sm' | 'md' | 'lg';
}

export function FedExLogo({ size = 'md' }: FedExLogoProps) {
  const sizes = {
    sm: { height: '20px', fontSize: '18px' },
    md: { height: '28px', fontSize: '24px' },
    lg: { height: '40px', fontSize: '36px' },
  };

  const currentSize = sizes[size];

  return (
    <Flex alignItems="center" gap={0} height={currentSize.height}>
      <Box
        as="span"
        fontSize={currentSize.fontSize}
        fontWeight="bold"
        color="fedex.purple"
        letterSpacing="-0.05em"
        fontFamily="Arial, Helvetica, sans-serif"
      >
        Fed
      </Box>
      <Box
        as="span"
        fontSize={currentSize.fontSize}
        fontWeight="bold"
        color="fedex.orange"
        letterSpacing="-0.05em"
        fontFamily="Arial, Helvetica, sans-serif"
      >
        Ex
      </Box>
    </Flex>
  );
}
