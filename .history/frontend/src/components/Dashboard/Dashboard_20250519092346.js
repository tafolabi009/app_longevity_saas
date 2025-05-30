import React from 'react';
import { 
  Box, 
  Heading, 
  Text, 
  SimpleGrid, 
  Stat, 
  StatLabel, 
  StatNumber, 
  StatHelpText,
  Button,
  VStack,
  useColorModeValue
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function Dashboard() {
  const { user } = useAuth();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Box p={6}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg" mb={2}>Welcome, {user?.name || 'User'}!</Heading>
          <Text color="gray.600">Your app analysis dashboard</Text>
        </Box>

        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
          <Stat
            px={4}
            py={5}
            bg={bgColor}
            shadow="base"
            rounded="lg"
            borderWidth="1px"
            borderColor={borderColor}
          >
            <StatLabel>Total Analyses</StatLabel>
            <StatNumber>0</StatNumber>
            <StatHelpText>Since joining</StatHelpText>
          </Stat>

          <Stat
            px={4}
            py={5}
            bg={bgColor}
            shadow="base"
            rounded="lg"
            borderWidth="1px"
            borderColor={borderColor}
          >
            <StatLabel>Last Analysis</StatLabel>
            <StatNumber>N/A</StatNumber>
            <StatHelpText>No analyses yet</StatHelpText>
          </Stat>

          <Stat
            px={4}
            py={5}
            bg={bgColor}
            shadow="base"
            rounded="lg"
            borderWidth="1px"
            borderColor={borderColor}
          >
            <StatLabel>Account Status</StatLabel>
            <StatNumber>Active</StatNumber>
            <StatHelpText>Free Plan</StatHelpText>
          </Stat>
        </SimpleGrid>

        <Box
          p={6}
          bg={bgColor}
          shadow="base"
          rounded="lg"
          borderWidth="1px"
          borderColor={borderColor}
        >
          <VStack spacing={4} align="stretch">
            <Heading size="md">Quick Actions</Heading>
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
              <Button
                as={RouterLink}
                to="/app/predict"
                colorScheme="blue"
                size="lg"
                height="100px"
              >
                New Analysis
              </Button>
              <Button
                as={RouterLink}
                to="/app/history"
                colorScheme="teal"
                size="lg"
                height="100px"
              >
                View History
              </Button>
            </SimpleGrid>
          </VStack>
        </Box>

        <Box
          p={6}
          bg={bgColor}
          shadow="base"
          rounded="lg"
          borderWidth="1px"
          borderColor={borderColor}
        >
          <VStack spacing={4} align="stretch">
            <Heading size="md">Getting Started</Heading>
            <Text>
              Welcome to the App Analysis Dashboard! Here's what you can do:
            </Text>
            <VStack align="stretch" spacing={2}>
              <Text>• Analyze your app's potential success using our AI models</Text>
              <Text>• Compare your app with competitors in the market</Text>
              <Text>• Track your app's predicted performance over time</Text>
              <Text>• Get actionable recommendations for improvement</Text>
            </VStack>
          </VStack>
        </Box>
      </VStack>
    </Box>
  );
}

export default Dashboard; 
