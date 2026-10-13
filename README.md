# ai-model-passport

> **Contributed by [@stevenzhao07](https://github.com/stevenzhao07) · Affiliation: MedXpert (medical-device RA & regulatory consultancy) · Pure technical input, no commercial promotion.**

把「护照官（AI 护照制度）」理念做成可部署的参考实现：为每一个 AI 系统签发一份机器可读的『AI 护照』JSON（身份、模型卡引用、训练数据、预期用途、风险分级、符合性声明、签发哈希），支持签发与验证。（对应『AI 护照系统』能力缺口。）

这是 MedXpert 把"医疗 AI 信任"方法论工程化落地的可插拔模块之一——把抽象的合规要求变成一条可重复运行的命令或参考实现。方法论四要素（白话版）：**治理守护者 XCGS** ＝ 为 AI 留下可核验的治理证据；**立法者 A³ Laws** ＝ 给自主系统划权限 / 监督 / 追责三条硬边界；**护照官 AI 护照** ＝ 为模型签发可追溯的身份凭证；**人机共存** ＝ 明确人类与 AI 的分工与兜底。

---

## 可插拔模块契约（lgd-skeleton/1.0）

本仓库是一个 **`lgd-skeleton/1.0` 可插拔模块**：

- **一切即插件**：仅依赖声明式 `module.json`，零配置；
- **按需装（lazy）**：仅 triggers 命中时加载；
- **可嵌套（nested）**：可被 `medical-ai-toolkit` 总入口路由发现；
- **扩展点**：`plugins/`(新增符合性声明类型：在 `CONFORMANCE_CLAIMS` 枚举扩展，验证器自动校验。)。

机器可发现入口：`AGENTS.md` · `CLAUDE.md` · `llms.txt`。

## 特性

- 护照 schema：schema_version / passport_id / issuer / model / intended_use / risk_class(I–IV) / training_data_refs / conformance_claims / issued_at / hash
- 签发：`issue()` 对规范化 JSON 计算 SHA-256 作为防篡改指纹
- 验证：`verify()` 校验指纹 + 必填字段 + 风险分级合法
- 零依赖 + CLI：`issue` / `verify` 子命令

## 内容说明

AI 护照 = 给 AI 系统一张『身份证』，让监管、医院、患者都能查到它从哪来、能干什么、风险多高。

## 免责声明

本工具仅提供结构化模板与计算能力，**不构成法规建议、合规结论或专业意见**。医疗 AI / 医疗器械相关的落地决策，须由合资格人员依据目标辖区（NMPA / FDA / EU MDR / PMDA）最新法规文本作出；条款与限值以官方发布文本为准。使用本工具产生的一切后果由使用者自行承担。

## 使用

```bash
python scripts/ai_passport.py issue --name ortho-ai --risk-class II --intended-use "骨科植入物风险分诊辅助"
python scripts/ai_passport.py verify passport.json
```

> `--intended-use` 为必填：预期用途是 AI 护照的实质内容，不允许空签发。

## 快速开始（30 秒）

```bash
git clone https://github.com/stevenzhao07/ai-model-passport.git && cd ai-model-passport
python scripts/ai_passport.py --demo
```

> 想参与或遇到问题？[提 Issue](https://github.com/stevenzhao07/ai-model-passport/issues) · 完整《AI 参与指南》见 [medical-ai-toolkit](https://github.com/stevenzhao07/medical-ai-toolkit)。

## 路由（总入口）

本模块由 **[medical-ai-toolkit](https://github.com/stevenzhao07/medical-ai-toolkit)** 作为 `lgd-skeleton/1.0` 总入口自动路由发现。

## 关联模块

- [ai-a3-laws](https://github.com/stevenzhao07/ai-a3-laws)
- [ai-governance-checklist](https://github.com/stevenzhao07/ai-governance-checklist)
- [delivery-guard](https://github.com/stevenzhao07/delivery-guard)

## 许可

CC0 — 见 [LICENSE](./LICENSE)。

## 关联（方法论来源）

- 理念溯源：个人专家关于医疗 AI 信任与治理的公开方法论（个人观点，不构成标准）
- 同账号系列：见 `medical-ai-toolkit` 导航
