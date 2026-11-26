# VendSolution IoT 设备建模与配方参数配置 PRD（v2.0）

| 项目 | 内容 |
|---|---|
| 文档名称 | VendSolution IoT 设备建模与配方参数配置 Demo PRD |
| 版本 | v2.0（在 v1.0 基础上对齐会议纪要 + 借鉴涂鸦物模型 + 真实奶咖参数落地） |
| 状态 | 待评审 |
| 关联会议 | 新机型适配配置方案讨论会（2026-11-24） |
| 参考范式 | 涂鸦智能（Tuya）DP 数据点物模型（仅借鉴建模思路，术语保留 VendSolution 自有体系） |
| 真实数据源 | FUJI 大容量-新款「大容量奶咖组合初始默认配方.xlsx」 |

---

## 0. 修订说明（v2.0 相对 v1.0 的增量）

| # | 增量 | 来源 |
|---|---|---|
| 1 | 明确「机型」与「模板」两个概念，并区分其职责与生命周期 | 会议纪要 |
| 2 | 组件从「定义」拆出「组件实例」层，新增实例属性（可清洗 / 可配置参数） | 会议纪要 |
| 3 | 新增「协议转换映射」层：平台标准参数 → 主控底层硬件指令 | 会议纪要 / ER 图 |
| 4 | 数据点取值约束补全 step（步长）、scale（精度/倍数）、字节宽度 | 借鉴 Tuya DP |
| 5 | 数据类型、方向枚举与 Tuya 对齐（bool/value/enum/string/raw；RO/WR/RW） | 借鉴 Tuya DP |
| 6 | 配方参数以真实奶咖 118 项参数 + 7 阶段工艺模板落地 | 真实 Excel |

---

## 1. 背景与目标

### 1.1 背景

新机型接入目前依赖「产品设计页面 + 研发定制开发」的流程，每接入一款新机型都要后端定制开发页面，成本高、周期长。会议纪明确的解法是：**把通用硬件抽象为统一标准组件库，把配方/工艺抽象为参数体系，让产品运营通过后台配置完成新机型接入，研发无需额外开发页面。**

### 1.2 目标

1. 建立**统一标准组件库**：搅拌器、风扇、锅炉、冲泡器、水泵、电机等通用硬件组件，每个组件定义参数、值类型、取值范围，支持按设备类型打标签筛选。
2. 建立**机型配置流程**：新建机型时从组件库勾选实际搭载组件，自定义组件属性（是否可清洗、是否可配置参数），无需研发开发页面。
3. 建立**配方参数体系**：以真实奶咖配方为样板，把「配方头 + 参数字典 + 默认值」结构化，支持 Excel 导入与参数校验。
4. 建立**协议转换分工**：平台向主控下发统一标准参数，主控侧转换为对应机型底层硬件指令，屏蔽机型协议差异。

### 1.3 排期（会议纪要）

| 阶段 | 时间 | 交付 |
|---|---|---|
| 产品定型 | 本周 | 组件参数体系逻辑 + 页面设计 |
| 后台 Demo | 下周二前 | 可配置 Demo + 自测，开放配置入口 |
| 终端对接 | 下周三–周五 | 主控驱动适配 + 自测 |
| 测试交付 | 预留一周 | 全链路测试改 Bug，双 12 前后交付可测试版本 |

### 1.4 本期非目标

- 不实现从已调优设备「一键生成模板」（后续扩展，仅保留设计占位）。
- 不实现多语言（会议纪要明确为后续并行安排）。
- 不把底层协议转换做成平台可编辑的完整工具（本期只建模映射结构，主控侧实现转换）。

---

## 2. 名词与概念

| 名词 | 定义 | 来源 |
|---|---|---|
| 机型（Hardware Model） | 硬件层面标准型号（如万事达 1008 系列），平台统一创建管理，不随客户运营需求变更 | 会议纪要 |
| 模板（Product Template） | 基于同一机型衍生的运营配置，适配不同客户货道数量、默认原料、广告图等差异化需求 | 会议纪要 |
| 组件（Component） | 全局可复用的通用硬件抽象，如搅拌器、风扇、锅炉、冲泡器 | 会议纪要 |
| 组件实例（Component Instance） | 组件在某机型/模板中的一次装配，携带实例级属性（可清洗、可配置参数、安装位置、指令代码） | 会议纪要 + v1.0 |
| 数据点（Data Point） | 描述设备能力的最小数据单元（对应 Tuya 的 DP），含类型、方向、取值约束 | 借鉴 Tuya |
| 配方参数（Recipe Parameter） | 设备执行工艺的可配置参数，如研磨时间、热水量、搅拌强度 | 真实 Excel |
| 协议转换（Protocol Mapping） | 平台标准参数 ↔ 主控底层硬件指令的映射关系 | 会议纪要 / ER 图 |

