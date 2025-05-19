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
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  IconButton,
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import { FaEllipsisV, FaTrash } from 'react-icons/fa';

function PredictionHistory() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        const response = await fetch('/api/v1/predictions/predictions');
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

  const handleDelete = async (id) => {
    try {
      const response = await fetch(`/api/v1/predictions/predictions/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete prediction');
      }

      setPredictions(predictions.filter(p => p.id !== id));
      toast({
        title: 'Success',
        description: 'Prediction deleted successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to delete prediction',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const getSuccessLevel = (score) => {
    if (score >= 80) return { color: 'green', label: 'High Success' };
    if (score >= 60) return { color: 'yellow', label: 'Moderate Success' };
    return { color: 'red', label: 'Low Success' };
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
          <Heading size="lg">App Analysis History</Heading>
          <Text color="gray.600">View your past app predictions and their results</Text>
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
            <Text mb={4}>You haven't analyzed any apps yet.</Text>
            <Button
              as={RouterLink}
              to="/app/predict"
              colorScheme="blue"
            >
              Analyze Your First App
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
                  <Th>App Name</Th>
                  <Th>Analysis Date</Th>
                  <Th>Success Score</Th>
                  <Th>Predicted Longevity</Th>
                  <Th>Model Used</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {predictions.map((prediction) => (
                  <Tr key={prediction.id}>
                    <Td>{prediction.app_name}</Td>
                    <Td>{new Date(prediction.created_at).toLocaleDateString()}</Td>
                    <Td>
                      <Badge colorScheme={getSuccessLevel(prediction.success_score).color}>
                        {prediction.success_score}%
                      </Badge>
                    </Td>
                    <Td>{prediction.predicted_months} months</Td>
                    <Td>{prediction.model_name || 'Default'}</Td>
                    <Td>
                      <Menu>
                        <MenuButton
                          as={IconButton}
                          icon={<FaEllipsisV />}
                          variant="ghost"
                          size="sm"
                        />
                        <MenuList>
                          <MenuItem
                            as={RouterLink}
                            to={`/app/predictions/${prediction.id}`}
                          >
                            View Details
                          </MenuItem>
                          <MenuItem
                            onClick={() => handleDelete(prediction.id)}
                            color="red.500"
                            icon={<FaTrash />}
                          >
                            Delete
                          </MenuItem>
                        </MenuList>
                      </Menu>
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
