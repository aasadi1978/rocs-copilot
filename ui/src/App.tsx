import { useState, useRef, useEffect } from 'react';
import { ChakraProvider, Box, Flex, Text, Spinner } from '@chakra-ui/react';
import { ChatHeader } from './components/ChatHeader';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { WelcomeScreen } from './components/WelcomeScreen';
import { system } from './theme';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: string;
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
}

function ChatApp() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const currentConversation = conversations.find(c => c.id === currentConversationId);
  const messages = currentConversation?.messages || [];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const getCurrentTime = () => {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const generateBotResponse = (userMessage: string): string => {
    const messageLower = userMessage.toLowerCase();
    
    if (messageLower.includes('track') || messageLower.includes('package')) {
      return "I can help you track your package! Please provide your tracking number (typically 12-14 digits). You can also track packages through FedEx.com or the FedEx Mobile App.";
    } else if (messageLower.includes('ship') || messageLower.includes('rate') || messageLower.includes('cost')) {
      return "I'd be happy to help you with shipping rates! To provide accurate pricing, I'll need:\n\n• Package weight and dimensions\n• Origin and destination ZIP codes\n• Desired service type (Express, Ground, etc.)\n\nYou can also get instant rates at FedEx.com.";
    } else if (messageLower.includes('location') || messageLower.includes('office') || messageLower.includes('store')) {
      return "You can find FedEx locations near you by:\n\n• Visiting FedEx.com/locate\n• Using the FedEx mobile app\n• Searching 'FedEx near me'\n\nWe have FedEx Office locations, Ship Centers, and authorized retail partners worldwide.";
    } else if (messageLower.includes('delivery') || messageLower.includes('when')) {
      return "FedEx offers various delivery options:\n\n• FedEx Express: 1-3 business days\n• FedEx Ground: 1-5 business days\n• FedEx Same Day: Same business day\n\nDelivery times vary based on origin and destination. For specific estimates, please provide your package details.";
    } else if (messageLower.includes('hello') || messageLower.includes('hi') || messageLower.includes('hey')) {
      return "Hello! Welcome to FedEx Chat. I'm here to help you with package tracking, shipping rates, locations, delivery information, and general FedEx services. How can I assist you today?";
    } else {
      return "Thank you for your message! I'm here to help with FedEx services including:\n\n• Package tracking\n• Shipping rates and quotes\n• Finding FedEx locations\n• Delivery timeframes\n• General service information\n\nWhat would you like to know?";
    }
  };

  const generateConversationTitle = (firstMessage: string): string => {
    return firstMessage.length > 40 
      ? firstMessage.substring(0, 40) + '...' 
      : firstMessage;
  };

  const handleSendMessage = async (text: string) => {
    const timestamp = getCurrentTime();
    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      isUser: true,
      timestamp,
    };

    // If no conversation exists, create a new one
    if (!currentConversationId) {
      const newConversation: Conversation = {
        id: Date.now().toString(),
        title: generateConversationTitle(text),
        messages: [userMessage],
      };
      setConversations(prev => [newConversation, ...prev]);
      setCurrentConversationId(newConversation.id);
    } else {
      // Add message to current conversation
      setConversations(prev => prev.map(conv => 
        conv.id === currentConversationId
          ? { ...conv, messages: [...conv.messages, userMessage] }
          : conv
      ));
    }

    setIsLoading(true);

    // Simulate AI response time
    await new Promise((resolve) => setTimeout(resolve, 800 + Math.random() * 700));

    const botMessage: Message = {
      id: (Date.now() + 1).toString(),
      text: generateBotResponse(text),
      isUser: false,
      timestamp: getCurrentTime(),
    };

    setConversations(prev => prev.map(conv => 
      conv.id === currentConversationId
        ? { ...conv, messages: [...conv.messages, botMessage] }
        : conv
    ));
    
    setIsLoading(false);
  };

  const handleNewChat = () => {
    setCurrentConversationId(null);
  };

  const handleSelectConversation = (id: string) => {
    setCurrentConversationId(id);
  };

  return (
    <Flex direction="column" h="100vh" w="100%" bg="gray.50">
      <ChatHeader 
        onNewChat={handleNewChat}
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
      />
      
      <Box flex={1} overflowY="auto">
        {messages.length === 0 ? (
          <WelcomeScreen />
        ) : (
          <Box>
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message.text}
                isUser={message.isUser}
                timestamp={message.timestamp}
              />
            ))}
            
            {isLoading && (
              <Box px={{ base: 4, md: 6 }} py={6} bg="fedex.purpleLight">
                <Flex gap={4} maxW="4xl" mx="auto">
                  <Box
                    flexShrink={0}
                    w="36px"
                    h="36px"
                    borderRadius="md"
                    bg="fedex.purple"
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                  >
                    <Spinner size="sm" color="white" />
                  </Box>
                  <Box flex={1}>
                    <Text fontSize="sm" fontWeight="semibold" mb={2} color="gray.700">
                      FedEx Assistant
                    </Text>
                    <Text fontSize="sm" color="gray.500">
                      Thinking...
                    </Text>
                  </Box>
                </Flex>
              </Box>
            )}
            
            <div ref={messagesEndRef} />
          </Box>
        )}
      </Box>

      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </Flex>
  );
}

export default function App() {
  return (
    <ChakraProvider value={system}>
      <ChatApp />
    </ChakraProvider>
  );
}