---

## 3. 核心设计判断

> **这不是一个把所有参数都塞进「传感器」的系统。**
> 传感器定义测量/状态能力，组件定义机器由什么组成，配方参数定义设备如何执行工艺。三者在产品模板中组合，但数据类型和生命周期必须分开。

### 3.1 参数五分类（沿用 v1.0，作为所有参数的归属铁律）

| 数据类别 | 示例 | 系统归属 | 关键规则 |
|---|---|---|---|
| 传感器测量 | 温度、压力、流量、水位 | Sensor / Telemetry | 必须有真实数据源或明确 Demo Mock |
| 逻辑状态 | 水箱缺失、渣盒已满、奶壶未安装 | Signal / Device Event | 底层检测方式未确认时不得标为真实传感器 |
| 维护/计数 | 除钙到期、滤芯到期、奶壶清洁提醒 | Maintenance Rule / Event | 规则或计数派生，不等于物理传感器 |
| 配方工艺参数 | 研磨时间、热水量、搅拌强度、萃取延迟 | Recipe Parameter Schema | 不能放进传感器库 |
| 静态规格 | 水箱容量、豆槽容量、泵压规格 | Product Attributes | 静态属性，非实时测量值 |

---

## 4. 信息架构与实体模型

### 4.1 实体分层

| 层级 | 实体 | 关键字段 | 职责 |
|---|---|---|---|
| 能力层 | Sensor Definition | code、name、category、description、source_type、status、version | 定义测量/状态能力 |
| 能力层 | Sensor Point Definition | point_code、data_type、unit、precision、min/max、step、scale、enum_values、direction、required | 定义单个数据点（借鉴 Tuya DP） |
| 硬件层 | Hardware Model（机型） | manufacturer、model、interface、protocol、datasheet、firmware_compatibility | 硬件标准型号，平台统一管理 |
| 组装层 | Component Definition | component_code、category、device_type_tags、default_attributes | 全局组件库定义 |
| 组装层 | Component Instance | instance_name、definition_id、quantity、install_position、channel、is_washable、is_param_configurable、command_code | 组件在某机型的装配实例 |
| 配置层 | Product Template（模板） | product_code、model_id、device_category、version、source_documents、lane_count、default_ingredients、ad_image | 基于机型的运营配置模板 |
| 工艺层 | Recipe Schema | parameter_no、stage、description、source_bytes、range、data_type、unit、step、scale | 配方参数字典（全局唯一） |
| 工艺层 | Recipe Variant | recipe_id、parameter_no、value | 配方默认值（recipe_id → 参数值） |
| 运行层 | Device Instance | device_id、SN、tenant、site、template_version、connection_state、instance_overrides | 实际设备 |
| 数据层 | Telemetry / Event | point_code、value、unit、event_time、quality、origin、severity、ack_status | 遥测与事件 |
| 协议层 | Protocol Mapping | command_id、command_name、master_id、standard_parameter、data_type、report_cycle、report_type | 标准参数 ↔ 硬件指令映射 |

### 4.2 实体关系

```
机型（Hardware Model） ──派生──▶ 模板（Product Template）
       │                              │
       │ 勾选组件，生成                 │ 继承/覆盖参数值
       ▼                              ▼
组件实例（Component Instance）    配方变体（Recipe Variant）
       │ 装配自                        │ 引用
       ▼                              ▼
组件定义（Component Definition）   配方模式（Recipe Schema）
                                        │ 约束
                                        ▼
                             数据点（Sensor Point Definition）
                                        │ 映射
                                        ▼
                        协议转换（Protocol Mapping）──▶ 主控硬件指令
```

---

## 5. 参数与数据点建模规范（借鉴 Tuya DP）

> 本章借鉴涂鸦 DP 数据点的建模思路，术语保留 VendSolution 自有命名（`point_code` / `data_type` / `direction` 等）。

### 5.1 数据类型（data_type）

