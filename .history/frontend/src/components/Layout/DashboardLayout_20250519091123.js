import React from 'react';
import { Box, Container, Flex } from '@chakra-ui/react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Navbar from './Navbar';

function DashboardLayout() {
  return (
    <Box minH="100vh">
      <Navbar />
      <Flex>
        <Sidebar />
        <Box flex="1" p={6}>
          <Container maxW="container.xl">
            <Outlet />
          </Container>
        </Box>
      </Flex>
    </Box>
  );
}

export default DashboardLayout; 
