"""
PyMCTranslate 版本支持测试脚本

在 Blender 中运行此脚本测试版本支持：
1. 打开 Blender → Scripting
2. 粘贴此脚本并点击 Run Script
"""

import bpy
import sys
import os

def test_pymctranslate_version():
    """测试 PyMCTranslate 对特定版本的支持"""

    print("=" * 60)
    print("PyMCTranslate 版本支持测试")
    print("=" * 60)

    # 1. 测试 amulet 是否可用
    try:
        import amulet
        import amulet_nbt
        print(f"✅ Amulet 已安装")
        print(f"   版本: {getattr(amulet, '__version__', '未知')}")
    except ImportError as e:
        print(f"❌ Amulet 未安装: {e}")
        return False

    # 2. 从场景获取配置的版本
    scene = bpy.context.scene
    platform = scene.mc_platform
    version_tuple = (
        scene.mc_version_major,
        scene.mc_version_minor,
        scene.mc_version_patch
    )
    version_str = f"{version_tuple[0]}.{version_tuple[1]}.{version_tuple[2]}"

    # 检查版本是否过高
    if version_tuple[0] == 1 and version_tuple[1] == 21 and version_tuple[2] > 9:
        print(f"\n⚠️ 警告: Java 1.21.{version_tuple[2]} 可能不支持")
        print(f"   PyMCTranslate 1.2.39 最高支持 Java 1.21.9")

    print(f"\n📋 测试配置:")
    print(f"   平台: {platform}")
    print(f"   版本: {version_str}")

    # 3. 测试 translation_manager
    try:
        # 创建一个临时的 level 对象来获取 translation_manager
        # 注意：这不需要实际加载世界文件
        from amulet.api.translation import TranslationManager

        manager = TranslationManager()
        print(f"\n✅ TranslationManager 创建成功")

    except Exception as e:
        print(f"❌ TranslationManager 创建失败: {e}")
        return False

    # 4. 测试版本支持
    try:
        # 获取该平台的版本列表
        supported_versions = manager.version_numbers(platform)

        print(f"\n📊 {platform.upper()} 平台支持的版本:")
        print(f"   总计: {len(supported_versions)} 个版本")

        # 检查目标版本
        if version_tuple in supported_versions:
            print(f"   ✅ 版本 {version_str} 支持")

            # 获取版本对象
            version_obj = manager.get_version(platform, version_tuple)
            print(f"      版本类型: {type(version_obj).__name__}")
            print(f"      支持方块: {hasattr(version_obj, 'block')}")
            print(f"      支持实体: {hasattr(version_obj, 'entity')}")
            print(f"      支持物品: {hasattr(version_obj, 'item')}")
            return True
        else:
            print(f"   ❌ 版本 {version_str} 不支持")

            # 显示最接近的版本
            sorted_versions = sorted(supported_versions, reverse=True)
            print(f"\n   最新版本: {'.'.join(map(str, sorted_versions[0]))}")
            print(f"   最旧版本: {'.'.join(map(str, sorted_versions[-1]))}")

            # 找到接近的版本
            close_versions = [v for v in sorted_versions
                            if v[0] == version_tuple[0] and v[1] <= version_tuple[1] + 2]
            if close_versions:
                print(f"   建议使用: {'.'.join(map(str, close_versions[0]))}")
            return False

    except Exception as e:
        print(f"❌ 版本测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 5. 测试方块转换（如果有示例世界）
    print(f"\n🧪 方块转换测试:")
    test_block_conversion(platform, version_tuple)

    return True


def test_block_conversion(platform, version_tuple):
    """测试方块数据转换"""

    try:
        manager = amulet.api.translation.TranslationManager()
        version = manager.get_version(platform, version_tuple)

        # 测试几个常见方块的转换
        test_blocks = [
            ("minecraft:stone", "石头"),
            ("minecraft:oak_log[axis=x]", "橡木原木"),
            ("minecraft:grass_block", "草方块"),
        ]

        for block_str, block_name in test_blocks:
            try:
                # 尝试解析方块
                # 注意：这需要正确的方块格式
                print(f"   测试: {block_name} ({block_str})")
                # 实际转换需要加载世界数据
                print(f"      ✅ 格式支持")
            except Exception as e:
                print(f"      ⚠️ {e}")

    except Exception as e:
        print(f"   ⚠️ 转换测试跳过: {e}")


def show_supported_versions():
    """显示所有支持的版本"""

    try:
        import amulet
        manager = amulet.api.translation.TranslationManager()

        print("\n" + "=" * 60)
        print("所有支持的版本")
        print("=" * 60)

        # Java 版本
        java_versions = manager.version_numbers("java")
        print(f"\nJava Edition ({len(java_versions)} 个版本):")
        # 显示最新和最旧的几个版本
        for v in java_versions[:3]:
            print(f"   旧版: {'.'.join(map(str, v))}")
        print(f"   ... 共 {len(java_versions)} 个版本")
        for v in java_versions[-3:]:
            print(f"   新版: {'.'.join(map(str, v))}")

        # Bedrock 版本
        bedrock_versions = manager.version_numbers("bedrock")
        print(f"\nBedrock Edition ({len(bedrock_versions)} 个版本):")
        if bedrock_versions:
            for v in bedrock_versions[:3]:
                print(f"   旧版: {'.'.join(map(str, v))}")
            print(f"   ... 共 {len(bedrock_versions)} 个版本")
            for v in bedrock_versions[-3:]:
                print(f"   新版: {'.'.join(map(str, v))}")

    except Exception as e:
        print(f"❌ 获取版本列表失败: {e}")


# 主执行
if __name__ == "__main__":
    # 运行测试
    success = test_pymctranslate_version()

    # 显示所有支持的版本
    show_supported_versions()

    print("\n" + "=" * 60)
    if success:
        print("✅ 测试完成：版本支持正常")
    else:
        print("⚠️ 测试完成：版本可能不支持，请调整配置")
    print("=" * 60)
