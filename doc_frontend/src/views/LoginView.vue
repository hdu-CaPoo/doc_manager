<template>
  <div class="auth-container">
    <el-card class="auth-card">
      <h2>凌云文档管理系统-登录</h2>
      <el-form :model="form" label-width="0">
        <el-form-item>
          <el-input v-model="form.username" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-button type="primary" class="w-100 mb-3" @click="handleLogin" :loading="loading">登录</el-button>
        
        <!-- 新增：底部链接 -->
        <div class="auth-footer">
          <el-link type="primary" @click="$router.push('/register')">注册新账号</el-link>
          <el-link type="info" @click="$router.push('/reset-password')">忘记密码？</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import request from '@/utils/request'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

const handleLogin = async () => {
  if (!form.username || !form.password) return ElMessage.warning('请填写完整')
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('username', form.username)
    formData.append('password', form.password)
    // 调用登录接口 [1]
    const res = await request.post('/auth/login', formData)
    localStorage.setItem('token', res.access_token)
    ElMessage.success('登录成功')
    router.push('/app')
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 共用样式 */
.auth-container { display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f2f5; }
.auth-card { width: 400px; padding: 20px; }
.w-100 { width: 100%; }
.mb-3 { margin-bottom: 15px; }
h2 { text-align: center; margin-bottom: 30px; }
/* 底部链接样式 */
.auth-footer { display: flex; justify-content: space-between; margin-top: 10px; }
</style>