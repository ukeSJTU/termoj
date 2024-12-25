# 格式化代码
format:
	black .
	isort .

# Lint 检查
lint:
	isort --check-only .

# 运行测试
test:
	pytest

# 运行所有检查
all: format lint type-check test