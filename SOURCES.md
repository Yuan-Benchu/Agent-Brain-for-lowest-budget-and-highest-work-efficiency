# 设计取舍与参考

查阅日期：2026-09-10。Agent Brain 的使用入口是 [执行流程](skills/agent-brain/references/operating-playbook.md) 和 [本地代码](skills/agent-brain/scripts/brain.py)。这一页用于追溯设计，不是让使用者去其他项目自行拼装方案。

| 启发来源 | 我们采用的具体设计 | 本仓库的落点与取舍 |
| --- | --- | --- |
| [RTK](https://github.com/rtk-ai/rtk) 的命令输出过滤 | 原文留在文件；送入上下文的是失败关键行、相邻内容、退出码和检索位置 | `brain.py digest`。采用通用日志摘取，不实现 RTK 的命令专用解析器；省略信息显式标记，失败原因可能需要回查 |
| [ccusage](https://github.com/ccusage/ccusage) 的分组用量观察 | 以任务/调用为单位记录，再按 Agent、池、指标、单位汇总；未知值单独计数 | `brain.py account`。处理显式传入的事件，不扫描账号日志；要求调用自身的增量，拒绝重复事件和父级汇总 |
| [Context Engineering Skills](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) 的状态与上下文管理 | 固定保留交付约束，相关信息局部加载，成功输出收缩，当前状态覆盖过时计划，交接前检查信息是否足够 | 执行手册第 3 节及任务包约定。以可执行的交接过程代替泛泛的“少读上下文” |
| [RouteLLM](https://github.com/lm-sys/RouteLLM) 的任务路由与校准 | 先过能力和质量门槛，再检查池与预留额度，最后比较完整任务估算；不能比较时明确退回配置偏好 | `brain.py plan`。原创确定性规则，不加载训练路由模型，不增加 embedding 请求；通过实际返工成本修正后续偏好 |
| [LLMLingua](https://github.com/microsoft/LLMLingua) 的上下文预算思路 | 保留目标、权限、验收和精确标识；压缩冗余后检查任务能否继续执行 | 执行手册第 3 节与日志摘取预算。采用结构化删冗与局部检索，不声称实现其学习式压缩算法或性能 |
| [acpx](https://github.com/openclaw/acpx) 的会话与结构化交互 | 统一任务包、会话 ID、状态、返回结果及续接约定；依赖顺序执行，超时先查状态 | 执行手册第 4–5 节。由主控映射到实际可用渠道；桌面、CLI 和 API 仍分别验证，不将协议相似视为已接通 |

这些设计共同形成 Agent Brain 自己的工作闭环：选人 → 交接 → 执行 → 修复 → 验收 → 用结果改进下次选择。代码和文字独立编写，未复制上述项目的实现或大段提示词；无需安装它们即可使用本仓库的辅助工具。

可复查的行为验证在 [test_brain.py](evaluations/test_brain.py)，执行记录在 [results.md](evaluations/results.md)。本项目没有将上游宣传数字转换为自己的效果承诺。
