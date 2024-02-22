<template>
  <div>
    <n-form ref="formRef" :model="form" :rules="rules">
      <n-form-item label="Email" path="email">
        <n-input v-model:value="form.email" placeholder="Enter your email" />
      </n-form-item>
      <n-form-item label="Verification Code" path="code">
        <n-input v-model:value="form.code" placeholder="Enter your code" />
      </n-form-item>
      <n-form-item label="New Password" path="newPassword">
        <n-input v-model:value="form.newPassword" type="password" placeholder="Enter new password" />
      </n-form-item>
    </n-form>
  </div>
</template>

<script setup>
import { ref ,watch} from 'vue';

const formRef = ref(null);

const form = ref({
  email: '',
  code: '',
  newPassword: '',
});

const rules = {
  email: [{ required: true, message: 'Email is required', trigger: 'blur' }],
  code: [{ required: true, message: 'Verification code is required', trigger: 'blur' }],
  newPassword: [{ required: true, message: 'New password is required', trigger: 'blur' }],
};

// Emit an event with the form data
const emit = defineEmits(['input']);
watch(form, () => {
  emit('input', form.value);
}, { deep: true });
</script>

