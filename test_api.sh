#!/bin/bash
# Test the GPT Engineer API locally or on Railway

# Configuration
if [ -z "$1" ]; then
    BASE_URL="http://localhost:8000"
else
    BASE_URL="$1"
fi

echo "🧪 Testing GPT Engineer API at: $BASE_URL"
echo "================================================"

# Test 1: Health Check
echo -e "\n1️⃣ Health Check:"
curl -s "$BASE_URL/health" | python3 -m json.tool

# Test 2: API Info
echo -e "\n2️⃣ API Information:"
curl -s "$BASE_URL/api" | python3 -m json.tool

# Test 3: List Projects
echo -e "\n3️⃣ List Projects:"
curl -s "$BASE_URL/projects" | python3 -m json.tool

# Test 4: Generate Code (requires valid API key)
echo -e "\n4️⃣ Generate Code Test:"
echo "⚠️  Skipping generation test (requires valid OPENAI_API_KEY)"
echo "To test generation, run:"
echo 'curl -X POST "'$BASE_URL'/generate" \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '"'"'{'
echo '    "prompt": "Create a simple Python hello world script",'
echo '    "model": "gpt-4o"'
echo '  }'"'"''

echo -e "\n✅ Basic tests complete!"
echo "📖 View interactive docs: $BASE_URL/docs"
echo "🌐 View web interface: $BASE_URL"
