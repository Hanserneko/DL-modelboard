<template>
  <div class="model-panel">
    <div class="header-bar">
      <el-button type="primary" @click="handleUploadBtn">上传模型</el-button>
    </div>
    <el-table :data="models.slice((currentPage-1)*pageSize, currentPage*pageSize)" style="width: 100%; margin-top: 16px;">
      <el-table-column prop="name" label="模型名称" width="180" />
      <el-table-column prop="uploader" label="上传者" width="120" />
      <el-table-column label="标签">
        <template #default="scope">
          <el-tag v-for="tag in scope.row.tags" :key="tag" style="margin-right: 4px;">{{ tag }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="需求">
        <template #default="scope">
          <el-tag v-for="need in scope.row.needs" :key="need" type="success" style="margin-right: 4px;">{{ need }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="date" label="上传日期" width="120" />
      <el-table-column prop="desc" label="描述" />
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
    <!-- 上传对话框 -->
    <el-dialog v-model="dialogVisible" title="上传模型" width="500px">
      <el-form label-width="50px">
        <el-form-item label="名称">
          <el-input v-model="uploadName" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="文件">
          <div class="upload-wrapper">
            <el-upload
              drag
              action="#"
              :auto-upload="false"
              v-model:file-list="uploadFileList"
              :limit="1"
              :on-remove="(file: any) => uploadFileList.splice(uploadFileList.indexOf(file), 1)"
              :on-change="(_file: any) => uploadFileList.length = 1"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
              <div class="el-upload__tip">仅支持.zip格式文件</div>
            </el-upload>
          </div>
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="uploadTags" multiple placeholder="请选择标签">
            <el-option v-for="item in tagOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="需求">
          <el-select v-model="uploadNeeds" multiple placeholder="请选择需求标签">
            <el-option v-for="item in needOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="uploadDesc" type="textarea" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpload">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'
import { UploadFilled } from '@element-plus/icons-vue'

const userStore = useUserStore()

// 模型列表数据 测试
const models = ref([
  { name: '模型A', uploader: '张三', tags: ['分类', '公开'], needs: ['高精度'], date: '2025-06-01', desc: '示例模型A' },
  { name: '模型B', uploader: '李四', tags: ['回归'], needs: ['低延迟'], date: '2025-06-10', desc: '示例模型B' },
  { name: '模型C', uploader: '王五', tags: ['聚类', '私有'], needs: ['大数据'], date: '2025-06-15', desc: '示例模型C' },
  // ...可添加更多数据
])

// 分页相关
const currentPage = ref(1)
const pageSize = ref(5)
const total = ref(models.value.length)

// 上传对话框
const dialogVisible = ref(false)
const uploadFileList = ref<any[]>([])
const uploadDesc = ref('')
const uploadTags = ref([])
const uploadNeeds = ref([])
const uploadName = ref('')

const tagOptions = [
  { label: '分类', value: '分类' },
  { label: '回归', value: '回归' },
  { label: '聚类', value: '聚类' },
  { label: '公开', value: '公开' },
  { label: '私有', value: '私有' },
]

const needOptions = [
  { label: '高精度', value: '高精度' },
  { label: '低延迟', value: '低延迟' },
  { label: '大数据', value: '大数据' },
  { label: '易部署', value: '易部署' },
  { label: '可解释性', value: '可解释性' },
]

const handleUploadBtn = () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再上传模型！')
    return
  }
  dialogVisible.value = true
}

const handleUpload = () => {
  if (!uploadName.value || uploadFileList.value.length === 0) {
    ElMessage.error('请填写名称并上传文件')
    return
  }
  models.value.unshift({
    name: uploadName.value,
    uploader: userStore.username || '当前用户',
    tags: [...uploadTags.value],
    needs: [...uploadNeeds.value],
    date: new Date().toISOString().slice(0, 10),
    desc: uploadDesc.value
  })
  total.value = models.value.length
  dialogVisible.value = false
  uploadFileList.value = []
  uploadDesc.value = ''
  uploadTags.value = []
  uploadNeeds.value = []
  uploadName.value = ''
  ElMessage.success('上传成功！')
}
</script>

<style scoped>
.model-panel {
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
