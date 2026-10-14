#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai_passport.py — AI 护照身份档案参考实现
==========================================
为每一个 AI 系统签发一份机器可读的『AI 护照』JSON：
  schema_version / passport_id / issuer / model / intended_use
  / risk_class(I–IV) / training_data_refs / conformance_claims
  / issued_at / hash

`issue()`  对规范化 JSON 计算 SHA-256 作为防篡改指纹
`verify()` 校验指纹 + 必填字段 + 风险分级合法
必填字段含 intended_use（预期用途为 AI 护照的实质内容，不允许空签发）。
零依赖（仅 Python 3.8+ 标准库）。（对应『AI 护照系统』能力缺口。）
"""
from __future__ import annotations
import sys
import os
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone

SCHEMA_VERSION = "ai-passport/1.0"
VALID_RISK = {"I", "II", "III", "IV"}
# intended_use 为必填：预期用途是护照的实质内容（领域复审 P1 修复项）
REQUIRED = ["passport_id", "issuer", "model", "intended_use", "risk_class"]


def _sanitize_id(name: str) -> str:
    """把模型名规范为 passport_id 安全片段（防路径/空格注入）。"""
    return re.sub(r"[^a-z0-9\-]", "-", name.strip().lower()) or "unnamed"


def _canonical(obj: dict) -> bytes:
    # 排除 hash 字段后做稳定序列化，保证指纹可复现
    o = {k: v for k, v in obj.items() if k != "hash"}
    return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def issue(name: str, risk_class: str, issuer: str = "@stevenzhao07/MedXpert",
          intended_use: str = "", training_data_refs: list | None = None,
          conformance_claims: list | None = None) -> dict:
    if risk_class not in VALID_RISK:
        raise ValueError(f"risk_class 须为 {sorted(VALID_RISK)} 之一")
    if not intended_use or not intended_use.strip():
        raise ValueError("intended_use 为必填：AI 护照须声明预期用途（领域复审 P1 修复项）")
    pp = {
        "schema_version": SCHEMA_VERSION,
        "passport_id": f"pp-{_sanitize_id(name)}-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        "issuer": issuer,
        "model": name,
        "intended_use": intended_use,
        "risk_class": risk_class,
        "training_data_refs": training_data_refs or [],
        "conformance_claims": conformance_claims or [],
        "issued_at": datetime.now(timezone.utc).isoformat(),
    }
    pp["hash"] = hashlib.sha256(_canonical(pp)).hexdigest()
    return pp


def verify(pp: dict) -> list[str]:
    errs = []
    for k in REQUIRED:
        if not pp.get(k):
            errs.append(f"缺少必填字段: {k}")
    if pp.get("risk_class") and pp.get("risk_class") not in VALID_RISK:
        errs.append(f"risk_class 非法: {pp.get('risk_class')}")
    if "hash" not in pp:
        errs.append("缺少 hash 指纹")
    else:
        expect = hashlib.sha256(_canonical(pp)).hexdigest()
        if expect != pp["hash"]:
            errs.append("指纹校验失败（内容被篡改）")
    return errs


def _demo() -> int:
    pp = issue("ortho-ai-demo", "II", intended_use="骨科植入物风险分诊辅助（演示）")
    print(json.dumps(pp, ensure_ascii=False, indent=2))
    errs = verify(pp)
    print("\n[demo] 自验证:", "PASS 指纹一致、字段合法。" if not errs else f"BLOCK {errs}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="AI 护照签发/验证")
    ap.add_argument("--demo", action="store_true", help="跑内置样例护照并自验证")
    ap.add_argument("--selftest", action="store_true", help="跑内置自测（断言 + 负对照 + xfail）")
    sub = ap.add_subparsers(dest="cmd")
    pi = sub.add_parser("issue", help="签发护照")
    pi.add_argument("--name", required=True)
    pi.add_argument("--risk-class", required=True, choices=sorted(VALID_RISK))
    pi.add_argument("--intended-use", required=True,
                    help="预期用途（必填：AI 护照须声明预期用途）")
    pi.add_argument("--out", default="passport.json")
    pv = sub.add_parser("verify", help="验证护照")
    pv.add_argument("file", help="护照 JSON 路径")
    args = ap.parse_args()
    if getattr(args, "selftest", False):
        return _selftest()
    if args.demo:
        return _demo()

    if args.cmd == "issue":
        try:
            pp = issue(args.name, args.risk_class, intended_use=args.intended_use)
        except ValueError as e:
            print(f"[error] {e}", file=sys.stderr)
            return 2
        parent = os.path.dirname(os.path.abspath(args.out))
        try:
            os.makedirs(parent, exist_ok=True)
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(pp, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"[error] 无法写入 {args.out}: {e}", file=sys.stderr)
            return 2
        print(f"[issued] {args.out}  (risk_class={args.risk_class})")
        return 0
    if args.cmd == "verify":
        # 友好处理缺失/坏 JSON/空文件（2026-10-12 压力测试修复）
        if not os.path.isfile(args.file):
            print(f"[error] 护照文件不存在: {args.file}", file=sys.stderr)
            return 2
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                pp = json.load(f)
        except (ValueError, UnicodeDecodeError) as e:
            print(f"[error] 不是合法 JSON 护照: {args.file}（{e}）", file=sys.stderr)
            return 2
        if not isinstance(pp, dict):
            print("[error] 护照须为 JSON 对象", file=sys.stderr)
            return 2
        errs = verify(pp)
        if errs:
            print("[BLOCK] 验证未通过:")
            for e in errs:
                print(f"  - {e}")
            return 1
        print("[PASS] 护照有效，指纹一致。")
        return 0
    ap.print_help()
    return 2


# ==================== 内置自测（--selftest） ====================
# 由 conformance 补丁于 2026-10-14 生成（生成器 v2）。
# 特性：端到端 CLI 调用 + 内容断言 + 负对照 + xfail（已知缺陷显式标注，不掩盖）。
_SELFTEST_CASES = [(['--demo'], 0, [], [], None), (['issue', '--name', 'X', '--risk-class', 'II', '--intended-use', 'diagnosis'], 0, ['issued'], [], None)]


def _selftest() -> int:
    import os as _os
    import subprocess as _sp
    _here = _os.path.dirname(_os.path.abspath(__file__))
    # 仓库根：脚本位于 <repo>/scripts/ 时取上一级；否则取脚本所在目录
    _root = _os.path.dirname(_here) if _os.path.basename(_here) == "scripts" else _here
    _script = _os.path.abspath(__file__)
    _fail, _xfail, _n = [], [], 0
    for _case in _SELFTEST_CASES:
        _args, _rc, _must, _mustnot = _case[0], _case[1], _case[2], _case[3]
        _reason = _case[4] if len(_case) > 4 else None
        _n += 1
        _p = _sp.run([sys.executable, _script] + _args, capture_output=True, cwd=_root)
        _out = _p.stdout.decode("utf-8", "replace")
        _bad = []
        if _p.returncode != _rc:
            _bad.append(f"rc={_p.returncode} 期望 {_rc}")
        for _m in _must:
            if _m not in _out:
                _bad.append(f"输出缺少 {_m!r}")
        for _m in _mustnot:
            if _m in _out:
                _bad.append(f"输出含禁止内容 {_m!r}")
        if _rc == 0 and not _out.strip():
            _bad.append("rc=0 但输出为空（假绿）")
        if _bad:
            if _reason:
                _xfail.append(f"xfail args={_args}：{'；'.join(_bad)} ← 已知缺陷：{_reason}")
            else:
                _fail.append(f"args={_args}：{'；'.join(_bad)}")
    # 通用负对照：未知参数必须非零
    _n += 1
    _p = _sp.run([sys.executable, _script, "--__nonexistent_flag__"], capture_output=True, cwd=_root)
    if _p.returncode == 0:
        _fail.append("负对照失败：未知参数竟返回 0")
    for _x in _xfail:
        print("[selftest][xfail] " + _x)
    if _fail:
        print(f"[selftest] FAILED {len(_fail)}/{_n}")
        for _f in _fail:
            print("  - " + _f)
        return 1
    print(f"[selftest] PASS {_n - len(_xfail)}/{_n}（含负对照；xfail {len(_xfail)} 项为已知缺陷）")
    return 0


if __name__ == "__main__":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
