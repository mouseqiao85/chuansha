# 集成PocketBase到赛博朋克AI工具聚合网站

## 概述

本项目演示了如何将PocketBase集成到赛博朋克风格的AI工具聚合网站中，以提供强大的后端数据库功能。

## PocketBase简介

PocketBase 是一个开源的后端服务，提供了：
- SQLite数据库
- 实时数据同步
- 身份验证系统
- 文件存储
- REST/Realtime APIs
- Admin dashboard

## 安装PocketBase

### 方法1：下载预编译二进制文件

```bash
# 下载最新版本 (以Linux AMD64为例)
wget https://github.com/pocketbase/pocketbase/releases/latest/download/pocketbase_0.22.20_linux_amd64.zip

# 解压
unzip pocketbase_0.22.20_linux_amd64.zip

# 启动PocketBase
./pocketbase serve
```

### 方法2：使用Docker

```bash
docker run -p 8090:8090 -v ./pb_data:/pb_data pocketbase/pocketbase:latest serve --http=0.0.0.0:8090
```

### 方法3：从源码构建

```bash
# 安装Go (如果尚未安装)
# 参考: https://go.dev/doc/install

# 克隆PocketBase
git clone https://github.com/pocketbase/pocketbase.git

# 构建
cd pocketbase
go build -o pocketbase .

# 运行
./pocketbase serve
```

## 配置PocketBase

首次启动后，访问 http://localhost:8090/_/ 来设置管理员账户。

## 运行集成服务器

```bash
# 设置环境变量
export PB_ADMIN_EMAIL="your-admin-email@example.com"
export PB_ADMIN_PASSWORD="your-admin-password"

# 运行集成服务器
python pocketbase_integration.py
```

## 数据模型

### AI工具表 (ai_tools)

- `name` (text, required) - 工具名称
- `description` (text, required) - 工具描述
- `url` (url, required) - 工具网址
- `category` (text, required) - 工具类别
- `rating` (number) - 评分 (0-5)
- `is_free` (bool, required) - 是否免费
- `is_featured` (bool) - 是否推荐
- `language_support` (text) - 语言支持
- `tags` (text) - 标签

## API端点

- `GET /api/tools` - 获取所有AI工具
- `GET /api/tools/category/{category}` - 按类别获取工具
- `GET /api/search/{query}` - 搜索工具
- 主页 - `http://localhost:8095`

## 集成功能

1. **数据持久化** - 所有AI工具信息存储在数据库中
2. **动态内容** - 工具列表动态从数据库加载
3. **搜索功能** - 强大的全文搜索
4. **实时更新** - 通过Admin面板可实时更新工具信息
5. **分类管理** - 灵活的工具分类系统

## 部署

### 生产环境部署

```bash
# 使用PM2运行 (需要先安装PM2)
npm install -g pm2
pm2 start pocketbase_integration.py --name "cyberpunk-ai-pocketbase"
```

### Nginx反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8095;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 扩展功能

1. **用户系统** - 添加用户注册/登录功能
2. **评论系统** - 用户可对工具进行评论和评分
3. **收藏功能** - 用户可收藏喜欢的工具
4. **API密钥** - 为外部应用提供API访问
5. **数据分析** - 统计工具使用情况

## 故障排除

### 常见问题

1. **无法连接到PocketBase**
   - 检查PocketBase是否正在运行 (默认端口: 8090)
   - 检查认证凭据是否正确

2. **数据表创建失败**
   - 确保有足够的权限创建数据表
   - 检查网络连接

3. **API请求失败**
   - 检查CORS设置
   - 确认API端点URL正确

### 调试

启用调试模式：

```bash
DEBUG=true python pocketbase_integration.py
```

## 许可证

MIT License