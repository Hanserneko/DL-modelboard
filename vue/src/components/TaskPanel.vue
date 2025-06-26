<template>
  <div class="task-panel">
    <div class="header-bar">
      <el-button type="primary" @click="handleCreateBtn">创建任务</el-button>
    </div>
    <el-table :data="tasks.slice((currentPage-1)*pageSize, currentPage*pageSize)" style="width: 100%; margin-top: 16px;">
      <el-table-column prop="id" label="任务ID" width="160" />
      <el-table-column prop="creator" label="发起者" width="130" />
      <el-table-column prop="type" label="任务类型" width="100" />
      <el-table-column prop="modelName" label="模型" width="120" />
      <el-table-column prop="datasetName" label="数据集" width="120" />
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
    <el-dialog v-model="dialogVisible" title="创建任务" width="600px">
      <el-form label-width="90px">
        <el-form-item label="类型">
          <el-select v-model="taskType" placeholder="请选择任务类型" @change="onTaskTypeChange">
            <el-option label="训练" value="train" />
            <el-option label="预测" value="predict" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择模型">
          <el-select v-model="selectedModel" filterable placeholder="请选择模型" @change="onModelChange">
            <el-option v-for="m in modelOptions" :key="m.id" :label="m.name" :value="m.id">
              <div style="display:flex;justify-content:space-between;align-items:center;width:100%">
                <span>{{ m.name }}</span>
                <span>
                  <el-tag v-for="tag in m.needs" :key="tag" size="small" style="margin-left:4px;">{{ tag }}</el-tag>
                </span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item v-if="taskType==='train'" label="选择数据集">
          <el-select v-model="selectedDataset" filterable placeholder="请选择数据集" :disabled="!selectedModel">
            <el-option v-for="d in filteredDatasetOptions" :key="d.id" :label="d.name" :value="d.id">
              <div style="display:flex;justify-content:space-between;align-items:center;width:100%">
                <span>{{ d.name }}</span>
                <span>
                  <el-tag v-for="tag in d.tags" :key="tag" size="small" style="margin-left:4px;">{{ tag }}</el-tag>
                </span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item v-if="taskType==='predict'" label="预测数据集">
          <el-select v-model="selectedDataset" filterable placeholder="选择已有数据集" :disabled="!selectedModel">
            <el-option v-for="d in filteredDatasetOptions" :key="d.id" :label="d.name" :value="d.id">
              <div style="display:flex;justify-content:space-between;align-items:center;width:100%">
                <span>{{ d.name }}</span>
                <span>
                  <el-tag v-for="tag in d.tags" :key="tag" size="small" style="margin-left:4px;">{{ tag }}</el-tag>
                </span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="参数配置">
          <el-input v-model="taskParam" placeholder="参数配置（预留）" disabled />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="taskDesc" placeholder="请输入任务描述" />
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
            <el-descriptions-item label="模型">{{ detailTask?.modelName }}</el-descriptions-item>
            <el-descriptions-item label="数据集">{{ detailTask?.datasetName }}</el-descriptions-item>
            <el-descriptions-item label="参数">{{ detailTask?.param || '（预留）' }}</el-descriptions-item>
            <el-descriptions-item label="描述">{{ detailTask?.desc }}</el-descriptions-item>
            <el-descriptions-item label="详细信息">{{ detailTask?.detail }}</el-descriptions-item>
          </el-descriptions>
          <div v-if="detailTask && detailTask.creator === userStore.username" style="margin-top: 16px; text-align: right;">
            <el-button type="danger" @click="handleDelete(detailTask)">删除任务</el-button>
          </div>
        </div>
        <div class="terminal-output">
          <span style="opacity: 0.6;">（终端输出预留）</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '../stores/user'
import axios from 'axios'

const userStore = useUserStore()

const tasks = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(5)
const total = ref(0)

const dialogVisible = ref(false)
const taskType = ref<'train'|'predict'>('train')
const taskDesc = ref('')
const taskDetail = ref('')
const taskParam = ref('') // 预留参数
const selectedModel = ref()
const selectedDataset = ref()
const selectedParam = ref()

const modelOptions = ref<any[]>([])
const datasetOptions = ref<any[]>([])
const paramOptions = ref<any[]>([])

