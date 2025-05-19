import React, { useEffect, useState } from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Button,
  useColorModeValue,
  useToast,
  Link,
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

function PredictionHistory() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        const response = await fetch('/api/predictions');
        if (!response.ok) {
          throw new Error('Failed to fetch predictions');
        }
        const data = await response.json();
        setPredictions(data);
      } catch (error) {
        toast({
          title: 'Error',
          description: error.message || 'Failed to fetch predictions',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchPredictions();
  }, [toast]);

  const getStatusColor = (age) => {
    if (age >= 80) return 'green';
    if (age >= 70) return 'yellow';
    return 'red';
  };

  if (loading) {
    return (
      <Box p={6}>
        <Text>Loading prediction history...</Text>
      </Box>
    );
  }

  return (
    <Box p={6}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg">Prediction History</Heading>
          <Text color="gray.600">View your past predictions and their results</Text>
        </Box>

        {predictions.length === 0 ? (
          <Box
            p={6}
            bg={bgColor}
            shadow="base"
            rounded="lg"
            borderWidth="1px"
            borderColor={borderColor}
            textAlign="center"
          >
            <Text mb={4}>You haven't made any predictions yet.</Text>
            <Button
              as={RouterLink}
              to="/app/predict"
              colorScheme="blue"
            >
              Make Your First Prediction
            </Button>
          </Box>
        ) : (
          <Box
            overflowX="auto"
            bg={bgColor}
            shadow="base"
            rounded="lg"
            borderWidth="1px"
            borderColor={borderColor}
          >
            <Table variant="simple">
              <Thead>
                <Tr>
                  <Th>Date</Th>
                  <Th>Predicted Age</Th>
                  <Th>Status</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {predictions.map((prediction) => (
                  <Tr key={prediction.id}>
                    <Td>{new Date(prediction.created_at).toLocaleDateString()}</Td>
                    <Td>{prediction.predicted_age} years</Td>
                    <Td>
                      <Badge colorScheme={getStatusColor(prediction.predicted_age)}>
                        {prediction.predicted_age >= 80 ? 'Above Average' : 'Below Average'}
                      </Badge>
                    </Td>
                    <Td>
                      <Button
                        as={RouterLink}
                        to={`/app/predictions/${prediction.id}`}
                        size="sm"
                        colorScheme="blue"
                        variant="ghost"
                      >
                        View Details
                      </Button>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
        )}
      </VStack>
    </Box>
  );
}

export default PredictionHistory; 
