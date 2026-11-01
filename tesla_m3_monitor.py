#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tesla 中国官网 Model 3 认证二手车监控
- 数据源: https://www.tesla.cn/inventory/api/v4/inventory-results (公开页面对应接口)
- 基线:   /home/user/Doubao/chats/34278022675783170/tesla_m3_used_baseline.json
- 仅播报: 新上架(VIN 首次出现)、降价(同 VIN 现价 < 基线价)
- 首轮: 基线不存在 -> 仅建立基线，不播报新上架
- 接口/页面读取失败: 非零退出，不改动基线
"""
import json, os, sys, re, time, urllib.parse, urllib.request, http.cookiejar, datetime, traceback

BASELINE = "/home/user/Doubao/chats/34278022675783170/tesla_m3_used_baseline.json"
LIST_PAGE = "https://www.tesla.cn/inventory/used/m3"
API = "https://www.tesla.cn/inventory/api/v4/inventory-results"
REPORT_BASE = "https://www.tesla.cn/inventory/api/v4/files/"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def fetch_results():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.addheaders = [
        ("User-Agent", UA),
        ("Accept", "application/json"),
        ("Referer", LIST_PAGE),
    ]
    inner = {
        "model": "m3", "condition": "used", "options": {},
        "arrangeby": "price", "order": "asc",
        "market": "CN", "language": "zh", "super_region": "CN",
    }
    payload = {"query": inner, "offset": 0, "count": 500,
               "outsideOffset": 0, "outsideSearch": False}
    q = urllib.parse.urlencode({"query": json.dumps(payload, ensure_ascii=False)})
    url = API + "?" + q
    last_err = None
    for attempt in range(3):
        try:
            r = op.open(url, timeout=30)
            raw = r.read().decode("utf-8", "ignore")
            data = json.loads(raw)
            if not isinstance(data, dict) or "results" not in data:
                raise ValueError("响应缺少 results 字段: " + raw[:200])
            return data
        except Exception as e:
            last_err = e
            time.sleep(2 + attempt * 2)
    raise RuntimeError(f"接口读取失败: {last_err}")


def _opt(opts, group):
    for x in opts:
        if x.get("group") == group:
            return x
    return {}


def parse_one(r):
    opts = r.get("OptionCodeData", [])
    paint = _opt(opts, "PAINT").get("description") or ""
    wheels = _opt(opts, "WHEELS").get("description") or ""

    # 续航: 优先取 OptionCodeSpecs 展示口径(标注 CLTC/NEDC)
    range_km, range_std = "", ""
    specs = (r.get("OptionCodeSpecs") or {}).get("C_SPECS", {}).get("options", [])
    for s in specs:
        if s.get("code") == "SPECS_RANGE":
            range_km = re.sub(r"[^\d]", "", s.get("name", ""))
            desc = s.get("description", "")
            range_std = "CLTC" if "CLTC" in desc else ("NEDC" if "NEDC" in desc else "")
    if not range_km:
        rg = _opt(opts, "SPECS_RANGE")
        range_km = str(rg.get("value", ""))
        range_std = "NEDC" if "NEDC" in rg.get("range_source", "") else "CLTC"

    trim_name = r.get("TrimName", "")
    # 批次标签(尾部 YYYY-MM)
    m = re.search(r"(\d{4}-\d{2})\s*$", trim_name)
    batch_label = m.group(1) if m else ""
    # 版本描述: 去掉 "Model 3" 前缀、交付来源、批次标签
    version = trim_name
    version = re.sub(r"^Model 3\s*", "", version)
    version = re.sub(r"\s*特斯拉中国\s*" + re.escape(batch_label) + r"\s*$", "", version)
    version = re.sub(r"\s*" + re.escape(batch_label) + r"\s*$", "", version)
    version = version.strip()

    # 平台判定: 2023-10 起 Highland 焕新平台
    platform = "Highland焕新平台" if batch_label >= "2023-10" else "老平台(怀挡拨杆)"

    # 上牌月份: 首次交付日期; 缺失时回退出厂月份 / 批次标签
    first_reg = (r.get("OriginalDeliveryDate") or "")[:7]
    if not first_reg:
        g = (r.get("FactoryGatedDate") or "")[:7]
        first_reg = g if g else batch_label

    price = r.get("TotalPrice") or r.get("Price") or r.get("InventoryPrice")
    guid = r.get("InspectionDocumentGuid")
    return {
        "vin": r["VIN"],
        "year": r.get("Year"),
        "version": version,
        "batch_label": batch_label,
        "platform": platform,
        "first_reg_month": first_reg,
        "odometer_km": r.get("Odometer"),
        "price": price,
        "city": r.get("VehicleCity") or r.get("City") or "",
        "province": r.get("StateProvince") or "",
        "wheels": wheels,
        "range_km": range_km,
        "range_std": range_std,
        "paint": paint,
        "trim_name": trim_name,
        "report_url": (REPORT_BASE + guid) if guid else "",
        "order_url": f"https://www.tesla.cn/m3/order/{r['VIN']}",
        "vrl_name": r.get("VrlName") or "",
    }


def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    now_iso = now.isoformat(timespec="seconds")

    data = fetch_results()
    current = {p["vin"]: p for p in (parse_one(x) for x in data["results"])}
    total_found = data.get("total_matches_found", len(current))

    baseline_exists = os.path.exists(BASELINE)
    baseline = {"vehicles": {}}
    if baseline_exists:
        with open(BASELINE, encoding="utf-8") as f:
            baseline = json.load(f)

    old = baseline.get("vehicles", {})
    is_first_round = not baseline_exists or not old

    new_list, drops, removed = [], [], []
    if not is_first_round:
        for vin, cur in current.items():
            if vin not in old:
                new_list.append(cur)
            else:
                old_price = old[vin].get("price")
                if isinstance(old_price, int) and isinstance(cur["price"], int) and cur["price"] < old_price:
                    cur2 = dict(cur)
                    cur2["old_price"] = old_price
                    cur2["drop"] = old_price - cur["price"]
                    drops.append(cur2)
        for vin, prev in old.items():
            if vin not in current:
                removed.append({"vin": vin, "price": prev.get("price"),
                                 "city": prev.get("city"), "version": prev.get("version")})

    # 刷新基线(成功读取后)
    new_baseline = {
        "baseline_created_at": baseline.get("baseline_created_at", now_iso),
        "updated_at": now_iso,
        "round": int(baseline.get("round", 0)) + 1,
        "source": LIST_PAGE,
        "total_found": total_found,
        "vehicles": current,
    }
    os.makedirs(os.path.dirname(BASELINE), exist_ok=True)
    with open(BASELINE, "w", encoding="utf-8") as f:
        json.dump(new_baseline, f, ensure_ascii=False, indent=2)

    out = {
        "fetched_at": now_iso,
        "is_first_round": is_first_round,
        "total_found": total_found,
        "current_count": len(current),
        "new_list": new_list,
        "drops": drops,
        "removed": removed,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        print(json.dumps({"error": str(e), "action": "baseline_not_touched"}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
