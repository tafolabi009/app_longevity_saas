import React from 'react';
import {
  Box,
  Flex,
  Text,
  IconButton,
  Button,
  Stack,
  Collapse,
  Icon,
  Link as ChakraLink,
  Popover,
  PopoverTrigger,
  PopoverContent,
  useColorModeValue,
  useBreakpointValue,
  useDisclosure,
  Container,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
} from '@chakra-ui/react';
import { Link as RouterLink, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { 
  HamburgerIcon, 
  CloseIcon, 
  ChevronDownIcon, 
  ChevronRightIcon,
} from '@chakra-ui/icons';
import { FaChartBar, FaHistory, FaUser, FaSignOutAlt } from 'react-icons/fa';
import { useContext } from 'react';
import AuthContext from '../../context/AuthContext';
import { APP_NAME, MAX_FREE_PREDICTIONS } from '../../config';

const DashboardLayout = () => {
  const { isOpen, onToggle } = useDisclosure();
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  return (
    <Box minH="100vh" display="flex" flexDirection="column">
      <Box bg={useColorModeValue('white', 'gray.800')} boxShadow="sm">
        <Container maxW="container.xl">
          <Flex
            color={useColorModeValue('gray.600', 'white')}
            minH={'60px'}
            py={2}
            align={'center'}
          >
            <Flex
              flex={{ base: 1, md: 'auto' }}
              ml={{ base: -2 }}
              display={{ base: 'flex', md: 'none' }}
            >
              <IconButton
                onClick={onToggle}
                icon={
                  isOpen ? <CloseIcon w={3} h={3} /> : <HamburgerIcon w={5} h={5} />
                }
                variant={'ghost'}
                aria-label={'Toggle Navigation'}
              />
            </Flex>
            
            <Flex flex={{ base: 1 }} justify={{ base: 'center', md: 'start' }}>
              <Text
                textAlign={useBreakpointValue({ base: 'center', md: 'left' })}
                fontFamily={'heading'}
                color={useColorModeValue('brand.600', 'white')}
                fontWeight="bold"
                as={RouterLink}
                to="/app"
              >
                {APP_NAME}
              </Text>

              <Flex display={{ base: 'none', md: 'flex' }} ml={10}>
                <DesktopNav location={location} />
              </Flex>
            </Flex>

            <Stack
              flex={{ base: 1, md: 0 }}
              justify={'flex-end'}
              direction={'row'}
              spacing={6}
            >
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
                    name={user?.username}
                  />
                </MenuButton>
                <MenuList>
                  <Text px={3} py={2} fontWeight="medium">{user?.username}</Text>
                  <Text px={3} py={1} fontSize="sm" color="gray.500">{user?.email}</Text>
                  <MenuDivider />
                  <MenuItem as={RouterLink} to="/app/account" icon={<FaUser />}>
                    Account Settings
                  </MenuItem>
                  <MenuItem onClick={handleLogout} icon={<FaSignOutAlt />}>
                    Sign Out
                  </MenuItem>
                </MenuList>
              </Menu>
            </Stack>
          </Flex>

          <Collapse in={isOpen} animateOpacity>
            <MobileNav location={location} />
          </Collapse>
        </Container>
      </Box>

      <Box flex="1" py={8}>
        <Container maxW="container.xl">
          <Outlet />
        </Container>
      </Box>

      {/* Footer */}
      <Box as="footer" py={6} bg="gray.50">
        <Container maxW="container.xl">
          <Flex direction={{ base: 'column', md: 'row' }} align="center" justify="space-between">
            <Text color="gray.500" mb={{ base: 4, md: 0 }} fontSize="sm">
              &copy; {new Date().getFullYear()} {APP_NAME}. Free tier: {MAX_FREE_PREDICTIONS} predictions per day.
            </Text>
            
            <Flex gap={6}>
              <ChakraLink fontSize="sm" color="gray.500" href="#">Privacy</ChakraLink>
              <ChakraLink fontSize="sm" color="gray.500" href="#">Terms</ChakraLink>
              <ChakraLink fontSize="sm" color="gray.500" href="#">Support</ChakraLink>
            </Flex>
          </Flex>
        </Container>
      </Box>
    </Box>
  );
};

const DesktopNav = ({ location }) => {
  const linkColor = useColorModeValue('gray.600', 'gray.200');
  const linkHoverColor = useColorModeValue('brand.800', 'white');
  const activeLinkColor = useColorModeValue('brand.600', 'brand.400');
  
  return (
    <Stack direction={'row'} spacing={4}>
      {NAV_ITEMS.map((navItem) => {
        const isActive = location.pathname === navItem.href;
        
        return (
          <Box key={navItem.label}>
            <Popover trigger={'hover'} placement={'bottom-start'}>
              <PopoverTrigger>
                <ChakraLink
                  p={2}
                  href={navItem.href ?? '#'}
                  fontSize={'sm'}
                  fontWeight={500}
                  color={isActive ? activeLinkColor : linkColor}
                  _hover={{
                    textDecoration: 'none',
                    color: linkHoverColor,
                  }}
                  as={RouterLink}
                  to={navItem.href}
                >
                  <Flex align="center">
                    {navItem.icon && <Icon as={navItem.icon} mr={2} />}
                    {navItem.label}
                  </Flex>
                </ChakraLink>
              </PopoverTrigger>

              {navItem.children && (
                <PopoverContent
                  border={0}
                  boxShadow={'xl'}
                  bg={useColorModeValue('white', 'gray.800')}
                  p={4}
                  rounded={'xl'}
                  minW={'sm'}
                >
                  <Stack>
                    {navItem.children.map((child) => (
                      <DesktopSubNav key={child.label} {...child} />
                    ))}
                  </Stack>
                </PopoverContent>
              )}
            </Popover>
          </Box>
        );
      })}
    </Stack>
  );
};

const DesktopSubNav = ({ label, href, subLabel }) => {
  return (
    <ChakraLink
      href={href}
      role={'group'}
      display={'block'}
      p={2}
      rounded={'md'}
      _hover={{ bg: useColorModeValue('brand.50', 'gray.900') }}
      as={RouterLink}
      to={href}
    >
      <Stack direction={'row'} align={'center'}>
        <Box>
          <Text
            transition={'all .3s ease'}
            _groupHover={{ color: 'brand.400' }}
            fontWeight={500}
          >
            {label}
          </Text>
          <Text fontSize={'sm'}>{subLabel}</Text>
        </Box>
        <Flex
          transition={'all .3s ease'}
          transform={'translateX(-10px)'}
          opacity={0}
          _groupHover={{ opacity: '100%', transform: 'translateX(0)' }}
          justify={'flex-end'}
          align={'center'}
          flex={1}
        >
          <Icon color={'brand.400'} w={5} h={5} as={ChevronRightIcon} />
        </Flex>
      </Stack>
    </ChakraLink>
  );
};

const MobileNav = ({ location }) => {
  return (
    <Stack
      bg={useColorModeValue('white', 'gray.800')}
      p={4}
      display={{ md: 'none' }}
    >
      {NAV_ITEMS.map((navItem) => (
        <MobileNavItem key={navItem.label} {...navItem} isActive={location.pathname === navItem.href} />
      ))}
    </Stack>
  );
};

const MobileNavItem = ({ label, children, href, icon, isActive }) => {
  const { isOpen, onToggle } = useDisclosure();
  const activeLinkColor = useColorModeValue('brand.600', 'brand.400');
  const linkColor = useColorModeValue('gray.600', 'gray.200');

  return (
    <Stack spacing={4} onClick={children && onToggle}>
      <Flex
        py={2}
        as={RouterLink}
        to={href ?? '#'}
        justify={'space-between'}
        align={'center'}
        _hover={{
          textDecoration: 'none',
        }}
      >
        <Flex align="center">
          {icon && <Icon as={icon} mr={2} />}
          <Text
            fontWeight={600}
            color={isActive ? activeLinkColor : linkColor}
          >
            {label}
          </Text>
        </Flex>
        {children && (
          <Icon
            as={ChevronDownIcon}
            transition={'all .25s ease-in-out'}
            transform={isOpen ? 'rotate(180deg)' : ''}
            w={6}
            h={6}
          />
        )}
      </Flex>

      <Collapse in={isOpen} animateOpacity style={{ marginTop: '0!important' }}>
        <Stack
          mt={2}
          pl={4}
          borderLeft={1}
          borderStyle={'solid'}
          borderColor={useColorModeValue('gray.200', 'gray.700')}
          align={'start'}
        >
          {children &&
            children.map((child) => (
              <ChakraLink 
                key={child.label} 
                py={2} 
                as={RouterLink}
                to={child.href}
              >
                {child.label}
              </ChakraLink>
            ))}
        </Stack>
      </Collapse>
    </Stack>
  );
};

const NAV_ITEMS = [
  {
    label: 'Dashboard',
    href: '/app',
    icon: FaChartBar,
  },
  {
    label: 'New Prediction',
    href: '/app/predict',
    icon: FaChartBar,
  },
  {
    label: 'History',
    href: '/app/history',
    icon: FaHistory,
  },
];

export default DashboardLayout; 
