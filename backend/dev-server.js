#!/usr/bin/env node

/**
 * Alternative development server script
 * Use this if nodemon has permission issues
 */

const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Starting development server...');

// Use node with --watch flag (Node.js 18+)
const nodeVersion = process.version;
const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);

if (majorVersion >= 18) {
  console.log('Using Node.js --watch flag');
  const child = spawn('node', ['--watch', 'src/server.js'], {
    stdio: 'inherit',
    shell: true
  });
  
  child.on('error', (err) => {
    console.error('Failed to start server:', err);
    process.exit(1);
  });
  
  child.on('exit', (code) => {
    console.log(`Server exited with code ${code}`);
  });
} else {
  console.log('Node.js version < 18, using simple node restart');
  const child = spawn('node', ['src/server.js'], {
    stdio: 'inherit',
    shell: true
  });
  
  child.on('error', (err) => {
    console.error('Failed to start server:', err);
    process.exit(1);
  });
  
  child.on('exit', (code) => {
    console.log(`Server exited with code ${code}, restarting...`);
    setTimeout(() => {
      console.log('Restarting server...');
      // Restart the server
      require('./dev-server.js');
    }, 1000);
  });
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down development server...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Shutting down development server...');
  process.exit(0);
});
