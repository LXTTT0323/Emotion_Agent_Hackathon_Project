# Luminea iOS 应用

Luminea 是一款基于情绪和健康数据分析的 iOS 应用，通过收集和分析用户的健康数据，提供情绪跟踪和健康状况趋势分析。

## 功能页面

应用包含四个主要功能模块：

1. **情绪记录 (Emotion)** - 用户记录和跟踪每日情绪变化
2. **趋势分析 (Trends)** - 基于收集的数据展示情绪和健康趋势
3. **健康数据 (Data)** - 从 HealthKit 获取和展示健康数据
4. **设置 (Settings)** - 用户配置和账户管理

## 健康数据功能

健康数据页面（DataView）实现了以下功能：

- 请求并获取用户健康数据（HealthKit）权限
- 获取并显示各类健康指标：
  - 心率 (Heart Rate)
  - 心率变异性 (HRV)
  - 睡眠时长 (Sleep Hours)
  - 步数 (Steps)
  - 活动能量消耗 (Active Energy Burned)
  - 正念时间 (Mindful Minutes)
  - 情绪状态 (State of Mind)
  - 经期记录 (Period)
- 将健康数据发送到 Azure 后端 API

### 数据获取流程

1. 应用启动时检查 HealthKit 权限状态
2. 若未授权，提示用户授权访问健康数据
3. 获得授权后，应用读取最近的健康数据
4. 数据以卡片形式展示在界面上
5. 用户可触发"同步数据到服务器"将数据发送至 Azure 后端

## Azure 后端 API

为支持数据分析和存储，项目包含一个部署在 Azure 上的 FastAPI 后端服务。

### API 架构

- **技术栈**：Python FastAPI, Azure App Service
- **API 基础 URL**：https://luminea-cheme6xxxxx.australiacentral-01.azurewebsites.net
- **API 文档**：https://luminea-cheme6xxxxx.australiacentral-01.azurewebsites.net/docs

### 部署信息

- **资源组**：logicnovasolution.au.com
- **区域**：Australia Central
- **服务计划**：已创建的 App Service 计划

### 部署新版本

如需部署新版本的 API，请使用项目根目录下的部署脚本：

```bash
cd azure_api
python deploy.py
```

## 后端 API 规范

### 健康数据上传 API

**端点**: `POST /api/health-data`

**请求头**:

```
Content-Type: application/json
Authorization: Bearer {user_token}
```

**请求体**:

```json
{
  "userId": "string",
  "timestamp": "number",
  "heartRate": "number",
  "heartRateVariability": "number",
  "sleepHours": "number",
  "steps": "number",
  "activeEnergyBurned": "number",
  "mindfulMinutes": "number",
  "stateOfMind": "string",
  "lastPeriodDate": "string"
}
```

**字段说明**:

- `userId`: 用户唯一标识
- `timestamp`: 数据记录时间戳（Unix 时间戳，秒）
- `heartRate`: 心率，单位 BPM
- `heartRateVariability`: 心率变异性，单位毫秒(ms)
- `sleepHours`: 睡眠时长，单位小时
- `steps`: 步数，整数
- `activeEnergyBurned`: 活动能量消耗，单位卡路里
- `mindfulMinutes`: 正念冥想时间，单位分钟
- `stateOfMind`: 情绪状态，字符串
- `lastPeriodDate`: 上次经期日期，字符串

**响应**:

```json
{
  "success": true,
  "message": "数据接收成功",
  "dataId": "generated_data_id"
}
```

**错误响应**:

```json
{
  "success": false,
  "error": "错误代码",
  "message": "错误描述"
}
```

### 身份验证需求

- 所有 API 请求需要包含有效的 JWT 令牌
- 令牌通过用户登录获取
- 令牌包含用户 ID 和权限信息

## 开发注意事项

1. **HealthKit 权限**:

   - 应用已配置必要的 Info.plist 和 entitlements 权限
   - 请确保测试设备已授权应用访问健康数据

2. **数据安全**:

   - 健康数据属于敏感个人信息
   - 确保数据传输过程使用 HTTPS 加密
   - 不在本地持久化存储原始健康数据

3. **后端 API 集成**:

   - DataView.swift 中已实现 API 调用
   - API 地址：https://luminea-xxxx.regionalid-01.azurewebsites.net/api/health-data
   - 生产环境需更新为正确的 API 端点

4. **UI/UX 考量**:
   - 健康数据卡片设计采用黑色背景
   - 各数据类型使用不同颜色标识
   - 添加数据同步状态指示器

## 未来扩展

1. 增加更多健康指标（如血氧、血压等）
2. 实现数据导出功能
3. 增加历史数据查看和比较功能
4. 添加数据异常提醒
5. 在 Azure 后端实现数据分析和洞察功能
