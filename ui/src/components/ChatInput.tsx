import { useState } from 'react';
import { Box, Flex, Textarea, IconButton } from '@chakra-ui/react';
import { Send } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
}

export function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <Box borderTop="1px" borderColor="gray.200" bg="white" p={4} boxShadow="md">
      <Box maxW="4xl" mx="auto">
        <form onSubmit={handleSubmit}>
          <Flex
            alignItems="flex-end"
            gap={2}
            bg="gray.50"
            borderRadius="lg"
            p={2}
            border="1px"
            borderColor="gray.300"
            _focusWithin={{
              borderColor: 'fedex.purple',
              boxShadow: '0 0 0 1px #4D148C',
            }}
          >
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder="Type your message..."
              bg="transparent"
              border="none"
              resize="none"
              px={2}
              py={2}
              maxH="120px"
              minH="40px"
              rows={1}
              disabled={isLoading}
              _focus={{ boxShadow: 'none' }}
              _placeholder={{ color: 'gray.400' }}
            />
            
            <IconButton
              type="submit"
              aria-label="Send message"
              disabled={!input.trim() || isLoading}
              bg={input.trim() && !isLoading ? 'fedex.purple' : 'gray.300'}
              color="white"
              size="sm"
              borderRadius="md"
              _hover={
                input.trim() && !isLoading
                  ? { bg: 'fedex.purpleDark' }
                  : {}
              }
            >
              <Send style={{ width: '18px', height: '18px' }} />
            </IconButton>
          </Flex>
        </form>
      </Box>
    </Box>
  );
}