| 类型 | 代码 | 说明 | 奶咖配方映射示例 |
|---|---|---|---|
| 布尔型 | bool | 二值（真/假） | 清洗开关、维护开关 |
| 数值型 | value | 线性可调 | 豆量（g）、水量（ml）、时间（s）、搅拌强度（1~5） |
| 枚举型 | enum | 有限集合 | 刮板次数（1/2）、档位（低/中/高） |
| 字符串型 | string | 复杂文本（≤255 字节） | 配方名称、设备型号（静态） |
| 透传型 | raw | Hex 十六进制透传 | 底层指令透传 |

### 5.2 方向（direction）

| 方向 | 代码 | 说明 |
|---|---|---|
| 只读 | RO | 仅设备上报（遥测、状态） |
| 只写 | WR | 仅云端下发（配方参数下发） |
| 读写 | RW | 可上报可下发 |

### 5.3 取值约束

| 字段 | 说明 | 示例 |
|---|---|---|
| min / max | 取值上下界 | 0 ~ 99.9 |
| step | 步长（线性增量） | 0.1 |
| scale | 倍数/精度（小数位） | 0.1 分辨率 = scale 0.1 |
| unit | 单位 | g、ml、s、℃、% |
| enum_values | 枚举值集合（enum 类型） | [1, 2] |
| precision | 上报精度 | 1 位小数 |
| source_bytes | 协议数据宽度 | 1 字节 / 2 字节 |

### 5.4 字节宽度与数据类型对应（真实奶咖特征）

| 字节宽度 | 适用场景 | 奶咖中的数量 |
|---|---|---|
| 1 字节 | 档位/次数/强度/水平类小整数 | 31 项 |
| 2 字节 | 时间/水量/重量等较大范围值 | 87 项 |

---

## 6. 配方参数建模（真实奶咖参数落地）

### 6.1 数据模型

真实奶咖配方 = **配方头 + 118 项参数字典 + 12 组默认值**，本质是一张 `recipe_id → (parameter_no, value)` 的参数配置表。

| 维度 | 内容 | 数量 |
|---|---|---|
| 配方头 | 饮品名称 × 杯型 | 12 个配方（原味混合 S/M/L/大杯、淡味混合 S/M/L、浓缩滴滤、冰咖啡 S/M/L/大杯） |
| 参数字典 | 阶段 / No. / 字节数 / 内容 / 设定范围 | 118 项，全局唯一 |
| 阶段结构 | 预润 + 5 次萃取 + 结束清洗 | 7 段 |
| 默认值 | 每个配方 116 项已填 + 2 项空白（No.5、No.30） | 12 组 |

### 6.2 阶段工艺模板

萃取循环高度模板化，第 1–5 次萃取的子参数结构完全一致，可抽象为**可循环的「萃取步骤模板」**，由「重复次数」（No.4，1~5）控制执行轮次：

```
预润阶段（No.1–18）
  ├─ 豆原料量（豆1/豆2/豆3）
  ├─ 豆仓运行时机、豆→研磨器等待
  ├─ 搅拌水平、搅拌时间
  └─ 动作重复次数（No.4）
萃取循环（No.19–113，模板 × 5 次）
  ├─ 蒸煮等待
  ├─ 第1次喷淋（延迟/强度/水量）
  ├─ 第1次空气搅拌（延迟/强度/时间/蒸煮等待）
  ├─ 第2次喷淋（强度/水量）
  ├─ 第1次空气抽出（延迟/加压强度/时间）
  ├─ 添加热水（延迟/水量）
  └─ 第2次空气抽出（延迟/强度/时间）
结束清洗（No.114–118）
  ├─ 制作结束→销售结束间隔
  ├─ 刮板动作次数
  └─ 冲洗时间
```

### 6.3 设定范围 → 校验规则映射（9 种模式）

| 范围表达式 | data_type | unit | 精度 | 字节 | 校验规则 |
|---|---|---|---|---|---|
| `0~36.0g` | value | g | 0.1 | 2 | min=0, max=36.0, step=0.1 |
| `1~5` | value | — | 1 | 1 | min=1, max=5, step=1 |
| `1~4` | value | — | 1 | 1 | min=1, max=4, step=1 |
| `0~99.9s` | value | s | 0.1 | 2 | min=0, max=99.9, step=0.1 |
| `0~99s` | value | s | 1 | 1 | min=0, max=99, step=1 |
| `0~150ml` | value | ml | 1 | 2 | min=0, max=150, step=1 |
| `0~50ml` | value | ml | 1 | 2 | min=0, max=50, step=1 |
| `1~2` | value | — | 1 | 1 | min=1, max=2, step=1 |
| `0~99.9g`（源表笔误，应为 s） | value | s | 0.1 | 2 | 单位纠正为 s |

