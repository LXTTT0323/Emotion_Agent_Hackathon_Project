#!/bin/bash

echo "开始运行情感代理上下文存储系统测试..."
echo ""

# 检查Python是否已安装
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo "错误: 未找到Python安装。请安装Python 3.6或更高版本。"
    exit 1
fi

echo "使用 $PYTHON 运行测试..."
echo ""

# 检查context_store.py文件是否存在
if [ ! -f "context_store.py" ]; then
    echo "错误: 未找到context_store.py文件。请确保你在正确的目录中。"
    exit 1
fi

# 检查test_context_store.py文件是否存在
if [ ! -f "test_context_store.py" ]; then
    echo "错误: 未找到test_context_store.py文件。请确保你在正确的目录中。"
    exit 1
fi

# 运行测试脚本
echo "运行测试脚本..."
$PYTHON test_context_store.py

# 检查测试是否成功
if [ $? -eq 0 ]; then
    echo ""
    echo "测试成功完成！"
    
    # 检查是否生成了memory_updated.json文件
    if [ -f "memory_updated.json" ]; then
        FILE_SIZE=$(du -h "memory_updated.json" | cut -f1)
        echo "生成的memory_updated.json文件大小: $FILE_SIZE"
    else
        echo "警告: 未找到memory_updated.json文件。"
    fi
else
    echo ""
    echo "测试运行失败。请查看上面的错误信息。"
fi

echo ""
echo "如需更多信息，请参考README.md文件。" 