# AES 项目实施路径规划

**日期**: 2026-03-07

---

## 一、阶段性目标总览

| 阶段 | 目标 | 关键成果 |
|------|------|----------|
| 1 | 原型梳理与评估 | 项目现状评估报告、依赖清单 |
| 2 | 结构优化与模块化 | 模块化架构图、API文档 |
| 3 | 文档与测试体系 | 用户手册、测试套件 |
| 4 | 团队协作准备 | 贡献指南、代码规范 |
| 5 | 开放协作与持续演进 | 社区贡献、版本发布 |

---

## 二、当前状态

### 2.1 已完成

- [x] 核心算法实现
- [x] 理论框架文档
- [x] 实验验证
- [x] 论文初稿

### 2.2 待处理

- [ ] 模块化重构
- [ ] API文档
- [ ] 测试套件
- [ ] 用户手册

---

## 三、代码结构优化（阶段2）

### 3.1 模块划分

```
aes/
├── core/              # 核心算法
│   ├── environment.py
│   ├── agent.py
│   └── evolution.py
├── experiments/       # 实验
│   ├── v04_mobile.py
│   └── test_*.py
├── docs/             # 文档
│   ├── THEORY.md
│   ├── EXPERIMENT.md
│   └── PAPER.md
└── main.py            # 入口
```

### 3.2 接口设计

```python
class Environment:
    def step(self)
    def get_view(self, x, y)
    def get_state(self)

class Agent:
    def act(self, obs)
    def mutate(self)
    def copy_weights_from(self, other)

class EvolutionEngine:
    def select(self, agents)
    def reproduce(self, agent)
```

---

## 四、文档体系（阶段3）

| 文档 | 状态 |
|------|------|
| 架构设计 | 待完成 |
| API文档 | 待完成 |
| 用户手册 | 待完成 |
| 贡献指南 | 待完成 |

---

## 五、测试能力（阶段3）

| 测试类型 | 目标 | 工具 |
|----------|------|------|
| 单元测试 | ≥80%覆盖率 | pytest |
| 集成测试 | 主流程 | pytest |
| 性能测试 | 建立基线 | time |

---

## 六、下一步行动

### 立即（1-2小时）
1. 创建模块化目录结构
2. 拆分核心代码

### 短期（1-2天）
3. 编写API文档
4. 添加基础测试

### 中期（1周）
5. 完善用户手册
6. 建立CI流程

---

*规划整合自项目协作文档*
