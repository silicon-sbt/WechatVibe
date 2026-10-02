# WechatVibe（silicon-sbt 的个人 fork）

上游仓库：[tswawa/WechatVibe](https://github.com/tswawa/WechatVibe)。

本 fork 在上游 `main`（1.2.2）的基础上，放进了我们自己提给上游的修复和一套自用改动，
方便自己构建、也给朋友用。上游的功能说明、下载安装、隐私与免责声明请以上游仓库为准。

## 我们的改动

### 一、已提给上游的修复

- **[PR #13](https://github.com/tswawa/WechatVibe/pull/13) 逐条情绪 / 意图**
  - 逐条显示的情绪题换成实测更优的宽情绪题（粗粒度准确率 19.7% → 64.3%）；
  - `caring` / `surprised` 选项措辞（同一模型 38.9% → 57.2%），并补中文显示映射；
  - 悬空判断句（如「我这是」）不再出标签；标签 schema `generic-v9` → `generic-v10`；
  - 修 [#14](https://github.com/tswawa/WechatVibe/issues/14)：API 模式逐条标签改用短编号逐条输出
    （不再只回第一条，prompt 约 1000 → 440 字节）；画像分析容忍本机模型的常见输出形状，
    不再整条报「模型返回格式不正确」。
- **[PR #10](https://github.com/tswawa/WechatVibe/pull/10) 本地分析多 worker 并行 + 弹性负载调节**。

### 二、自用改动（分支 `selfuse/v1.2.0`）

这套改动是在 v1.2.0 上做的。上游 1.2.2 把 `bridge/real_backend.py`、`chatui/app.js` 等
重构成 `backend_service.py`、`message-labels.js` 等新模块，无法机械合并，所以原样保留在
[`selfuse/v1.2.0`](https://github.com/silicon-sbt/WechatVibe/tree/selfuse/v1.2.0) 分支：

- 会话一次全量加载 + 「全部添加」按钮 + 新会话自动跟踪；
- 服务号 / 系统号过滤（`gh_`、`brandsessionholder`、`notifymessage` 等，保留 `filehelper`）；
- 消息内嵌图片渲染；
- 设置里的「后台分析全部会话」开关与分析总览。

## 分支

| 分支 | 内容 |
| --- | --- |
| `main` | 上游 1.2.2 + 上面「已提给上游的修复」 |
| `selfuse/v1.2.0` | v1.2.0 + 上面「自用改动」 |
| `feat/parallel-analysis-workers` | PR #10 的开发分支 |
| `fix/emotion-question-options` | PR #13 的开发分支（含 #14 的修复） |

## 许可

沿用上游 [Apache-2.0](LICENSE) 许可证。
