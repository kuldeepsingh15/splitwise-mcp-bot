// Test script to verify chat context functionality
const testContext = async () => {
  const baseUrl = 'http://localhost:8000';
  
  // Test 1: Simple query without context
  console.log('Test 1: Simple query without context');
  const response1 = await fetch(`${baseUrl}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      query: 'Hello, how are you?',
      chat_history: []
    })
  });
  const result1 = await response1.json();
  console.log('Response:', result1);
  
  // Test 2: Query with context
  console.log('\nTest 2: Query with context');
  const response2 = await fetch(`${baseUrl}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      query: 'What did I ask before?',
      chat_history: [
        { user: 'Hello, how are you?' },
        { server: 'I am doing well, thank you for asking! How can I help you with your Splitwise data today?' }
      ]
    })
  });
  const result2 = await response2.json();
  console.log('Response:', result2);
  
  // Test 3: Debug context endpoint
  console.log('\nTest 3: Debug context');
  const response3 = await fetch(`${baseUrl}/debug-context`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      query: 'Debug this context',
      chat_history: [
        { user: 'First message' },
        { server: 'First response' },
        { user: 'Second message' },
        { server: 'Second response' }
      ]
    })
  });
  const result3 = await response3.json();
  console.log('Debug Response:', result3);
};

// Run the test
testContext().catch(console.error); 