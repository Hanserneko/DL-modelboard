<template>
  <div>
    <el-button type="primary" @click="dialogVisible = true">登录</el-button>

    <el-dialog title="登录" v-model="dialogVisible" width="30%" :close-on-click-modal="false">
      <el-form :model="loginForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="loginForm.password" show-password />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleLogin">登录</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const dialogVisible = ref(false)

const loginForm = ref({
  username: '',
  password: ''
})

const handleLogin = () => {
  console.log('用户名:', loginForm.value.username)
  console.log('密码:', loginForm.value.password)


  dialogVisible.value = false
}
</script>
