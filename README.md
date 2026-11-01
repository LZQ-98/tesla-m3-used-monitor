# Tesla Model3 认证二手车监控看板

- 用途：特斯拉官网 Model3 认证二手车性价比看板 + 每日监控简报
- 目标车源：2023-10 Highland 后驱｜白色（珍珠白/冷光白）+ 原厂18寸轮毂
- 备选车源：2023-10 Highland 后驱｜黑色 + 18寸轮毂
- 在线访问：https://lzq-98.github.io/tesla-m3-used-monitor/
- 更新方式：每日监控任务生成简报 → repository_dispatch 触发 workflow → render.py 渲染 → 自动 commit/push → GitHub Pages 刷新

## 目录
- `index.html`：看板页面
- `render.py`：简报渲染脚本（接收 REPORT/UPDATE_TIME 环境变量，写入 index.html）
- `.github/workflows/receive-report.yml`：接收 repository_dispatch 并自动提交

## 触发示例
```http
POST https://api.github.com/repos/LZQ-98/tesla-m3-used-monitor/dispatches
{
  "event_type": "submit-report",
  "client_payload": {
    "update_time": "2026-11-01 18:09:07",
    "report": "【基线状态】...\n【目标匹配✅】..."
  }
}
```
