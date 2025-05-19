import React, { useState } from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  FormControl,
  FormLabel,
  Input,
  Button,
  useToast,
  useColorModeValue,
  Divider,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react';
import { useAuth } from '../../context/AuthContext';

function Account() {
  const { user, updateProfile } = useAuth();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await updateProfile({
        name: formData.name,
        email: formData.email,
      });

      toast({
        title: 'Profile Updated',
        description: 'Your profile has been successfully updated.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to update profile',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordUpdate = async (e) => {
    e.preventDefault();
    
    if (formData.newPassword !== formData.confirmPassword) {
      toast({
        title: 'Error',
        description: 'New passwords do not match',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }

    setLoading(true);

    try {
      await updateProfile({
        currentPassword: formData.currentPassword,
        newPassword: formData.newPassword,
      });

      toast({
        title: 'Password Updated',
        description: 'Your password has been successfully updated.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

      setFormData(prev => ({
        ...prev,
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      }));
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to update password',
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
          <Heading size="lg">Account Settings</Heading>
          <Text color="gray.600">Manage your account information and preferences</Text>
        </Box>

        <Alert status="info" rounded="md">
          <AlertIcon />
          <Box>
            <AlertTitle>Free Plan</AlertTitle>
            <AlertDescription>
              You are currently on the free plan. Upgrade to access more features and predictions.
            </AlertDescription>
          </Box>
        </Alert>

        <Box
          p={6}
          bg={bgColor}
          shadow="base"
          rounded="lg"
          borderWidth="1px"
          borderColor={borderColor}
        >
          <form onSubmit={handleProfileUpdate}>
            <VStack spacing={6} align="stretch">
              <Heading size="md">Profile Information</Heading>
              
              <FormControl isRequired>
                <FormLabel>Full Name</FormLabel>
                <Input
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Your full name"
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Email</FormLabel>
                <Input
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="your@email.com"
                />
              </FormControl>

              <Button
                type="submit"
                colorScheme="blue"
                isLoading={loading}
              >
                Update Profile
              </Button>
            </VStack>
          </form>
        </Box>

        <Box
          p={6}
          bg={bgColor}
          shadow="base"
          rounded="lg"
          borderWidth="1px"
          borderColor={borderColor}
        >
          <form onSubmit={handlePasswordUpdate}>
            <VStack spacing={6} align="stretch">
              <Heading size="md">Change Password</Heading>

              <FormControl isRequired>
                <FormLabel>Current Password</FormLabel>
                <Input
                  name="currentPassword"
                  type="password"
                  value={formData.currentPassword}
                  onChange={handleChange}
                  placeholder="Enter current password"
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>New Password</FormLabel>
                <Input
                  name="newPassword"
                  type="password"
                  value={formData.newPassword}
                  onChange={handleChange}
                  placeholder="Enter new password"
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Confirm New Password</FormLabel>
                <Input
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="Confirm new password"
                />
              </FormControl>

              <Button
                type="submit"
                colorScheme="blue"
                isLoading={loading}
              >
                Update Password
              </Button>
            </VStack>
          </form>
        </Box>
      </VStack>
    </Box>
  );
}

export default Account; 
