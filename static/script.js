// 全局变量
let localFileValid = false;
let nationalFileValid = false;

// DOM 加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeFileUploads();
    initializeCompareButton();
});

// 初始化文件上传
function initializeFileUploads() {
    const localFileInput = document.getElementById('localFile');
    const nationalFileInput = document.getElementById('nationalFile');

    if (localFileInput) {
        localFileInput.addEventListener('change', function(e) {
            handleFileUpload(e.target.files[0], 'local');
        });
    }

    if (nationalFileInput) {
        nationalFileInput.addEventListener('change', function(e) {
            handleFileUpload(e.target.files[0], 'national');
        });
    }
}

// 处理文件上传
async function handleFileUpload(file, type) {
    if (!file) return;

    const statusElement = document.getElementById(`${type}Status`);
    const progressElement = document.getElementById(`${type}Progress`);

    // 检查文件大小（10MB）
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        showStatus(statusElement, 'error', '文件大小超过限制（最大10MB）');
        return;
    }

    // 检查文件扩展名
    const allowedExtensions = ['.xls', '.xlsx'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!allowedExtensions.includes(fileExtension)) {
        showStatus(statusElement, 'error', '文件格式不支持，仅支持 .xls 和 .xlsx');
        return;
    }

    // 显示上传中状态
    showStatus(statusElement, 'validating', '正在上传和校验...');
    progressElement.style.display = 'block';

    // 创建表单数据
    const formData = new FormData();
    formData.append('file', file);

    try {
        // 上传文件
        const endpoint = type === 'local' ? '/upload/local' : '/upload/national';
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        // 隐藏进度条
        progressElement.style.display = 'none';

        if (data.success) {
            if (data.valid) {
                // 校验成功
                showStatus(statusElement, 'success', '✓ 文件上传成功，格式校验通过');
                if (type === 'local') {
                    localFileValid = true;
                } else {
                    nationalFileValid = true;
                }
            } else {
                // 校验失败
                let errorMsg = '✗ ' + (data.error || '模板格式不正确');
                showStatus(statusElement, 'error', errorMsg);
                if (type === 'local') {
                    localFileValid = false;
                } else {
                    nationalFileValid = false;
                }
            }
        } else {
            // 上传失败
            showStatus(statusElement, 'error', '✗ ' + (data.error || '上传失败'));
            if (type === 'local') {
                localFileValid = false;
            } else {
                nationalFileValid = false;
            }
        }

        // 更新比对按钮状态
        updateCompareButton();

    } catch (error) {
        console.error('上传失败:', error);
        progressElement.style.display = 'none';
        showStatus(statusElement, 'error', '✗ 上传失败，请重试');
        if (type === 'local') {
            localFileValid = false;
        } else {
            nationalFileValid = false;
        }
        updateCompareButton();
    }
}

// 显示状态消息
function showStatus(element, type, message) {
    element.className = `status-message ${type}`;
    element.textContent = message;
}

// 初始化比对按钮
function initializeCompareButton() {
    const compareBtn = document.getElementById('compareBtn');

    if (compareBtn) {
        compareBtn.addEventListener('click', async function() {
            if (!localFileValid || !nationalFileValid) {
                alert('请先上传并校验两个文件');
                return;
            }

            // 禁用按钮
            compareBtn.disabled = true;

            // 显示加载动画
            const progressElement = document.getElementById('compareProgress');
            if (progressElement) {
                progressElement.style.display = 'flex';
            }

            try {
                // 执行比对
                const response = await fetch('/compare', {
                    method: 'POST'
                });

                const data = await response.json();

                if (data.success) {
                    // 跳转到结果页面
                    window.location.href = '/result';
                } else {
                    alert('比对失败: ' + (data.error || '未知错误'));
                    compareBtn.disabled = false;
                    if (progressElement) {
                        progressElement.style.display = 'none';
                    }
                }

            } catch (error) {
                console.error('比对失败:', error);
                alert('比对失败，请重试');
                compareBtn.disabled = false;
                if (progressElement) {
                    progressElement.style.display = 'none';
                }
            }
        });
    }
}

// 更新比对按钮状态
function updateCompareButton() {
    const compareBtn = document.getElementById('compareBtn');
    if (compareBtn) {
        compareBtn.disabled = !(localFileValid && nationalFileValid);
    }
}

// 折叠/展开区域（用于结果页面）
function toggleSection(id) {
    const element = document.getElementById(id);
    if (!element) return;

    const header = element.previousElementSibling;
    const icon = header ? header.querySelector('.toggle-icon, .toggle-icon-small') : null;

    if (element.classList.contains('collapsed')) {
        element.classList.remove('collapsed');
        if (icon) {
            icon.textContent = icon.classList.contains('toggle-icon') ? '▼' : '▼';
        }
    } else {
        element.classList.add('collapsed');
        if (icon) {
            icon.textContent = icon.classList.contains('toggle-icon') ? '▶' : '►';
        }
    }
}
