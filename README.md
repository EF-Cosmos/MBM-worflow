# MBM Workflow / BaiGave's Tool

一个用于在 Blender 内直接导入、编辑和导出 Minecraft 地图的插件。与 Mineways 或 jmc2obj 等工具不同，本插件导入的是带有方块属性的点云数据，通过几何节点实例化方块模型，支持非破坏性编辑。

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://github.com/BaiGave/BaiGave_Plugin/blob/main/LICENSE)
[![Blender](https://img.shields.io/badge/Blender-5.0+-orange.svg)](https://www.blender.org/download/)

## 功能概览

| 功能类别 | 描述 |
|---------|------|
| **地图导入** | 支持 .schem、.litematic、.nbt 文件及世界存档 |
| **地图编辑** | 方块笔刷、区域复制、方块移动、延时建筑动画 |
| **网格转换** | 将普通 Blender 网格转换为 Minecraft 方块 |
| **地图导出** | 导出为 .schem 文件或直接写入存档 |
| **版本转换** | 支持 Java 1.12~1.21.9 和 Bedrock 1.10~1.20.x |
| **网格优化** | 合并重叠面、植物摇摆动画、水体处理 |

---

## 地图导入

### 支持的文件格式

| 格式 | 描述 | 依赖 |
|------|------|------|
| `.schem` | WorldEdit / Sponge Schematic | amulet-core |
| `.litematic` | Litematica 模组格式 | litemapy |
| `.nbt` | 原版结构文件 | amulet-nbt |
| 存档目录 | Minecraft 世界存档 | amulet-core |

### 导入特性

- **多区域支持**：Litematic 文件的每个区域创建独立的 Blender 对象
- **坐标转换**：自动转换 MC 坐标 (x, y, z) 到 Blender (x, -z, y)
- **方块状态保留**：完整保留方块属性（如楼梯朝向、红砖状态等）
- **群系信息**：保留群系数据用于后续着色

### 使用流程

1. **配置模组和资源包**
   - 在插件面板中安装模组 `.jar` 文件和资源包 `.zip`
   - 调整优先级顺序（越靠上优先级越高）

2. **导入文件**
   ```
   Blender → 侧边栏 (N) → BaiGave's Tool → 导入地图
   ```

3. **导入模式选择**
   - **点云模式**（默认）：保留非破坏性编辑能力
   - **按方块状态分离**：每个方块类型创建独立对象

---

## 地图编辑

### 方块笔刷

基于哈希字典的精确坐标查找系统：

- **精确定位**：使用整数坐标哈希查找，无距离误差
- **支持操作**：放置、替换、删除方块
- **笔刷设置**：大小、形状、方块类型

```python
# 笔刷索引构建
self.vertex_map = {}
for i, v in enumerate(mesh.vertices):
    coord = (int(v.co.x), int(v.co.y), int(v.co.z))
    self.vertex_map[coord] = i
```

### 区域操作

- **区域复制**：选择区域并复制到新位置
- **方块移动**：移动单个或多个方块
- **批量替换**：按类型或属性批量替换方块

### 几何节点特效

| 特效 | 描述 |
|------|------|
| **延时建筑** | 通过几何节点实现方块逐个出现的动画 |
| **地形破坏** | 模拟方块被破坏的效果 |
| **植物摇摆** | 自动为植物和树叶添加风力摇摆动画 |

### 群系着色

通过调整顶点的 `biome` 属性实现群系颜色变化：
- 草方块颜色随群系变化
- 树叶、藤蔓等植物受群系影响
- 实时预览效果

---

## 网格转方块

将普通 Blender 网格体转换为 Minecraft 方块结构：

### 转换流程

1. **创建预览**：使用 `ObjToBlocks` 几何节点组生成方块预览
2. **完整转换**：应用 `模型转换节点组` 进行完整转换
3. **特殊方块支持**：自动识别楼梯、台阶、栅栏等特殊方块

### 支持的方块类型

| 类别 | 示例 |
|------|------|
| 实心方块 | 石头、泥土、木头 |
| 楼梯/台阶 | 所有材质的楼梯和台阶 |
| 栅栏/墙 | 各类栅栏和墙方块 |
| 植物 | 花、草、藤蔓（需特殊处理） |
| 红石元件| 活塞、侦测器等 |

---

## 网格优化

### 合并重叠面

优化算法：移除相邻方块之间不可见的面

```
应用修改器 → 合并重叠面 → 面数显著减少
```

**效果示例**：
- 玻璃窗 UV 错误修复
- 固体方块内部面自动移除
- 保持外部视觉完全一致

### 使用步骤

1. 应用几何节点修改器（不可逆操作）
2. 选中需要优化的网格体
3. 执行 `合并重叠面` 操作

---

## 地图导出

### 导出格式

| 格式 | 描述 | 版本转换 |
|------|------|---------|
| `.schem` | Sponge Schematic 格式 | 支持 |
| 存档写入 | 直接写入 Minecraft 存档 | 支持 |

### 版本转换系统

基于 **PyMCTranslate** 的版本转换架构：

```
源版本 (1.12) → Universal Format → 目标版本 (1.21)
```

**支持范围**：
- Java Edition: 1.12 ~ 1.21.9
- Bedrock Edition: 1.10 ~ 1.20.x

**版本配置**：
```python
# 在 Blender 场景属性中配置
mc_platform: "java" | "bedrock"
mc_version_major: 1
mc_version_minor: 21
mc_version_patch: 9
```

---

## 安装与配置

### 系统要求

- **Blender**: 5.0 或更高版本
- **操作系统**: Windows / macOS / Linux

### 安装步骤

1. 下载 [Release](https://github.com/BaiGave/BaiGave_Plugin/releases) 文件
2. 在 Blender 中：`编辑 → 偏好设置 → 插件 → 安装`
3. 选择下载的 `.zip` 文件
4. 启用插件

### 依赖管理

插件使用 `wheels/` 目录管理 Python 依赖：

| 包名 | 版本 | 用途 |
|------|------|------|
| amulet-core | 1.9.33 | Minecraft 世界解析 |
| PyMCTranslate | 1.2.39 | 版本转换 |
| amulet-nbt | 2.1.5 | NBT 数据格式 |
| litemapy | 0.9.0b0 | Litematic 支持 |
| pillow | 12.1.0 | 图像处理 |

Blender 5.0+ 会自动通过 `blender_manifest.toml` 安装这些依赖。

---

## 开发

### 项目结构

```
MBM_workflow/
├── __init__.py                 # 插件入口
├── load_modules.py             # 模块加载系统
├── blender_manifest.toml       # Blender 5.0+ 清单
├── codes/
│   ├── dependency_manager.py   # 依赖管理
│   ├── property.py             # 场景属性
│   ├── schem.py                # schem/litematic 处理
│   ├── importfile.py           # 导入操作符
│   ├── exportfile.py           # 导出操作符
│   ├── blockstates.py          # 方块状态解析
│   ├── register.py             # 方块注册系统
│   ├── functions/
│   │   ├── brush.py            # 方块笔刷
│   │   ├── mesh_to_mc.py       # 网格转方块
│   │   ├── surface_optimization.py  # 面优化
│   │   └── sway_animation.py   # 摇摆动画
│   └── blend_files/            # 几何节点和材质库
└── doc/                        # 详细文档
```

### 常用命令

```python
# 重载插件（Blender 控制台）
import importlib
import MBM_workflow.load_modules as load_modules
importlib.reload(load_modules)
load_modules.register()

# 测试版本支持
python test_version_quick.py
```

### 核心设计

- **哈希字典笔刷**：O(1) 坐标查找，精确无误差
- **几何节点实例化**：非破坏性编辑，支持动画
- **版本抽象层**：Universal Format 实现跨版本转换

---

## 贡献者

| 角色 | 贡献者 |
|------|--------|
| 主要开发 | BaiGave (bilibili) |
| 几何节点 | 火锅料理、抛瓦尔第、暗影苦力怕、Piggestpig、荒芜新谷 |
| 着色器 | WangXinRui |
| 多进程支持 | Piggestpig / 冬猫夏羊工作室 |
| 翻译 | marshmallowlands |

---

## 许可证

本项目采用 [AGPL-3.0](https://github.com/BaiGave/BaiGave_Plugin/blob/main/LICENSE) 许可证。

---

## 联系与支持

- **QQ 群**: 878232347（Bug 反馈与交流）
- **Bilibili**: [白给的个人空间](https://space.bilibili.com/3461563635731405)
- **GitHub Issues**: [报告问题](https://github.com/BaiGave/BaiGave_Plugin/issues)

---

## 相关文档

- [CLAUDE.md](CLAUDE.md) - 项目开发指南
- [doc/data-flow-diagrams.md](doc/data-flow-diagrams.md) - 数据流程图
- [doc/dependency-update-guide.md](doc/dependency-update-guide.md) - 依赖更新指南
