<template>
  <div class="dataset-panel">
    <div class="header-bar">
      <el-button type="primary" @click="handleUploadBtn">上传数据集</el-button>
    </div>
    <el-table :data="datasets.slice((currentPage - 1) * pageSize, currentPage * pageSize)" style="width: 100%; margin-top: 16px;" :loading="loading">
      <el-table-column prop="name" label="数据集名称" width="160" />
      <el-table-column prop="uploader" label="上传者" width="130" />
      <el-table-column label="标签">
        <template #default="scope">
          <el-tag v-for="tag in scope.row.tags" :key="tag" style="margin-right: 4px;">{{ tag }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="date" label="上传日期" width="120" />
      <el-table-column prop="desc" label="描述" />
      <el-table-column label="操作" width="100">
        <template #default="scope">
          <el-button v-if="scope.row.uploader === userStore.username" type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div style="margin: 16px 0; text-align: right;">
      <el-pagination background layout="prev, pager, next" :total="total" :page-size="pageSize" v-model:current-page="currentPage" />
    </div>
    <!-- 上传对话框 -->
    <el-dialog v-model="dialogVisible" title="上传数据集" width="500px">
      <el-form label-width="50px">
        <el-form-item label="名称">
          <el-input v-model="uploadName" placeholder="请输入数据集名称" maxlength="20" show-word-limit />
        </el-form-item>
        <el-form-item label="文件">
          <div class="upload-wrapper">
            <el-upload drag action="#" :auto-upload="false" v-model:file-list="uploadFileList" :limit="1"
              :on-remove="(file: any) => uploadFileList.splice(uploadFileList.indexOf(file), 1)"
              :on-change="(_file: any) => uploadFileList.length = 1">
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
              <div class="el-upload__tip">仅支持.zip格式文件</div>
            </el-upload>
          </div>
        </el-form-item>
        <el-form-item label="标签">
          <div style="display: flex; align-items: center; gap: 8px; width: 100%;">
            <el-select v-model="uploadTags" multiple placeholder="请选择标签" filterable style="flex:1">
              <el-option v-for="item in tagOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
            <el-button type="primary" size="small" @click="addTagDialogVisible = true">添加标签</el-button>
          </div>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="uploadDesc" type="textarea" placeholder="请输入描述" maxlength="100" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpload">上传</el-button>
      </template>
    </el-dialog>
    <!-- 添加标签弹窗 -->
    <el-dialog v-model="addTagDialogVisible" title="添加新标签" width="350px">
      <el-input v-model="newTagInput" placeholder="请输入新标签" @keyup.enter="handleAddTag" />
      <template #footer>
        <el-button @click="addTagDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddTag">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '../stores/user'
import { UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'

const userStore = useUserStore()

const datasets = ref<any[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(5)
const total = ref(0)

const dialogVisible = ref(false)
const uploadFileList = ref<any[]>([])
const uploadDesc = ref('')
const uploadTags = ref<string[]>([])
const uploadName = ref('')

const tagOptions = ref<{ label: string, value: string }[]>([])
const addTagDialogVisible = ref(false)
const newTagInput = ref('')

const fetchTags = async () => {
  try {
    const res = await axios.get('/api/tags')
    if (res.data.success) {
      tagOptions.value = res.data.data.map((t: string) => ({ label: t, value: t }))
    }
  } catch (e) {
    // 忽略
  }
}

const fetchDatasets = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/datasets')
    datasets.value = res.data.data || res.data || []
    total.value = res.data.total || datasets.value.length
  } catch (e) {
    ElMessage.error('获取数据集列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchTags()
  fetchDatasets()
})

const handleUploadBtn = () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再上传数据集！')
    return
  }
  dialogVisible.value = true
}

const addTagToLibrary = async (tag: string) => {
  try {
    await axios.post('/api/add_tag', { tag })
    fetchTags()
  } catch { }
}

const handleAddTag = async () => {
  const tag = newTagInput.value.trim()
  if (!tag) {
    ElMessage.warning('请输入标签')
    return
  }
  await addTagToLibrary(tag)
  newTagInput.value = ''
  addTagDialogVisible.value = false
  ElMessage.success('标签已添加')
}

const handleUpload = async () => {
  if (!uploadName.value || uploadFileList.value.length === 0) {
    ElMessage.error('请填写名称并上传文件')
    return
  }
  const formData = new FormData()
  formData.append('name', uploadName.value)
  formData.append('desc', uploadDesc.value)
  formData.append('tags', JSON.stringify(uploadTags.value))
  formData.append('uploader', userStore.username || '当前用户')
  formData.append('file', uploadFileList.value[0].raw)
  try {
    await axios.post('/api/upload_dataset', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success('上传成功！')
    dialogVisible.value = false
    uploadFileList.value = []
    uploadDesc.value = ''
    uploadTags.value = []
    uploadName.value = ''
    fetchDatasets()
    fetchTags()
  } catch (e: any) {
    ElMessage.error('上传失败: ' + (e.response?.data?.message || e.message || '未知错误'))
  }
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm('确定要删除该数据集吗？', '提示', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await axios.post('/api/delete_dataset', { id: row.id, username: userStore.username })
      ElMessage.success('删除成功')
      fetchDatasets()
    } catch (e: any) {
      ElMessage.error('删除失败: ' + (e.response?.data?.message || e.message || '未知错误'))
    }
  }).catch(() => { })
}
</script>

<style scoped>
.dataset-panel {
  padding: 16px;
}

.header-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.upload-wrapper {
  width: 100%;
}

.upload-wrapper .el-upload {
  width: 100%;
}
</style>
