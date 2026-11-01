import os
from datetime import datetime

HTML_TPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Model3 认证二手车｜性价比监控看板</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        body {{
            background: #121212;
            color: #eee;
            padding: 16px;
            max-width: 800px;
            margin: 0 auto;
        }}
        .header {{
            border-bottom: 1px solid #333;
            padding-bottom: 12px;
            margin-bottom: 16px;
        }}
        .header h1 {{
            font-size: 22px;
            color: #fff;
        }}
        .update-time {{
            color: #aaa;
            font-size: 14px;
            margin-top: 6px;
        }}
        .tip-box {{
            background: #1a2433;
            border-left: 4px solid #4285f4;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 18px;
            font-size: 14px;
            line-height: 1.5;
        }}
        .rank-card {{
            border-radius: 8px;
            padding: 14px;
            margin-bottom: 14px;
        }}
        .s-rank {{
            background: #182c22;
            border: 1px solid #27ae60;
        }}
        .a-rank {{
            background: #28261c;
            border: 1px solid #f39c12;
        }}
        .b-rank {{
            background: #202230;
            border: 1px solid #3498db;
        }}
        .c-rank {{
            background: #2c1c1c;
            border: 1px solid #e74c3c;
        }}
        .rank-title {{
            font-size: 17px;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .price-tag {{
            color: #ffd066;
            font-weight: 500;
        }}
        .good, .bad {{
            font-size: 14px;
            margin-top: 6px;
            line-height: 1.5;
        }}
        .good span {{
            color: #73d188;
        }}
        .bad span {{
            color: #ff8888;
        }}
        .monitor-area {{
            margin-top: 24px;
            border-top: 1px solid #333;
            padding-top: 16px;
        }}
        .monitor-area h2 {{
            font-size: 19px;
            margin-bottom: 12px;
        }}
        .target-mark {{
            color: #73d188;
            font-weight: bold;
        }}
        .alt-mark {{
            color: #ffd066;
            font-weight: bold;
        }}
        .log-item {{
            background: #1e1e1e;
            padding:10px;
            border-radius:6px;
            margin-bottom:8px;
            font-size:14px;
            line-height:1.45;
        }}
        .footer-note {{
            margin-top:24px;
            color:#999;
            font-size:13px;
            line-height:1.5;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏁 Model3 特斯拉认证二手车 性价比看板</h1>
        <div class="update-time">最近更新：{now_str}</div>
    </div>

    <div class="tip-box">
        ✅ 适用场景：深圳单人通勤、预算14–20w、在意颈椎/脊柱舒适性、优先省心耐用；
        ⚠️ 重要红线：FSD/EAP过户后会回收，不要为智驾软件溢价买单；
        📌 两代区分：Highland焕新版（2023-10后，带通风+后排8寸屏）｜老平台21/22款（无通风，不优先）
    </div>

    <!-- S级 首选目标 -->
    <div class="rank-card s-rank">
        <div class="rank-title">🏆 S级｜主目标（监控置顶【目标匹配✅】）</div>
        <div>2023-10 Highland 后轮驱动版｜珍珠白/冷光白 + 原厂18英寸光子轮毂</div>
        <div class="price-tag">行情参考：2–4万公里，17.2w ~ 18.3w｜好价锚点：≤17.5w</div>
        <div class="good"><span>✅优点：</span>能耗最优、胎壁厚抗鼓包、滤震友好、前排座椅通风、保值率最高</div>
        <div class="bad"><span>❌缺点：</span>货源稀缺，上架容易被抢</div>
    </div>

    <!-- A级 备选 -->
    <div class="rank-card a-rank">
        <div class="rank-title">🥈 A级｜备选兜底（监控标记【备选高性价比✅】）</div>
        <div>A2：2023-10 Highland 后驱｜黑色车漆 + 18寸轮毂</div>
        <div class="price-tag">行情参考：同里程比白色便宜4k~7k</div>
        <div class="good"><span>✅优点：</span>硬件和目标完全一致，货源多、性价比高</div>
        <div class="bad"><span>❌缺点：</span>不是白色车漆，不符合颜值偏好</div>
        <br>
        <div>A1：2023-10 Highland 后驱｜白色 + 19寸新星轮毂</div>
        <div class="price-tag">行情参考：同里程比18寸便宜3k~6k</div>
        <div class="good"><span>✅优点：</span>外观好看</div>
        <div class="bad"><span>❌缺点：</span>续航缩水、胎易鼓包、胎噪更大、底盘更硬，对你脊柱不友好</div>
    </div>

    <div class="rank-card a-rank">
        <div class="rank-title">🥈 A级｜预算极限备选（不主动蹲）</div>
        <div>2021/2022老平台后驱，18寸轮毂</div>
        <div class="price-tag">行情参考：13.5w ~ 15.5w</div>
        <div class="good"><span>✅优点：</span>价格便宜，保有量大</div>
        <div class="bad"><span>❌缺点：</span>无座椅通风、隔音差、老车机，舒适性短板明显</div>
    </div>

    <!-- B级 一般 -->
    <div class="rank-card b-rank">
        <div class="rank-title">🥉 B级｜性价比一般，按需选择</div>
        <div>Highland 长续航全轮驱动版</div>
        <div class="price-tag">行情参考：19w ~ 21w，容易顶预算上限</div>
        <div class="good"><span>✅优点：</span>续航更长、四驱雨雪稳定</div>
        <div class="bad"><span>❌缺点：</span>电耗更高、溢价高；你年里程仅5000km，几乎用不上四驱和长续航</div>
    </div>

    <!-- C级 避雷 -->
    <div class="rank-card c-rank">
        <div class="rank-title">❌ C级｜不推荐/避雷</div>
        <div>1. Performance高性能版：普遍22w+，超预算，代步溢价严重</div>
        <div>2. 里程＞6万公里焕新版：电池循环多，折旧风险上升</div>
        <div>3. 2020及更早老款：无热泵、车机卡顿</div>
        <div>4. 特殊红漆版本：车漆溢价高，二手折价更大</div>
    </div>

    <!-- 每日监控数据区域 -->
    <div class="monitor-area">
        <h2>📡 官网认证二手车监控当日简报</h2>
        {report_content}
    </div>

    <div class="footer-note">
        监控续期节点：2026-11-30；<br>
        说明：本看板仅为个人参考，价格为特斯拉官网认证二手挂牌价，不含议价；所有车源以特斯拉中国官网实时页面为准。
    </div>

</body>
</html>"""


def main():
    report = os.getenv("REPORT", "暂无简报")
    update_time = os.getenv("UPDATE_TIME", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    lines = report.split("\n")
    report_html = ""
    for line in lines:
        if line.strip() != "":
            report_html += f'<div class="log-item">{line}</div>\n'
    out = HTML_TPL.format(now_str=update_time, report_content=report_html)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(out)
    print("rendered index.html at", update_time)


if __name__ == "__main__":
    main()
