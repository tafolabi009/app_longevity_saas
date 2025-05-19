import React from 'react';
import {
  Box,
  Button,
  Container,
  Heading,
  Text,
  VStack,
  SimpleGrid,
  Icon,
  useColorModeValue,
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import { FaChartLine, FaRobot, FaHistory } from 'react-icons/fa';

function LandingPage() {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const features = [
    {
      icon: FaChartLine,
      title: 'Predict App Success',
      description: 'Get accurate predictions about your app\'s potential success and longevity in the market.',
    },
    {
      icon: FaRobot,
      title: 'AI-Powered Analysis',
      description: 'Leverage advanced machine learning models to analyze your app\'s potential.',
    },
    {
      icon: FaHistory,
      title: 'Track Performance',
      description: 'Monitor your app\'s predicted performance over time and make data-driven decisions.',
    },
  ];

  return (
    <Box>
      <Container maxW="container.xl" py={20}>
        <VStack spacing={16} align="stretch">
          {/* Hero Section */}
          <VStack spacing={8} textAlign="center">
            <Heading
              size="2xl"
              bgGradient="linear(to-r, blue.400, blue.600)"
              bgClip="text"
              fontWeight="extrabold"
            >
              Predict Your App's Success
            </Heading>
            <Text fontSize="xl" color="gray.600" maxW="2xl">
              Use our advanced AI models to analyze your app's potential success and longevity in the market.
              Make data-driven decisions and optimize your app's performance.
            </Text>
            <Button
              as={RouterLink}
              to="/register"
              size="lg"
              colorScheme="blue"
              px={8}
            >
              Get Started
            </Button>
          </VStack>

          {/* Features Section */}
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={10}>
            {features.map((feature, index) => (
              <Box
                key={index}
                p={8}
                bg={bgColor}
                shadow="base"
                rounded="lg"
                borderWidth="1px"
                borderColor={borderColor}
                textAlign="center"
              >
                <Icon
                  as={feature.icon}
                  w={10}
                  h={10}
                  color="blue.500"
                  mb={4}
                />
                <Heading size="md" mb={4}>
                  {feature.title}
                </Heading>
                <Text color="gray.600">
                  {feature.description}
                </Text>
              </Box>
            ))}
          </SimpleGrid>

          {/* CTA Section */}
          <Box
            p={8}
            bg={bgColor}
            shadow="base"
            rounded="lg"
            borderWidth="1px"
            borderColor={borderColor}
            textAlign="center"
          >
            <VStack spacing={4}>
              <Heading size="lg">Ready to Analyze Your App?</Heading>
              <Text color="gray.600">
                Join thousands of developers who use our platform to make better decisions about their apps.
              </Text>
              <Button
                as={RouterLink}
                to="/register"
                size="lg"
                colorScheme="blue"
                px={8}
              >
                Start Free Trial
              </Button>
            </VStack>
          </Box>
        </VStack>
      </Container>
    </Box>
  );
}

export default LandingPage; 
