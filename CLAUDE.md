# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 Blender 插件（BaiGave's Tool / MBM-workflow），用于在 Blender 内直接导入、编辑和导出 Minecraft 地图数据。与 Mineways 或 jmc2obj 等工具不同，该插件导入的是带有 blockid 和 biome 属性的点云数据，通过几何节点实例化方块模型，支持非破坏性编辑。

## 核心架构

### 模块加载系统
- `__init__.py`: 插件入口，定义 `bl_info` 元数据
- `load_modules.py`: 管理所有模块的动态加载和重载，使用 `importlib.reload()` 支持开发时热更新
- `codes/dependency_manager.py`: 依赖管理模块，提供安全导入接口和优雅降级

### 核心功能模块
- `ui.py`: 定义插件的 UI 面板和操作界面
- `codes/property.py`: 定义所有 Blender 场景属性，包括路径配置、方块切换列表、MC 版本配置
- `codes/register.py`: 方块注册系统，将 Minecraft 方块状态映射到 Blender 对象 ID
- `codes/importfile.py`: 导入 .schem、.nbt 文件和世界存档
- `codes/exportfile.py`: 导出为 .schem 文件或直接写入存档
- `codes/schem.py`: 处理 schem 数据结构，创建点云网格和几何节点
- `codes/blockstates.py`: 解析 Minecraft blockstate JSON 文件，缓存方块模型数据
- `codes/functions/mesh_to_mc.py`: 将普通网格体转换为 Minecraft 方块，包含面优化算法
- `codes/functions/surface_optimization.py`: 包含“合并重叠面”等网格优化算法
- `codes/functions/sway_animation.py`: 实现植物和树叶的摇摆动画

### 几何节点系统
插件依赖外部 `.blend` 文件中的几何节点组（位于 `codes/blend_files/GeometryNodes.blend`）：
- **Schem 节点组**: 将点云实例化为方块模型
- **ObjToBlocks 节点组**: 普通网格转方块预览
- **模型转换节点组**: 完整的网格到方块转换，支持楼梯、台阶等特殊方块

### 多进程支持（实验性）
位于 `multiprocess/` 目录：
- `multiprocess_pool.py`: 进程池管理
- `schem_mp.py`: 多进程 Schem 处理逻辑
- 此模块用于加速大型文件的处理，目前可能未完全启用

## Minecraft 版本转换系统

### PyMCTranslate 架构

插件使用 PyMCTranslate 库进行 Minecraft 版本间的方块数据转换：

```
特定版本 → Universal Format → 目标版本
(1.12)        (中间层)          (1.21)
```

**Universal Format** 是平台无关的方块表示：
```python
{
    "namespace": "minecraft",
    "base_name": "oak_log",
    "properties": {"axis": "x"}
}
```

### 版本配置系统

版本配置已从硬编码改为可配置属性（`property.py`）：
```python
bpy.types.Scene.mc_platform        # 平台 (java/bedrock)
bpy.types.Scene.mc_version_major   # 主版本 (1)
bpy.types.Scene.mc_version_minor   # 次版本 (21)
bpy.types.Scene.mc_version_patch   # 补丁版本 (9)
```

**获取版本配置的辅助函数**：
```python
# 在 blockstates.py, schem.py 中
def get_mc_version_config():
    platform, version_tuple = scene.mc_platform, (...)
    return platform, version_tuple
```

**版本支持范围**（PyMCTranslate 1.2.39）：
- Java Edition: 1.12 ~ 1.21.9
- Bedrock Edition: 1.10 ~ 1.20.x

## 依赖管理（Blender 5.0+）

### 依赖结构

```
blender_manifest.toml  ← Blender 5.0+ 自动处理
    ↓
wheels/
    ├── py3-none-any.whl  (跨平台)
    └── cp311-win_amd64.whl  (平台特定)
```

### 关键依赖

