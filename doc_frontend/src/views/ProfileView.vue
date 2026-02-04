<template>
  <div class="profile-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>个人中心</span>
        </div>
      </template>
      
      <div class="user-info">
        <!-- 头像区域 -->
        <div class="avatar-section">
          <el-avatar :size="100" :src="avatarUrl" class="mb-4">
            <!-- 如果没有头像，显示默认文字 -->
            {{ user.nickname ? user.nickname.charAt(0).toUpperCase() : 'U' }}
          </el-avatar>
          
          <!-- 上传组件 -->
          <!-- action: 后端接口地址 -->
          <!-- headers: 必须手动带 Token，因为 el-upload 不走我们封装的 axios -->
          <el-upload
            class="avatar-uploader"
            action="http://127.0.0.1:8000/users/me/avatar"
            :headers="uploadHeaders"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload"
            name="file" 
          >
            <el-button type="primary" size="small">更换头像</el-button>
          </el-upload>
        </div>

        <el-divider />

        <!-- 基本信息 -->
        <el-descriptions title="账户信息" :column="1" border>
          <el-descriptions-item label="用户ID">{{ user.id }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ user.email }}</el-descriptions-item>
          <el-descriptions-item label="昵称">{{ user.nickname || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="注册时间">{{ formatDate(user.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="角色">
            <el-tag :type="user.is_superuser ? 'danger' : 'info'">
              {{ user.is_superuser ? '超级管理员' : '普通用户' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const user = ref({})

// 1. 计算头像的完整 URL
// 后端存的是 /static/avatars/xxx.jpg，我们需要拼接上 http://127.0.0.1:8000
const avatarUrl = computed(() => {
  if (user.value.avatar_url) {
    return 'http://127.0.0.1:8000' + user.value.avatar_url
  }
  return ''
})

// 2. 上传所需的 Headers (Token)
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

// 3. 获取用户信息
const fetchUser = async () => {
  try {
    // 假设后端有这个接口，通常是 /auth/me 或者 /users/me
    // 如果没有专门的 me 接口，你可能需要用登录时返回的信息，或者解码 Token
    // 这里我们暂时复用之前提到的 /auth/me，确保你后端实现了它
    const res = await request.get('/auth/me') 
    user.value = res
  } catch (e) {
    console.error(e)
  }
}

// 4. 上传成功回调
const handleAvatarSuccess = (response) => {
  ElMessage.success('头像上传成功')
  // response 是后端返回的 UserOut 对象 [1]，里面包含了新的 avatar_url
  user.value.avatar_url = response.avatar_url
}

// 5. 上传前校验
const beforeAvatarUpload = (rawFile) => {
  if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png') {
    ElMessage.error('头像必须是 JPG 或 PNG 格式!')
    return false
  } else if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('头像大小不能超过 2MB!')
    return false
  }
  return true
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

onMounted(() => {
  fetchUser()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
  display: flex;
  justify-content: center;
}
.box-card {
  width: 600px;
}
.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}
.mb-4 {
  margin-bottom: 16px;
}
</style>