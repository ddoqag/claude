// Windows路径兼容性修复工具
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('=== Windows路径兼容性诊断和修复 ===');

// 检查当前路径格式
console.log('\n1. 当前工作目录:');
const currentDir = process.cwd();
console.log('  process.cwd():', currentDir);
console.log('  __dirname:', __dirname);

// 测试路径转换
console.log('\n2. 路径转换测试:');
const gitBashPath = '/c/Users/ddo/AppData/Roaming/npm';
const windowsPath = 'C:\\Users\\ddo\\AppData\\Roaming\\npm';
console.log('  Git Bash格式:', gitBashPath);
console.log('  Windows格式:', windowsPath);
console.log('  path.resolve():', path.resolve(gitBashPath));

// 检查可执行文件
console.log('\n3. 可执行文件检查:');
const executables = [
  'C:\\Program Files\\nodejs\\node.exe',
  'C:\\Program Files\\nodejs\\npx.cmd',
  'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe',
  'C:\\Windows\\System32\\cmd.exe'
];

executables.forEach(exe => {
  const exists = fs.existsSync(exe);
  console.log(`  ${exe}: ${exists ? '✓' : '✗'}`);
});

// 生成路径修复建议
console.log('\n4. 路径兼容性建议:');
console.log('  ✓ 使用path.join()而非硬编码路径分隔符');
console.log('  ✓ 在Git Bash中使用/c/格式，在Windows中使用C:\\格式');
console.log('  ✓ 使用fs.realpathSync()获取真实路径');
console.log('  ✓ 避免混合使用不同路径格式');

// 环境变量检查
console.log('\n5. 环境变量:');
console.log('  PATH:', process.env.PATH ? process.env.PATH.split(';').slice(0, 3).join(';') + '...' : 'undefined');
console.log('  USERPROFILE:', process.env.USERPROFILE || 'undefined');
console.log('  APPDATA:', process.env.APPDATA || 'undefined');