const addTagDialogVisible = ref(false)
const newTagInput = ref('')

const detailDialogVisible = ref(false)
const detailTask = ref<any>(null)

const filteredDatasetOptions = computed(() => {
  if (!selectedModel.value) return datasetOptions.value
  const model = modelOptions.value.find(m => m.id === selectedModel.value)
  if (!model || !model.needs?.length) return datasetOptions.value
  // 训练任务：只返回不含“预测”标签且包含所有需求标签的数据集
  if (taskType.value === 'train') {
    return datasetOptions.value.filter(d => !d.tags?.includes('预测') && model.needs.every((need: string) => d.tags?.includes(need)))
  }
  // 预测任务：只返回含“预测”标签且包含所有需求标签的数据集
  if (taskType.value === 'predict') {
    return datasetOptions.value.filter(d => d.tags?.includes('预测') && model.needs.every((need: string) => d.tags?.includes(need)))
  }
  return datasetOptions.value
})

const onModelChange = () => {
  // 训练参数/数据集联动，参数选项预留
  selectedDataset.value = undefined
  selectedParam.value = undefined
  // paramOptions.value = ... // 预留
}

const onTaskTypeChange = () => {
  selectedModel.value = undefined
  selectedDataset.value = undefined
  selectedParam.value = undefined
}

const fetchModels = async () => {
  try {
    const res = await axios.get('/api/models')
    modelOptions.value = res.data.data || []
  } catch {}
}
const fetchDatasets = async () => {
  try {
    const res = await axios.get('/api/datasets')
    datasetOptions.value = res.data.data || []
  } catch {}
}
const fetchTasks = async () => {
  // 预留后端接口
  // const res = await axios.get('/api/tasks')
  // tasks.value = res.data.data || []
  // total.value = res.data.total || tasks.value.length
}
onMounted(() => {
  fetchModels()
  fetchDatasets()
  fetchTasks()
})

const handleCreateBtn = () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再创建任务！')
    return
  }
  dialogVisible.value = true
}

const handleCreate = () => {
  if (!selectedModel.value) {
    ElMessage.error('请选择模型')
    return
  }
  if (taskType.value === 'train' && !selectedDataset.value) {
    ElMessage.error('请选择数据集')
    return
  }
  if (taskType.value === 'predict' && !selectedParam.value) {
    ElMessage.error('请选择训练参数')
    return
  }
  // 预测时数据集只能选filteredDatasetOptions中的
  if (taskType.value === 'predict' && !selectedDataset.value) {
    ElMessage.error('请选择预测数据集')
    return
  }
  if (taskType.value === 'predict' && selectedDataset.value) {
    const validIds = filteredDatasetOptions.value.map(d => d.id)
    if (!validIds.includes(selectedDataset.value)) {
      ElMessage.error('请选择符合要求的数据集')
      return
    }
  }
  const newId = `T${new Date().toISOString().replace(/[-:T.]/g, '').slice(0, 12)}`
  tasks.value.unshift({
    id: newId,
    creator: userStore.username || '当前用户',
    type: taskType.value === 'train' ? '训练' : '预测',
    modelName: modelOptions.value.find(m => m.id === selectedModel.value)?.name || '',
    datasetName: datasetOptions.value.find(d => d.id === selectedDataset.value)?.name || '',
    date: new Date().toISOString().slice(0, 10),
    desc: taskDesc.value,
    param: taskParam.value,
    detail: taskDetail.value || '无详细信息'
  })
  total.value = tasks.value.length
  dialogVisible.value = false
  taskType.value = 'train'
  taskDesc.value = ''
  taskDetail.value = ''
  taskParam.value = ''
  selectedModel.value = undefined
  selectedDataset.value = undefined
  selectedParam.value = undefined
  ElMessage.success('任务创建成功！（仅前端模拟）')
}

const showDetail = (row: any) => {
  detailTask.value = row
  detailDialogVisible.value = true
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm('确定要删除该任务吗？', '提示', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    tasks.value = tasks.value.filter(t => t.id !== row.id)
    total.value = tasks.value.length
    ElMessage.success('删除成功')
  }).catch(() => {})
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
