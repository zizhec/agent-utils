---
name: add_feature
description: |
  管理需求变更并在各文档间保持同步。当用户提出新需求或需求变更时，自动创建 feature 目录、更新相关文档。
  适用于：新增功能、需求变更、功能迭代、需求文档管理等场景。
  关键词：需求、feature、功能、变更、改动、新增、修改需求、更新PRD、测试用例
---

# Add Feature Skill

管理需求变更，创建 feature 目录，同步 PRD/测试案例/CLAUDE.md 等文档。
重点：先完成需求记录，完成汇报，和用户同步好了后，再开始开发。


## 工作流程

总体来说，分成：
   1. 需求需求创建，需求文件更新。
   2. tdd 开发
   3. 功能verification, 测试， 回归测试, 日志检查（确保没有错误日志，服务运行正常）
   4. code-review，检查代码质量，检查架构合理性。
   5. 让用户确认功能完成。
   6. 如果3,4,5 发现问题，回到1，更新需求，或者直接修复问题。直到最终通过。
   7. git commit
   8. 运行/lessons skill来总结所有经验教训。
   9. mark as done


其中，需求创建部分的流程如下：

### 1. 解析需求

先尝试理解需求，如果需求本身很明确，那么继续下一步；如果需求不明确，先和用户沟通确认需求细节，直到需求明确为止。你可以尝试使用brainstorming的方式来帮助用户明确需求细节。如果用户的需求有缺漏，或者你觉得可以改进，那么可以提议。和用户共建出最合理的需求。注意说清楚本次改动是否是breaking change, 旧数据库是否兼容，是否需要数据迁移等。

当需求明确后，
提取以下信息：
- Feature 名称、类型（新增/修改/优化/修复）、优先级
- 如果是空项目，默认创建 `init-features` 作为初始 Feature

### 2. 检查现有 Feature

**如果 features 目录不存在：**
- 创建 `features/` 目录
- 创建 `features/README.md`（使用模板：references/readme-template.md）

- 询问用户处理方式：
```
您希望如何处理这个新需求？
1. Merge 到当前Feature, 更新当前Feature的 文档。
2. 创建新 Feature（当前 Feature 保持未完成）
3. 取消
```


### 3. 创建/更新 Feature

**目录结构：**
```
features/
├── README.md                   # Feature 列表总览
├── main-features/              # 初始 Feature
│   ├── feature.md              # 需求描述
│   ├── progress.md             # 进度跟踪
│   └── test-cases.md           # E2E 测试案例
└── {ID}/                       # 后续创建的 Feature
    ├── feature.md
    ├── progress.md
    └── test-cases.md
```
ID格式：`简写-YYYYMMDD`
- 初始 Feature：ID 为 `init-features`
- 后续 Feature：使用日期格式（如 `UPLOAD-2026030508`）, 即名称+日期，名称简洁但是能反映功能内容，日期为创建日期（到小时），确保唯一性。


**创建文档（使用模板）：**
1. feature.md → 使用模板 `references/feature-template.md`
2. progress.md → 使用模板 `references/progress-template.md`
3. test-cases.md → 使用模板 `references/test-cases-template.md`
4. 更新 README.md → 使用模板 `references/readme-template.md`

### 4. 校验创建结果

**必须执行以下检查：**

```
校验清单:
□ features/{feature-dir}/ 目录存在
□ features/{feature-dir}/feature.md 文件存在且有内容
□ features/{feature-dir}/progress.md 文件存在且有内容
□ features/{feature-dir}/test-cases.md 文件存在且有内容
□ features/README.md 已更新
□ CLAUDE.md 已更新
```

**如果任何一项检查失败：**
- 立即重新创建缺失的文件
- 如果连续2次失败，报告错误给用户

### 5. 更新 CLAUDE.md

添加/更新以下部分：
```markdown
## 当前 Feature

**当前工作**: `{feature-id}` - {名称}
**Feature 目录**: [features/{feature-dir}/](features/{feature-dir}/)

### 快捷链接
- [📋 需求文档](features/{feature-dir}/feature.md)
- [📊 进度跟踪](features/{feature-dir}/progress.md)
- [🧪 测试案例](features/{feature-dir}/test-cases.md)
- [📋 所有 Feature](features/README.md)

### Feature 列表
| ID | 目录 | 状态 | 优先级 |
|----|------|------|--------|
| {id} | {feature-dir}/ | 规划中 | {优先级} |
```

### 6. 同步 PRD.md

- 新增功能：在相应章节添加描述
- 需求变更：添加变更历史记录

## 输出格式

**创建新 Feature：**
```
✅ Feature 已创建

📁 Feature ID: {id}
📂 目录位置: features/{feature-dir}/

📝 已创建文档:
   - feature.md - 需求描述
   - progress.md - 进度跟踪
   - test-cases.md - E2E 测试指导

✅ 校验结果:
   - 目录结构: 通过
   - 文档完整性: 通过
   - README.md 更新: 通过
   - CLAUDE.md 更新: 通过

🔄 已更新:
   - features/README.md - Feature 列表
   - CLAUDE.md - 当前 Feature 指向

💡 下一步:
   1. 完善 test-cases.md 中的测试用例
   2. 开始编码实现
   3. 期间同步更新 progress.md 状态
```

## 边界情况

| 情况 | 处理方式 |
|------|---------|
| features 目录不存在 | 创建目录结构，README.md，main-features |
| README.md 不存在 | 创建并扫描现有 Feature 目录 |
| CLAUDE.md 不存在 | 跳过 |
| Feature ID 已存在 | 询问：创建新版本 / 更新现有 / 取消 |

## 目录结构示例

```
project/
├── CLAUDE.md
├── PRD.md
├── features/
│   ├── README.md              # Feature 列表总览
│   ├── main-features/         # 初始 Feature
│   │   ├── feature.md
│   │   ├── progress.md
│   │   └── test-cases.md
│   └── EXPORT-20260306/       # 后续 Feature
│       ├── feature.md
│       ├── progress.md
│       └── test-cases.md
└── ...
```

## 重要说明

1. **每个 Feature 有自己的 progress.md** - 没有 global progress
2. **main-features** - 只是第一个 feature 的名字
3. **README.md** - 打开可快速查看所有 Feature 状态


## 参考模板

本文档使用以下模板（位于 references/ 目录）：
- `feature-template.md` - Feature 需求文档模板
- `progress-template.md` - 进度跟踪文档模板
- `test-cases-template.md` - E2E 测试案例模板
- `readme-template.md` - Feature 列表模板

需要查看完整模板内容时，读取相应文件。
