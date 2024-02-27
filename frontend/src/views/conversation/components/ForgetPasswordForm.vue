<template>
  <div>
    <n-form ref="formRef" :model="form" :rules="rules">
      <n-form-item label="邮箱" path="email">
        <n-input v-model:value="form.email" placeholder="Enter your email" />
         <n-button @click="sendEmail" :disabled="sendingEmail" class="send-email-button">Send Email</n-button>
      </n-form-item>
      <n-form-item label="验证码" path="code">
        <n-input v-model:value="form.code" placeholder="Enter your code" />
      </n-form-item>
      <n-form-item label="新密码" path="password">
        <n-input v-model:value="form.password" type="password" placeholder="Enter new password" />
      </n-form-item>
    </n-form>
  </div>
</template>

<script setup>
import { ref ,watch} from 'vue';

const formRef = ref(null);
const sendingEmail = ref(false);
const form = ref({
  email: '',
  code: '',
  password: '',
});

const rules = {
  email: [{ required: true, message: 'Email is required', trigger: 'blur' }],
  code: [{ required: true, message: 'Verification code is required', trigger: 'blur' }],
  password: [{ required: true, message: 'New password is required', trigger: 'blur' }],
};
// 异步函数用于调用后端发送邮件的API
async function sendForgetPasswordEmail(email) {
  try {
    const response = await fetch('/api/send/email?email=' + encodeURIComponent(email), {
      method: 'GET', // 根据后端定义，这里使用GET请求
    });

    if (!response.ok) {
      // 如果响应状态码不是2xx，抛出错误
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to send reset password email');
    }

    // 请求成功，可以在这里处理响应数据，如显示成功消息
    console.log('Reset password email sent successfully');
    return await response.json(); // 返回成功解析的数据
  } catch (error) {
    console.error('Error sending reset password email:', error.message);
    throw error; // 把错误抛出，让调用者处理
  }
}

const sendEmail = async () => {
  if (form.value.email) {
    sendingEmail.value = true;
    try {
      // 调用上述定义的发送邮件函数
      await sendForgetPasswordEmail(form.value.email);
      // 显示成功消息
      alert('Reset password email sent successfully. Please check your inbox.');
    } catch (error) {
      // 显示错误消息
      alert(`Failed to send reset password email: ${error.message}`);
    } finally {
      sendingEmail.value = false; // 重新启用发送按钮
    }
  } else {
    alert('Email is missing');
  }
};
// Emit an event with the form data
const emit = defineEmits(['input']);
watch(form, () => {
  emit('input', form.value);
}, { deep: true });
</script>

