#!/usr/bin/env node

const axios = require('axios');

const query = process.argv.slice(2).join(' ');

if (!query) {
  console.error('Please provide a query.');
  process.exit(1);
}

axios.post('http://localhost:8081/deep_research', { query })
  .then(response => {
    if (response.data.choices && response.data.choices[0] && response.data.choices[0].message) {
      console.log(response.data.choices[0].message.content);
    } else if (response.data.error) {
        console.error('Error from server:', response.data.error.message);
    }
    else {
      console.log(JSON.stringify(response.data, null, 2));
    }
  })
  .catch(error => {
    if (error.response) {
        console.error('Error:', error.response.status, error.response.data.error);
    } else {
        console.error('Error making request:', error.message);
    }
    process.exit(1);
  });
