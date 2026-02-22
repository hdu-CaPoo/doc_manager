<template>
  <div class="project-container" v-loading="loading">
    <div class="project-header">
      <div class="left">
        <h2>{{ project.name }}</h2>
        <p class="desc">{{ project.description || '暂无描述' }}</p>
      </div>
      <div class="right">
        <el-tag type="info">ID: {{ project.id }}</el-tag>
        <el-tag class="ml-2" type="success">创建者ID: {{ project.owner_id }}</el-tag>
        
        <!-- 需求1：只有 Owner 才能看到邀请码 -->
        <el-button 
          v-if="isOwner" 
          class="ml-2" 
          type="primary" 
          plain 
          @click="copyInviteCode"
        >
          邀请码: {{ project.invitation_code }}
        </el-button>

        <el-button 
          v-if="isOwner" 
          class="ml-2" 
          type="danger" 
          @click="handleDeleteProject"
        >
          删除项目
        </el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="mt-4" type="border-card">
      <el-tab-pane label="文档管理" name="docs">
        <DocPanel :projectId="projectId" v-if="activeTab === 'docs'" />
      </el-tab-pane>
      
      <el-tab-pane label="问题反馈" name="issues">
        <IssuePanel :projectId="projectId" v-if="activeTab === 'issues'" />
      </el-tab-pane>
      
      <!-- 需求3：无权限显示“成员列表”，有权限显示“成员管理” -->
      <el-tab-pane :label="canManage ? '成员管理' : '成员列表'" name="members">
        <!-- 将当前用户权限和项目信息传给子组件 -->
        <MemberPanel 
          :projectId="projectId" 
          :currentUser="currentUser"
          :projectOwnerId="project.owner_id"
          v-if="activeTab === 'members'" 
        />
      </el-tab-pane>

      <el-tab-pane label="回收站" name="trash">
        <TrashPanel :projectId="projectId" v-if="activeTab === 'trash'" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router' // 1. 补上 useRouter
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus' // 2. 补上 ElMessageBox

import DocPanel from './components/DocPanel.vue'
import IssuePanel from './components/IssuePanel.vue'
import MemberPanel from './components/MemberPanel.vue'
import TrashPanel from './components/TrashPanel.vue'

const route = useRoute()
const router = useRouter() // 3. 初始化 router 实例
const projectId = route.params.id
const loading = ref(false)
const project = ref({})
const currentUser = ref({})
const members = ref([]) // 我们在这里获取一次成员列表，用于判断自己的身份
const activeTab = ref('docs')

// 1. 判断是否是拥有者
const isOwner = computed(() => {
  return project.value.owner_id === currentUser.value.id
})

// 2. 判断是否是管理员 (在成员列表中查找自己，并看 role 是否为 admin)
const isAdmin = computed(() => {
  const me = members.value.find(m => m.user_id === currentUser.value.id)
  return me && me.role === 'admin'
})

// 3. 是否有管理权限 (Owner 或 Admin)
const canManage = computed(() => isOwner.value || isAdmin.value)

const fetchData = async () => {
  loading.value = true
  try {
    // 并行请求：项目详情、用户信息、成员列表
    const [resProject, resUser, resMembers] = await Promise.all([
      request.get(`/projects/${projectId}`),
      request.get('/auth/me'),
      request.get(`/teams/${projectId}`)
    ])
    
    project.value = resProject
    currentUser.value = resUser
    members.value = resMembers
    
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const copyInviteCode = () => {
  navigator.clipboard.writeText(project.value.invitation_code)
  ElMessage.success('邀请码已复制')
}


const handleDeleteProject = () => {
  ElMessageBox.confirm(
    '确定要删除该项目吗？此操作将永久删除项目及其所有文档、问题和成员关系，无法恢复！',
    '危险操作',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger', // Make the confirm button red for emphasis
    }
  ).then(async () => {
    try {
      // API: DELETE /projects/{project_id}
      await request.delete(`/projects/${projectId}`)
      
      ElMessage.success('项目已删除')
      // Redirect to home page
      router.push('/app')
    } catch (e) {
      console.error(e)
    }
  }).catch(() => {
    // User cancelled
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.project-container { padding: 20px; }
.project-header { 
  background: white; padding: 20px; border-radius: 4px; 
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}
.desc { color: #909399; font-size: 14px; margin-top: 5px; }
.mt-4 { margin-top: 20px; }
.ml-2 { margin-left: 10px; }
</style>