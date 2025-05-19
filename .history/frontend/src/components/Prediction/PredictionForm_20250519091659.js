import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Heading,
  Text,
  useToast,
  Switch,
  FormHelperText,
  Select,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';

function PredictionForm() {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    app_name: '',
    compare_competitors: false,
    model_name: '',
  });
  const [availableModels, setAvailableModels] = useState([]);
  const navigate = useNavigate();
  const toast = useToast();

  // Fetch available models on component mount
  React.useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await fetch('/api/v1/predictions/available-models');
        if (!response.ok) {
          throw new Error('Failed to fetch available models');
        }
        const data = await response.json();
        setAvailableModels(data);
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Failed to load available models',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    };

    fetchModels();
  }, [toast]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('/api/v1/predictions/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to get prediction');
      }

      const data = await response.json();
      navigate(`/app/predictions/${data.id}`);
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to get prediction',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box maxW="2xl" mx="auto" p={6}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg">App Longevity Prediction</Heading>
          <Text color="gray.600">Analyze your app's potential success and longevity</Text>
        </Box>

        <form onSubmit={handleSubmit}>
          <VStack spacing={6} align="stretch">
            <FormControl isRequired>
              <FormLabel>App Name</FormLabel>
              <Input
                name="app_name"
                value={formData.app_name}
                onChange={handleChange}
                placeholder="Enter your app name"
              />
              <FormHelperText>
                Enter the exact name of your app as it appears in the app store
              </FormHelperText>
            </FormControl>

            <FormControl>
              <FormLabel>Prediction Model</FormLabel>
              <Select
                name="model_name"
                value={formData.model_name}
                onChange={handleChange}
                placeholder="Select a model (optional)"
              >
                {availableModels.map((model) => (
                  <option key={model.name} value={model.name}>
                    {model.name} - {model.description}
                  </option>
                ))}
              </Select>
              <FormHelperText>
                Leave empty to use the default model
              </FormHelperText>
            </FormControl>

            <FormControl display="flex" alignItems="center">
              <FormLabel htmlFor="compare_competitors" mb="0">
                Compare with Competitors
              </FormLabel>
              <Switch
                id="compare_competitors"
                name="compare_competitors"
                isChecked={formData.compare_competitors}
                onChange={handleChange}
              />
              <FormHelperText ml={2}>
                Get insights by comparing with similar apps
              </FormHelperText>
            </FormControl>

            <Button
              type="submit"
              colorScheme="blue"
              size="lg"
              width="full"
              isLoading={loading}
            >
              Analyze App
            </Button>
          </VStack>
        </form>
      </VStack>
    </Box>
  );
}

export default PredictionForm; 
