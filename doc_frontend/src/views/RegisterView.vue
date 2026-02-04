<template>
  <div class="auth-container">
    <el-card class="auth-card">
      <h2>注册账号</h2>
      <el-form :model="form" label-width="0">
        <el-form-item>
          <el-input v-model="form.email" placeholder="邮箱" />
        </el-form-item>
        
        <el-form-item>
          <div class="flex-row">
            <el-input v-model="form.verification_code" placeholder="验证码" style="flex: 1; margin-right: 10px;" />
            <el-button @click="sendCode" :disabled="timer > 0">
              {{ timer > 0 ? `${timer}s后重发` : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>

        <el-form-item>
          <el-input v-model="form.nickname" placeholder="昵称 (可选)" />
        </el-form-item>

        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="设置密码" show-password />
        </el-form-item>

        <el-button type="primary" class="w-100 mb-3" @click="handleRegister">立即注册</el-button>
        
        <div class="auth-footer center">
          <el-link type="info" @click="$router.push('/login')">已有账号？去登录</el-link>
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
const form = reactive({ email: '', verification_code: '', password: '', nickname: '' })
const timer = ref(0)

// 发送验证码
const sendCode = async () => {
  if (!form.email) return ElMessage.warning('请先填写邮箱')
  try {
    // 调用发送验证码接口，类型为 register [1]
    await request.post('/utils/send-verification-code', {
      email: form.email,
      type: 'register'
    })
    ElMessage.success('验证码已发送')
    // 倒计时逻辑
    timer.value = 60
    const interval = setInterval(() => {
      timer.value--
      if (timer.value <= 0) clearInterval(interval)
    }, 1000)
  } catch (e) {
    console.error(e)
  }
}

// 注册
const handleRegister = async () => {
  if (!form.email || !form.verification_code || !form.password) {
    return ElMessage.warning('请填写必填项')
  }
  try {
    // 调用注册接口 [1]
    await request.post('/auth/register', form)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (e) {
    console.error(e)
  }
}
</script>

<style scoped>
.auth-container { display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f2f5; }
.auth-card { width: 400px; padding: 20px; }
.w-100 { width: 100%; }
.mb-3 { margin-bottom: 15px; }
h2 { text-align: center; margin-bottom: 30px; }
.flex-row { display: flex; width: 100%; }
.auth-footer.center { justify-content: center; display: flex; }
</style>