import { Box, Flex, Heading, Text, VStack } from '@chakra-ui/react';
import { ImageWithFallback } from './figma/ImageWithFallback';

export function WelcomeScreen() {
  return (
    <Flex
      flex={1}
      alignItems="center"
      justifyContent="center"
      p={8}
      bg="gray.50"
    >
      <VStack maxW="3xl" w="full" gap={8} textAlign="center">
        <Box
          display="inline-flex"
          alignItems="center"
          justifyContent="center"
          w="80px"
          h="80px"
          bg="fedex.purple"
          borderRadius="xl"
          boxShadow="lg"
          p={4}
        >
          <ImageWithFallback 
            src="https://cdn-icons-png.flaticon.com/512/10063/10063451.png"
            alt="Chatbot Icon"
            style={{ width: '100%', height: '100%', objectFit: 'contain', filter: 'brightness(0) invert(1)' }}
          />
        </Box>
        
        <VStack gap={3}>
          <Heading size="2xl" color="fedex.purple">
            Welcome to ROCS AI Assistant
          </Heading>
          
          <Text color="gray.600" fontSize="lg" maxW="xl">
            Your AI-powered assistant for all ROCS-related inquiries and questions
          </Text>
        </VStack>

        <Flex
          alignItems="center"
          gap={2}
          px={4}
          py={2}
          bg="fedex.purpleLight"
          borderRadius="full"
          color="fedex.purple"
        >
          <Box w="8px" h="8px" borderRadius="full" bg="fedex.green" />
          <Text fontSize="sm" fontWeight="medium">
            AI-Powered • 24/7 Available
          </Text>
        </Flex>
      </VStack>
    </Flex>
  );
}