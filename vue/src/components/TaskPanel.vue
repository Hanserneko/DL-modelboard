<template>
  <div class="task-panel">
    <div class="header-bar">
      <el-button type="primary" @click="handleCreateBtn">创建任务</el-button>
    </div>
    <el-table :data="tasks.slice((currentPage-1)*pageSize, currentPage*pageSize)" style="width: 100%; margin-top: 16px;">
      <el-table-column prop="id" label="任务ID" width="160" />
      <el-table-column prop="creator" label="发起者" width="130" />
      <el-table-column prop="type" label="任务类型" width="100" />
      <el-table-column prop="date" label="创建时间" width="120" />
      <el-table-column prop="desc" label="描述" />
      <el-table-column label="操作" width="100">
        <template #default="scope">
          <el-button type="text" @click="showDetail(scope.row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div style="margin: 16px 0; text-align: right;">
      <el-pagination
        background
        layout="prev, pager, next"
        :total="total"
        :page-size="pageSize"
        v-model:current-page="currentPage"
      />
    </div>
    <!-- 创建任务对话框 -->
    <el-dialog v-model="dialogVisible" title="创建任务" width="500px">
      <el-form label-width="80px">
        <el-form-item label="类型">
          <el-select v-model="taskType" placeholder="请选择任务类型">
            <el-option label="训练" value="训练" />
            <el-option label="预测" value="预测" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="taskDesc" placeholder="请输入任务描述" />
        </el-form-item>
        <el-form-item label="详细信息">
          <el-input v-model="taskDetail" type="textarea" placeholder="请输入详细信息（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
    <!-- 任务详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="任务详情" width="900px" :show-close="true">
      <div class="task-detail-layout">
        <div class="task-info">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="任务ID">{{ detailTask?.id }}</el-descriptions-item>
            <el-descriptions-item label="发起者">{{ detailTask?.creator }}</el-descriptions-item>
            <el-descriptions-item label="类型">{{ detailTask?.type }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ detailTask?.date }}</el-descriptions-item>
            <el-descriptions-item label="描述">{{ detailTask?.desc }}</el-descriptions-item>
            <el-descriptions-item label="详细信息">{{ detailTask?.detail }}</el-descriptions-item>
          </el-descriptions>
        </div>
        <div class="terminal-output">
          <span style="opacity: 0.6;">print(hello)</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()

// 任务列表数据
const tasks = ref([
  { id: 'T20250625001', creator: '张三', type: '训练', date: '2025-06-25', desc: '训练任务A', detail: '详细信息A' },
  { id: 'T20250625002', creator: '李四', type: '预测', date: '2025-06-24', desc: '预测任务B', detail: '详细信息B' },
  // ...可添加更多数据
])

// 分页相关
const currentPage = ref(1)
const pageSize = ref(5)
const total = ref(tasks.value.length)

// 创建任务对话框
const dialogVisible = ref(false)
const taskType = ref('训练')
const taskDesc = ref('')
const taskDetail = ref('')

// 任务详情对话框
const detailDialogVisible = ref(false)
const detailTask = ref<any>(null)

const handleCreateBtn = () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再创建任务！')
    return
  }
  dialogVisible.value = true
}

const handleCreate = () => {
  if (!taskDesc.value) {
    ElMessage.error('请填写任务描述')
    return
  }
  const newId = `T${new Date().toISOString().replace(/[-:T.]/g, '').slice(0, 12)}`
  tasks.value.unshift({
    id: newId,
    creator: userStore.username || '当前用户',
    type: taskType.value,
    date: new Date().toISOString().slice(0, 10),
    desc: taskDesc.value,
    detail: taskDetail.value || '无详细信息'
  })
  total.value = tasks.value.length
  dialogVisible.value = false
  taskType.value = '训练'
  taskDesc.value = ''
  taskDetail.value = ''
  ElMessage.success('任务创建成功！')
}

const showDetail = (row: any) => {
  detailTask.value = row
  detailDialogVisible.value = true
}
</script>

<style scoped>
.task-panel {
  padding: 16px;
}
.header-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}
.task-detail-layout {
  display: flex;
  flex-direction: row;
  gap: 24px;
  min-height: 220px;
}
.task-info {
  flex: 0 0 320px;
  max-width: 340px;
  min-width: 220px;
}
.terminal-output {
  flex: 1 1 0;
  min-width: 0;
  margin-top: 0;
  min-height: 220px;
  background: #181818;
  border-radius: 6px;
  padding: 12px;
  color: #e0e0e0;
  font-family: 'Fira Mono', 'Consolas', 'Menlo', 'Monaco', 'monospace';
  font-size: 14px;
  line-height: 1.7;
  box-shadow: 0 2px 8px 0 rgba(0,0,0,0.04);
  white-space: pre-wrap;
  display: flex;
  align-items: flex-start;
}
</style>
