# Mandate Revocation Scenario

This scenario demonstrates the mandate lifecycle management capabilities of the Agent Payments Protocol, specifically showing how users can revoke mandates before they are executed.

## Overview

This scenario showcases:
- Creating an Intent Mandate for a conditional purchase
- Revoking the mandate before the condition is met
- Demonstrating that revoked mandates cannot be executed
- Standardized error handling for mandate lifecycle operations

## Scenario Flow

1. **User Creates Intent Mandate**: The user creates an Intent Mandate for a conditional purchase (e.g., "buy this item if the price drops below $50")
2. **Mandate is Active**: The mandate is created in ACTIVE status and can be executed
3. **User Revokes Mandate**: The user decides to revoke the mandate before the condition is met
4. **Mandate Status Updated**: The mandate status is updated to REVOKED
5. **Execution Attempt Fails**: Any attempt to execute the revoked mandate will fail with a proper error message

## Prerequisites

- Python 3.10 or higher
- Google API key set in environment variable `GOOGLE_API_KEY`

## Running the Scenario

1. Navigate to the root of the repository:
   ```bash
   cd AP2
   ```

2. Run the scenario:
   ```bash
   bash samples/python/scenarios/mandate-revocation/run.sh
   ```

3. Follow the interactive prompts to:
   - Create an Intent Mandate for a conditional purchase
   - Revoke the mandate
   - Attempt to execute the revoked mandate (which should fail)

## Expected Behavior

- **Mandate Creation**: The Intent Mandate should be created successfully with ACTIVE status
- **Mandate Revocation**: The revocation should succeed and update the mandate status to REVOKED
- **Execution Failure**: Any attempt to execute a revoked mandate should return a standardized error response

## Error Handling

This scenario demonstrates the standardized error handling defined in the AP2 protocol:

- **Mandate Not Found**: Returns 404 with proper error details
- **Mandate Already Revoked**: Returns 409 with conflict details
- **Invalid Mandate Status**: Returns 409 when trying to execute non-ACTIVE mandates

## Key Features Demonstrated

1. **Mandate Lifecycle Management**: Shows the complete lifecycle from creation to revocation
2. **Standardized Error Responses**: Uses RFC 7807-compliant error format
3. **Status Validation**: Prevents execution of mandates in invalid states
4. **Audit Logging**: All lifecycle events are logged for compliance

## Technical Details

- Uses the A2A protocol for agent communication
- Implements the AP2 mandate lifecycle state machine
- Follows RFC 7807 for error reporting
- Includes proper validation and security checks

## Troubleshooting

If you encounter issues:

1. **API Key**: Ensure `GOOGLE_API_KEY` is set correctly
2. **Port Conflicts**: Make sure ports 8001-8004 are available
3. **Dependencies**: Run `pip install -r requirements-docs.txt` to install dependencies

## Next Steps

After running this scenario, you can:
- Explore other mandate lifecycle operations (amendment, expiration)
- Test error handling with various invalid scenarios
- Integrate mandate lifecycle management into your own applications
