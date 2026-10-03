# WechatVibe（silicon-sbt 的个人 fork）

上游仓库：[tswawa/WechatVibe](https://github.com/tswawa/WechatVibe)。

本 fork 在上游 **v1.2.3** 的基础上，放进了我们自己提给上游的修复和一套自用改动，
方便自己构建、也给朋友用。上游的功能说明、下载安装、隐私与免责声明请以上游仓库为准。

## 我们的改动

### 一、提给上游的 PR

| PR | 内容 | 状态 |
| --- | --- | --- |
| [#13](https://github.com/tswawa/WechatVibe/pull/13) | 逐条情绪 / 意图：宽情绪题（粗粒度 19.7% → 64.3%）、`caring` / `surprised` 选项（38.9% → 57.2%）、悬空判断句守卫、schema `generic-v9` → `generic-v10`；顺带修掉 [#14](https://github.com/tswawa/WechatVibe/issues/14) 的 API 逐条标签 | **已合并**（只采纳 API 标签部分，见下） |
| [#10](https://github.com/tswawa/WechatVibe/pull/10) | 本地分析多 worker 并行 + 弹性负载调节 | 开放：已按 review 修掉四处并收窄范围 |
| [#18](https://github.com/tswawa/WechatVibe/pull/18) | 服务号 / 系统会话不进会话列表（本机 203 → 149） | 开放 |
| [#19](https://github.com/tswawa/WechatVibe/pull/19) | 一键把全部会话加进侧边栏（首次自动填满 + 新会话跟进） | 开放 |
| [#20](https://github.com/tswawa/WechatVibe/pull/20) | 只读的整账号分析进度 / 耗时接口 | 开放 |
| [#21](https://github.com/tswawa/WechatVibe/pull/21) | 后台分析全部会话的开关、侧栏总进度与并行档位（依赖 #20 与 #10） | 开放 |
| [#17](https://github.com/tswawa/WechatVibe/pull/17) | 消息内嵌图片直接显示（点击放大） | 开放；上游表示改动面较大、后续自己做，本 fork 保留该功能 |

**#13 的采纳情况**（上游在 1.2.3 里手工移植）：

- **采纳**：API 模式逐条标签改用短编号逐条输出（prompt 约 1000 → 440 字节），这条同时修掉 [#14](https://github.com/tswawa/WechatVibe/issues/14)；
  上游另补上了乱序、重复与流式结果的对应。
- **未采纳（本 fork 保留）**：逐条显示改用宽情绪题、`caring` / `surprised` 选项、标签 schema `generic-v10`。
  上游的理由是「会让已保存的结果全部重算」，并希望情绪题单独提 PR 再议。
- **未采纳（已丢弃）**：画像输出的容错解析 —— 上游指出 `I:70` 会被算成偏 E 70%（方向反了），
  且 1.2.3 的画像已改为程序统一计分，这段逻辑不再需要。

**#10 按 review 修掉的问题**：

- `subprocess` 从未导入，探测 `nvidia-smi` 一直抛 `NameError` 又被 `except` 吞掉——显卡 / 显存检测实际从未生效；
- 每次采样都新建 `psutil.Process()`，`cpu_percent(interval=None)` 恒为 0，自身占用扣不掉；
- 上限降到 0 时，**已经阻塞在 `tasks.get()` 上**的 worker 仍会取走新任务（现改为取到任务后复查上限，超限就放回队列）；
- 监控线程退出后句柄没清空，账号清除失败后 resume 时弹性模式不会重启。

服务号过滤、会话全选、统计接口与结果库 WAL 已从这个 PR 移出，分别走 #18 / #19 / #20。

### 二、自用改动（已并入 `main`）

这套改动最初做在 v1.2.0 上；上游 1.2.2 重构了后端与前端模块，1.2.3 又重写了画像，
所以按功能逐块重写了两轮，现在跟着 v1.2.3 走：

- 会话一次全量加载 + 「全部添加」按钮 + 新会话自动补进侧栏（→ [#19](https://github.com/tswawa/WechatVibe/pull/19)）；
- 服务号 / 系统号过滤（`gh_`、`brandsessionholder`、`notifymessage` 等，保留 `filehelper` 与群聊）（→ [#18](https://github.com/tswawa/WechatVibe/pull/18)）；
- 设置里的「后台分析全部会话」开关、侧栏总进度条与「本地分析并行数」档位（→ [#20](https://github.com/tswawa/WechatVibe/pull/20) + [#21](https://github.com/tswawa/WechatVibe/pull/21)）；
- 消息内嵌图片渲染，点击放大；首次需在微信里点开一张图以派生解密密钥（→ [#17](https://github.com/tswawa/WechatVibe/pull/17)）。

每个拆出来的 PR 都带一个**在补丁前会失败**的测试；`main` 上 `tsc`、Node 测试 409 项与 Python 全套通过。

### 三、与上游的已知分歧

保留自用判定逻辑会带来两处可预期的不一致，下次升级上游时需要留意：

- 情绪题是 **8 个桶**（`caring` 取代 `affectionate`，`surprised` 从 `amused` 拆出），上游是 7 个。
  因此 `tests/api-portrait-classifier.test.ts` 的两处断言按本 fork 的题库调整过（59 → 60、`affectionate` → `caring`）。
- 逐条显示走宽情绪题 `EMOTION_QUESTION`，上游的逐条显示仍走 18 个立场词。

升级上游时的做法：以目标版本为底座做三方合并（base = 上一版上游 / ours = 本 fork / theirs = 目标版本），
自用改动按功能逐块重贴；直接整体覆盖会把这套改动冲掉。v1.2.0 上那份原始补丁仍原样存档在
[`selfuse/v1.2.0`](https://github.com/silicon-sbt/WechatVibe/tree/selfuse/v1.2.0) 分支，仅作历史对照，不再维护。

## 分支

| 分支 | 内容 |
| --- | --- |
| `main` | 跟随上游 v1.2.3 + 「自用改动」 |
| `feat/selfuse-on-1.2.3` | 自用改动搬到 1.2.3 的开发分支（已并入 `main`） |
| `feat/parallel-analysis-workers` | PR #10 多 worker 并行 |
| `fix/emotion-question-options` | PR #13 逐条情绪 / 意图（含 #14 的修复，已合并） |
| `feat/service-account-filter` | PR #18 服务号过滤 |
| `feat/conversation-add-all` | PR #19 一键全部添加 |
| `feat/analysis-overview` | PR #20 只读进度 / 耗时接口 |
| `feat/background-sweep-ui` | PR #21 后台分析开关与进度条 |
| `feat/inline-image` | PR #17 消息内嵌图片 |
| `feat/selfuse-on-1.2.2` | 自用改动搬到 1.2.2 的开发分支（历史） |
| `selfuse/v1.2.0` | v1.2.0 + 旧的原始自用补丁（存档，不再维护） |

## 许可

沿用上游 [Apache-2.0](LICENSE) 许可证。
