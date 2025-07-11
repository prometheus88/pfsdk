#!/usr/bin/env node
/**
 * Update TypeScript package.json version from centralized VERSION file
 */

const fs = require('fs');
const path = require('path');

function updateVersion() {
    // Read version from centralized VERSION file
    const versionFile = path.join(__dirname, '../../VERSION');
    if (!fs.existsSync(versionFile)) {
        console.error('❌ VERSION file not found at:', versionFile);
        process.exit(1);
    }
    
    const version = fs.readFileSync(versionFile, 'utf8').trim();
    console.log('📦 Reading version:', version);
    
    // Update package.json
    const packageJsonPath = path.join(__dirname, '../package.json');
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    
    const oldVersion = packageJson.version;
    packageJson.version = version;
    
    fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2) + '\n');
    console.log(`✅ Updated package.json version: ${oldVersion} → ${version}`);
    
    // Update TypeScript source files
    updateTypeScriptFiles(version);
}

function updateTypeScriptFiles(version) {
    // Update src/index.ts
    const indexPath = path.join(__dirname, '../src/index.ts');
    if (fs.existsSync(indexPath)) {
        let content = fs.readFileSync(indexPath, 'utf8');
        content = content.replace(
            /export const VERSION = '[^']+';/,
            `export const VERSION = '${version}';`
        );
        fs.writeFileSync(indexPath, content);
        console.log('✅ Updated src/index.ts version');
    }
    
    // Update src/client/base.ts User-Agent
    const clientPath = path.join(__dirname, '../src/client/base.ts');
    if (fs.existsSync(clientPath)) {
        let content = fs.readFileSync(clientPath, 'utf8');
        content = content.replace(
            /'User-Agent': 'PostFiat-TypeScript-SDK\/[^']+'/,
            `'User-Agent': 'PostFiat-TypeScript-SDK/${version}'`
        );
        fs.writeFileSync(clientPath, content);
        console.log('✅ Updated src/client/base.ts User-Agent');
    }
}

if (require.main === module) {
    updateVersion();
}

module.exports = { updateVersion };