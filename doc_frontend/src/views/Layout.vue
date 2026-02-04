<template>
  <div class="common-layout">
    <el-container>
      <!-- 左侧侧边栏 -->
      <el-aside width="200px" class="aside-menu">
        <div class="logo">
          <h3>凌云文档管理系统</h3>
        </div>
        
        <el-menu
          active-text-color="#409EFF"
          background-color="#304156"
          text-color="#fff"
          :default-active="route.path"
          router
          class="el-menu-vertical"
        >
          <!-- 导航菜单 -->
          <el-menu-item index="/app">
            <el-icon><Menu /></el-icon>
            <span>项目列表</span>
          </el-menu-item>
          
          <el-menu-item index="/app/profile">
            <el-icon><User /></el-icon>
            <span>个人中心</span>
          </el-menu-item>

          <!-- 分割线 -->
          <div style="height: 1px; background: #455a74; margin: 10px 0;"></div>

          <!-- 功能按钮 (注意：这里不设 index，而是绑定点击事件) -->
          <el-menu-item index="" @click="createVisible = true">
            <el-icon><Plus /></el-icon>
            <span>创建项目</span>
          </el-menu-item>

          <el-menu-item index="" @click="joinVisible = true">
            <el-icon><Connection /></el-icon>
            <span>加入项目</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 右侧主体 -->
      <el-container>
        <el-header class="header">
          <div class="breadcrumb">
             <el-breadcrumb separator="/">
                <el-breadcrumb-item :to="{ path: '/app' }">首页</el-breadcrumb-item>
                <el-breadcrumb-item v-if="route.path !== '/app'">
                  {{ route.meta.title || '当前页面' }}
                </el-breadcrumb-item>
             </el-breadcrumb>
          </div>
          <div class="user-info">
            <el-dropdown>
              <span class="el-dropdown-link">
                {{ user.nickname || user.email }}
                <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>

    <!-- 弹窗 1：创建项目 -->
    <el-dialog v-model="createVisible" title="创建新项目" width="30%">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="项目名称">
          <el-input v-model="createForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="createForm.description" type="textarea" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createVisible = false">取消</el-button>
          <el-button type="primary" @click="handleCreateProject">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 弹窗 2：加入项目 -->
    <el-dialog v-model="joinVisible" title="加入项目" width="30%">
      <el-form :model="joinForm" label-width="80px">
        <el-form-item label="邀请码">
          <el-input v-model="joinForm.invitation_code" placeholder="请输入邀请码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="joinVisible = false">取消</el-button>
          <el-button type="primary" @click="handleJoinProject">加入</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'
import { Menu, User, ArrowDown, Plus, Connection } from '@element-plus/icons-vue' // 引入新图标
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const user = ref({})

// 弹窗控制状态
const createVisible = ref(false)
const joinVisible = ref(false)

// 表单数据
const createForm = reactive({ name: '', description: '' })
const joinForm = reactive({ invitation_code: '' })

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const res = await request.get('/auth/me')
    user.value = res
  } catch (e) {
    console.error(e)
  }
}

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

// 1. 处理创建项目
const handleCreateProject = async () => {
  if (!createForm.name) return ElMessage.warning('项目名称不能为空')
  
  try {
    // 调用 POST /projects/ 接口 [1]
    await request.post('/app/projects/', createForm)
    
    ElMessage.success('创建成功')
    createVisible.value = false
    createForm.name = ''
    createForm.description = ''
    
    // 如果在首页，刷新列表 (简单做法是刷新页面，或者使用事件总线/Pinia)
    if (route.path === '/app') {
       window.location.reload()
    } else {
       router.push('/app')
    }
  } catch (e) {
    console.error(e)
  }
}

// 2. 处理加入项目
const handleJoinProject = async () => {
  if (!joinForm.invitation_code) return ElMessage.warning('请输入邀请码')
  
  try {
    // 调用 POST /members/join 接口 [1]
    await request.post('/members/join', { 
        invitation_code: joinForm.invitation_code 
    })
    
    ElMessage.success('加入成功')
    joinVisible.value = false
    joinForm.invitation_code = ''
    
    // 跳转回首页查看新项目
    if (route.path === '/app') {
       window.location.reload()
    } else {
       router.push('/app')
    }
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  fetchUserInfo()
})
</script>

<style scoped>
.common-layout, .el-container { height: 100vh; }
.aside-menu { background-color: #304156; color: #fff; }
.logo { height: 60px; line-height: 60px; text-align: center; font-size: 18px; color: white; background-color: #2b3649; }
.el-menu-vertical { border-right: none; }
.header { background-color: #fff; border-bottom: 1px solid #dcdfe6; display: flex; justify-content: space-between; align-items: center; font-size: 14px; }
.el-dropdown-link { cursor: pointer; display: flex; align-items: center; }
</style>