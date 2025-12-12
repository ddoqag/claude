// GLM Coding API Node.js 客户端
const https = require('https');
const http = require('http');

class GLMCodingClient {
    constructor() {
        this.apiKey = '13beba9abe974c7d97250b9778ca4447.8yR9f0F44Yv0YEX8';
        this.endpoint = 'https://open.bigmodel.cn/api/coding/paas/v4/chat/completions';
        this.model = 'glm-4';
    }

    // 发送API请求
    async sendRequest(prompt) {
        const data = JSON.stringify({
            model: this.model,
            messages: [
                {
                    role: 'user',
                    content: prompt
                }
            ]
        });

        return new Promise((resolve, reject) => {
            const url = new URL(this.endpoint);
            const options = {
                hostname: url.hostname,
                path: url.pathname,
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json',
                    'Content-Length': Buffer.byteLength(data)
                }
            };

            const req = https.request(options, (res) => {
                let responseData = '';

                res.on('data', (chunk) => {
                    responseData += chunk;
                });

                res.on('end', () => {
                    try {
                        const result = JSON.parse(responseData);
                        if (result.choices && result.choices.length > 0) {
                            resolve(result.choices[0].message.content);
                        } else {
                            reject(new Error('API返回异常'));
                        }
                    } catch (error) {
                        reject(new Error('解析响应失败: ' + error.message));
                    }
                });
            });

            req.on('error', (error) => {
                reject(error);
            });

            req.write(data);
            req.end();
        });
    }

    // 生成代码
    async generateCode(prompt, language = null) {
        if (language) {
            prompt = `用${language}编写：${prompt}`;
        }
        return this.sendRequest(prompt);
    }

    // 代码审查
    async reviewCode(code, language = null) {
        const prompt = `请审查以下${language || ''}代码，提出改进建议：\n\n${code}`;
        return this.sendRequest(prompt);
    }

    // 生成单元测试
    async generateTests(code, language = null) {
        const prompt = `为以下${language || ''}代码生成单元测试：\n\n${code}`;
        return this.sendRequest(prompt);
    }
}

// 使用示例
async function main() {
    const client = new GLMCodingClient();

    try {
        // 示例1：生成React组件
        console.log('=== 生成React组件 ===');
        const reactComponent = await client.generateCode(
            '创建一个TodoList组件，包含添加、删除、标记完成功能',
            'React'
        );
        console.log(reactComponent);

        // 示例2：生成API路由
        console.log('\n=== 生成Express.js API路由 ===');
        const apiRoute = await client.generateCode(
            '创建用户注册和登录的API路由',
            'Node.js/Express'
        );
        console.log(apiRoute);

    } catch (error) {
        console.error('请求失败:', error.message);
    }
}

// 如果直接运行此文件，则执行main函数
if (require.main === module) {
    main();
}

module.exports = GLMCodingClient;