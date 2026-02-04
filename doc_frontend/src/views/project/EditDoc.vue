<template>
  <div class="editor-container">
    <div class="toolbar">
      <div class="left">
        <el-button @click="$router.back()">返回</el-button>
        <span class="file-name ml-3">{{ fileName }}</span>
      </div>
      <div class="right">
        <span class="status-text mr-3">{{ statusText }}</span>
        <el-button type="primary" @click="saveContent" :loading="saving">保存 (Ctrl+S)</el-button>
      </div>
    </div>
    
    <!-- 编辑器挂载点 -->
    <div id="vditor" class="editor-main"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import request from '@/utils/request'
import Vditor from 'vditor'
import 'vditor/dist/index.css'
import { ElMessage } from 'element-plus'

const route = useRoute()
const projectId = route.params.id
const docId = route.params.docId

const vditor = ref(null)
const fileName = ref('加载中...')
const statusText = ref('')
const saving = ref(false)

// 初始化编辑器
const initVditor = () => {
  vditor.value = new Vditor('vditor', {
    height: 'calc(100vh - 80px)', // 减去头部高度
    width: '100%',
    placeholder: '在此输入 Markdown 内容...',
    mode: 'ir', // 即时渲染模式 (所见即所得)
    toolbarConfig: {
      pin: true,
    },
    cache: {
      enable: false,
    },
    after: () => {
      // 编辑器加载完毕后，去后端拉取内容
      loadContent()
    },
    // 监听 Ctrl+S
    ctrlEnter: (value) => {
      saveContent()
    },
    input: (value) => {
      statusText.value = '有未保存的修改...'
    }
  })
}

// 获取文档内容
const loadContent = async () => {
  try {
    // 1. 先获取文档列表拿到文件名 (可选，为了显示文件名)
    // 这里偷懒直接请求内容，文件名可以后续优化
    fileName.value = `文档 ID: ${docId}`

    // 2. 获取内容
    // API: GET /projects/{project_id}/docs/{document_id}/content
    const res = await request.get(`/projects/${projectId}/docs/${docId}/content`)
    
    // 填充到编辑器
    vditor.value.setValue(res.content || '')
    statusText.value = '已加载最新内容'
  } catch (e) {
    console.error(e)
    ElMessage.error('读取内容失败')
  }
}

// 保存文档
const saveContent = async () => {
  if (!vditor.value) return
  saving.value = true
  statusText.value = '正在保存...'
  
  try {
    const content = vditor.value.getValue()
    
    // API: PUT /projects/{project_id}/docs/{document_id}/content
    // Body: { "content": "..." }
    await request.put(`/projects/${projectId}/docs/${docId}/content`, {
      content: content
    })
    
    statusText.value = '保存成功 ' + new Date().toLocaleTimeString()
    ElMessage.success('保存成功')
  } catch (e) {
    console.error(e)
    statusText.value = '保存失败'
  } finally {
    saving.value = false
  }
}

// 快捷键监听
const handleKeydown = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault()
    saveContent()
  }
}

onMounted(() => {
  initVditor()
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
  if (vditor.value) {
    vditor.value.destroy()
  }
})
</script>

<style scoped>
.editor-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: white;
}

.toolbar {
  height: 60px;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background-color: #f5f7fa;
}

.file-name {
  font-weight: bold;
  color: #303133;
}

.status-text {
  font-size: 12px;
  color: #909399;
}

.ml-3 { margin-left: 12px; }
.mr-3 { margin-right: 12px; }
</style>