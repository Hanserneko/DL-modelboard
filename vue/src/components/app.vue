<template>
  <!-- 主布局容器 -->
  <el-container class="app-root">
    <!-- 侧边栏 -->
    <el-aside :width="asideWidth + 'px'" class="sidebar" :class="{ collapsed: asideWidth < 200 }">
      <!-- 菜单 -->
      <el-menu :default-active="activeMenu" class="el-menu-vertical-demo" @select="handleSelect"
        background-color="var(--el-bg-color-overlay)" text-color="var(--el-text-color-primary)"
        active-text-color="var(--el-color-primary)">
        <el-menu-item index="1">
          <el-icon>
            <HomeFilled />
          </el-icon>
          <span>主页</span>
        </el-menu-item>
        <el-menu-item index="2">
          <el-icon>
            <Cpu />
          </el-icon>
          <span>模型管理</span>
        </el-menu-item>
        <el-menu-item index="3">
          <el-icon>
            <Files />
          </el-icon>
          <span>数据集管理</span>
        </el-menu-item>
        <el-menu-item index="4">
          <el-icon>
            <List />
          </el-icon>
          <span>任务管理</span>
        </el-menu-item>
        <el-menu-item index="5">
          <el-icon>
            <Setting />
          </el-icon>
          <span>设置</span>
        </el-menu-item>
      </el-menu>
      <!-- 拖拽条：用于调整侧边栏宽度 -->
      <div class="drag-bar" @mousedown="startDrag"></div>
    </el-aside>

    <!-- 右侧内容区 -->
    <el-container>
      <!-- 顶栏 -->
      <el-header class="header-bar">
        <div class="header-right">
          <!-- 未登录时显示登录/注册按钮和弹窗 -->
          <div v-if="!userStore.isLoggedIn">
            <el-button type="primary"
              @click="isRegisterMode = false; dialogVisible = true; resetFormData()">登录</el-button>
            <el-button type="default" style="margin-left: 8px"
              @click="isRegisterMode = true; dialogVisible = true; resetFormData()">注册</el-button>

            <!-- 登录/注册弹窗 -->
            <el-dialog :title="isRegisterMode ? '注册' : '登录'" v-model="dialogVisible" width="30%"
              :close-on-click-modal="true">
              <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="80px">
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="loginForm.username" />
                </el-form-item>
                <el-form-item label="密码" prop="password">
                  <el-input type="password" v-model="loginForm.password" :show-password="true"
                    @keyup.enter="onSubmit" />
                </el-form-item>
                <!-- 注册模式下额外显示 -->
                <el-form-item v-if="isRegisterMode" label="确认密码" prop="confirmPassword">
                  <el-input type="password" v-model="loginForm.confirmPassword" :show-password="true" />
                </el-form-item>
                <el-form-item v-if="isRegisterMode" label="邮箱" prop="email">
                  <el-input v-model="loginForm.email" />
                </el-form-item>
              </el-form>
              <template #footer>
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" @click="onSubmit">{{ isRegisterMode ? '注册' : '登录' }}</el-button>
                <el-button type="link" @click="toggleMode">
                  {{ isRegisterMode ? '已有账号？去登录' : '没有账号？去注册' }}
                </el-button>
              </template>
            </el-dialog>
          </div>
          <!-- 已登录时显示头像和下拉菜单 -->
          <div v-else>
            <el-dropdown trigger="click">
              <el-avatar :size="32" :icon="UserFilled" />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item disabled>你好，{{ userStore.username }}</el-dropdown-item>
                  <el-dropdown-item divided @click="userStore.logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
