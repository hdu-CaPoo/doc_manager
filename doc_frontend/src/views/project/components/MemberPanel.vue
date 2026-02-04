<template>
  <div> <!-- 添加根 div 包裹，虽然 Vue3 支持多根节点，但在某些情况下可能有问题，加上更保险 -->
    <el-table :data="members" style="width: 100%" v-loading="loading">
      <!-- 修正点 1：只保留这一个昵称列，包含点击查看详情的功能 -->
      <el-table-column label="昵称">
        <template #default="scope">
          <el-button link type="primary" @click="showUserInfo(scope.row.user)">
            {{ scope.row.user.nickname || scope.row.user.email }}
          </el-button>
          <el-tag v-if="scope.row.user_id === currentUser.id" size="small" type="info">我</el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="role" label="角色">
        <template #default="scope">
          <el-tag :type="getRoleTagType(scope.row)">{{ getRoleLabel(scope.row) }}</el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="joined_at" label="加入时间" width="180">
        <template #default="scope">{{ new Date(scope.row.joined_at).toLocaleDateString() }}</template>
      </el-table-column>
      <!-- 需求2：操作列 -->
      <el-table-column label="操作" width="250">
        <template #default="scope">
          <!-- 如果是当前用户自己 -->
          <div v-if="scope.row.user_id === currentUser.id">
              <!-- 退出项目按钮 -->
              <!-- 注意：项目拥有者不能直接退出，需要先转让权限 -->
              <el-button 
                v-if="scope.row.user_id !== projectOwnerId" 
                link 
                type="danger" 
                size="small" 
                @click="handleLeave"
              >
                退出项目
              </el-button>
              <el-tag v-else type="info">拥有者无法直接退出</el-tag>
          </div>

          <!-- 如果是其他用户（之前的管理逻辑） -->
          <div v-else-if="canManageSome">
            
            <!-- 修改权限 (只有 Owner 可见) -->
            <el-dropdown 
              v-if="isMeOwner" 
              trigger="click" 
              class="mr-2"
              @command="(cmd) => handleChangeRole(scope.row, cmd)"
            >
              <el-button link type="primary" size="small">
                调整权限<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="admin" :disabled="scope.row.role === 'admin'">设为管理员</el-dropdown-item>
                  <el-dropdown-item command="member" :disabled="scope.row.role === 'member'">设为普通成员</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <!-- 踢出成员 -->
            <el-button 
              v-if="canKick(scope.row)" 
              link 
              type="danger" 
              size="small" 
              @click="handleKick(scope.row)"
            >
              移除
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
    <!-- 修正点 2：添加查看用户信息的弹窗 -->
    <el-dialog v-model="userInfoVisible" title="成员信息" width="30%">
      <div style="text-align: center;">
        <el-avatar :size="80" :src="selectedUser.avatar_url ? 'http://127.0.0.1:8000' + selectedUser.avatar_url : ''">
            {{ selectedUser.nickname ? selectedUser.nickname.charAt(0).toUpperCase() : 'U' }}
        </el-avatar>
        <h3>{{ selectedUser.nickname || '无昵称' }}</h3>
        <p>{{ selectedUser.email }}</p>
      </div>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted, computed } from 'vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const props = defineProps(['projectId', 'currentUser', 'projectOwnerId'])
const members = ref([])
const loading = ref(false)
const router = useRouter()

// 修正点 3：定义弹窗状态和选中用户变量
const userInfoVisible = ref(false)
const selectedUser = ref({})
// --- 权限计算辅助 ---
// 1. 我是不是 Owner
const isMeOwner = computed(() => props.currentUser.id === props.projectOwnerId)
// 2. 我是不是 Admin (在列表中查找自己)
const isMeAdmin = computed(() => {
  const me = members.value.find(m => m.user_id === props.currentUser.id)
  return me && me.role === 'admin'
})
// 3. 只要是 Owner 或 Admin，就显示操作列
const canManageSome = computed(() => isMeOwner.value || isMeAdmin.value)
// 4. 判断我能否踢某人
const canKick = (targetMember) => {
  // 肯定是不能踢自己的 (模板里已经用 v-if 排除，这里双重保险)
  if (targetMember.user_id === props.currentUser.id) return false
  
  // 如果我是 Owner: 只要对方不是我自己，都能踢 (Owner最大)
  if (isMeOwner.value) return true
  
  // 如果我是 Admin: 只能踢 member，不能踢 admin 或 owner
  if (isMeAdmin.value) {
    if (targetMember.user_id === props.projectOwnerId) return false // 不能踢老板
    if (targetMember.role === 'admin') return false // 不能踢同事
    return true
  }
  
  return false
}
// --- 业务逻辑 ---
const getRoleTagType = (row) => {
  if (row.user_id === props.projectOwnerId) return 'warning' // Owner 用橙色
  if (row.role === 'admin') return 'danger' // Admin 用红色
  return '' // Member 默认蓝色
}
const getRoleLabel = (row) => {
  if (row.user_id === props.projectOwnerId) return '拥有者 (Owner)'
  if (row.role === 'admin') return '管理员'
  return '成员'
}
const fetchMembers = async () => {
  loading.value = true
  try {
    members.value = await request.get(`/members/${props.projectId}`)
  } finally {
    loading.value = false
  }
}
// 修正点 4：添加 showUserInfo 函数
const showUserInfo = (user) => {
  selectedUser.value = user
  userInfoVisible.value = true
}
// 踢人
const handleKick = (row) => {
  ElMessageBox.confirm(`确定要移除成员 ${row.user.nickname || row.user.email} 吗?`, '警告', {
    type: 'warning',
    confirmButtonText: '移除',
    confirmButtonClass: 'el-button--danger'
  }).then(async () => {
    // API: DELETE /members/{project_id}/{user_id} [1]
    await request.delete(`/members/${props.projectId}/${row.user_id}`)
    ElMessage.success('成员已移除')
    fetchMembers()
  })
}
// 改权限
const handleChangeRole = async (row, newRole) => {
  try {
    // API: POST /members/{project_id}/change_role/{user_id}?new_role=xxx [1]
    await request.post(`/members/${props.projectId}/change_role/${row.user_id}`, null, {
      params: { new_role: newRole }
    })
    ElMessage.success('权限修改成功')
    fetchMembers()
  } catch (e) {
    console.error(e)
  }
}

// 处理退出项目
const handleLeave = () => {
  ElMessageBox.confirm('确定要退出该项目吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      // 调用后端 API: POST /members/{project_id}/leave [1]
      await request.post(`/members/${props.projectId}/leave`)
      ElMessage.success('已退出项目')
      // 退出后跳转回首页
      router.push('/app')
    } catch (e) {
      console.error(e)
    }
  }).catch(() => {
    // 取消操作
  })
}

onMounted(fetchMembers)
</script>
<style scoped>
.mr-2 { margin-right: 10px; }
</style>