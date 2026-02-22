<template>
  <div class="issue-container" v-loading="loading">
    <el-page-header @back="$router.back()" content="问题详情" class="mb-4" />
    
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h2>{{ issue.title }}</h2>
            <el-tag class="ml-2" :type="issue.status === 'open' ? 'danger' : 'success'">
              {{ issue.status === 'open' ? 'Open' : 'Closed' }}
            </el-tag>
            <el-tag class="ml-2" effect="plain" :type="getPriorityType(issue.priority)">
              {{ issue.priority }}
            </el-tag>
          </div>
          
          <!-- 新增：操作按钮区，使用 v-if="canEdit" 控制显示 -->
          <div class="header-right" v-if="canEdit">
            <el-button 
              v-if="issue.status === 'open'" 
              type="success" 
              plain 
              size="small"
              @click="handleUpdateStatus('closed')"
            >
              关闭问题
            </el-button>
            <el-button 
              v-else 
              type="danger" 
              plain 
              size="small"
              @click="handleUpdateStatus('open')"
            >
              重新打开
            </el-button>
            
            <el-button type="primary" link @click="openEditDialog">编辑内容</el-button>
          </div>
        </div>
      </template>
      
      <div class="content markdown-body" v-html="renderMarkdown(issue.content)"></div>
      
      <!-- 底部元信息 -->
      <div class="issue-meta mt-4">
        <span>提问者: {{ issue.creator_id }}</span> <!-- 如果后端返回了creator对象更好 -->
        <span class="ml-3">时间: {{ new Date(issue.created_at).toLocaleString() }}</span>
      </div>
    </el-card>
    <!-- 评论区保持不变 -->
    <div class="comments-section mt-4">
      <h3>评论 ({{ comments.length }})</h3>
      <div v-for="comment in comments" :key="comment.id" class="comment-item">
        <div class="comment-header">
          <span class="username">{{ comment.user.nickname || comment.user.email }}</span>
          <span class="time">{{ new Date(comment.created_at).toLocaleString() }}</span>
        </div>
        <div class="comment-content">{{ comment.content }}</div>
      </div>
      
      <div class="reply-box mt-4">
        <el-input v-model="newComment" type="textarea" rows="3" placeholder="写下你的评论..." />
        <el-button type="primary" class="mt-2" @click="postComment">回复</el-button>
      </div>
    </div>
    <!-- 新增：编辑内容弹窗 -->
    <el-dialog v-model="editVisible" title="修改问题内容" width="50%">
      <el-form>
        <el-form-item>
          <el-input 
            v-model="editForm.content" 
            type="textarea" 
            rows="6" 
            placeholder="支持 Markdown" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted, computed } from 'vue' // Added computed
import { useRoute } from 'vue-router'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'

const route = useRoute()
const projectId = route.params.id
const issueId = route.params.issueId
const loading = ref(false)
const issue = ref({})
const comments = ref([])
const newComment = ref('')

// Added currentUser and memberRole refs
const currentUser = ref({})
const memberRole = ref('')

// 编辑相关状态
const editVisible = ref(false)
const editForm = reactive({ content: '' })

// Computed property for edit permission
const canEdit = computed(() => {
  if (!issue.value.id || !currentUser.value.id) return false
  
  const isCreator = issue.value.creator_id === currentUser.value.id
  const isAdmin = memberRole.value === 'admin' || memberRole.value === 'owner'
  
  return isCreator || isAdmin
})

const renderMarkdown = (text) => {
    return text ? marked(text) : ''
}

const fetchData = async () => {
  loading.value = true
  try {
    // Parallel requests: issue details, comments, current user, and members list (to find role)
    const [resIssue, resComments, resUser, resMember] = await Promise.all([
      request.get(`/projects/${projectId}/issues/${issueId}`),
      request.get(`/projects/${projectId}/issues/${issueId}/comments`),
      request.get('/auth/me'),
      request.get(`/teams/${projectId}`)
    ])
    
    issue.value = resIssue
    comments.value = resComments
    currentUser.value = resUser
    
    // Find self in members list to get role
    const myMemberInfo = resMember.find(m => m.user_id === resUser.id)
    memberRole.value = myMemberInfo ? myMemberInfo.role : ''

  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

// 1. 修改状态 (关闭/打开)
const handleUpdateStatus = async (newStatus) => {
  try {
    const actionText = newStatus === 'closed' ? '关闭' : '重新打开'
    await ElMessageBox.confirm(`确定要${actionText}这个问题吗？`, '提示', { type: 'warning' })
    
    const formData = new FormData()
    formData.append('new_status', newStatus)
    
    await request.put(`/projects/${projectId}/issues/${issueId}/update`, formData)
    
    ElMessage.success(`已${actionText}`)
    fetchData() // 刷新数据
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

// 2. 打开编辑框
const openEditDialog = () => {
  editForm.content = issue.value.content
  editVisible.value = true
}

// 3. 提交内容修改
const submitEdit = async () => {
  try {
    const formData = new FormData()
    formData.append('new_content', editForm.content)
    
    await request.put(`/projects/${projectId}/issues/${issueId}/update`, formData)
    
    ElMessage.success('修改成功')
    editVisible.value = false
    fetchData()
  } catch (e) {
    console.error(e)
  }
}

const postComment = async () => {
  if (!newComment.value) return
  try {
    await request.post(`/projects/${projectId}/issues/${issueId}/comments`, {
        content: newComment.value
    })
    ElMessage.success('回复成功')
    newComment.value = ''
    fetchData() 
  } catch (e) {
    console.error(e)
  }
}

const getPriorityType = (p) => {
    if (p === 'high') return 'danger'
    if (p === 'medium') return 'warning'
    return 'info'
}

onMounted(fetchData)
</script>
<style scoped>
.issue-container { padding: 20px; max-width: 800px; margin: 0 auto; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; }
.ml-2 { margin-left: 8px; }
.ml-3 { margin-left: 12px; }
.mt-4 { margin-top: 20px; }
.issue-meta { font-size: 12px; color: #909399; border-top: 1px solid #EBEEF5; padding-top: 10px; }
.comment-item { border-bottom: 1px solid #eee; padding: 15px 0; }
.comment-header { color: #666; font-size: 12px; margin-bottom: 5px; }
.username { font-weight: bold; margin-right: 10px; color: #333; }
.mt-2 { margin-top: 10px; }
.mb-4 { margin-bottom: 20px; }
</style>