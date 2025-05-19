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
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Progress,
  SimpleGrid,
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
        const response = await fetch(`/api/v1/predictions/predictions/${id}`);
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

  const getSuccessLevel = (score) => {
    if (score >= 80) return { color: 'green', label: 'High Success Potential' };
    if (score >= 60) return { color: 'yellow', label: 'Moderate Success Potential' };
    return { color: 'red', label: 'Low Success Potential' };
  };

  return (
    <Box maxW="4xl" mx="auto" p={6}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg">App Analysis Results</Heading>
          <Text color="gray.600">
            Prediction for {prediction.app_name}
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
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
              <Stat>
                <StatLabel>Success Score</StatLabel>
                <StatNumber>{prediction.success_score}%</StatNumber>
                <StatHelpText>
                  <StatArrow type={prediction.success_score >= 60 ? 'increase' : 'decrease'} />
                  {getSuccessLevel(prediction.success_score).label}
                </StatHelpText>
              </Stat>

              <Stat>
                <StatLabel>Predicted Longevity</StatLabel>
                <StatNumber>{prediction.predicted_months} months</StatNumber>
                <StatHelpText>
                  Expected active lifespan in the market
                </StatHelpText>
              </Stat>
            </SimpleGrid>

            <Divider />

            <Box>
              <Heading size="md" mb={4}>Key Success Factors</Heading>
              <VStack align="stretch" spacing={4}>
                {prediction.success_factors.map((factor, index) => (
                  <Box key={index}>
                    <Text fontWeight="bold">{factor.name}</Text>
                    <Progress
                      value={factor.score}
                      colorScheme={factor.score >= 70 ? 'green' : factor.score >= 40 ? 'yellow' : 'red'}
                      mb={2}
                    />
                    <Text color="gray.600">{factor.description}</Text>
                  </Box>
                ))}
              </VStack>
            </Box>

            {prediction.compare_competitors && (
              <>
                <Divider />
                <Box>
                  <Heading size="md" mb={4}>Competitor Analysis</Heading>
                  <Table variant="simple">
                    <Thead>
                      <Tr>
                        <Th>Competitor</Th>
                        <Th>Success Score</Th>
                        <Th>Market Position</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {prediction.competitors.map((competitor, index) => (
                        <Tr key={index}>
                          <Td>{competitor.name}</Td>
                          <Td>
                            <Badge colorScheme={getSuccessLevel(competitor.score).color}>
                              {competitor.score}%
                            </Badge>
                          </Td>
                          <Td>{competitor.market_position}</Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </Box>
              </>
            )}

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
              Analyze Another App
            </Button>
          </VStack>
        </Box>
      </VStack>
    </Box>
  );
}

export default PredictionResults; 
