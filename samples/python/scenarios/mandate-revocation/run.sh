#!/bin/bash

# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Mandate Revocation Scenario Runner
# This script demonstrates mandate lifecycle management in the AP2 protocol

set -e

echo "🚀 Starting Mandate Revocation Scenario"
echo "======================================"
echo ""

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Error: GOOGLE_API_KEY environment variable is not set"
    echo "Please set your Google API key:"
    echo "export GOOGLE_API_KEY=your_key_here"
    exit 1
fi

echo "✅ Google API key is set"
echo ""

# Install dependencies if needed
echo "📦 Installing dependencies..."
pip install -r ../../requirements-docs.txt > /dev/null 2>&1
echo "✅ Dependencies installed"
echo ""

# Start the agents in the background
echo "🤖 Starting AP2 agents..."
echo ""

# Start Credentials Provider Agent (port 8002)
echo "Starting Credentials Provider Agent on port 8002..."
cd src && python -m roles.credentials_provider_agent &
CREDENTIALS_PID=$!
cd ..

# Start Merchant Payment Processor Agent (port 8003)
echo "Starting Merchant Payment Processor Agent on port 8003..."
cd src && python -m roles.merchant_payment_processor_agent &
PROCESSOR_PID=$!
cd ..

# Start Merchant Agent (port 8001)
echo "Starting Merchant Agent on port 8001..."
cd src && python -m roles.merchant_agent &
MERCHANT_PID=$!
cd ..

# Wait a moment for agents to start
sleep 3

# Start Shopping Agent (port 8000)
echo "Starting Shopping Agent on port 8000..."
cd src && python -m roles.shopping_agent &
SHOPPING_PID=$!
cd ..

# Wait for all agents to start
sleep 5

echo "✅ All agents started successfully!"
echo ""

# Display agent URLs
echo "🌐 Agent URLs:"
echo "  - Shopping Agent: http://localhost:8000"
echo "  - Merchant Agent: http://localhost:8001"
echo "  - Credentials Provider: http://localhost:8002"
echo "  - Payment Processor: http://localhost:8003"
echo ""

echo "📋 Scenario Instructions:"
echo "1. Open http://localhost:8000 in your browser"
echo "2. Create an Intent Mandate for a conditional purchase"
echo "3. Revoke the mandate before execution"
echo "4. Observe the error handling when trying to execute a revoked mandate"
echo ""

echo "🎯 Example conversation:"
echo "  User: 'I want to buy a pair of shoes if the price drops below $50'"
echo "  Agent: [Creates Intent Mandate]"
echo "  User: 'Actually, revoke that mandate'"
echo "  Agent: [Revokes mandate successfully]"
echo "  User: 'Try to buy the shoes now'"
echo "  Agent: [Shows error - mandate is revoked]"
echo ""

echo "Press Ctrl+C to stop all agents when you're done testing"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Stopping all agents..."
    kill $SHOPPING_PID $MERCHANT_PID $CREDENTIALS_PID $PROCESSOR_PID 2>/dev/null || true
    echo "✅ All agents stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
