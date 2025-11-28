import { Box, Flex, Text } from '@chakra-ui/react';
import { User, Bot } from 'lucide-react';

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp?: string;
}

export function ChatMessage({ message, isUser, timestamp }: ChatMessageProps) {
  return (
    <Box
      px={{ base: 4, md: 6 }}
      py={6}
      bg={isUser ? 'white' : 'fedex.purpleLight'}
    >
      <Flex gap={4} maxW="4xl" mx="auto">
        <Box
          flexShrink={0}
          w="36px"
          h="36px"
          borderRadius="md"
          bg={isUser ? 'fedex.orange' : 'fedex.purple'}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          {isUser ? (
            <User style={{ width: '20px', height: '20px', color: 'white' }} />
          ) : (
            <Bot style={{ width: '20px', height: '20px', color: 'white' }} />
          )}
        </Box>
        <Box flex={1}>
          <Flex alignItems="center" gap={2} mb={2}>
            <Text fontSize="sm" fontWeight="semibold" color="gray.700">
              {isUser ? 'You' : 'FedEx Assistant'}
            </Text>
            {timestamp && (
              <Text fontSize="xs" color="gray.500">{timestamp}</Text>
            )}
          </Flex>
          <Text fontSize="sm" lineHeight="1.7" whiteSpace="pre-wrap" color="gray.800">
            {message}
          </Text>
        </Box>
      </Flex>
    </Box>
  );
}
