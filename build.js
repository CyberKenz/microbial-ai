import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const frontendDir = resolve(__dirname, 'frontend');
process.chdir(frontendDir);

if (!existsSync('node_modules')) {
  console.log('Installing dependencies...');
  execSync('npm install --no-bin-links', { stdio: 'inherit' });
}

console.log('Building frontend...');
execSync('npm run build', { stdio: 'inherit' });
