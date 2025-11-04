#!/bin/bash

# Test Authentication Login
# This script tests the login functionality with different credentials

echo "=========================================="
echo "Testing Marcus E-commerce Authentication"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_URL="http://localhost:8000/api/auth/login/"

echo "${YELLOW}Test 1: Login with username${NC}"
response=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice.j", "password": "P@ssword123"}')

if echo "$response" | grep -q "refresh"; then
  echo "${GREEN}✅ SUCCESS: Login with username works${NC}"
  echo "   User: $(echo $response | grep -o '"username":"[^"]*"' | cut -d'"' -f4)"
  echo "   Email: $(echo $response | grep -o '"email":"[^"]*"' | cut -d'"' -f4)"
else
  echo "${RED}❌ FAILED: Login with username failed${NC}"
  echo "   Response: $response"
fi
echo ""

echo "${YELLOW}Test 2: Login with email${NC}"
response=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice.j@example.com", "password": "P@ssword123"}')

if echo "$response" | grep -q "refresh"; then
  echo "${GREEN}✅ SUCCESS: Login with email works${NC}"
  echo "   User: $(echo $response | grep -o '"username":"[^"]*"' | cut -d'"' -f4)"
  echo "   Email: $(echo $response | grep -o '"email":"[^"]*"' | cut -d'"' -f4)"
else
  echo "${RED}❌ FAILED: Login with email failed${NC}"
  echo "   Response: $response"
fi
echo ""

echo "${YELLOW}Test 3: Login with bob.smith${NC}"
response=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"username": "bob.smith", "password": "P@ssword123"}')

if echo "$response" | grep -q "refresh"; then
  echo "${GREEN}✅ SUCCESS: bob.smith login works${NC}"
  echo "   User: $(echo $response | grep -o '"username":"[^"]*"' | cut -d'"' -f4)"
  echo "   Email: $(echo $response | grep -o '"email":"[^"]*"' | cut -d'"' -f4)"
else
  echo "${RED}❌ FAILED: bob.smith login failed${NC}"
  echo "   Response: $response"
fi
echo ""

echo "${YELLOW}Test 4: Login with wrong password (should fail)${NC}"
response=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice.j", "password": "WrongPassword"}')

if echo "$response" | grep -q "Invalid credentials"; then
  echo "${GREEN}✅ SUCCESS: Wrong password correctly rejected${NC}"
else
  echo "${RED}❌ FAILED: Wrong password was not rejected${NC}"
  echo "   Response: $response"
fi
echo ""

echo "=========================================="
echo "All tests completed!"
echo "=========================================="
