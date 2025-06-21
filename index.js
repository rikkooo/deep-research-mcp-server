#!/usr/bin/env node

const fetch = require('node-fetch');

const query = process.argv.slice(2).join(' ');

if (!query) {
  console.error('Please provide a query.');
  process.exit(1);
}

const body = { query };

async function run() {
  try {
    const response = await fetch('http://localhost:5000/deep_research', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Error from server: ${response.status} ${response.statusText}. Response: ${errorText}`);
      process.exit(1);
    }

    for await (const chunk of response.body) {
      const lines = chunk.toString().split('\n');
      for (const line of lines) {
        if (line.startsWith('data:')) {
          const jsonString = line.substring(5).trim();
          if (jsonString && jsonString !== '[DONE]') {
            try {
              const data = JSON.parse(jsonString);
              if (data.choices && data.choices[0].delta && data.choices[0].delta.content) {
                process.stdout.write(data.choices[0].delta.content);
              } else if (data.error) {
                console.error(`\nError from stream: ${data.error}`);
              }
            } catch (e) {
              // Ignore JSON parsing errors for incomplete chunks
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('Error making request:', error.message);
    process.exit(1);
  }
}

run();
