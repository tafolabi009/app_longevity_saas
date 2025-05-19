import React from 'react';
import {
  Box,
  VStack,
  Icon,
  Text,
  Link,
  useColorModeValue,
} from '@chakra-ui/react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import { FaChartBar, FaHistory, FaUser } from 'react-icons/fa';

function Sidebar() {
  const location = useLocation();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const activeBgColor = useColorModeValue('blue.50', 'blue.900');
  const activeColor = useColorModeValue('blue.600', 'blue.200');

  const menuItems = [
    { icon: FaChartBar, label: 'Dashboard', path: '/app' },
    { icon: FaChartBar, label: 'New Prediction', path: '/app/predict' },
    { icon: FaHistory, label: 'History', path: '/app/history' },
    { icon: FaUser, label: 'Account', path: '/app/account' },
  ];

  return (
    <Box
      w={{ base: 'full', md: 60 }}
      bg={bgColor}
      borderRight="1px"
      borderColor={borderColor}
      h="calc(100vh - 60px)"
      py={4}
    >
      <VStack spacing={1} align="stretch">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              as={RouterLink}
              to={item.path}
              _hover={{ textDecoration: 'none' }}
            >
              <Box
                px={4}
                py={3}
                bg={isActive ? activeBgColor : 'transparent'}
                color={isActive ? activeColor : 'inherit'}
                _hover={{
                  bg: isActive ? activeBgColor : useColorModeValue('gray.50', 'gray.700'),
                }}
              >
                <Box display="flex" alignItems="center">
                  <Icon as={item.icon} mr={3} />
                  <Text fontWeight={isActive ? 'bold' : 'normal'}>
                    {item.label}
                  </Text>
                </Box>
              </Box>
            </Link>
          );
        })}
      </VStack>
    </Box>
  );
}

export default Sidebar; 