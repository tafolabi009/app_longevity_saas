import React from 'react';
import { Box, Flex, Button, Spacer, Text, Container, Link as ChakraLink } from '@chakra-ui/react';
import { Link as RouterLink, Outlet, useLocation } from 'react-router-dom';
import { APP_NAME } from '../../config';

const PublicLayout = () => {
  const location = useLocation();
  
  return (
    <Box minH="100vh" display="flex" flexDirection="column">
      {/* Nav bar */}
      <Box as="header" bg="white" boxShadow="sm" py={4}>
        <Container maxW="container.xl">
          <Flex align="center">
            <ChakraLink as={RouterLink} to="/">
              <Text fontSize="xl" fontWeight="bold" color="brand.500">
                {APP_NAME}
              </Text>
            </ChakraLink>
            
            <Spacer />
            
            <Flex>
              {location.pathname !== '/login' && (
                <Button
                  as={RouterLink}
                  to="/login"
                  variant="ghost"
                  colorScheme="brand"
                  mr={2}
                >
                  Log In
                </Button>
              )}
              
              {location.pathname !== '/register' && (
                <Button
                  as={RouterLink}
                  to="/register"
                  variant="solid"
                  colorScheme="brand"
                >
                  Sign Up
                </Button>
              )}
            </Flex>
          </Flex>
        </Container>
      </Box>
      
      {/* Main content */}
      <Box flex="1" py={8}>
        <Container maxW="container.xl">
          <Outlet />
        </Container>
      </Box>
      
      {/* Footer */}
      <Box as="footer" py={8} bg="gray.50">
        <Container maxW="container.xl">
          <Flex direction={{ base: 'column', md: 'row' }} align="center" justify="space-between">
            <Text color="gray.500" mb={{ base: 4, md: 0 }}>
              &copy; {new Date().getFullYear()} {APP_NAME}. All rights reserved.
            </Text>
            
            <Flex gap={6}>
              <ChakraLink color="gray.500" href="#">Privacy Policy</ChakraLink>
              <ChakraLink color="gray.500" href="#">Terms of Service</ChakraLink>
              <ChakraLink color="gray.500" href="#">Contact Us</ChakraLink>
            </Flex>
          </Flex>
        </Container>
      </Box>
    </Box>
  );
};

export default PublicLayout; 
