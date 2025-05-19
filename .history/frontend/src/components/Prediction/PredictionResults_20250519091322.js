import React, { useEffect, useState } from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  useColorModeValue,
  Divider,
  Button,
  useToast,
} from '@chakra-ui/react';
import { useParams, useNavigate } from 'react-router-dom';

function PredictionResults() {
  const { id } = useParams();
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    const fetchPrediction = async () => {
      try {
        const response = await fetch(`/api/predictions/${id}`);
        if (!response.ok) {
          throw new Error('Failed to fetch prediction');
        }
        const data = await response.json();
        setPrediction(data);
      } catch (error) {
        toast({
          title: 'Error',
          description: error.message || 'Failed to fetch prediction',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        navigate('/app/history');
      } finally {
        setLoading(false);
      }
    };

    fetchPrediction();
  }, [id, navigate, toast]);

  if (loading) {
    return (
      <Box p={6}>
        <Text>Loading prediction results...</Text>
      </Box>
    );
  }

  if (!prediction) {
    return null;
  }

  return (
    <Box maxW="2xl" mx="auto" p={6}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg">Prediction Results</Heading>
          <Text color="gray.600">
            Based on your health and lifestyle data
          </Text>
        </Box>

        <Box
          p={6}
          bg={bgColor}
          shadow="base"
          rounded="lg"
          borderWidth="1px"
          borderColor={borderColor}
        >
          <VStack spacing={6} align="stretch">
            <Stat>
              <StatLabel>Predicted Life Expectancy</StatLabel>
              <StatNumber>{prediction.predicted_age} years</StatNumber>
              <StatHelpText>
                <StatArrow type={prediction.predicted_age > 80 ? 'increase' : 'decrease'} />
                {prediction.predicted_age > 80 ? 'Above average' : 'Below average'}
              </StatHelpText>
            </Stat>

            <Divider />

            <Box>
              <Heading size="md" mb={4}>Key Factors</Heading>
              <VStack align="stretch" spacing={4}>
                {prediction.factors.map((factor, index) => (
                  <Box key={index}>
                    <Text fontWeight="bold">{factor.name}</Text>
                    <Text color="gray.600">{factor.description}</Text>
                  </Box>
                ))}
              </VStack>
            </Box>

            <Divider />

            <Box>
              <Heading size="md" mb={4}>Recommendations</Heading>
              <VStack align="stretch" spacing={4}>
                {prediction.recommendations.map((recommendation, index) => (
                  <Box key={index}>
                    <Text fontWeight="bold">{recommendation.title}</Text>
                    <Text color="gray.600">{recommendation.description}</Text>
                  </Box>
                ))}
              </VStack>
            </Box>

            <Button
              colorScheme="blue"
              onClick={() => navigate('/app/predict')}
            >
              Make Another Prediction
            </Button>
          </VStack>
        </Box>
      </VStack>
    </Box>
  );
}

export default PredictionResults; 
