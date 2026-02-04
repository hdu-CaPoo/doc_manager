<template>
  <div class="issue-container" v-loading="loading">
    <el-page-header @back="$router.back()" content="问题详情" class="mb-4" />
    
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>{{ issue.title }}</h2>
          <el-tag :type="issue.status === 'open' ? 'danger' : 'success'">{{ issue.status }}</el-tag>
        </div>
      </template>
      <div class="content markdown-body" v-html="renderMarkdown(issue.content)"></div>
    </el-card>

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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { marked } from 'marked' // You need to install marked: npm install marked

const route = useRoute()
const projectId = route.params.id
const issueId = route.params.issueId
const loading = ref(false)
const issue = ref({})
const comments = ref([])
const newComment = ref('')

const renderMarkdown = (text) => {
    return text ? marked(text) : ''
}

const fetchData = async () => {
  loading.value = true
  try {
    const [resIssue, resComments] = await Promise.all([
      request.get(`/projects/${projectId}/issues/${issueId}`),
      request.get(`/projects/${projectId}/issues/${issueId}/comments`)
    ])
    issue.value = resIssue
    comments.value = resComments
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
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
    fetchData() // Reload comments
  } catch (e) {
    console.error(e)
  }
}

onMounted(fetchData)
</script>

<style scoped>
.issue-container { padding: 20px; max-width: 800px; margin: 0 auto; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.comment-item { border-bottom: 1px solid #eee; padding: 15px 0; }
.comment-header { color: #666; font-size: 12px; margin-bottom: 5px; }
.username { font-weight: bold; margin-right: 10px; color: #333; }
.mt-4 { margin-top: 20px; }
.mt-2 { margin-top: 10px; }
.mb-4 { margin-bottom: 20px; }
</style>