// -------------------- 导入依赖 --------------------
import { ref } from 'vue'
import {
  UserFilled,
  HomeFilled,
  Cpu,
  Files,
  List,
  Setting,
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import type { FormInstance } from 'element-plus'

// -------------------- 侧边栏菜单相关 --------------------
const activeMenu = ref('1')
const router = useRouter()

const handleSelect = (index: string) => {
  activeMenu.value = index
  // 根据菜单项跳转路由
  switch (index) {
    case '1':
      router.push({ name: 'home' })
      break
    case '2':
      router.push({ name: 'model' })
      break
    case '3':
      router.push({ name: 'dataset' })
      break
    case '4':
      router.push({ name: 'task' })
      break
    case '5':
      router.push({ name: 'setting' })
      break
  }
}

// -------------------- 侧边栏拖拽相关 --------------------
const asideWidth = ref(200) // 侧边栏初始宽度
const minWidth = 200        // 最小宽度
const maxWidth = 300        // 最大宽度
const collapsedWidth = 70; // 侧边栏折叠后的宽度，与样式保持一致
const snapThreshold = 20; // 吸附阈值，越小越丝滑
let startX = 0              // 拖拽起始鼠标位置
let startWidth = 0          // 拖拽起始宽度
let isDragging = false;

const startDrag = (e: MouseEvent) => {
  startX = e.clientX;
  startWidth = asideWidth.value;
  isDragging = true;
  document.body.style.cursor = 'ew-resize';
  document.addEventListener('mousemove', onDrag);
  document.addEventListener('mouseup', stopDrag);
};

const onDrag = (e: MouseEvent) => {
  if (!isDragging) return;
  const delta = e.clientX - startX;
  let newWidth = startWidth + delta;

  // 丝滑吸附逻辑
  if (newWidth < collapsedWidth + snapThreshold) {
    newWidth = collapsedWidth;
  } else if (newWidth < minWidth) {
    newWidth = minWidth;
  }
  if (newWidth > maxWidth) {
    newWidth = maxWidth;
  }
  asideWidth.value = newWidth;
};

const stopDrag = () => {
  isDragging = false;
  document.body.style.cursor = '';
  // 松手时如果接近折叠宽度则吸附
  if (asideWidth.value < collapsedWidth + snapThreshold) {
    asideWidth.value = collapsedWidth;
  }
  document.removeEventListener('mousemove', onDrag);
  document.removeEventListener('mouseup', stopDrag);
}

// -------------------- 深色模式 --------------------
document.documentElement.classList.add('dark')

// -------------------- 用户信息与登录注册相关 --------------------
const userStore = useUserStore()
userStore.init()
const dialogVisible = ref(false)
const isRegisterMode = ref(false) // true 表示注册模式

// 登录/注册表单校验规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z0-9_]{3,14}$/,
      message: '用户名只能包含字母、数字和下划线，且长度为3-14位',
      trigger: 'blur'
    }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码不能少于8位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (value !== loginForm.value.password) {
          callback(new Error('两次密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    {
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      message: '邮箱格式不正确',
      trigger: 'blur'
    }
  ]
}

// 登录/注册表单数据
const loginForm = ref({
  username: '',
  password: '',
  confirmPassword: '',
  email: ''
})
const loginFormRef = ref<FormInstance | null>(null)

// 重置表单
const resetFormData = () => {
  Object.assign(loginForm.value, {
    username: '',
    password: '',
    confirmPassword: '',
    email: ''
  })
  loginFormRef.value?.clearValidate()
}

// 切换登录/注册模式
const toggleMode = () => {
  isRegisterMode.value = !isRegisterMode.value
  resetFormData()
}

// 登录/注册提交
const onSubmit = () => {
  if (!loginFormRef.value) return
  loginFormRef.value.validate((valid: boolean) => {
    if (!valid) return
    if (isRegisterMode.value) {
      // 注册逻辑
      console.log('注册成功:', loginForm.value)
      userStore.login(loginForm.value.username) // 自动登录
    } else {
      // 登录逻辑
      console.log('登录成功:', loginForm.value)
      userStore.login(loginForm.value.username)
    }
    dialogVisible.value = false
    resetFormData()
  })
}
</script>

<style scoped>
/* 主容器填充全屏 */
.app-root {
  width: 100vw;
  height: 100vh;
  min-width: 0;
  min-height: 0;
  box-sizing: border-box;
  overflow: hidden;
  background: var(--el-bg-color);
}

/* 侧边栏样式 */
.sidebar {
  height: 100vh;
  background: var(--el-bg-color-overlay);
  border-right: 1px solid var(--el-border-color-dark);
  box-sizing: border-box;
  position: relative;
}

/* 调整拖拽条样式 */
.drag-bar {
  position: absolute;
  top: 0;
  right: 0;
  width: 5px;
  height: 100%;
  cursor: ew-resize;
  background: var(--el-border-color-dark);
  z-index: 10;
  transition: background 0.2s, right 0.2s;
  /* 拖拽时更宽，提升体验 */
}

.drag-bar:hover {
  background: var(--el-color-primary);
}

/* 折叠状态下的侧边栏样式 */
.sidebar.collapsed {
  width: 70px;
  overflow: hidden;
}

/* 调整菜单图标和文字样式 */
.sidebar.collapsed .el-menu-item span {
  display: none;
}

.sidebar.collapsed .el-menu-item .el-icon {
  margin: 0 auto;
}

/* 顶栏样式 */
.header-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  background: var(--el-bg-color-overlay);
  border-bottom: 1px solid var(--el-border-color-dark);
  height: 60px;
}

/* 顶栏右侧内容 */
.header-right {
  display: flex;
  align-items: center;
}

/* 主内容区样式 */
.main-content {
  background: var(--el-bg-color);
  height: calc(100vh - 60px);
  overflow: auto;
  color: var(--el-text-color-primary);
}
</style>