| 包名 | 作用 | 版本 |
|------|------|------|
| amulet-core | Minecraft 世界解析 | 1.9.33 |
| PyMCTranslate | 版本转换系统 | 1.2.39 |
| amulet-nbt | NBT 数据格式 | 2.1.5 |
| portalocker | 文件锁定 | 3.2.0 |
| pillow | 图像处理 | 12.1.0 |

### 安全导入模式

使用 `codes/dependency_manager.py` 提供安全导入：
```python
from .codes.dependency_manager import amulet, amulet_nbt

# 依赖缺失时返回 None，优雅降级
if amulet is None:
    return {'CANCELLED'}
```

## Blender 5.0+ API 变化

### 几何节点修改器属性访问

```python
# Blender 5.0+ 正确方式
try:
    modifier['Input_58'] = value  # 旧语法
except (KeyError, TypeError):
    if modifier.node_group:
        for socket in modifier.node_group.inputs:
            if socket.identifier == 'Input_58':
                socket.default_value = value
                break
```

### 版本配置属性

使用 `IntProperty` 替代硬编码：
```python
bpy.types.Scene.mc_version_major = bpy.props.IntProperty(
    name="主版本号",
    default=1,
    min=1,
    max=2
)
```

## 常用命令

### 开发调试
```bash
# 在 Blender 控制台中重载插件
import importlib
import MBM_worflow.load_modules as load_modules
importlib.reload(load_modules)
load_modules.register()

# 查看当前注册的方块映射
import bpy
id_map = eval(bpy.data.texts.get("Blocks.py").as_string())

# 测试版本支持
python test_version_quick.py
```

### 测试导入
```python
# 导入 .schem 文件（在 Blender 中）
bpy.ops.baigave.import_schem(filepath='/path/to/file.schem')

# 应用修改器并合并重叠面（优化面数）
bpy.ops.object.modifier_apply(modifier="Schem")
bpy.ops.baigave.merge_overlapping_faces()
```

## 重要数据流

### 方块注册流程
1. `register_blocks(ids)` 在 `codes/register.py` 中被调用
2. 创建/更新 `Blocks` 集合，包含所有方块状态的模型对象
3. 在 Blender 文本数据中维护 `id_map` 字典（方块状态字符串 → 数字 ID）
4. 缓存在 `cached_models` 中避免重复解析 blockstate JSON

### 几何节点工作流
1. 导入时创建只包含顶点的网格，每个顶点有 `blockid`、`biome`、`waterlogged` 属性
2. 应用几何节点修改器，引用 `Blocks` 集合
3. 节点根据顶点的 `blockid` 属性实例化对应方块
4. 应用修改器后可使用"合并重叠面"优化面数

### 坐标系统
- Minecraft 坐标 (x, y, z) 转换为 Blender (x, -z, y)
- Y 轴在 MC 中是高度，在 Blender 中映射到 Z 轴

## 配置文件

### blender_manifest.toml

Blender 5.0+ 插件清单文件：
```toml
schema_version = "1.0.0"
type = "add-on"
blender_version_min = "5.0.0"

wheels = [
    "./wheels/amulet_core-1.9.33-py3-none-any.whl",
    "./wheels/pymctranslate-1.2.39-py3-none-any.whl",
    # ... 其他依赖
]
```

### 版本配置

场景属性（可通过 Blender UI 或代码修改）：
- `mc_platform`: "java" 或 "bedrock"
- `mc_version_major`: 1
- `mc_version_minor`: 21
- `mc_version_patch`: 9

## 注意事项

1. **坐标转换**: 始终注意 MC 和 Blender 的坐标轴差异
2. **方块 ID 映射**: 修改方块后需同步更新 `Blocks.py` 文本数据
3. **几何节点路径**: `geometrynodes_blend_path` 属性指向包含节点组的 .blend 文件
4. **缓存清理**: 更新模组/资源包后需删除 `schemcache/` 缓存
5. **不可逆操作**: 应用几何节点修改器后无法恢复到点云编辑状态
6. **版本限制**: PyMCTranslate 1.2.39 最高支持 Java 1.21.9，配置超过此版本会失败
7. **私有 API**: 避免使用 `amulet_nbt._load_nbt` 等私有模块，使用公共 API `amulet_nbt.load()`

