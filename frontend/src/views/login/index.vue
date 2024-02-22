<template>
  <!-- Login Form -->
  <div class="flex relative flex-col justify-center items-center w-full h-full">
    <div class="absolute top-4 right-4 space-x-3">
      <n-dropdown :options="languageOptions" placement="bottom-start">
        <n-button secondary circle>
          <n-icon :component="Language" />
        </n-button>
      </n-dropdown>
      <n-button secondary circle @click="toggleTheme">
        <n-icon :component="themeIcon" />
      </n-button>
    </div>
    <div class="mb-6">
      <!-- <CWSIcon :color="appStore.theme == 'dark' ? 'white': 'black'" class="w-60" /> -->
      <n-gradient-text :size="32" type="success" class="select-none">
        ChatGPT● Web Share
      </n-gradient-text>
    </div>
    <n-card embedded class="w-90 p-6 m-6 rounded-lg">
      <n-form
        ref="formRef"
        class="space-y-2"
        :model="formValue"
        :show-label="false"
        :rules="loginRules"
        :wrapper-col="{ span: 16 }"
      >
        <n-form-item path="username">
          <n-input
            v-model:value="formValue.username"
            :placeholder="$t('tips.pleaseEnterUsername')"
            :input-props="{
              autoComplete: 'username',
            }"
          >
            <template #prefix>
              <n-icon><PersonFilled /></n-icon>
            </template>
          </n-input>
        </n-form-item>
        <n-form-item path="password">
          <n-input
            v-model:value="formValue.password"
            type="password"
            show-password-on="click"
            :placeholder="$t('tips.pleaseEnterPassword')"
            :input-props="{
              autoComplete: 'current-password',
            }"
            @keyup.enter="login"
          >
            <template #prefix>
              <n-icon><LockFilled /></n-icon>
            </template>
          </n-input>
        </n-form-item>
      </n-form>
      <div class="flex justify-end mt-3 mb-5">
        <n-checkbox v-model:checked="rememberPassword">
          {{ $t('commons.rememberPassword') }}
        </n-checkbox>


      </div>
       <div class="auth-container">
        <n-button class="auth-button login-button" type="primary" :loading="loading" @click="login">
          {{ $t('commons.login') }}
        </n-button>
        <a class="forget-password-link" @click="resetPassword">{{ $t('commons.forgetPassword') }}</a>
<!--    <ForgetPasswordDialog :isShown="isForgetPasswordDialogShown" @update:show="isForgetPasswordDialogShown = $event" />-->
        <n-button class="auth-button register-button" type="primary" @click="drawer.open('create', null)">
          {{ $t('commons.addUser') }}
        </n-button>
      </div>

    </n-card>
  </div>
  <n-drawer
    v-if="drawer.show.value"
    v-model:show="drawer.show.value"
    :width="gtsm() ? '30%' : '60%'"
    :placement="'left'"
  >
    <n-drawer-content closable :title="drawer.title.value" :native-scrollbar="false">

      <CreateUserForm v-if="drawer.name.value == 'create'" @save="handleCreateUser" />
      <UpdateUserBasicForm
        v-else-if="drawer.name.value == 'updateBasic'"
        :user="currentUser"
        @save="handleUpdateUserBasic"
      />
      <UpdateUserSettingForm
        v-else-if="drawer.name.value == 'updateSetting'"
        :user="currentUser"
        @save="handleUpdateUserSetting"
      />
    </n-drawer-content>
  </n-drawer>
</template>

<script setup lang="ts">
import { Language } from '@vicons/ionicons5';
import { DarkModeRound, LightModeRound, LockFilled,PersonFilled } from '@vicons/material';
import {FormInst, NButton} from 'naive-ui';
import { FormRules, FormValidationError } from 'naive-ui/es/form';
import { computed, reactive, ref} from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

import {
  deleteUserApi,
  // getAllUserApi,
  LoginData,
  registerApi,
  updateUserByIdApi, updateUserMeApi,
  updateUserSettingApi
} from '@/api/user';
import CWSIcon from '@/components/icons/CWSIcon.vue';
import { useAppStore, useUserStore } from '@/store';
import {Dialog, Message} from '@/utils/tips';
import {useDrawer} from "@/hooks/drawer";
const currentUser = ref<UserReadAdmin | null>(null);
const gtsm = screenWidthGreaterThan('sm');
import {UserCreate, UserReadAdmin, UserSettingSchema, UserUpdateAdmin} from "@/types/schema";
import UpdateUserSettingForm from "@/views/admin/components/UpdateUserSettingForm.vue";
import UpdateUserBasicForm from "@/views/admin/components/UpdateUserBasicForm.vue";
import CreateUserForm from "@/views/admin/components/CreateUserForm.vue";
import {screenWidthGreaterThan} from "@/utils/media";
const userManagerRef = ref(null);
const data = ref<Array<UserReadAdmin>>([]);
const router = useRouter();
const { t } = useI18n();
const userStore = useUserStore();
const appStore = useAppStore();
import ForgetPasswordDialog from './ForgetPasswordDialog.vue';
import {popupForgetPasswordDialog, popupNewConversationDialog, popupResetUserPasswordDialog} from "@/utils/renders";

