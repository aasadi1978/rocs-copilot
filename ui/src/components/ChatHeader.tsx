import { Box, Flex, Heading, Button, Text } from '@chakra-ui/react';
import { Plus, ChevronDown } from 'lucide-react';
import { MenuContent, MenuItem, MenuRoot, MenuTrigger } from '@chakra-ui/react';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface Conversation {
  id: string;
  title: string;
}

interface ChatHeaderProps {
  onNewChat?: () => void;
  conversations: Conversation[];
  currentConversationId: string | null;
  onSelectConversation: (id: string) => void;
}

export function ChatHeader({
  onNewChat,
  conversations,
  currentConversationId,
  onSelectConversation,
}: ChatHeaderProps) {
  const currentConversation = conversations.find(
    (c) => c.id === currentConversationId
  );

  return (
    <Box
      borderBottom="1px"
      borderColor="gray.200"
      bg="white"
      position="sticky"
      top={0}
      zIndex={10}
      boxShadow="sm"
    >
      <Flex
        maxW="7xl"
        mx="auto"
        px={4}
        py={3}
        alignItems="center"
        justifyContent="space-between"
        gap={4}
      >
        <Flex alignItems="center" gap={3} flex={1}>
          <ImageWithFallback
            src="https://logo.com/image-cdn/images/kts928pd/production/c423a9d143ae2a03c1e7076e9abf851a19fceaec-1600x900.png?w=1080&q=72&fm=webp"
            alt="ROCS Logo"
            style={{ height: '40px', width: 'auto', objectFit: 'contain' }}
          />
        </Flex>

        <Flex alignItems="center" gap={3}>
          {conversations.length > 0 && (
            <MenuRoot>
              <MenuTrigger asChild>
                <Button variant="outline" size="sm" colorScheme="gray">
                  {currentConversation?.title || 'Select Conversation'}
                  <ChevronDown style={{ width: '16px', height: '16px' }} />
                </Button>
              </MenuTrigger>
              <MenuContent>
                {conversations.map((conv) => (
                  <MenuItem
                    key={conv.id}
                    value={conv.id}
                    onClick={() => onSelectConversation(conv.id)}
                    bg={
                      conv.id === currentConversationId
                        ? 'fedex.purpleLight'
                        : 'transparent'
                    }
                    _hover={{ bg: 'fedex.purpleLight' }}
                  >
                    {conv.title}
                  </MenuItem>
                ))}
              </MenuContent>
            </MenuRoot>
          )}

          <Button
            onClick={onNewChat}
            bg="fedex"
            color="white"
            size="sm"
            _hover={{ bg: 'fedex.purpleDark' }}
          >
            <Plus
              style={{
                width: '16px',
                height: '16px',
                marginLeft: '10px',
              }}
            />
            <Text margin={2}>New Chat</Text>
          </Button>
        </Flex>
      </Flex>
    </Box>
  );
}
