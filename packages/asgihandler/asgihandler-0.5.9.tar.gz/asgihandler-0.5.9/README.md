# 4.1、可以先升级打包工具
pip install --upgrade setuptools wheel twine

# 4.2、打包
python setup.py sdist bdist_wheel

# 4.3、可以先检查一下包
twine check dist/*

# 4.4、上传包到pypi（需输入用户名、密码）
twine upload dist/*