const formRef = ref<FormInst>();
const drawer = useDrawer([
  { name: 'create', title: t('commons.createUser') },
  {
    name: 'updateBasic',
    title: t('commons.updateUserBasic'),
    beforeOpen: (row: UserReadAdmin) => {
      currentUser.value = JSON.parse(JSON.stringify(row));
    },
    afterClose: () => {
      currentUser.value = null;
    },
  },
  {
    name: 'updateSetting',
    title: t('commons.updateUserSetting'),
    beforeOpen: (row: UserReadAdmin) => {
      currentUser.value = JSON.parse(JSON.stringify(row));
    },
    afterClose: () => {
      currentUser.value = null;
    },
  },
]);
const handleCreateUser = (userCreate: UserCreate) => {
  registerApi(userCreate)
    .then(() => {
      // 如果创建成功，显示成功消息并关闭抽屉
      Message.success(t('tips.createSuccess'));
      drawer.close(); // 成功后关闭抽屉
    })
    .catch((error) => {
      // 如果创建失败，显示错误消息但不关闭抽屉
      // Message.error(t('tips.createFailed') + ': ' + error.message);
      drawer.close(false); // 失败时不关闭抽屉
    });
};
// const handleCreateUser = (userCreate: UserCreate) => {
//   registerApi(userCreate)
//     .then(() => {
//       Message.success(t('tips.createSuccess'));
//
//     })
//     .finally(() => {
//       drawer.close();
//     });
// };
const handleUpdateUserBasic = (userUpdate: Partial<UserUpdateAdmin>) => {
  if (!currentUser.value) return;
  if (userUpdate.password === '') {
    delete userUpdate.password;
  }
  updateUserByIdApi(currentUser.value.id, userUpdate)
    .then((res) => {
      Message.success(t('tips.updateSuccess'));
      data.value = data.value.map((item) => {
        if (item.id === res.data.id) {
          return res.data;
        } else {
          return item;
        }
      });
    })
    .finally(() => {
      drawer.close();
    });
};

const handleUpdateUserSetting = (userSetting: Partial<UserSettingSchema>) => {
  if (!currentUser.value) return;
  updateUserSettingApi(currentUser.value.id, userSetting)
    .then((res) => {
      Message.success(t('tips.updateSuccess'));
      data.value = data.value.map((item) => {
        if (item.id === res.data.id) {
          return res.data;
        } else {
          return item;
        }
      });
    })
    .finally(() => {
      drawer.close();
    });
};

const handleDeleteUser = (row: UserReadAdmin) => {
  const d = Dialog.warning({
    title: t('commons.deleteUser'),
    content: t('tips.deleteUserConfirm'),
    positiveText: t('commons.confirm'),
    negativeText: t('commons.cancel'),
    onPositiveClick: () => {
      d.loading = true;
      return new Promise((resolve, reject) => {
        deleteUserApi(row.id)
          .then(() => {
            Message.success(t('tips.deleteUserSuccess'));

            resolve(true);
          })
          .catch((err) => {
            Message.error(t('tips.deleteUserFailed') + ': ' + err);
            reject(err);
          })
          .finally(() => {
            d.loading = false;
          });
      });
    },
  });
};

const resetPassword = () => {
  popupForgetPasswordDialog().then(() => {
    // 这里可以添加密码重置成功后的代码
  }).catch((error) => {
    // 这里可以处理错误情况
    console.error(error);
  });
};
const rememberPassword = computed({
  get: () => userStore.savedLoginForm.rememberPassword,
  set: (value) => {
    userStore.savedLoginForm.rememberPassword = value;
    if (!value) {
      userStore.savedLoginForm.savedUsername = '';
      userStore.savedLoginForm.savedPassword = '';
    }
  },
});

const themeIcon = computed(() => {
  if (appStore.theme == 'dark') {
    return DarkModeRound;
  } else {
    return LightModeRound;
  }
});

const toggleTheme = () => {
  appStore.toggleTheme();
};

const formValue = reactive({
  username: userStore.savedLoginForm.savedUsername || '',
  password: userStore.savedLoginForm.savedPassword || '',
});

const loading = ref(false);
const loginRules = {
  username: { required: true, message: t('tips.pleaseEnterUsername') },
  password: { required: true, message: t('tips.pleaseEnterPassword') },
} as FormRules;

const login = async () => {
  if (loading.value) return;
  formRef.value
    ?.validate((errors?: Array<FormValidationError>) => {
      if (!errors) {
        loading.value = true;
      }
    })
    .then(async () => {
      try {
        await userStore.login(formValue as LoginData);
        const { redirect } = router.currentRoute.value.query;
        await userStore.fetchUserInfo();
        Message.success(t('tips.loginSuccess'));
        if (redirect) {
          await router.push(redirect as string);
          return;
        }
        await router.push({
          name: userStore.user?.is_superuser ? 'admin' : 'conversation',
        });
        if (rememberPassword.value) userStore.setSavedLoginInfo(formValue.username, formValue.password);
      } catch (error) {
        console.log(error);
      } finally {
        loading.value = false;
      }
    });
};

const languageOptions = [
  {
    label: '简体中文',
    key: 'zh-CN',
    props: {
      onClick: () => {
        appStore.setLanguage('zh-CN');
      },
    },
  },
  {
    label: 'Bahasa Melayu',
    key: 'ms-MY',
    props: {
      onClick: () => {
        appStore.setLanguage('ms-MY');
      },
    },
  },
  {
    label: 'English',
    key: 'en-US',
    props: {
      onClick: () => {
        appStore.setLanguage('en-US');
      },
    },
  },
];

if (userStore.user) {
  router.push({ name: 'conversation' });
}
</script>

<style scoped>
@keyframes blink {
  0%,
  100% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
}

.blink {
  animation: blink 1s ease-in-out infinite;
}

.auth-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px; /* Adjust the gap between elements */
}

.auth-button {
  width: 100%; /* Make buttons full width */
}

.forget-password-link {
  color: #007bff; /* Make forget password link blue */
  cursor: pointer;
  margin: 10px 0; /* Add some margin for spacing */
}

</style>