## 开发提示

- 添加新方块类型时需更新 `codes/classification_files/block_type.py`
- 修改 UI 需编辑 `ui.py`
- 几何节点修改需编辑外部 `blend_files/GeometryNodes.blend`
- 使用 `bpy.app.timers.register()` 处理耗时操作的完成回调
- **修改几何节点属性时**：始终使用 `set_modifier_socket_value()` 辅助函数，该函数封装了 Blender 5.0+ 的兼容性处理
- **版本检查**：不再需要支持 Blender 4.x，所有新代码应直接使用 Blender 5.0+ API
- **版本转换**：使用 `level.translation_manager.get_version(platform, version)` 获取版本转换器
- **配置持久化**：`config.py` 用于存储插件配置，包含默认的模组列表和资源包配置

## 常见开发任务

### 添加新的几何节点属性访问

当需要操作几何节点修改器的输入/输出 socket 时，使用 `set_modifier_socket_value()` 辅助函数：

```python
from codes.functions.mesh_to_mc import set_modifier_socket_value

# 设置输入 socket 值
set_modifier_socket_value(modifier, 'Input_58', 'UV', uv_value, is_input=True)

# 设置输出属性名称
set_modifier_socket_value(modifier, 'Output_2_attribute_name', 'attribute', 'blockid', is_input=False)
```

### 获取 Minecraft 版本配置

```python
from codes.property import get_mc_version

platform, version_tuple = get_mc_version(context)
# 例如: ("java", (1, 21, 9))
```

### 安全导入依赖

```python
from codes.dependency_manager import amulet, amulet_nbt

# 检查依赖是否可用
if amulet is None:
    return {'CANCELLED'}
```

### 读取方块 ID 映射

```python
import bpy

text_data = bpy.data.texts.get("Blocks.py")
if text_data:
    id_map = eval(text_data.as_string())
    # id_map: {"minecraft:stone": 0, ...}
```

## 相关文档

- `doc/data-flow-diagrams.md`: 详细的数据流程图
- `doc/dependency-update-guide.md`: 依赖更新指南
- `doc/water-handling-analysis.md`: 水体方块处理分析
- `test_version_support.py`: 版本支持测试脚本
- `test_version_quick.py`: 快速版本测试脚本（控制台用）

## 项目结构概览

```
MBM_workflow/
├── __init__.py                 # 插件入口
├── load_modules.py             # 模块加载和重载
├── blender_manifest.toml       # Blender 5.0+ 清单文件
├── config.py                   # 配置持久化
├── CLAUDE.md                   # 本文档
├── wheels/                     # Python 依赖包
├── codes/
│   ├── dependency_manager.py   # 依赖管理
│   ├── property.py             # 场景属性定义
│   ├── register.py             # 方块注册系统
│   ├── blockstates.py          # 方块状态解析
│   ├── block.py                # 方块对象创建
│   ├── model.py                # 材质系统
│   ├── schem.py                # 导入处理
│   ├── exportfile.py           # 导出处理
│   ├── importfile.py           # 导入操作符
│   ├── create_world.py         # 存档创建
│   ├── functions/              # 功能模块
│   │   ├── mesh_to_mc.py       # 网格转方块
│   │   ├── surface_optimization.py  # 面优化
│   │   ├── sway_animation.py   # 摇摆动画
│   │   ├── brush.py            # 笔刷工具
│   │   ├── paint.py            # 上色工具
│   │   └── ...
│   ├── classification_files/   # 方块分类
│   │   └── block_type.py
│   └── blend_files/            # 外部资源
│       ├── GeometryNodes.blend # 几何节点组
│       └── Material.blend      # 材质着色器库
├── mutf8/                      # UTF-8 修改支持
├── colors/                     # 颜色对照表
├── doc/                        # 文档目录
├── multiprocess/               # 多进程支持（实验性）
└── test_version_*.py           # 测试脚本
```
