<template>
  <n-modal :show="isShown" @update:show="updateShow" title="Forget Password" width="600">
    <n-form ref="formRef" :model="form" :rules="rules">
      <n-form-item label="Email" path="email">
        <n-input v-model:value="form.email" placeholder="Enter your email" />
      </n-form-item>
      <n-form-item label="Verification Code" path="code">
        <n-input v-model:value="form.code" placeholder="Enter your code" />
        <n-button @click="sendCode">Send Code</n-button>
      </n-form-item>
      <n-form-item label="New Password" path="newPassword">
        <n-input v-model:value="form.newPassword" placeholder="Enter new password" type="password" />
      </n-form-item>
      <n-form-item label="Confirm New Password" path="confirmNewPassword">
        <n-input v-model:value="form.confirmNewPassword" placeholder="Confirm new password" type="password" />
      </n-form-item>
    </n-form>
    <template #footer>
      <n-button @click="resetPassword" type="primary">Reset Password</n-button>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue';

const props = defineProps({
  isShown: Boolean
});
const emit = defineEmits(['update:show']);

const form = ref({
  email: '',
  code: '',
  newPassword: '',
  confirmNewPassword: ''
});
const rules = {
  // Add your validation rules here
};

const formRef = ref(null);

const sendCode = () => {
  // Implement sending code logic here
  console.log('Sending verification code to:', form.value.email);
};

const resetPassword = () => {
  // Validate form and implement reset password logic here
  console.log('Reset password with:', form.value);
  emit('update:show', false); // Close dialog after resetting the password
};

const updateShow = (value) => {
  emit('update:show', value);
};
</script>
