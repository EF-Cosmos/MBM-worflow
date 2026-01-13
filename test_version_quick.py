"""
快速版本支持测试（Blender 控制台中运行）

在 Blender 控制台（Window → Toggle System Console）中粘贴以下代码：
"""

# 快速测试脚本
import sys
try:
    import amulet
    manager = amulet.api.translation.TranslationManager()

    # 获取配置的版本
    scene = bpy.context.scene
    platform = scene.mc_platform
    version = (scene.mc_version_major, scene.mc_version_minor, scene.mc_version_patch)

    # 获取所有支持的版本
    supported = manager.version_numbers(platform)

    print(f"\n=== 版本支持测试 ===")
    print(f"平台: {platform}")
    print(f"配置版本: {'.'.join(map(str, version))}")
    print(f"支持版本数: {len(supported)}")
    print(f"是否支持: {version in supported}")

    if version not in supported:
        print(f"\n⚠️ 警告: 版本 {'.'.join(map(str, version))} 不支持！")
        print(f"最新版本: {'.'.join(map(str, sorted(supported, reverse=True)[0]))}")

except ImportError:
    print("❌ Amulet 未安装，请在 Blender 5.0+ 中安装插件")
except Exception as e:
    print(f"❌ 错误: {e}")
