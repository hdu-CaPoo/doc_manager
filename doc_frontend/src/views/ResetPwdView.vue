<template>
  <div class="auth-container">
    <el-card class="auth-card">
      <h2>重置密码</h2>
      <el-form :model="form" label-width="0">
        <el-form-item>
          <el-input v-model="form.email" placeholder="请输入注册邮箱" />
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
          <el-input v-model="form.new_password" type="password" placeholder="设置新密码" show-password />
        </el-form-item>

        <el-button type="primary" class="w-100 mb-3" @click="handleReset">重置密码</el-button>
        
        <div class="auth-footer center">
          <el-link type="info" @click="$router.push('/login')">返回登录</el-link>
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
// 这里的字段名要对应 OpenAPI 中的 ResetPasswordSchema [1]
const form = reactive({ email: '', verification_code: '', new_password: '' }) 
const timer = ref(0)

const sendCode = async () => {
  if (!form.email) return ElMessage.warning('请先填写邮箱')
  try {
    // 调用发送验证码接口，类型为 reset [1]
    await request.post('/utils/send-verification-code', {
      email: form.email,
      type: 'reset'
    })
    ElMessage.success('验证码已发送')
    timer.value = 60
    const interval = setInterval(() => {
      timer.value--
      if (timer.value <= 0) clearInterval(interval)
    }, 1000)
  } catch (e) {
    console.error(e)
  }
}

const handleReset = async () => {
  if (!form.email || !form.verification_code || !form.new_password) {
    return ElMessage.warning('请填写完整')
  }
  try {
    // 调用重置密码接口 [1]
    await request.post('/auth/reset-password', form)
    ElMessage.success('密码重置成功，请重新登录')
    router.push('/login')
  } catch (e) {
    console.error(e)
  }
}
</script>

<style scoped>
/* 样式与注册页一致 */
.auth-container { display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f2f5; }
.auth-card { width: 400px; padding: 20px; }
.w-100 { width: 100%; }
.mb-3 { margin-bottom: 15px; }
h2 { text-align: center; margin-bottom: 30px; }
.flex-row { display: flex; width: 100%; }
.auth-footer.center { justify-content: center; display: flex; }
</style>