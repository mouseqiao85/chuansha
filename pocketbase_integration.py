#!/usr/bin/env python3
"""
PocketBase集成示例 - 为赛博朋克AI工具聚合网站添加数据库功能
"""

import requests
import json
import os
from datetime import datetime
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs


class PocketBaseCyberpunkServer:
    """
    集成PocketBase的赛博朋克AI工具聚合网站服务器
    """
    
    def __init__(self, pocketbase_url="http://localhost:8090"):
        self.pocketbase_url = pocketbase_url
        self.admin_email = os.getenv("PB_ADMIN_EMAIL", "admin@example.com")
        self.admin_password = os.getenv("PB_ADMIN_PASSWORD", "admin123")
        self.auth_token = None
        
    def authenticate(self):
        """
        认证到PocketBase
        """
        try:
            auth_url = f"{self.pocketbase_url}/api/admins/auth-with-password"
            payload = {
                "identity": self.admin_email,
                "password": self.admin_password
            }
            
            response = requests.post(auth_url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["token"]
                print("✅ PocketBase认证成功")
                return True
            else:
                print(f"❌ PocketBase认证失败: {response.text}")
                return False
        except Exception as e:
            print(f"❌ PocketBase认证异常: {str(e)}")
            return False
    
    def create_collections(self):
        """
        创建数据表结构
        """
        if not self.auth_token:
            print("❌ 未认证到PocketBase")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # 创建AI工具表
        tools_collection = {
            "schema": [
                {"name": "name", "type": "text", "required": True},
                {"name": "description", "type": "text", "required": True},
                {"name": "url", "type": "url", "required": True},
                {"name": "category", "type": "text", "required": True},
                {"name": "rating", "type": "number", "required": False},
                {"name": "is_free", "type": "bool", "required": True},
                {"name": "is_featured", "type": "bool", "required": False},
                {"name": "language_support", "type": "text", "required": False},
                {"name": "tags", "type": "text", "required": False}
            ],
            "name": "ai_tools",
            "type": "base",
            "options": {}
        }
        
        try:
            response = requests.post(
                f"{self.pocketbase_url}/api/collections",
                headers=headers,
                json=tools_collection
            )
            
            if response.status_code in [200, 201]:
                print("✅ AI工具表创建成功")
            elif response.status_code == 400 and "already exists" in response.text.lower():
                print("ℹ️  AI工具表已存在")
            else:
                print(f"❌ AI工具表创建失败: {response.text}")
        except Exception as e:
            print(f"❌ 创建AI工具表异常: {str(e)}")
    
    def populate_sample_data(self):
        """
        填充示例数据
        """
        if not self.auth_token:
            print("❌ 未认证到PocketBase")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # 示例AI工具数据
        sample_tools = [
            {
                "name": "ChatGPT",
                "description": "OpenAI开发的高级对话AI，能够回答问题、创作文字、编程等。",
                "url": "https://chat.openai.com",
                "category": "text_generation",
                "rating": 4.9,
                "is_free": True,
                "is_featured": True,
                "language_support": "zh,en,ja,ko",
                "tags": "chat,gpt,llm"
            },
            {
                "name": "Midjourney",
                "description": "业界领先的AI图像生成工具，通过简单的文本描述就能创造出令人惊叹的艺术作品。",
                "url": "https://www.midjourney.com",
                "category": "image_generation",
                "rating": 4.9,
                "is_free": False,
                "is_featured": True,
                "language_support": "en",
                "tags": "image,art,generation"
            },
            {
                "name": "通义千问",
                "description": "阿里巴巴集团旗下的通义实验室自主研发的超大规模语言模型。",
                "url": "https://tongyi.aliyun.com",
                "category": "text_generation",
                "rating": 4.8,
                "is_free": True,
                "is_featured": True,
                "language_support": "zh,en",
                "tags": "chinese,llm,chat"
            }
        ]
        
        success_count = 0
        for tool in sample_tools:
            try:
                response = requests.post(
                    f"{self.pocketbase_url}/api/collections/ai_tools/records",
                    headers=headers,
                    json=tool
                )
                
                if response.status_code in [200, 201]:
                    success_count += 1
                else:
                    print(f"❌ 添加工具失败: {response.text}")
            except Exception as e:
                print(f"❌ 添加工具异常: {str(e)}")
        
        print(f"✅ 成功添加 {success_count}/{len(sample_tools)} 个示例工具")
        return success_count > 0
    
    def get_all_tools(self):
        """
        获取所有AI工具
        """
        try:
            response = requests.get(f"{self.pocketbase_url}/api/collections/ai_tools/records")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 获取工具列表失败: {response.text}")
                return None
        except Exception as e:
            print(f"❌ 获取工具列表异常: {str(e)}")
            return None
    
    def get_tools_by_category(self, category):
        """
        按类别获取AI工具
        """
        try:
            params = {"filter": f"category='{category}'"}
            response = requests.get(
                f"{self.pocketbase_url}/api/collections/ai_tools/records",
                params=params
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 获取类别工具失败: {response.text}")
                return None
        except Exception as e:
            print(f"❌ 获取类别工具异常: {str(e)}")
            return None
    
    def search_tools(self, query):
        """
        搜索AI工具
        """
        try:
            params = {"filter": f"name~'{query}'||description~'{query}'"}
            response = requests.get(
                f"{self.pocketbase_url}/api/collections/ai_tools/records",
                params=params
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 搜索工具失败: {response.text}")
                return None
        except Exception as e:
            print(f"❌ 搜索工具异常: {str(e)}")
            return None


class CyberpunkPocketBaseHandler(http.server.BaseHTTPRequestHandler):
    """
    集成PocketBase的赛博朋克处理器
    """
    
    def __init__(self, pocketbase_client, *args, **kwargs):
        self.pb_client = pocketbase_client
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """
        处理GET请求
        """
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        # API路由处理
        if path == '/api/tools':
            self.serve_tools_api(query_params)
        elif path.startswith('/api/tools/category/'):
            category = path.split('/')[-1]
            self.serve_category_api(category)
        elif path.startswith('/api/search/'):
            query = path.split('/')[-1]
            self.serve_search_api(query)
        else:
            # 返回赛博朋克主页
            self.serve_cyberpunk_homepage()
    
    def serve_tools_api(self, query_params):
        """
        提供工具API
        """
        try:
            tools_data = self.pb_client.get_all_tools()
            if tools_data:
                self.send_json_response(tools_data)
            else:
                self.send_error(500, "无法获取工具数据")
        except Exception as e:
            print(f"API错误: {str(e)}")
            self.send_error(500, f"服务器错误: {str(e)}")
    
    def serve_category_api(self, category):
        """
        提供类别API
        """
        try:
            tools_data = self.pb_client.get_tools_by_category(category)
            if tools_data:
                self.send_json_response(tools_data)
            else:
                self.send_error(500, f"无法获取类别 {category} 的工具数据")
        except Exception as e:
            print(f"API错误: {str(e)}")
            self.send_error(500, f"服务器错误: {str(e)}")
    
    def serve_search_api(self, query):
        """
        提供搜索API
        """
        try:
            tools_data = self.pb_client.search_tools(query)
            if tools_data:
                self.send_json_response(tools_data)
            else:
                self.send_error(500, f"无法搜索 '{query}' 的结果")
        except Exception as e:
            print(f"API错误: {str(e)}")
            self.send_error(500, f"服务器错误: {str(e)}")
    
    def serve_cyberpunk_homepage(self):
        """
        返回赛博朋克主页
        """
        html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>赛博朋克AI工具库 - 基于PocketBase</title>
    <style>
        :root {
            --cyber-primary: #00ffff; /* 青色霓虹 */
            --cyber-secondary: #ff00ff; /* 品红霓虹 */
            --cyber-accent: #ff006e; /* 粉红霓虹 */
            --cyber-dark: #0a0a12; /* 深蓝黑色背景 */
            --cyber-darker: #000000; /* 纯黑 */
            --cyber-light: #ffffff; /* 白色文字 */
            --neon-glow: 0 0 10px var(--cyber-primary), 0 0 20px var(--cyber-primary), 0 0 30px var(--cyber-primary), 0 0 40px var(--cyber-primary);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', 'Orbitron', monospace;
            background: var(--cyber-dark);
            color: var(--cyber-light);
            line-height: 1.6;
            min-height: 100vh;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
            background-image: 
                linear-gradient(rgba(0, 255, 255, 0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 255, 0.05) 1px, transparent 1px);
            background-size: 50px 50px;
        }
        
        .cyber-container {
            max-width: 1200px;
            margin: 0 auto;
            position: relative;
            z-index: 2;
        }
        
        .cyber-header {
            text-align: center;
            padding: 60px 20px 40px;
            margin-bottom: 50px;
            position: relative;
            overflow: hidden;
            background: rgba(10, 10, 18, 0.8);
            border: 2px solid var(--cyber-primary);
            border-radius: 10px;
            backdrop-filter: blur(10px);
            box-shadow: var(--neon-glow);
        }
        
        .cyber-title {
            font-size: 4rem;
            margin-bottom: 20px;
            background: linear-gradient(45deg, var(--cyber-primary), var(--cyber-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 800;
            letter-spacing: 3px;
            text-transform: uppercase;
            font-family: 'Orbitron', monospace;
        }
        
        .cyber-slogan {
            font-size: 1.6rem;
            color: var(--cyber-primary);
            margin-bottom: 25px;
            text-shadow: var(--neon-glow);
        }
        
        .cyber-search-container {
            position: relative;
            max-width: 700px;
            margin: 0 auto 25px;
        }
        
        .cyber-search-input {
            width: 100%;
            padding: 20px 70px 20px 25px;
            font-size: 1.2rem;
            border: 2px solid var(--cyber-primary);
            border-radius: 10px;
            background: rgba(0, 0, 0, 0.7);
            color: var(--cyber-light);
            outline: none;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            font-family: 'Courier New', monospace;
        }
        
        .cyber-search-input:focus {
            border-color: var(--cyber-secondary);
            box-shadow: var(--neon-glow-secondary);
            background: rgba(0, 0, 0, 0.9);
        }
        
        .cyber-tools-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }
        
        .cyber-tool-card {
            background: rgba(10, 10, 18, 0.8);
            border: 2px solid var(--cyber-primary);
            border-radius: 15px;
            padding: 30px;
            transition: all 0.4s ease;
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
            box-shadow: var(--neon-glow);
        }
        
        .cyber-tool-card:hover {
            transform: translateY(-10px);
            box-shadow: var(--neon-glow-secondary);
            border-color: var(--cyber-secondary);
        }
        
        .cyber-tool-title {
            font-size: 1.8rem;
            color: var(--cyber-secondary);
            margin-bottom: 15px;
            font-weight: bold;
            text-shadow: var(--neon-glow-secondary);
        }
        
        .cyber-tool-description {
            color: var(--cyber-light);
            margin-bottom: 20px;
            line-height: 1.6;
        }
        
        .cyber-tool-category {
            display: inline-block;
            background: rgba(0, 255, 255, 0.2);
            color: var(--cyber-primary);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            margin-bottom: 15px;
            border: 1px solid var(--cyber-primary);
        }
        
        .cyber-tool-actions {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }
        
        .cyber-tool-link {
            display: inline-block;
            background: linear-gradient(45deg, var(--cyber-primary), var(--cyber-secondary);
            color: var(--cyber-darker);
            padding: 12px 25px;
            border-radius: 10px;
            text-decoration: none;
            font-weight: bold;
            transition: all 0.3s ease;
            border: none;
            font-family: 'Courier New', monospace;
        }
        
        .cyber-tool-link:hover {
            transform: scale(1.05);
            box-shadow: var(--neon-glow-secondary);
        }
        
        .cyber-status {
            text-align: center;
            padding: 20px;
            color: var(--cyber-primary);
            font-size: 1.2rem;
            margin: 20px 0;
        }
        
        @media (max-width: 768px) {
            .cyber-title {
                font-size: 2.5rem;
            }
            
            .cyber-tools-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
</head>
<body>
    <div class="cyber-container">
        <header class="cyber-header">
            <h1 class="cyber-title" style="font-family: 'Orbitron', monospace;">CYBER AI HUB</h1>
            <p class="cyber-slogan" style="font-family: 'Orbitron', monospace;">基于PocketBase的赛博朋克AI工具聚合平台</p>
            
            <div class="cyber-search-container">
                <input type="text" id="cyberSearchInput" class="cyber-search-input" placeholder="搜索AI工具..." autocomplete="off" style="font-family: 'Orbitron', monospace;">
            </div>
        </header>
        
        <div class="cyber-status" id="cyberStatus">
            加载工具数据中...
        </div>
        
        <main>
            <div class="cyber-tools-grid" id="cyberToolsGrid">
                <!-- 工具卡片将通过JavaScript动态加载 -->
            </div>
        </main>
    </div>
    
    <script>
        // 加载工具数据
        async function loadTools() {
            try {
                const response = await fetch('/api/tools');
                const data = await response.json();
                
                const toolsContainer = document.getElementById('cyberToolsGrid');
                const statusElement = document.getElementById('cyberStatus');
                
                if (data && data.items && data.items.length > 0) {
                    toolsContainer.innerHTML = '';
                    
                    data.items.forEach(tool => {
                        const toolCard = document.createElement('div');
                        toolCard.className = 'cyber-tool-card';
                        
                        toolCard.innerHTML = `
                            <span class="cyber-tool-category">${tool.category.replace('_', ' ').toUpperCase()}</span>
                            <h3 class="cyber-tool-title">${tool.name}</h3>
                            <p class="cyber-tool-description">${tool.description}</p>
                            <div class="cyber-tool-actions">
                                <a href="${tool.url}" target="_blank" class="cyber-tool-link">访问网站</a>
                            </div>
                        `;
                        
                        toolsContainer.appendChild(toolCard);
                    });
                    
                    statusElement.textContent = `共加载 ${data.items.length} 个AI工具`;
                } else {
                    statusElement.textContent = '暂无工具数据';
                }
            } catch (error) {
                console.error('加载工具数据失败:', error);
                document.getElementById('cyberStatus').textContent = '加载失败: ' + error.message;
            }
        }
        
        // 搜索功能
        document.getElementById('cyberSearchInput').addEventListener('input', async (e) => {
            const query = e.target.value.trim();
            
            if (query.length > 0) {
                try {
                    const response = await fetch(`/api/search/${encodeURIComponent(query)}`);
                    const data = await response.json();
                    
                    const toolsContainer = document.getElementById('cyberToolsGrid');
                    const statusElement = document.getElementById('cyberStatus');
                    
                    if (data && data.items && data.items.length > 0) {
                        toolsContainer.innerHTML = '';
                        
                        data.items.forEach(tool => {
                            const toolCard = document.createElement('div');
                            toolCard.className = 'cyber-tool-card';
                            
                            toolCard.innerHTML = `
                                <span class="cyber-tool-category">${tool.category.replace('_', ' ').toUpperCase()}</span>
                                <h3 class="cyber-tool-title">${tool.name}</h3>
                                <p class="cyber-tool-description">${tool.description}</p>
                                <div class="cyber-tool-actions">
                                    <a href="${tool.url}" target="_blank" class="cyber-tool-link">访问网站</a>
                                </div>
                            `;
                            
                            toolsContainer.appendChild(toolCard);
                        });
                        
                        statusElement.textContent = `搜索到 ${data.items.length} 个结果`;
                    } else {
                        toolsContainer.innerHTML = '<div class="cyber-status">未找到匹配的工具</div>';
                        statusElement.textContent = '未找到匹配的工具';
                    }
                } catch (error) {
                    console.error('搜索失败:', error);
                }
            } else {
                // 如果搜索框为空，则重新加载所有工具
                loadTools();
            }
        });
        
        // 页面加载完成后获取工具数据
        document.addEventListener('DOMContentLoaded', () => {
            loadTools();
        });
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_json_response(self, data):
        """发送JSON响应"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))


def run_pocketbase_server(pocketbase_url="http://localhost:8090", port=8095):
    """
    运行集成PocketBase的赛博朋克服务器
    """
    print("🚀 启动集成PocketBase的赛博朋克AI工具聚合网站服务器...")
    print(f"🔌 PocketBase URL: {pocketbase_url}")
    print(f"🌐 服务器地址: http://localhost:{port}")
    
    # 初始化PocketBase客户端
    pb_client = PocketBaseCyberpunkServer(pocketbase_url)
    
    # 尝试认证
    if pb_client.authenticate():
        print("✅ 连接到PocketBase服务器")
        
        # 创建数据表
        pb_client.create_collections()
        
        # 填充示例数据
        pb_client.populate_sample_data()
    else:
        print("⚠️ 无法连接到PocketBase服务器，将以只读模式运行")
    
    # 创建处理器
    def handler_factory(*args, **kwargs):
        return CyberpunkPocketBaseHandler(pb_client, *args, **kwargs)
    
    try:
        with socketserver.TCPServer(("", port), handler_factory) as httpd:
            print(f"✅ 服务器启动成功! 访问: http://localhost:{port}")
            print("🛑 按 Ctrl+C 停止服务器")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except OSError as e:
        print(f"\n❌ 端口{port}已被占用，请尝试其他端口: {e}")


if __name__ == "__main__":
    import sys
    port = int(os.environ.get('PORT', 8095))
    pocketbase_url = os.environ.get('POCKETBASE_URL', 'http://localhost:8090')
    run_pocketbase_server(pocketbase_url, port)