### 6.4 执行机构维度（配方参数归属）

| 执行机构 / 子系统 | 对应参数语义 | 单位/档位 |
|---|---|---|
| 豆仓 / 研磨器（电机） | 豆原料量、豆仓运行时机、研磨器运行时间 | g / s |
| 气缸 / 热水（水阀） | 热水量、喷淋水量、添加热水水量、冲洗量 | ml |
| 空气搅拌（气泵/搅拌电机） | 搅拌水平、搅拌时间、搅拌延迟 | 档位 / s |
| 空气抽出（气泵/加压） | 加压强度、抽出时间、抽出延迟 | 档位 / s |
| 喷淋投入（泵/喷嘴） | 喷淋强度、喷淋延迟 | 档位 / s |
| 刮板（清洁机构） | 刮板次数、冲洗量、冲洗时间 | 次 / ml / s |
| 时序控制（全局） | 延迟/等待/间隔、重复次数、销售结束间隔 | s / 次 |

---

## 7. 组件库与机型 / 模板（会议纪要对齐）

### 7.1 统一标准组件库

- 组件按**组件类型**归类（搅拌器 / 风扇 / 锅炉 / 冲泡器 / 水泵 / 电机 / 清洁机构…）。
- 每个组件定义**参数、值类型、取值范围**，支持**按设备类型打标签筛选**（咖啡机 / 售卖机 / 开门柜…）。
- 组件是全局资料：一个组件只维护一份，可供多个机型复用。

### 7.2 机型配置流程

```
新建机型 → 从组件库勾选组件 → 生成组件实例 → 配置实例属性 → 完成
```

组件实例级属性（会议纪要明确）：

| 属性 | 说明 |
|---|---|
| is_washable | 是否可清洗 |
| is_param_configurable | 是否可配置参数 |
| install_position | 安装位置 |
| channel | 通道/料道映射 |
| command_code | 关联级指令代码（同一组件在不同机型可不同） |

### 7.3 模板（运营配置）

- 模板基于机型派生，面向大规模品牌商批量统一配置，约束一线运维随意改参数。
- 模板内容：货道数量、默认原料、广告图、参数值快照。
- 保留单设备配置复制功能（适配小客户少量设备，无需建模板）。
- 后续扩展：从已调优稳定的设备直接生成模板。

### 7.4 协议转换分工

- 平台向主控下发**统一标准参数**。
- 主控侧负责将标准参数转换为对应机型的**底层硬件指令**，屏蔽机型协议差异。
- 平台侧维护 Protocol Mapping 结构（见 §8 FR-08），主控侧实现转换逻辑。

---

## 8. 功能需求（FR）

### FR-01 传感器定义（Sensor Library）
创建、编辑、启停传感器定义；为每个传感器定义数据点（point_code、data_type、unit、precision、min/max、step、scale、enum_values、direction、required）。

### FR-02 组件库（Component Library）
维护全局组件定义；组件分类（组件类型 + 设备类型标签）；组件默认属性。

### FR-03 机型与模板（Hardware Model & Product Template）
新建机型，勾选组件生成组件实例，配置实例属性（可清洗 / 可配置参数 / 指令代码）；基于机型派生模板，配置货道、默认原料、广告图、参数值快照。

### FR-04 配方参数导入（Recipe & Parameters）
导入 XLSX 配方；解析配方头、参数字典、默认值；按设定范围生成校验规则；参数行内编辑与版本比较。

### FR-05 设备实例（Device Instances）
从模板创建设备实例；继承模板参数，支持实例级覆盖；展示连接状态。

### FR-06 监控（Monitoring）
展示遥测、设备状态、事件、维护提醒。

### FR-07 权限
Root / Product / 只读等角色分级。

### FR-08 协议转换映射（Protocol Mapping）
维护「标准参数 ↔ 硬件指令」映射结构：command_id、command_name、master_id、standard_parameter、data_type、report_cycle、report_type。本期仅建模结构，主控侧实现转换。

---

## 9. 页面与导航

