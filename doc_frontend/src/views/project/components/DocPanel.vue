<template>
  <div>
    <div class="toolbar mb-3">
      <el-upload
        :action="`http://127.0.0.1:8000/projects/${projectId}/docs/upload`"
        :headers="uploadHeaders"
        :show-file-list="false"
        :on-success="handleSuccess"
        :on-error="handleError"
      >
        <el-button type="primary">上传文档</el-button>
      </el-upload>
      <el-input v-model="search" placeholder="搜索文件名" style="width: 200px; margin-left: 10px;" />
    </div>

    <el-table :data="filteredDocs" style="width: 100%" v-loading="loading">
      <el-table-column prop="original_filename" label="文件名" />
      <el-table-column prop="size_bytes" label="大小" width="120">
        <template #default="scope">{{ (scope.row.size_bytes / 1024).toFixed(2) }} KB</template>
      </el-table-column>
      <el-table-column prop="created_at" label="上传时间" width="180">
        <template #default="scope">{{ new Date(scope.row.created_at).toLocaleString() }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <!-- 预览/编辑按钮，之后对接 Markdown 编辑器 -->
          <el-button link type="primary" @click="previewDoc(scope.row)">预览/编辑</el-button>
          <el-button link type="danger" @click="deleteDoc(scope.row)">删除</el-button>
          <el-button link type="primary" @click="downloadDoc(scope.row)">下载</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>  
import { useRouter } from 'vue-router'
import { ref, onMounted, computed } from 'vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps(['projectId'])
const docs = ref([])
const loading = ref(false)
const search = ref('')
const router = useRouter()

const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

// 简单的搜索过滤
const filteredDocs = computed(() => {
  return docs.value.filter(d => d.original_filename.toLowerCase().includes(search.value.toLowerCase()))
})

const fetchDocs = async () => {
  loading.value = true
  try {
    // API: GET /projects/{id}/docs/list [1]
    docs.value = await request.get(`/projects/${props.projectId}/docs/list`)
  } finally {
    loading.value = false
  }
}

const handleSuccess = () => {
  ElMessage.success('上传成功')
  fetchDocs()
}

const handleError = (err) => {
  // el-upload 的 error 是个对象，需要解析
  const response = JSON.parse(err.message)
  ElMessage.error(response.detail || '上传失败')
}

const deleteDoc = (row) => {
  ElMessageBox.confirm('确定将该文档移入回收站吗?', '提示', { type: 'warning' })
    .then(async () => {
      // API: DELETE /docs/{id}/delete [1] (注意检查你的后端路径定义，可能是 /projects/.../docs/.../delete 或者 /docs/.../delete)
      // 根据之前的 openapi.json，路径是 /projects/{project_id}/docs/{document_id}/delete [1]
      await request.delete(`/projects/${props.projectId}/docs/${row.id}/delete`)
      ElMessage.success('删除成功')
      fetchDocs()
    })
}

const previewDoc = (row) => {
  // 1. 提示用户
  ElMessage.info(`即将打开: ${row.original_filename}`)
  
  // 2. 直接执行跳转
  router.push({
    name: 'edit-doc',
    params: { 
      id: props.projectId, 
      docId: row.id 
    }
  })
}

const downloadDoc = async (row) => {
  try {
    // We use fetch here to handle the blob response
    const response = await fetch(`http://127.0.0.1:8000/projects/${props.projectId}/docs/${row.id}/download`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = row.original_filename; // Set the filename
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } else {
      ElMessage.error('Download failed');
    }
  } catch (e) {
    console.error(e);
    ElMessage.error('Download error');
  }
}

onMounted(fetchDocs)
</script>

<style scoped>
.toolbar { display: flex; align-items: center; }
.mb-3 { margin-bottom: 15px; }
</style>

