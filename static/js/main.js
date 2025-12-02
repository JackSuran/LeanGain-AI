// 主JavaScript文件
document.addEventListener('DOMContentLoaded', function() {
    // 自动隐藏警告消息
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // 确认删除操作
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('确定要删除吗？此操作不可撤销。')) {
                e.preventDefault();
            }
        });
    });

    // 表单验证增强
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // 实时体重输入提示
    const weightInput = document.getElementById('weightInput');
    if (weightInput) {
        weightInput.addEventListener('input', function() {
            const value = parseFloat(this.value);
            const feedback = document.getElementById('weightFeedback');
            if (feedback) {
                if (value < 30) {
                    feedback.textContent = '体重过轻，请确认单位是否为公斤。';
                    feedback.className = 'invalid-feedback d-block';
                } else if (value > 200) {
                    feedback.textContent = '体重较重，请确认单位是否为公斤。';
                    feedback.className = 'invalid-feedback d-block';
                } else {
                    feedback.className = 'invalid-feedback d-none';
                }
            }
        });
    }
});

// 工具函数
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function showLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 处理中...';
    button.disabled = true;
    return originalText;
}

function hideLoading(button, originalText) {
    button.innerHTML = originalText;
    button.disabled = false;
}