| 菜单 | 子菜单/内容 |
|---|---|
| IoT Studio | 总览 |
| Sensor Library | 传感器列表、数据点定义、新建/编辑 |
| Component Library | 组件分类（类型 + 设备类型标签）、组件列表、组件详情 |
| Product Templates | 机型列表、模板构建器（勾选组件 + 实例属性）、版本管理 |
| Recipe & Parameters | 配方模板、Excel 导入、参数编辑、版本比较 |
| Device Instances | 设备列表、设备实例详情、模板继承 |
| Monitoring | 遥测、设备状态、事件、维护提醒 |
| Protocol Mapping | 标准参数 ↔ 硬件指令映射（新增） |

---

## 10. 关键流程

1. **创建机型**：新建硬件型号 → 从组件库勾选组件 → 配置组件实例属性 → 保存机型。
2. **派生模板**：基于机型创建模板 → 配置货道/默认原料/广告图 → 导入参数默认值 → 发布版本。
3. **导入配方**：上传奶咖 XLSX → 解析 118 参数字典 + 12 配方默认值 → 生成校验规则 → 确认入库。
4. **实例化设备**：选择模板 → 创建设备实例 → 继承参数（可覆盖）→ 下发标准参数 → 主控转硬件指令。

---

## 11. 数据模型（JSON 示例）

```json
{
  "hardware_model": {
    "model_code": "FUJI-LARGE-NEW",
    "manufacturer": "FUJI",
    "model": "大容量-新款",
    "interface": "uart",
    "protocol": "vend-standard"
  },
  "component_instance": [
    {
      "instance_name": "左搅拌器",
      "definition_id": "C-MIXL",
      "is_washable": true,
      "is_param_configurable": true,
      "install_position": "left",
      "command_code": "cmd_mixl"
    }
  ],
  "recipe_schema": {
    "schema_version": "1.0",
    "parameters": [
      {
        "parameter_no": 1,
        "stage": "预润阶段",
        "description": "设定豆1的原料量",
        "source_bytes": 2,
        "range": "0~36.0g",
        "data_type": "value",
        "unit": "g",
        "step": 0.1,
        "min": 0,
        "max": 36.0
      }
    ]
  },
  "recipe_variant": {
    "recipe_id": "RECIPE-01",
    "recipe_name": "原味混合咖啡 S",
    "values": { "1": 9.5, "4": 1, "13": 2 }
  },
  "protocol_mapping": {
    "command_id": "cmd_1",
    "command_name": "研磨器运行",
    "master_id": "master-2",
    "standard_parameter": 7,
    "data_type": "value",
    "report_cycle": "200",
    "report_type": "instruction"
  }
}
```

---

## 12. 验收标准

| ID | 验收项 | 通过标准 |
|---|---|---|
| AC-01 | 组件库 | 可新建组件，配置类型、设备类型标签、参数定义 |
| AC-02 | 机型配置 | 新建机型可勾选组件，配置可清洗/可配置参数属性 |
| AC-03 | 模板派生 | 基于机型派生模板，配置货道/默认原料/参数快照 |
| AC-04 | 配方导入 | 导入奶咖 XLSX，正确解析 118 参数 + 12 配方 |
| AC-05 | 参数校验 | 按 9 种范围模式生成校验规则，非法值拦截 |
| AC-06 | 阶段模板 | 5 次萃取抽象为可循环模板，重复次数控制轮次 |
| AC-07 | 协议映射 | 维护标准参数 ↔ 硬件指令映射结构 |
| AC-08 | 设备实例 | 从模板创建设备，继承参数可覆盖 |
| AC-09 | 数据点 | 数据点含类型/方向/约束，与 Tuya 建模对齐 |

---

## 13. 待确认事项与风险

1. **数据点挂载层级**：数据点挂在「组件」下（全局默认）还是「指令」下？（ER 图显示"组件→指令→参数"三级，会议措辞是"组件定义参数"，两者影响参数编辑入口与值类型归属。）
2. **设备类型标签枚举**：需终端侧提供（咖啡机 / 售卖机 / 开门柜 / 现制饮品机…）。
3. **组件类型枚举**：是否以"搅拌器/风扇/锅炉/冲泡器"为一级，现有"料道/清洗/非料道"降为二级。
4. **大容量奶咖 No.5 / No.30 空白参数**：确认为"可选/默认 0/预留"还是需补齐默认值。
5. **源表单位笔误**：No.114 / No.122 的 `0~99.9g` 疑为 `s`，需与硬件侧确认。
