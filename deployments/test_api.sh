#!/usr/bin/env bash

# Configuration
# Default to internal Docker port if running on VM, or adjust as needed
# Using VM IP as we are running this from the host
BASE_URL="http://192.168.56.2:8000/api/v1"
TIMESTAMP=$(date +%s)
USERNAME="user_${TIMESTAMP}"
EMAIL="user_${TIMESTAMP}@example.com"
PASSWORD="SecurePassword123!"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Helper to extract json value
extract_json_value() {
    local json="$1"
    local key="$2"
    
    if command -v jq &> /dev/null; then
        echo "$json" | jq -r ".$key"
    else
        # Fallback to python if jq is missing
        echo "$json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('$key', ''))" 2>/dev/null
    fi
}

echo "Starting API checks against $BASE_URL..."
echo "----------------------------------------"

# 1. Health/Root Check (Optional, assuming / or /health exists, if not we skip)
# Places Backend might not have a root endpoint documented, but usually docs is at /docs
echo -n "Checking API docs availability... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://192.168.56.2:8000/docs)
if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED ($HTTP_CODE)${NC}"
fi

# 2. Register
echo -n "Registering new user ($USERNAME)... "
REGISTER_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\",
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"confirm_password\": \"$PASSWORD\",
    \"full_name\": \"Test User $TIMESTAMP\"
  }")

REGISTER_BODY=$(echo "$REGISTER_RESPONSE" | head -n -1)
REGISTER_CODE=$(echo "$REGISTER_RESPONSE" | tail -n 1)

if [ "$REGISTER_CODE" -eq 201 ] || [ "$REGISTER_CODE" -eq 200 ]; then
    echo -e "${GREEN}OK ($REGISTER_CODE)${NC}"
else
    echo -e "${RED}FAILED ($REGISTER_CODE)${NC}"
    echo "Response: $REGISTER_BODY"
    exit 1
fi

# 3. Loginnnn
echo -n "Logging in... "
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"login\": \"$EMAIL\",
    \"password\": \"$PASSWORD\"
  }")

TOKEN=$(extract_json_value "$LOGIN_RESPONSE" "access_token")

if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo -e "${GREEN}OK${NC}"
    # echo "Token: ${TOKEN:0:20}..."
else
    echo -e "${RED}FAILED${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

# 4. Get User Profile (Protected Endpoint)
echo -n "Fetching user profile... "
USER_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/users/me" \
  -H "Authorization: Bearer $TOKEN")

USER_BODY=$(echo "$USER_RESPONSE" | head -n -1)
USER_CODE=$(echo "$USER_RESPONSE" | tail -n 1)

RETRIEVED_EMAIL=$(extract_json_value "$USER_BODY" "email")

if [ "$USER_CODE" -eq 200 ] && [ "$RETRIEVED_EMAIL" == "$EMAIL" ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED ($USER_CODE)${NC}"
    echo "Response: $USER_BODY"
    exit 1
fi

echo "----------------------------------------"
echo -e "${GREEN}All checks passed!${NC}"
