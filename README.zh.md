# Claude Code 网红寻源插件

从Instagram和TikTok查找、评分和排名网红/创作者候选人——由Apify抓取和Gemini AI评分驱动。

## 功能

- **按利基关键词从TikTok和Instagram寻找创作者**
- **使用Gemini对每个创作者的品牌匹配度进行AI评分**（1-10）
- **生成引用每个创作者实际内容的个性化外联DM**
- **导出CSV**供团队使用

## 设置

### 1. 安装插件
```bash
claude --plugin-dir /path/to/influencer-sourcing-plugin
```

### 2. 设置环境变量
```bash
export APIFY_TOKEN="your_apify_api_key"
export GEMINI_API_KEY="your_gemini_api_key"
```

### 3. 安装Python依赖
```bash
pip install requests
```

## 使用

### 快速寻源
```
/influencer-sourcing:source-influencers 清洁美容 护肤
```

### 对品牌简报评分
```
/influencer-sourcing:score-creators 品牌名 - 面向25-40岁女性的清洁美容保健品
```

### 导出结果
```
/influencer-sourcing:export-csv
```
