# AGENTS.md · ai-model-passport

> 机器可发现入口（AI 编码代理 / Codex / Claude / Cursor）。单一事实源：本文件。

## 这是什么
把「护照官（AI 护照制度）」理念做成可部署的参考实现：为每一个 AI 系统签发一份机器可读的『AI 护照』JSON（身份、模型卡引用、训练数据、预期用途、风险分级、符合性声明、签发哈希），支持签发与验证。（对应『AI 护照系统』能力缺口。）

## 运行
```bash
python scripts/ai_passport.py --demo
python scripts/ai_passport.py --help
```

## 扩展契约（lgd-skeleton/1.0）
- **一切即插件**：仅依赖声明式 `module.json`，零配置。
- **按需装（lazy）**：仅 triggers 命中时加载。
- **可嵌套（nested）**：可被 `medical-ai-toolkit` 总入口路由。
- **扩展点**：`plugins/`(新增符合性声明类型：在 `CONFORMANCE_CLAIMS` 枚举扩展，验证器自动校验。)

## 红线
纯技术贡献，不含商业营销；MedXpert 仅作为贡献者署名（@stevenzhao07）。
