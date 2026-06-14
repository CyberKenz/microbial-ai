import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { resolve } from 'path';

const frontendDir = resolve(import.meta.dirname, 'frontend');
process.chdir(frontendDir);

if (!existsSync('node_modules')) {
  console.log('Installing dependencies...');
  execSync('npm install --no-bin-links', { stdio: 'inherit' });
}

console.log('Building frontend...');
execSync('npm run build', { stdio: 'inherit' });
