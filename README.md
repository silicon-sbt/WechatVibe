# WechatVibe（silicon-sbt 的个人 fork）

上游仓库：[tswawa/WechatVibe](https://github.com/tswawa/WechatVibe)。

本 fork 在上游 **v1.2.3** 的基础上，放进了我们自己提给上游的修复和一套自用改动，
方便自己构建、也给朋友用。上游的功能说明、下载安装、隐私与免责声明请以上游仓库为准。

## 我们的改动

### 一、提给上游的修复

- **[PR #13](https://github.com/tswawa/WechatVibe/pull/13) 逐条情绪 / 意图** —— 已被上游合并，但只采纳了一部分：
  - **采纳**：API 模式逐条标签改用短编号逐条输出（不再只回第一条，prompt 约 1000 → 440 字节），
    这条同时修掉了 [#14](https://github.com/tswawa/WechatVibe/issues/14)。上游在 1.2.3 里手工移植，
    并自行补上了乱序、重复与流式结果的对应。
  - **未采纳（本 fork 保留）**：逐条显示改用宽情绪题（粗粒度准确率 19.7% → 64.3%）、
    `caring` / `surprised` 选项（同一模型 38.9% → 57.2%）、标签 schema `generic-v9` → `generic-v10`。
    上游的理由是「会让已保存的结果全部重算」，并希望情绪题单独提 PR 再议。
  - **未采纳（已丢弃）**：画像输出的容错解析 —— 上游指出 `I:70` 会被算成偏 E 70%（方向反了），
    且 1.2.3 的画像已改为程序统一计分，这段逻辑不再需要。
- **[PR #10](https://github.com/tswawa/WechatVibe/pull/10) 本地分析多 worker 并行 + 弹性负载调节** —— 仍未合并。
  上游认可方向，但列出三处必修问题，并要求把服务号过滤、全选、统计接口与 SQLite WAL 拆出去单独评估。

### 二、自用改动（已并入 `main`）

这套改动最初做在 v1.2.0 上；上游 1.2.2 重构了后端与前端模块，1.2.3 又重写了画像，
所以按功能逐块重写了两轮，现在跟着 v1.2.3 走：

- 会话一次全量加载 + 「全部添加」按钮 + 新会话自动补进侧栏；
- 服务号 / 系统号过滤（`gh_`、`brandsessionholder`、`notifymessage` 等，保留 `filehelper` 与群聊）；
- 设置里的「后台分析全部会话」开关、侧栏总进度条与「本地分析并行数」档位；
- 消息内嵌图片渲染（点击放大；首次需在微信里点开一张图以派生密钥）。

### 三、与上游的已知分歧

保留自用判定逻辑会带来两处可预期的不一致，下次升级上游时需要留意：

- 情绪题是 **8 个桶**（`caring` 取代 `affectionate`，`surprised` 从 `amused` 拆出），上游是 7 个。
  因此 `tests/api-portrait-classifier.test.ts` 的两处断言按本 fork 的题库调整过（59 → 60、`affectionate` → `caring`）。
- 逐条显示走宽情绪题 `EMOTION_QUESTION`，上游的逐条显示仍走 18 个立场词。

v1.2.0 上那份原始补丁仍原样存档在
[`selfuse/v1.2.0`](https://github.com/silicon-sbt/WechatVibe/tree/selfuse/v1.2.0) 分支，
仅作历史对照，不再维护。

## 分支

| 分支 | 内容 |
| --- | --- |
| `main` | 跟随上游 v1.2.3 + 「自用改动」 |
| `feat/selfuse-on-1.2.3` | 自用改动搬到 1.2.3 的开发分支（已并入 `main`） |
| `feat/selfuse-on-1.2.2` | 自用改动搬到 1.2.2 的开发分支（历史） |
| `selfuse/v1.2.0` | v1.2.0 + 旧的原始自用补丁（存档，不再维护） |
| `feat/parallel-analysis-workers` | PR #10 的开发分支 |
| `fix/emotion-question-options` | PR #13 的开发分支（含 #14 的修复） |

## 许可

沿用上游 [Apache-2.0](LICENSE) 许可证。
