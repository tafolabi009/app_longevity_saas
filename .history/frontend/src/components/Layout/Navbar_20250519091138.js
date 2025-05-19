import React from 'react';
import {
  Box,
  Flex,
  Text,
  Button,
  Stack,
  useColorModeValue,
  useBreakpointValue,
  Container,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
} from '@chakra-ui/react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const location = useLocation();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const handleLogout = () => {
    logout();
  };

  return (
    <Box bg={bgColor} borderBottom="1px" borderColor={borderColor}>
      <Container maxW="container.xl">
        <Flex
          minH={'60px'}
          py={2}
          align={'center'}
          justify={'space-between'}
        >
          <Flex align="center">
            <Text
              textAlign={useBreakpointValue({ base: 'center', md: 'left' })}
              fontFamily={'heading'}
              color={useColorModeValue('blue.600', 'white')}
              fontWeight="bold"
              as={RouterLink}
              to={isAuthenticated ? "/app" : "/"}
            >
              Longevity Predictor
            </Text>
          </Flex>

          <Stack direction={'row'} spacing={4}>
            {isAuthenticated ? (
              <Menu>
                <MenuButton
                  as={Button}
                  rounded={'full'}
                  variant={'link'}
                  cursor={'pointer'}
                  minW={0}
                >
                  <Avatar
                    size={'sm'}
                    name={user?.name}
                  />
                </MenuButton>
                <MenuList>
                  <Text px={3} py={2} fontWeight="medium">{user?.name}</Text>
                  <Text px={3} py={1} fontSize="sm" color="gray.500">{user?.email}</Text>
                  <MenuDivider />
                  <MenuItem as={RouterLink} to="/app/account">
                    Account Settings
                  </MenuItem>
                  <MenuItem onClick={handleLogout}>
                    Sign Out
                  </MenuItem>
                </MenuList>
              </Menu>
            ) : (
              <>
                {location.pathname !== '/login' && (
                  <Button
                    as={RouterLink}
                    to="/login"
                    variant="ghost"
                    colorScheme="blue"
                  >
                    Log In
                  </Button>
                )}
                {location.pathname !== '/register' && (
                  <Button
                    as={RouterLink}
                    to="/register"
                    variant="solid"
                    colorScheme="blue"
                  >
                    Sign Up
                  </Button>
                )}
              </>
            )}
          </Stack>
        </Flex>
      </Container>
    </Box>
  );
}

export default Navbar; 