import React from 'react';
import { Box, Container } from '@chakra-ui/react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';

function PublicLayout() {
  return (
    <Box minH="100vh">
      <Navbar />
      <Container maxW="container.xl" py={8}>
        <Outlet />
      </Container>
    </Box>
  );
}

export default PublicLayout; 
