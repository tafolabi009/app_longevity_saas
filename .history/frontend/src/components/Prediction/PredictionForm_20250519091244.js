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
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Select,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';

function PredictionForm() {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    age: '',
    gender: '',
    bmi: '',
    smoking_status: '',
    exercise_frequency: '',
    sleep_hours: '',
    stress_level: '',
    diet_quality: '',
  });
  const navigate = useNavigate();
  const toast = useToast();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleNumberChange = (name, value) => {
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('/api/predict', {
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
          <Heading size="lg">New Prediction</Heading>
          <Text color="gray.600">Enter your health and lifestyle information</Text>
        </Box>

        <form onSubmit={handleSubmit}>
          <VStack spacing={6} align="stretch">
            <FormControl isRequired>
              <FormLabel>Age</FormLabel>
              <NumberInput
                min={18}
                max={120}
                value={formData.age}
                onChange={(value) => handleNumberChange('age', value)}
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>

            <FormControl isRequired>
              <FormLabel>Gender</FormLabel>
              <Select
                name="gender"
                value={formData.gender}
                onChange={handleChange}
                placeholder="Select gender"
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </Select>
            </FormControl>

            <FormControl isRequired>
              <FormLabel>BMI (Body Mass Index)</FormLabel>
              <NumberInput
                min={10}
                max={50}
                step={0.1}
                value={formData.bmi}
                onChange={(value) => handleNumberChange('bmi', value)}
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>

            <FormControl isRequired>
              <FormLabel>Smoking Status</FormLabel>
              <Select
                name="smoking_status"
                value={formData.smoking_status}
                onChange={handleChange}
                placeholder="Select smoking status"
              >
                <option value="never">Never Smoked</option>
                <option value="former">Former Smoker</option>
                <option value="current">Current Smoker</option>
              </Select>
            </FormControl>

            <FormControl isRequired>
              <FormLabel>Exercise Frequency (times per week)</FormLabel>
              <NumberInput
                min={0}
                max={7}
                value={formData.exercise_frequency}
                onChange={(value) => handleNumberChange('exercise_frequency', value)}
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>

            <FormControl isRequired>
              <FormLabel>Average Sleep Hours</FormLabel>
              <NumberInput
                min={3}
                max={12}
                step={0.5}
                value={formData.sleep_hours}
                onChange={(value) => handleNumberChange('sleep_hours', value)}
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>

            <FormControl isRequired>
              <FormLabel>Stress Level (1-10)</FormLabel>
              <NumberInput
                min={1}
                max={10}
                value={formData.stress_level}
                onChange={(value) => handleNumberChange('stress_level', value)}
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>

            <FormControl isRequired>
              <FormLabel>Diet Quality (1-10)</FormLabel>
              <NumberInput
                min={1}
                max={10}
                value={formData.diet_quality}
                onChange={(value) => handleNumberChange('diet_quality', value)}
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>

            <Button
              type="submit"
              colorScheme="blue"
              size="lg"
              width="full"
              isLoading={loading}
            >
              Get Prediction
            </Button>
          </VStack>
        </form>
      </VStack>
    </Box>
  );
}

export default PredictionForm; 
