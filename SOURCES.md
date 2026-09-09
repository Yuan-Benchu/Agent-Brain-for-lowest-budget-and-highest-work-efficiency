# 方法来源

查阅日期：2026-09-10。下列链接是设计参考，不是安装依赖。上游声明不构成本 skill 的效果保证。

| 来源 | 吸收的方法 | 保留的边界 |
| --- | --- | --- |
| [RTK](https://github.com/rtk-ai/rtk) | 在工具输出进入上下文前，提取相关结果与失败信息 | 工具输出的压缩率不等于总费用节省率；保留原始证据 |
| [ccusage](https://github.com/ccusage/ccusage) | 从已有用量记录按任务、模型、时间观察消耗 | 费用估算不等于实际订阅扣款；注意字段和数据覆盖范围 |
| [Context Engineering Skills](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) | 渐进读取、精简交接、长会话状态摘要和有边界的分工 | 不导入整套技能；只加载当前工作需要的信息 |
| [RouteLLM](https://github.com/lm-sys/RouteLLM) | 根据任务选择强弱模型，并以实际任务校准质量与成本取舍 | 本 skill 不部署其 API 路由器，也不额外调用 embedding 服务 |
| [LLMLingua](https://github.com/microsoft/LLMLingua) | 用预算意识减少冗余上下文，并验证压缩后的任务质量 | 本 skill 不运行压缩模型；不损失关键约束和精确标识 |
| [acpx](https://github.com/openclaw/acpx) | 区分可用入口、会话管理和机器可读结果 | 协议统一不代表额度独立，也不代表桌面功能等价 |

未将上游模型价格、宣传压缩率或某个账号的额度写成永久规则。
